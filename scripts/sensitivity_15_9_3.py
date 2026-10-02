"""Why is [15,9,3] above the published bit-flip fit?  Sensitivity of the flag-free Z-memory rate
(block-level reduction, noop reading, d_Z = 9) to check order, number of outer rounds and decoder.
Writes results/sensitivity_15_9_3.json.

  python scripts/sensitivity_15_9_3.py
"""
import json
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.decode import wilson  # noqa: E402
from elevator.flags import (BpOsdFlagDecoder, ExclusiveMleDecoder, FlagConfig, FlagModel,  # noqa: E402
                            direct_mc)
from elevator.overhead import paper_pxl  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402


def run(args):
    label, d, p, order, n_outer, dec_name, shots, seed = args
    code = load_code("15_9_3")
    s = ElevatorSchedule(code, d, n_anc=1, n_outer=n_outer, check_order=order)
    bm = BlockModel(s, p, idle_ctx=("edge", "cnot"))
    fm = FlagModel(bm, FlagConfig.make(0.0))
    dec = ExclusiveMleDecoder(fm) if dec_name == "mle" else BpOsdFlagDecoder(fm)
    r = direct_mc(fm, dec, shots, seed)
    R, k = s.n_rounds, code.k
    conv = lambda x: 1 - (1 - x) ** (1 / (R * k))
    lo, hi = wilson(r["fails"], r["shots"])
    pl = conv(r["fails"] / r["shots"])
    return dict(label=label, d=d, p=p, decoder=dec_name, n_outer=n_outer, order=order, fails=r["fails"],
                shots=r["shots"], rounds=R, pL=pl, lo=conv(lo), hi=conv(hi), fit=paper_pxl("15_9_3", 1, d, p),
                ratio=pl / paper_pxl("15_9_3", 1, d, p))


def main():
    rng = np.random.default_rng(0)
    perms = [list(map(int, rng.permutation(6))) for _ in range(2)]
    tasks = [("natural", 9, 1e-6, None, 5, "bposd", 30000, 1),
             ("reversed", 9, 1e-6, [5, 4, 3, 2, 1, 0], 5, "bposd", 30000, 2),
             ("permutation 1", 9, 1e-6, perms[0], 5, "bposd", 30000, 3),
             ("permutation 2", 9, 1e-6, perms[1], 5, "bposd", 30000, 4),
             ("3 outer rounds", 9, 1e-6, None, 3, "bposd", 30000, 5),
             ("10 outer rounds", 9, 1e-6, None, 10, "bposd", 30000, 6)]
    for d in (9, 15):
        for p in (1e-6, 2e-6):
            for dn in ("bposd", "mle"):
                tasks.append((f"decoder {dn}", d, p, None, 5, dn, 30000, 100 + d + int(p * 1e7) + (dn == "mle")))
    with Pool(min(6, os.cpu_count())) as pool:
        res = pool.map(run, tasks, chunksize=1)
    for r in res:
        print(f"{r['label']:16s} d={r['d']} p={r['p']:.0e} {r['decoder']:5s} {r['fails']}/{r['shots']} "
              f"pL={r['pL']:.2e} ratio to fit {r['ratio']:.2f}")
    json.dump(res, open(os.path.join("results", "sensitivity_15_9_3.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
