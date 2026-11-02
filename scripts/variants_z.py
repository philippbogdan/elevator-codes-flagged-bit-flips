"""Flag-free Z-memory: sensitivity of p_XL to unstated circuit details (schedule, idle noise).

Usage: python scripts/variants_z.py OUT.json [shots]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool

from elevator.codes import load_code
from elevator.circuits import build_circuit
from elevator.decode import DemDecoder, sample_failures, per_round_per_lq

FITS = {"15_9_3": (37.18, 1.94, 2.33), "15_6_5": (115.14, 2.76, 3.73)}

VARIANTS = {
    "full/all-idle": dict(mode="full", idle_ctx=("edge", "cnot", "op")),
    "full/no-op-idle": dict(mode="full", idle_ctx=("edge", "cnot")),
    "full/cnot-idle-only": dict(mode="full", idle_ctx=("cnot",)),
    "span/all-idle": dict(mode="span", idle_ctx=("edge", "cnot", "op")),
}


def run(task):
    nm, d, p, vname, shots, seed = task
    code = load_code(nm)
    v = VARIANTS[vname]
    c, s = build_circuit(code, d, "Z", p_x=p, n_anc=1, n_outer=5, mode=v["mode"], idle_ctx=v["idle_ctx"])
    dem = c.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    r = sample_failures(c, shots, seed=seed, decoder=DemDecoder(dem), max_fail=3000)
    a, b, cc = FITS[nm]
    fit = d ** cc * (a * p) ** b
    pl = per_round_per_lq(r["fails"], r["shots"], s.n_rounds, code.k)
    out = dict(code=nm, d=d, p=p, variant=vname, rounds=s.n_rounds, k=code.k, fit=fit, pL=pl,
               ratio=pl / fit, **r)
    print(json.dumps(out), flush=True)
    return out


if __name__ == "__main__":
    outp = sys.argv[1]
    shots = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
    tasks = []
    seed = 100
    for nm in ["15_9_3", "15_6_5"]:
        for d in [9, 15]:
            for p in ([3e-6] if nm == "15_9_3" else [3e-6, 1e-6]):
                for vname in VARIANTS:
                    seed += 1
                    tasks.append((nm, d, p, vname, shots, seed))
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 6) as pool:
        res = pool.map(run, tasks, chunksize=1)
    json.dump(res, open(outp, "w"), indent=1)
