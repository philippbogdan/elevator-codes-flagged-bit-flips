"""Phase-flip (X-memory) logical error model built from simulations.

p_rep(d, p): per-round logical error of the isolated repetition code with the elevator's
             inner round (PyMatching), fitted to   log p_rep = a0 + a1 log p + h * (b0 + b1 log p + b2 log^2 p)
             with h = (d + 1) / 2  (an effective threshold and slope that may drift with p).
c          : ratio between the elevator X memory (per round, per block: p_ZL k / n_b) and
             p_rep at the same (d, p), fitted as log c = c0 + c1 log p + c2 h.
p_ZL(d, p) = (n_b / k) * c(d, p) * p_rep(d, p).
Every fit reports held-out checks (points left out of the fit and predicted).
"""
from __future__ import annotations

import glob
import json
import os

import numpy as np

from .decode import wilson


def load_rep(dirpath: str) -> list[dict]:
    rows = []
    for fn in glob.glob(os.path.join(dirpath, "*.json")):
        st = json.load(open(fn))
        sp = st["spec"]
        if not st["shots"] or st["fails"] == 0:
            continue
        P = st["fails"] / st["shots"]
        R = st["rounds"]
        lo, hi = wilson(st["fails"], st["shots"])
        conv = lambda x: 1 - (1 - x) ** (1 / R)
        rows.append(dict(d=sp["d"], p=sp["p_z"], fails=st["fails"], shots=st["shots"], R=R,
                         y=conv(P), lo=conv(lo), hi=conv(hi)))
    return rows


def load_elev_x(dirs) -> list[dict]:
    """Elevator X memory results (per round, per logical qubit) from task result dirs."""
    if isinstance(dirs, str):
        dirs = [dirs]
    rows = []
    for dd in dirs:
        for fn in glob.glob(os.path.join(dd, "*.json")):
            st = json.load(open(fn))
            sp = st["spec"]
            if sp.get("memory") != "X" or not st["shots"] or st["fails"] == 0:
                continue
            R, k = st["rounds"], st["k"]
            conv = lambda x: 1 - (1 - x) ** (1 / (R * k))
            P = st["fails"] / st["shots"]
            lo, hi = wilson(st["fails"], st["shots"])
            rows.append(dict(code=sp["code"], n_anc=sp["n_anc"], d=sp["d"], p=sp["p_z"],
                             anc_scale=float(sp.get("anc_scale", 1.0)),
                             variant=sp.get("variant"), idle=",".join(sp.get("idle_ctx", [])),
                             compress=sp.get("compress", False), decoder=sp["decoder"]["name"]
                             + ("-ms" if sp["decoder"].get("bp_method") == "minimum_sum" else ""),
                             fails=st["fails"], shots=st["shots"], y=conv(P), lo=conv(lo), hi=conv(hi)))
    return rows


def _design_rep(d, p):
    h = (np.asarray(d) + 1) / 2
    lp = np.log(np.asarray(p))
    return np.stack([np.ones_like(lp), lp, h, h * lp, h * lp ** 2], axis=1)


class RepModel:
    def __init__(self, rows, weights="poisson"):
        d = np.array([r["d"] for r in rows])
        p = np.array([r["p"] for r in rows])
        y = np.log(np.array([r["y"] for r in rows]))
        # weight by inverse variance of log y (~ 1/fails)
        w = np.array([r["fails"] for r in rows], dtype=float)
        X = _design_rep(d, p)
        W = np.sqrt(w)[:, None]
        coef, *_ = np.linalg.lstsq(X * W, y * W.ravel(), rcond=None)
        self.coef = coef
        resid = (y - X @ coef)
        self.rms = float(np.sqrt(np.sum(w * resid ** 2) / np.sum(w)))
        # parameter covariance (for prediction intervals)
        dof = max(len(y) - X.shape[1], 1)
        s2 = float(np.sum(w * resid ** 2) / dof)
        self.cov = s2 * np.linalg.pinv((X * W).T @ (X * W))

    def log_predict(self, d, p):
        X = _design_rep(np.atleast_1d(d), np.atleast_1d(p))
        mu = X @ self.coef
        var = np.einsum("ij,jk,ik->i", X, self.cov, X)
        return mu, np.sqrt(np.maximum(var, 0))

    def predict(self, d, p):
        mu, _ = self.log_predict(d, p)
        out = np.exp(mu)
        return float(out[0]) if np.ndim(d) == 0 and np.ndim(p) == 0 else out


def fit_ratio(elev_rows, rep_model: RepModel, nb_over_k: dict):
    """log c = c0 + c1 log p + c2 h, from elevator X-memory points."""
    X, y, w = [], [], []
    for r in elev_rows:
        nbk = nb_over_k[(r["code"], r["n_anc"])]
        pr = float(rep_model.predict(r["d"], r["p"]))
        c = r["y"] / (nbk * pr)
        h = (r["d"] + 1) / 2
        X.append([1.0, np.log(r["p"]), h])
        y.append(np.log(c))
        w.append(r["fails"])
    X, y, w = np.array(X), np.array(y), np.array(w, float)
    W = np.sqrt(w)[:, None]
    coef, *_ = np.linalg.lstsq(X * W, y * W.ravel(), rcond=None)
    resid = y - X @ coef
    dof = max(len(y) - 3, 1)
    s2 = float(np.sum(w * resid ** 2) / dof)
    cov = s2 * np.linalg.pinv((X * W).T @ (X * W))
    return coef, cov, resid


def sweep_fraction(n: int, d: int) -> float:
    """Fraction of an ancilla's lifetime spent sweeping (when its phase flips can reach a strict
    subset of a check's blocks): n + 1 rounds of a check that lasts max(n + 1, d) rounds."""
    return min(1.0, (n + 1) / max(n + 1, d))


def fit_two_component(elev_rows, rep_model: RepModel, nb_k: dict, data_only_rows=None):
    """p_ZL k = n a p_rep(d, p) + n_anc g s(d) p_rep(d, kappa p): the n data blocks behave like isolated
    repetition codes (factor a), each moving ancilla like one at kappa times the noise (weight g)
    during the sweeping fraction s(d) of its lifetime.
    Weighted least squares on log p_ZL over (a, g, kappa); data_only_rows (ancilla noise off)
    constrain a directly."""
    from scipy.optimize import least_squares

    rows = list(elev_rows)
    def model(theta, r, anc=True):
        la, lg, lk = theta
        n, k = nb_k[(r["code"], r["n_anc"])]
        pr = rep_model.predict(r["d"], r["p"])
        val = n * np.exp(la) * pr
        if anc:
            val += r["n_anc"] * np.exp(lg) * sweep_fraction(n, r["d"]) * rep_model.predict(r["d"], np.exp(lk) * r["p"])
        return val / k

    def resid(theta):
        out = []
        for r in rows:
            out.append(np.sqrt(r["fails"]) * (np.log(model(theta, r)) - np.log(r["y"])))
        for r in (data_only_rows or []):
            out.append(np.sqrt(r["fails"]) * (np.log(model(theta, r, anc=False)) - np.log(r["y"])))
        return np.array(out)

    sol = least_squares(resid, x0=np.array([0.0, 0.0, np.log(1.5)]))
    J = sol.jac
    dof = max(len(sol.fun) - 3, 1)
    s2 = float(np.sum(sol.fun ** 2) / dof)
    cov = s2 * np.linalg.pinv(J.T @ J)
    return sol.x, cov, model
