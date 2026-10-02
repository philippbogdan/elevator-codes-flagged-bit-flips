"""Decoder optimality under coarse flag timing: exclusive-window MLE (the study's decoder) vs the
exact maximum-likelihood decision for strata of flagged events only, (0, b).

For a configuration with b flagged windows and no unflagged error, every explanation with an
unflagged flip is suppressed by the unflagged prior (<= 1e-9 here), so the maximum-likelihood
coset is computed exactly (to that order) by enumerating every assignment 'window W flipped
column c, or nothing', weighting it by the window posteriors and summing per logical class.
Writes results/decoder_optimality_windows.json.

  python scripts/decoder_optimality_windows.py [n_per_case]    (b = 2 cases use 10x)
"""
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.flags import ExclusiveMleDecoder, FlagConfig, FlagModel  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402
from elevator.strata import StrataSampler  # noqa: E402

ALL = ("idle", "gate", "prep", "meas")


def pack(bits):
    """rows of 0/1 -> python ints (bit i = row i)"""
    out = []
    for col in bits.T:
        v = 0
        for i in np.nonzero(col)[0]:
            v |= 1 << int(i)
        out.append(v)
    return out


class WindowEnumML:
    def __init__(self, fm, mle):
        self.fm, self.mle = fm, mle
        self.Dp = pack(np.asarray(fm.bm.col_D, dtype=np.uint8))
        self.Lp = pack(np.asarray(fm.bm.col_L, dtype=np.uint8))
        self.k = fm.bm.col_L.shape[0]

    def decode(self, det, wins):
        terms = self.mle._window_terms(wins)
        opts = []
        for (uc, pc, p0, ids) in terms:
            o = [(0, 0, p0)] + [(self.Dp[c], self.Lp[c], float(p)) for c, p in zip(uc, pc) if p > 0]
            opts.append(o)
        target = 0
        for i in np.nonzero(det)[0]:
            target |= 1 << int(i)
        probs = {}
        for combo in itertools.product(*opts):
            s = lg = 0
            w = 1.0
            for (ds, ls, p) in combo:
                s ^= ds; lg ^= ls; w *= p
            if s == target:
                probs[lg] = probs.get(lg, 0.0) + w
        if not probs:
            return None, probs
        best = max(probs, key=probs.get)
        return np.array([(best >> j) & 1 for j in range(self.k)], dtype=np.uint8), probs


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    out = []
    cases = [("15_9_3", 1, 15, 1.0, ALL, w, b) for w in (64, 1024, 4096) for b in (2, 3)]
    cases += [("15_6_5", 2, 15, 1.0, ALL, w, b) for w in (1024, 4096) for b in (3,)]
    for code_name, n_anc, d, f, cls, w, b in cases:
        code = load_code(code_name)
        sched = ElevatorSchedule(code, d, n_anc=n_anc, n_outer=5)
        bm = BlockModel(sched, 1e-9, idle_ctx=("edge", "cnot"))
        fm = FlagModel(bm, FlagConfig.make(f, classes=cls, window=w))
        ss = StrataSampler(fm)
        mle = ExclusiveMleDecoder(fm)
        ml = WindowEnumML(fm, mle)
        rng = np.random.default_rng(7000 + 10 * w + b)
        cnt = dict(n=0, ml=0, mle=0, disagree=0, ml_ties=0)
        t0 = time.time()
        n_case = 10 * n if b == 2 else n          # F(0,2) ~ 1e-3: more samples for b = 2
        while cnt["n"] < n_case:
            flips, wins = ss.sample(0, b, rng)
            det, obs = fm.syndrome(flips)
            cnt["n"] += 1
            if not det.any() and not obs.any():
                continue
            p_ml, probs = ml.decode(det, wins)
            p_mle = mle.decode(det, wins)
            if p_ml is None:
                p_ml = p_mle
            vals = sorted(probs.values(), reverse=True)
            if len(vals) > 1 and abs(vals[0] - vals[1]) <= 1e-9 * vals[0]:
                cnt["ml_ties"] += 1
            cnt["ml"] += int(np.any(p_ml != obs))
            cnt["mle"] += int(np.any(p_mle != obs))
            cnt["disagree"] += int(np.any(p_ml != p_mle))
        rec = dict(code=code_name, n_anc=n_anc, d=d, f=f, classes=list(cls), window=w, stratum=[0, b],
                   seconds=time.time() - t0, **cnt)
        print(json.dumps(rec), flush=True)
        out.append(rec)
    os.makedirs("results", exist_ok=True)
    json.dump(out, open("results/decoder_optimality_windows.json", "w"), indent=1)


if __name__ == "__main__":
    main()
