"""Rigorous upper bounds ("caps") on the stratum failure probabilities F(a, b) of the most-likely-error
decoder, from the code's circuit-level distance and the decoder's own cost structure — no decoding.

Setting: exactly timed flags, no false flags, erasure events (a flagged event's X has probability 1/2),
the exclusive-window MLE decoder of elevator/flags.py.  Stratum (a, b): a unflagged X errors, b flagged
events.

Argument.  The decoder minimises  sum_c w_c x_c + sum_W v_{W,c} y_{W,c}  over explanations of the
syndrome; with exact timing every flagged window is one location and every v = log(pi_0 / pi_c) = 0
(X or no X, probability 1/2 each).  Compare the decoder's output (x^, y^) with the true explanation
(x', y') — the unflagged columns hit (at most a; an unflagged X at a flagged location is absorbed by
that window at no cost) and the flagged windows' true choices.  Optimality (within the MIP gap eps):

    sum_{c in x^} w_c  <=  sum_{c in x'} w_c + eps.

If the decoder fails, x^ + x' + (y^ + y') is an undetectable logical of the merged block-level DEM; a
window contributes at most one column to y^ + y', so with d_DEM the smallest number of columns that
form an undetectable logical, |x^| >= d_DEM - a - b =: k.  The decoder's column costs are at least
the background ones (removing the flagged locations only lowers q_c), so the left side is at least
S_k, the sum of the k smallest background costs.  The right side is at most sum_i W_b(u_i), where
W_b(u) is the cost of u's column after removing the b largest other contributions (u itself stays:
it is unflagged).  Hence, for k >= 1,

    F(a, b) <= P( sum_{i=1..a} W_b(u_i) >= S_k - eps ),   u_i iid ~ the unflagged-error distribution,

which is 0 when a * max W_b < S_k - eps.  The probability is evaluated exactly per (column, class)
bucket for a = 1 and by convolution on a grid with costs rounded up (an over-estimate) for a >= 2.

Inputs that make this exact: the per-column, per-class location counts are exact quadratics in d_Z
(checked at two further d_Z for every configuration), so the caps are computed at any d_Z, including
the transfer targets; d_DEM >= the outer-code distance is verified by an exhaustive meet-in-the-middle
search over all sets of up to 4 columns (enough for d = 3 and 5; d_DEM is taken as min(d, that bound)).

    python scripts/strata_caps.py        # writes results/strata_caps.json (count polynomials, d_DEM)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402

OUT = os.path.join(ROOT, "results", "strata_caps.json")
CLASS_X = np.array([1.0, 1.0 / 3.0, 1.0, 1.0])      # X probability / p_X of idle, gate, prep, meas
FIT_D = (17, 19, 21)
CHECK_D = (25, 33)
# configurations of the flag study (code, n_anc, n_outer, idle context)
# (for distance-3 codes the argument covers only F(1,0), which is computed exactly anyway)
CONFIGS = [("15_6_5", 1, 5, "edge,cnot"), ("15_6_5", 2, 5, "edge,cnot")]


def _model(code, n_anc, d, n_outer, idle):
    c = load_code(code)
    s = ElevatorSchedule(c, d, n_anc=n_anc, mode="full", n_outer=n_outer)
    return c, BlockModel(s, 1e-8, idle_ctx=tuple(idle.split(",")))


def col_counts(bm):
    """(n_col + 1) x 4 location counts per merged column and class; last row: effect-free slots."""
    L = bm.loc
    ok = L.slot >= 0
    col = bm.slot_col[L.slot[ok]]
    col = np.where(col >= 0, col, bm.n_col)
    n = np.zeros((bm.n_col + 1, 4), dtype=np.int64)
    np.add.at(n, (col, L.cls[ok]), 1)
    return n


def signature(bm):
    return hashlib.sha1(np.concatenate([bm.col_D, bm.col_L]).tobytes()).hexdigest()[:16]


def dem_distance_at_least(bm):
    """A lower bound on the smallest number of merged columns that form an undetectable logical:
    2 if one of <= 2 columns exists (1 if a single column), 3 if one of <= 4 exists, else 5.
    Exhaustive meet in the middle over all column sets of size <= 2."""
    D = bm.col_D.astype(bool)
    Lm = bm.col_L.astype(bool)
    nd, nc = D.shape
    nb = nd + Lm.shape[0]
    assert nb <= 128
    bits = np.concatenate([D, Lm], axis=0).T                 # (nc, nb)
    w = np.zeros((nc, 2), dtype=np.uint64)
    for j in range(nb):
        w[:, j // 64] |= (bits[:, j].astype(np.uint64) << np.uint64(j % 64))
    dmask = np.zeros(2, dtype=np.uint64)
    for j in range(nd):
        dmask[j // 64] |= np.uint64(1) << np.uint64(j % 64)

    def has_logical(E):
        """two entries with the same detector part and different observable part?"""
        det, obs = E & dmask, E & ~dmask
        order = np.lexsort((obs[:, 1], obs[:, 0], det[:, 1], det[:, 0]))
        dS, oS = det[order], obs[order]
        return bool(np.any(np.all(dS[1:] == dS[:-1], axis=1) & np.any(oS[1:] != oS[:-1], axis=1)))

    if np.any(~D.any(axis=0) & Lm.any(axis=0)):
        return 1
    small = np.concatenate([np.zeros((1, 2), dtype=np.uint64), w])          # sets of size 0, 1
    if has_logical(small):
        return 2
    iu, ju = np.triu_indices(nc, 1)
    if has_logical(np.concatenate([small, w[iu] ^ w[ju]])):                 # sets of size <= 2
        return 3
    return 5


def fit_config(code, n_anc, n_outer, idle):
    cnts, sigs = {}, {}
    dcode = None
    for d in FIT_D + CHECK_D:
        c, bm = _model(code, n_anc, d, n_outer, idle)
        dcode = c.d
        cnts[d] = col_counts(bm)
        sigs[d] = signature(bm)
        if d == FIT_D[0]:
            d_dem = dem_distance_at_least(bm)
    assert len(set(sigs.values())) == 1, "column structure changes with d_Z"
    X = np.array(FIT_D, dtype=float)
    Y = np.stack([cnts[d] for d in FIT_D]).reshape(len(FIT_D), -1).astype(float)
    coef = np.linalg.solve(np.vander(X, 3), Y)                 # rows: d^2, d, 1
    err = max(float(np.abs((np.vander([float(dc)], 3) @ coef).reshape(cnts[dc].shape) - cnts[dc]).max())
              for dc in CHECK_D)
    assert err < 1e-6, f"counts not quadratic in d_Z ({err})"
    return dict(code=code, n_anc=n_anc, n_outer=n_outer, idle=idle, d_code=int(dcode), d_dem_lb=int(d_dem),
                n_col=int(cnts[FIT_D[0]].shape[0] - 1), signature=sigs[FIT_D[0]],
                coef=np.round(coef, 9).tolist(), shape=list(cnts[FIT_D[0]].shape), check_err=err)


# ------------------------------------------------------------------ caps from the count polynomials
_DIRECT = {}


def counts_at(rec, d):
    """Per-column, per-class counts at d_Z = d and the d_DEM lower bound of that column structure: the
    quadratic for d >= its first fitted d_Z, else the model built at d (its own structure and search)."""
    if d >= FIT_D[0]:
        coef = np.asarray(rec["coef"], dtype=float)
        n = (np.vander([float(d)], 3) @ coef).reshape(rec["shape"])
        return np.rint(n).astype(np.int64), rec["d_dem_lb"]
    key = (rec["code"], rec["n_anc"], rec["n_outer"], rec["idle"], d)
    if key not in _DIRECT:
        _, bm = _model(rec["code"], rec["n_anc"], d, rec["n_outer"], rec["idle"])
        dd = rec["d_dem_lb"] if signature(bm) == rec["signature"] else dem_distance_at_least(bm)
        _DIRECT[key] = (col_counts(bm), dd)
    return _DIRECT[key]


def caps_for(rec, d, p_x, eff, strata, grid=0.005):
    """Upper bounds on F(a, b) for the given strata at d_Z = d.  eff: efficiency per class
    (idle, gate, prep, meas).  Returns {"a,b": cap} for the strata the argument covers (k >= 1)."""
    n, d_dem_lb = counts_at(rec, d)
    d_dem = min(rec["d_code"], d_dem_lb)
    ncol = n.shape[0] - 1
    eff = np.asarray(eff, dtype=float)
    x = p_x * CLASS_X
    xbg = x * (1 - eff) / (1 - 2 * x * eff)                     # no-flag posterior X probability
    lgx = np.log1p(-2 * np.minimum(xbg, 0.5 - 1e-15))          # per location of each class
    ncl = n[:ncol]
    lg = ncl @ lgx                                              # background log(1 - 2 q_c)
    with np.errstate(divide="ignore"):
        q = 0.5 * (1 - np.exp(lg))
        wcol = np.where(q > 0, np.log((1 - q) / np.maximum(q, 1e-300)), np.inf)
    wsorted = np.sort(wcol)
    # unflagged-error distribution over (column, class) buckets (+ effect-free bucket: no cost)
    mass = n * (x * (1 - eff))[None, :]
    U = mass.sum()
    if U <= 0:
        return {}
    order = np.argsort(-xbg)                                    # classes by contribution, largest first
    out = {}
    for (a, b) in strata:
        if a < 1:
            continue
        k = d_dem - a - b
        if k < 1:
            continue
        Sk = float(wsorted[:k].sum())
        if not np.isfinite(Sk):
            out[f"{a},{b}"] = 0.0
            continue
        eps = 1e-3 * Sk + 1e-3
        # W_b per (column, class): remove the b largest other contributions from the column
        Wb = np.zeros((ncol, 4))
        for t in range(4):
            rem = np.zeros(ncol)
            left = np.full(ncol, b, dtype=np.int64)
            for t2 in order:
                avail = ncl[:, t2] - (1 if t2 == t else 0)
                take = np.minimum(left, np.maximum(avail, 0))
                rem += take * lgx[t2]
                left -= take
            lgr = lg - rem
            with np.errstate(divide="ignore", invalid="ignore"):
                qr = 0.5 * (1 - np.exp(lgr))
                Wb[:, t] = np.where(qr > 0, np.log((1 - qr) / np.maximum(qr, 1e-300)), np.inf)
        pm = mass[:ncol] / U
        vals = Wb.ravel()
        probs = pm.ravel()
        keep = probs > 0
        vals, probs = vals[keep], probs[keep]
        p_null = float(mass[ncol].sum() / U)                    # effect-free errors cost nothing
        T = Sk - eps
        if a == 1:
            cap = float(probs[vals >= T].sum())
        else:
            if not np.all(np.isfinite(vals)):
                cap = 1.0
            else:
                idx = np.ceil(vals / grid).astype(np.int64)    # round costs up: over-estimates the sum
                h = np.bincount(idx, weights=probs)
                h[0] += p_null
                conv = h.copy()
                for _ in range(a - 1):
                    conv = np.convolve(conv, h)
                tidx = int(np.floor(T / grid))
                cap = float(conv[tidx:].sum()) if tidx < len(conv) else 0.0
        out[f"{a},{b}"] = min(max(cap, 0.0), 1.0)
    return out


_CACHE = {}


def load():
    if "t" not in _CACHE:
        _CACHE["t"] = json.load(open(OUT)) if os.path.exists(OUT) else []
    return _CACHE["t"]


def record_for(code, n_anc, n_outer, idle):
    for rec in load():
        if (rec["code"], rec["n_anc"], rec["n_outer"], rec["idle"]) == (code, n_anc, n_outer, idle):
            return rec
    return None


def main():
    recs = []
    for cfg in CONFIGS:
        rec = fit_config(*cfg)
        print(cfg, "d_code", rec["d_code"], "d_DEM lower bound", rec["d_dem_lb"], "check err", rec["check_err"], flush=True)
        recs.append(rec)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(recs, open(OUT, "w"))


if __name__ == "__main__":
    main()
