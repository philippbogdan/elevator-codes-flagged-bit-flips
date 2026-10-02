"""Most-likely-error decoding as an integer program (HiGHS via scipy.optimize.milp).

minimise  sum_c w_c x_c + sum_j v_j y_j
s.t.      H x + H_y y = s (mod 2)    (as H x + H_y y - 2 z = s, z integer >= 0)
          sum_{j in g} y_j <= 1       for every exclusive group g
x, y binary.  Returns the error vector x + scatter(y) restricted to the columns of H.
"""
from __future__ import annotations

import warnings

import numpy as np
import scipy.sparse as sp
from scipy.optimize import Bounds, LinearConstraint, milp

# HiGHS would start a thread pool of half the machine's hardware threads in every process; with many
# worker processes on a large node that oversubscribes the allocated cores.  One thread per solve.
# (scipy passes the option to HiGHS verbatim and warns that it does so.)
warnings.filterwarnings("ignore", message="Unrecognized options detected")
HIGHS_OPTIONS = dict(disp=False, threads=1)


def mle_solve(H: sp.csc_matrix, w: np.ndarray, det: np.ndarray, ycols=(), ycost=(), ygroup=()):
    nd, nc = H.shape
    ycols = np.asarray(ycols, dtype=np.int64)
    ny = len(ycols)
    Hy = H[:, ycols] if ny else sp.csc_matrix((nd, 0))
    A_eq = sp.hstack([H, Hy, -2 * sp.identity(nd, format="csc")]).tocsr()
    cons = [LinearConstraint(A_eq, det.astype(float), det.astype(float))]
    if ny:
        groups = np.asarray(ygroup, dtype=np.int64)
        ng = int(groups.max()) + 1
        A_ex = sp.csr_matrix((np.ones(ny), (groups, nc + np.arange(ny))), shape=(ng, nc + ny + nd))
        cons.append(LinearConstraint(A_ex, -np.inf, 1.0))
    c = np.concatenate([np.asarray(w, dtype=float), np.asarray(ycost, dtype=float), np.zeros(nd)])
    zmax = np.asarray(H.sum(axis=1)).ravel() // 2 + 2 + (np.asarray(Hy.sum(axis=1)).ravel() // 2 if ny else 0)
    lb = np.zeros(nc + ny + nd)
    ub = np.concatenate([np.ones(nc + ny), zmax])
    res = milp(c, constraints=cons, integrality=np.ones(nc + ny + nd), bounds=Bounds(lb, ub),
               options=dict(HIGHS_OPTIONS))
    if res.x is None:
        raise RuntimeError("MLE infeasible")
    x = np.round(res.x[:nc]).astype(np.int64)
    if ny:
        y = np.round(res.x[nc:nc + ny]).astype(np.int64)
        np.add.at(x, ycols, y)
    return (x & 1).astype(np.uint8)


def costs_from_probs(p: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), 1e-300, 0.5)
    return np.log((1 - p) / p)

