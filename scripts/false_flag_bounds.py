"""Upper bounds on the single-event strata F(1, 0) and F(0, 1) when false flags are present (r > 0),
for codes of distance 3.  The decoder (exclusive-window MLE) fails on one real event only if its
chosen explanation E' differs from the truth c0 by a nontrivial logical, |E' + c0| >= 3, i.e. |E'| >= 2.
An explanation that uses an unflagged column costs at least as much as the truth, so E' consists of
>= 2 columns of falsely flagged windows that complete c0 to a logical.  Hence

    F(1, 0), F(0, 1) <= sum_{c0} w(c0) sum_{c1 < c2 : c0 + c1 + c2 logical} P(c1 flagged) P(c2 flagged)  (+ O(r^3)),

with w the stratum's event weights (unflagged u, flagged s), P(c flagged) <= r_W N_W(c) (N_W: number
of timing windows holding a location of column c, r_W the false-flag probability of a window).
With exact timing F(0, 1) = 0 outright when two flagged locations always cost more than one (cost rule
below).  The sampled zero-failure Wilson bounds of these strata (~1/n) are replaced by min(Wilson, bound).
Writes results/false_flag_bounds.json keyed by result file.

  python scripts/false_flag_bounds.py
"""
import glob
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from elevator.flagstudy import _build  # noqa: E402


def pack(M):
    w = (np.uint64(1) << np.arange(M.shape[0], dtype=np.uint64))
    return (M.astype(np.uint64) * w[:, None]).sum(axis=0).astype(np.uint64)


def bounds_for(spec):
    code, sched, bm, fm, dec, ss = _build(spec)
    if code.d != 3:
        return None
    D = pack(np.asarray(bm.col_D, dtype=np.uint8))
    L = pack(np.asarray(bm.col_L, dtype=np.uint8))
    nc = bm.n_col
    col = np.where(fm.slot >= 0, bm.slot_col[np.maximum(fm.slot, 0)], -1)
    ok = col >= 0
    u = np.bincount(col[ok], weights=(fm.x * (1 - fm.f))[ok], minlength=nc)
    s = np.bincount(col[ok], weights=(fm.e * fm.f)[ok], minlength=nc)
    # number of distinct timing windows holding a location of each column
    pairs = np.unique(np.stack([col[ok], fm.win[ok]], axis=1), axis=0)
    nw = np.bincount(pairs[:, 0], minlength=nc).astype(float)
    r = float(spec["flag"]["false_rate"])
    w = int(spec["flag"]["window"])
    r_win = r if w <= 0 else 1.0 - (1.0 - r) ** w
    P = np.minimum(1.0, r_win * nw)
    # Q[(h, l)] = sum of P(c2) over columns with detector signature h and logical signature l
    Q = defaultdict(float)
    Qh = defaultdict(float)
    for c in range(nc):
        Q[(int(D[c]), int(L[c]))] += P[c]
        Qh[int(D[c])] += P[c]
    K = np.zeros(nc)
    Di = [int(x) for x in D]
    Li = [int(x) for x in L]
    for c0 in range(nc):
        tot = 0.0
        for c1 in range(nc):
            if c1 == c0 or P[c1] == 0:
                continue
            h = Di[c0] ^ Di[c1]
            l = Li[c0] ^ Li[c1]
            # c2 with H c2 = h and L c2 != l completes c0 + c1 to a nontrivial logical
            tot += P[c1] * (Qh.get(h, 0.0) - Q.get((h, l), 0.0))
        K[c0] = tot / 2.0          # unordered pairs
    U, S = float(u.sum()), float(s.sum())
    b10 = float((u * K).sum() / U) if U > 0 else 0.0
    b01 = float((s * K).sum() / S) if S > 0 else 0.0
    # F(0, 2), exact timing only (for r = 0 it vanishes there since b < d): a failure needs a falsely
    # flagged column completing the two real events to a logical (or, for a real event that left no
    # X, two falsely flagged columns: the pair term again)
    b02 = None
    if w <= 0 and S > 0:
        sn = s / S
        b02 = 0.0
        for c1 in range(nc):
            if sn[c1] == 0:
                continue
            for c2 in range(nc):
                if c2 == c1 or sn[c2] == 0:
                    continue
                h = Di[c1] ^ Di[c2]
                l = Li[c1] ^ Li[c2]
                b02 += sn[c1] * sn[c2] * (Qh.get(h, 0.0) - Q.get((h, l), 0.0))
        b02 += 2.0 * float((s * K).sum() / S)
    cost_rule = False
    if w <= 0:
        # exact timing: a flagged location l costs c_l = log((1 - pi_l) / pi_l), pi_l = e_l f_l / 2 / (r + e_l f_l).
        # With one real flagged event, an explanation through >= 2 other flagged locations costs at least
        # 2 c_min; if that exceeds c_max (the most a true location can cost) the MLE never takes it: F(0,1) = 0.
        ef = fm.e * fm.f
        m = (ef > 0) & ok
        pi = 0.5 * ef[m] / (r + ef[m])
        c = np.log((1 - pi) / pi)
        if 2 * c.min() > c.max():
            b01 = 0.0
            cost_rule = True
    out = {"1,0": min(1.0, b10), "0,1": min(1.0, b01), "r_win": r_win, "cost_rule_01": cost_rule}
    if b02 is not None:
        out["0,2"] = min(1.0, b02)
    return out


def main():
    out_path = os.path.join(ROOT, "results", "false_flag_bounds.json")
    out = json.load(open(out_path)) if os.path.exists(out_path) else {}
    files = sorted(glob.glob(os.path.join(ROOT, "results", "flag_*", "*.json")))
    for fn in files:
        key = os.path.relpath(fn, ROOT)
        if key in out:
            continue
        try:
            r = json.load(open(fn))
        except Exception:
            continue
        sp = r.get("spec", {})
        if sp.get("kind") != "strata" or float(sp.get("flag", {}).get("false_rate", 0.0)) <= 0:
            continue
        if sp["code"] not in ("15_9_3", "ham15", "ham31", "ham63"):
            continue
        b = bounds_for(dict(sp))
        if b is None:
            continue
        out[key] = b
        print(key, sp["code"], sp["d"], sp["flag"], {k: f"{v:.2e}" for k, v in b.items()}, flush=True)
        json.dump(out, open(out_path, "w"), indent=1)
    json.dump(out, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
