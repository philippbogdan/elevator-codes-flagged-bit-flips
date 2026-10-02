"""[16,3,8] flag-free Z memory at a sampled point of the paper's fit: block-level BP+OSD-CS7 (used for
the [16,3,8] reproduction runs) against the exact MLE on the same sampled shots.
Writes results/decoder_check_16_3_8.json.

  python scripts/decoder_check_16_3_8.py [shots]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.flags import BpOsdFlagDecoder, ExclusiveMleDecoder, FlagConfig, FlagModel  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402


def main():
    shots = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    out = []
    for d, px in [(9, 4.5e-6), (9, 2e-6)]:
        code = load_code("16_3_8")
        s = ElevatorSchedule(code, d, n_anc=1, n_outer=8)
        bm = BlockModel(s, px, idle_ctx=("edge", "cnot"))
        fm = FlagModel(bm, FlagConfig.make(0.0))
        dec = {"bposd_cs7": BpOsdFlagDecoder(fm), "mle": ExclusiveMleDecoder(fm)}
        rng = np.random.default_rng(16380 + d)
        fails = {k: 0 for k in dec}
        both = 0
        t0 = time.time()
        for _ in range(shots):
            flips, wins = fm.sample_poisson(rng)
            det, obs = fm.syndrome(flips)
            if not det.any() and not obs.any():
                continue
            w = {}
            for k, dd in dec.items():
                w[k] = bool(np.any(dd.decode(det, wins) != obs))
                fails[k] += w[k]
            both += w["bposd_cs7"] and w["mle"]
        R, k = s.n_rounds, code.k
        conv = lambda f: 1 - (1 - f / shots) ** (1 / (R * k))
        rec = dict(code="16_3_8", d=d, p_x=px, shots=shots, rounds=R, k=k, fails=fails, both=both,
                   pL={kk: conv(v) for kk, v in fails.items()},
                   fit=d ** 5.74 * (61.99 * px) ** 3.57, seconds=time.time() - t0)
        print(json.dumps(rec), flush=True)
        out.append(rec)
        json.dump(out, open("results/decoder_check_16_3_8.json", "w"), indent=1)


if __name__ == "__main__":
    main()
