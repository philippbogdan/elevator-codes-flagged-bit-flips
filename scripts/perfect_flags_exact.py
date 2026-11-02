"""Exactly timed, perfect flags (f = 1 on every location class, no false flags): the decoder knows the
location of every event, each event is an X with probability 1/2, so the only failures come from
event sets E that contain a non-empty subset C with H C = 0 and L C != 0 (an undetectable logical).
Given E, every consistent error is equally likely and maximum likelihood fails with probability
1 - |K0| / |K|, K = {C subset of E : H C = 0}, K0 = {C in K : L C = 0}.  So

    F(0, b) = E_E[1 - |K0|/|K|]    (E: b events drawn with the flagged-event intensities),

computed here by sampling event positions only (no decoding), to precision far beyond the
stratified decoder runs.  Exact-timing, perfect-flag rows of the analysis use these values.
Writes results/perfect_flags_exact.json.

  python scripts/perfect_flags_exact.py [samples]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.flags import FlagConfig, FlagModel  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402

ALL = ("idle", "gate", "prep", "meas")


def pack_cols(M):
    """(rows, cols) 0/1 -> uint64 per column (rows <= 64)."""
    assert M.shape[0] <= 64
    w = (np.uint64(1) << np.arange(M.shape[0], dtype=np.uint64))
    return (M.astype(np.uint64) * w[:, None]).sum(axis=0).astype(np.uint64)


def f0b(fm, b, n, rng, chunk=200000):
    bm = fm.bm
    hd = np.concatenate([pack_cols(bm.col_D), [np.uint64(0)]])     # index -1 -> no effect
    hl = np.concatenate([pack_cols(bm.col_L), [np.uint64(0)]])
    s = fm.e * fm.f
    cum = np.cumsum(s)
    S = float(cum[-1])
    col_of_loc = np.where(fm.slot >= 0, bm.slot_col[np.maximum(fm.slot, 0)], -1)
    masks = np.arange(1, 1 << b)
    sel = ((masks[:, None] >> np.arange(b)) & 1).astype(bool)        # (subsets, b)
    tot = 0.0
    done = 0
    nonzero = 0
    while done < n:
        m = min(chunk, n - done)
        idx = np.searchsorted(cum, rng.random((m, b)) * S, side="right")
        cols = col_of_loc[idx]                                      # (m, b), -1 = no effect
        D = hd[cols]
        L = hl[cols]
        sd = np.zeros((m, len(masks)), dtype=np.uint64)
        sl = np.zeros((m, len(masks)), dtype=np.uint64)
        for j in range(b):
            sd[:, sel[:, j]] ^= D[:, j:j + 1]
            sl[:, sel[:, j]] ^= L[:, j:j + 1]
        ker = (sd == 0)
        nk = ker.sum(axis=1) + 1                                    # |K| incl. the empty set
        nk0 = (ker & (sl == 0)).sum(axis=1) + 1
        fail = 1.0 - nk0 / nk
        tot += float(fail.sum())
        nonzero += int((fail > 0).sum())
        done += m
    return tot / n, nonzero, S


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
    out = []
    cfgs = [("15_9_3", 1, 5, [15, 17, 25, 33]), ("15_6_5", 1, 5, [15, 17, 25, 33]), ("15_6_5", 2, 5, [15, 17, 25, 33]),
            ("ham15", 1, 5, [15, 17]), ("ham31", 1, 5, [15]), ("xham16", 1, 5, [15]), ("ham63", 1, 3, [13, 15])]
    rng = np.random.default_rng(20261002)
    for nm, na, n_outer, ds in cfgs:
        code = load_code(nm)
        for d in ds:
            t0 = time.time()
            s = ElevatorSchedule(code, d, n_anc=na, n_outer=n_outer)
            bm = BlockModel(s, 1e-9, idle_ctx=("edge", "cnot"))
            fm = FlagModel(bm, FlagConfig.make(1.0, classes=ALL, window=0))
            rec = dict(code=nm, n_anc=na, d=d, n_outer=n_outer, rounds=s.n_rounds, k=code.k, samples=n, F={})
            for b in range(code.d, code.d + 4):
                F, nz, S = f0b(fm, b, n, rng)
                rec["F"][str(b)] = dict(F=F, nonzero=nz)
                rec["S_at_1e-9"] = S
            rec["seconds"] = time.time() - t0
            print(json.dumps(rec), flush=True)
            out.append(rec)
            json.dump(out, open("results/perfect_flags_exact.json", "w"), indent=1)
            del bm, fm


if __name__ == "__main__":
    main()
