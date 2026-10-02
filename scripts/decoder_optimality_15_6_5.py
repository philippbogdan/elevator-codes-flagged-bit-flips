"""Decoder optimality check for [15,6,5] in the p_Z = 1e-2 regime (p_X = 1e-8, d_Z = 17): the
exclusive-window MLE against exact maximum likelihood (trellis over the 2^P error frames of the rows,
exact for exactly timed flags) on the same sampled configurations of the strata that make up the
p_Z = 1e-2 floors.  Writes results/decoder_optimality_15_6_5.json.

  python scripts/decoder_optimality_15_6_5.py [n_per_stratum] [procs]
"""
import json
import os
import sys
import time
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

ALL = ("idle", "gate", "prep", "meas")
CONFIGS = [(0.0, ("idle",), [(3, 0)]),
           (0.9, ALL, [(3, 0), (2, 1), (2, 2)]),
           (0.99, ALL, [(2, 1), (1, 3), (2, 2), (3, 0)])]
_W = {}


def _init(f, cls):
    from elevator.blocklevel import BlockModel
    from elevator.codes import load_code
    from elevator.flags import ExclusiveMleDecoder, FlagConfig, FlagModel, TrellisMLDecoder
    from elevator.schedule import ElevatorSchedule
    from elevator.strata import StrataSampler
    code = load_code("15_6_5")
    sched = ElevatorSchedule(code, 17, n_anc=1, n_outer=5)
    bm = BlockModel(sched, 1e-8, idle_ctx=("edge", "cnot"))
    fm = FlagModel(bm, FlagConfig.make(f, classes=cls, window=0))
    _W.update(fm=fm, ss=StrataSampler(fm), mle=ExclusiveMleDecoder(fm), ml=TrellisMLDecoder(fm))


def _work(args):
    a, b, n, seed = args
    fm, ss, mle, ml = _W["fm"], _W["ss"], _W["mle"], _W["ml"]
    rng = np.random.default_rng(seed)
    cnt = dict(n=0, ml=0, mle=0, disagree=0, mle_only=0, ml_only=0)
    while cnt["n"] < n:
        flips, wins = ss.sample(a, b, rng)
        det, obs = fm.syndrome(flips)
        if not det.any() and not obs.any():
            continue
        cnt["n"] += 1
        p1 = ml.decode(det, wins)
        p2 = mle.decode(det, wins)
        f1, f2 = bool(np.any(p1 != obs)), bool(np.any(p2 != obs))
        cnt["ml"] += f1
        cnt["mle"] += f2
        cnt["disagree"] += int(np.any(p1 != p2))
        cnt["mle_only"] += int(f2 and not f1)
        cnt["ml_only"] += int(f1 and not f2)
    return cnt


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("OMP_NUM_THREADS", os.cpu_count()))
    out_path = os.path.join(ROOT, "results", "decoder_optimality_15_6_5.json")
    out = []
    for f, cls, strata in CONFIGS:
        with Pool(procs, initializer=_init, initargs=(f, cls)) as pool:
            for (a, b) in strata:
                t0 = time.time()
                per = -(-n // procs)
                jobs = [(a, b, per, 7919 * (1000 * a + 10 * b) + i + int(f * 1000)) for i in range(procs)]
                tot = dict(n=0, ml=0, mle=0, disagree=0, mle_only=0, ml_only=0)
                for c in pool.imap_unordered(_work, jobs):
                    for k in tot:
                        tot[k] += c[k]
                rec = dict(code="15_6_5", n_anc=1, d=17, p_x=1e-8, f=f, classes=list(cls), stratum=[a, b],
                           seconds=time.time() - t0, **tot)
                print(json.dumps(rec), flush=True)
                out.append(rec)
                json.dump(out, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
