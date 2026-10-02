"""Decoder optimality check: exclusive-window MLE vs exact maximum likelihood (trellis) on the
same sampled configurations of the leading strata, with exactly timed flags (where the trellis
is exact for the flag model).  Writes results/decoder_optimality.json.

  python scripts/decoder_optimality.py [n_per_stratum]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.flags import (BpOsdFlagDecoder, ExclusiveMleDecoder, FlagConfig, FlagModel,  # noqa: E402
                            TrellisMLDecoder)
from elevator.schedule import ElevatorSchedule  # noqa: E402
from elevator.strata import StrataSampler  # noqa: E402


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    out = []
    for code_name, d, cfgs in [
        ("15_9_3", 17, [(0.0, ("idle",)), (0.9, ("idle",)), (0.9, ("idle", "gate", "prep", "meas"))]),
    ]:
        code = load_code(code_name)
        sched = ElevatorSchedule(code, d, n_anc=1, n_outer=5)
        bm = BlockModel(sched, 1e-9, idle_ctx=("edge", "cnot"))
        for f, cls in cfgs:
            fm = FlagModel(bm, FlagConfig.make(f, classes=cls, window=0))
            ss = StrataSampler(fm)
            mle = ExclusiveMleDecoder(fm)
            ml = TrellisMLDecoder(fm)
            bp = BpOsdFlagDecoder(fm)
            strata = [(2, 0)] if f == 0 else [(2, 0), (1, 1), (0, 3)]
            for (a, b) in strata:
                if (a and ss.U <= 0) or (b and ss.S <= 0):
                    continue
                rng = np.random.default_rng(1000 * a + b)
                cnt = dict(n=0, ml=0, mle=0, bposd=0, disagree_ml_mle=0)
                t0 = time.time()
                while cnt["n"] < n:
                    flips, wins = ss.sample(a, b, rng)
                    det, obs = fm.syndrome(flips)
                    if not det.any() and not obs.any():
                        continue
                    cnt["n"] += 1
                    p1 = ml.decode(det, wins)
                    p2 = mle.decode(det, wins)
                    p3 = bp.decode(det, wins)
                    cnt["ml"] += int(np.any(p1 != obs))
                    cnt["mle"] += int(np.any(p2 != obs))
                    cnt["bposd"] += int(np.any(p3 != obs))
                    cnt["disagree_ml_mle"] += int(np.any(p1 != p2))
                rec = dict(code=code_name, d=d, f=f, classes=list(cls), stratum=[a, b], seconds=time.time() - t0, **cnt)
                print(json.dumps(rec), flush=True)
                out.append(rec)
    os.makedirs("results", exist_ok=True)
    json.dump(out, open("results/decoder_optimality.json", "w"), indent=1)


if __name__ == "__main__":
    main()
