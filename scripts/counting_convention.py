"""How logical errors are counted 'per logical qubit'.  For the same sampled shots: P_any (any of the k
logical observables wrong) and sum_i P_i (each logical qubit's error counted separately); the
per-round-per-logical-qubit rates are P_any/(R k) (this work's convention throughout) and
sum_i P_i/(R k) (the average per-qubit marginal).  Their ratio is the mean number of logical qubits
hit by a failure.  Compared with the paper's fits at its sampled points.
Writes results/counting_convention.json.

  python scripts/counting_convention.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.circuits import build_circuit  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.flags import BpOsdFlagDecoder, ExclusiveMleDecoder, FlagConfig, FlagModel  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402
from elevator.tasks import make_decoder  # noqa: E402
from summarize_repro import fit_x, fit_z  # noqa: E402

LSD = {"name": "bplsd", "bp_method": "minimum_sum", "ms_scaling_factor": 0.9, "max_iter": 30,
       "lsd_method": "lsd_cs", "lsd_order": 4}


def xmem(name, n_anc, d, pz, shots, seed):
    code = load_code(name)
    c, s = build_circuit(code, d, "X", p_x=0.0, p_z=pz, n_anc=n_anc, mode="full", n_outer=1, idle_ctx=("edge", "cnot"))
    dem = c.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    dec, L = make_decoder(dem, LSD)
    dets, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    anyf = tot = 0
    for i in range(shots):
        w = ((L @ dec.decode(dets[i].astype(np.uint8))) % 2) != obs[i]
        anyf += int(w.any())
        tot += int(w.sum())
    R, k = s.n_rounds, code.k
    fit = fit_x(name, n_anc, d, pz, k)
    p_any = 1 - (1 - anyf / shots) ** (1 / (R * k))
    return dict(memory="X", code=name, n_anc=n_anc, d=d, p=pz, shots=shots, any=anyf, sum=tot, mult=tot / max(anyf, 1),
                ratio_any=p_any / fit, ratio_sum=(tot / shots) / (R * k) / fit)


def zmem(name, n_anc, d, px, shots, seed, f=0.0, classes=("idle",), decoder="bposd"):
    code = load_code(name)
    s = ElevatorSchedule(code, d, n_anc=n_anc, n_outer=8 if name == "16_3_8" else 5)
    bm = BlockModel(s, px, idle_ctx=("edge", "cnot"))
    fm = FlagModel(bm, FlagConfig.make(f, classes=classes))
    dec = BpOsdFlagDecoder(fm) if decoder == "bposd" else ExclusiveMleDecoder(fm)
    rng = np.random.default_rng(seed)
    anyf = tot = 0
    for _ in range(shots):
        flips, wins = fm.sample_poisson(rng)
        det, obs = fm.syndrome(flips)
        if not det.any() and not obs.any():
            continue
        w = dec.decode(det, wins) != obs
        anyf += int(w.any())
        tot += int(w.sum())
    R, k = s.n_rounds, code.k
    fit = fit_z(name, n_anc, d, px)
    p_any = 1 - (1 - anyf / shots) ** (1 / (R * k))
    return dict(memory="Z", code=name, n_anc=n_anc, d=d, p=px, f=f, classes=list(classes), shots=shots, any=anyf, sum=tot,
                mult=tot / max(anyf, 1), ratio_any=p_any / fit, ratio_sum=(tot / shots) / (R * k) / fit)


def main():
    out = []
    jobs = [lambda: xmem("15_9_3", 1, 9, 1e-2, 1500, 1), lambda: xmem("15_9_3", 1, 11, 7e-3, 6000, 2),
            lambda: xmem("15_6_5", 1, 9, 1e-2, 1500, 3),
            lambda: zmem("15_9_3", 1, 9, 1e-5, 6000, 4), lambda: zmem("15_9_3", 1, 9, 2e-6, 40000, 5),
            lambda: zmem("15_6_5", 1, 9, 1e-5, 20000, 6), lambda: zmem("15_6_5", 2, 9, 1e-5, 20000, 7),
            lambda: zmem("16_3_8", 1, 9, 1e-5, 6000, 8),
            lambda: zmem("15_9_3", 1, 9, 1e-5, 6000, 9, f=0.9, classes=("idle", "gate", "prep", "meas"), decoder="mle")]
    for job in jobs:
        t0 = time.time()
        r = job()
        r["seconds"] = time.time() - t0
        print(json.dumps(r), flush=True)
        out.append(r)
        json.dump(out, open("results/counting_convention.json", "w"), indent=1)


if __name__ == "__main__":
    main()
