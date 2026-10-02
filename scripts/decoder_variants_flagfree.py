"""Flag-free decoder sensitivity at the paper's sampled points: the same sampled shots decoded by
BP+LSD-CS4 (this work's X-memory decoder), BP+OSD-CS7 (this work's Z-memory decoder) and BP+OSD-0
with ldpc's default settings (min-sum, max_iter = n; the paper names BP+OSD but not its settings).
Writes results/decoder_variants_flagfree.json.

  python scripts/decoder_variants_flagfree.py [shots]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402
from ldpc import BpLsdDecoder, BpOsdDecoder  # noqa: E402
from ldpc.ckt_noise.dem_matrices import detector_error_model_to_check_matrices  # noqa: E402

from elevator.circuits import build_circuit  # noqa: E402
from elevator.codes import load_code  # noqa: E402

DECODERS = {
    "bplsd_cs4": lambda H, pri: BpLsdDecoder(H, error_channel=pri, bp_method="product_sum", max_iter=100,
                                             lsd_method="lsd_cs", lsd_order=4),
    "bposd_cs7": lambda H, pri: BpOsdDecoder(H, error_channel=pri, bp_method="product_sum", max_iter=100,
                                             osd_method="osd_cs", osd_order=7),
    "bposd0_default": lambda H, pri: BpOsdDecoder(H, error_channel=pri),
}


def run(code_name, d, memory, p_x, p_z, shots, seed, names):
    code = load_code(code_name)
    c, s = build_circuit(code, d, memory, p_x=p_x, p_z=p_z, n_anc=1, mode="full",
                         n_outer=1 if memory == "X" else 5, idle_ctx=("edge", "cnot"))
    dem = c.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    m = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges=True)
    H, L = m.check_matrix.tocsr(), m.observables_matrix.tocsr()
    pri = list(np.array(m.priors, dtype=float))
    decs = {n: DECODERS[n](H, pri) for n in names}
    dets, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    res = {n: dict(fails=0, seconds=0.0) for n in names}
    both = 0
    for i in range(shots):
        if not dets[i].any():
            continue
        wrong = {}
        for n, dec in decs.items():
            t0 = time.time()
            e = dec.decode(dets[i].astype(np.uint8))
            res[n]["seconds"] += time.time() - t0
            wrong[n] = bool(np.any(((L @ e) % 2) != obs[i]))
            res[n]["fails"] += wrong[n]
    return dict(code=code_name, d=d, memory=memory, p_x=p_x, p_z=p_z, shots=shots, rounds=s.n_rounds, k=code.k,
                decoders=res)


def main():
    shots = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = []
    cases = [("15_9_3", 9, "X", 0.0, 1e-2, ["bplsd_cs4", "bposd0_default", "bposd_cs7"]),
             ("15_9_3", 9, "X", 0.0, 7e-3, ["bplsd_cs4", "bposd0_default"]),
             ("15_9_3", 9, "Z", 1e-5, 0.0, ["bposd_cs7", "bposd0_default"]),
             ("15_6_5", 9, "Z", 1e-5, 0.0, ["bposd_cs7", "bposd0_default"])]
    for (code, d, mem, px, pz, names) in cases:
        n = shots if mem == "X" else 20 * shots
        r = run(code, d, mem, px, pz, n, 4242, names)
        print(json.dumps(r), flush=True)
        out.append(r)
        json.dump(out, open("results/decoder_variants_flagfree.json", "w"), indent=1)


if __name__ == "__main__":
    main()
