"""Decoder-independent part of the elevator's phase-flip penalty on its data blocks.

A data block of the elevator takes part in the logical operations: per outer check the moving ancilla
passes it once (a CNOT and a SWAP, or a SWAP: three transversal CNOT layers), each CNOT adding Z on the
block's qubits with probability 2 p/3 (ZI, ZZ on the control; IZ, ZZ on the target).  A decoder told
every other block's and the ancilla's errors (a genie: it can only help) still faces an isolated
repetition code with this extra noise once every d_Z rounds.  Its failure rate, decoded with matching
(maximum likelihood within statistics for the repetition code), bounds the data block's phase flips
from below for any decoder.  This script measures that rate relative to the plain repetition code on
the same inner round (Stim + PyMatching), at p_Z where both are sampled with many failures.

    python scripts/op_noise_penalty.py      # writes results/op_noise_penalty.json
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402
import pymatching  # noqa: E402
import stim  # noqa: E402

from elevator.repcode import rep_circuit  # noqa: E402

POINTS = [(1e-2, 5, 2_000_000), (1e-2, 7, 2_000_000), (1e-2, 9, 2_000_000), (1e-2, 11, 6_000_000),
          (1e-2, 13, 6_000_000), (3e-3, 5, 40_000_000), (3e-3, 7, 40_000_000), (3e-3, 9, 20_000_000),
          (1e-3, 3, 20_000_000), (1e-3, 5, 40_000_000), (1e-3, 7, 40_000_000)]


def rep_op_circuit(d, rounds, p, op_every, op_q):
    """the inner-round repetition code with an extra Z channel op_q on every data qubit at the start of
    every op_every-th round"""
    D = " ".join(str(2 * j) for j in range(d))
    out, r = [], 0
    for line in str(rep_circuit(d, rounds, p)).split("\n"):
        out.append(line)
        if line.startswith("RX") and line != "RX " + D:          # inner-ancilla reset: a round starts
            if r % op_every == 0:
                out.append(f"Z_ERROR({op_q}) {D}")
            r += 1
    return stim.Circuit("\n".join(out))


def fails(c, shots, seed, batch=5_000_000):
    dem = c.detector_error_model(decompose_errors=True, approximate_disjoint_errors=True)
    m = pymatching.Matching.from_detector_error_model(dem)
    smp = c.compile_detector_sampler(seed=seed)
    f = n = 0
    while n < shots:
        b = min(batch, shots - n)
        det, obs = smp.sample(b, separate_observables=True, bit_packed=True)
        pred = m.decode_batch(det, bit_packed_shots=True, bit_packed_predictions=True)
        f += int(np.count_nonzero(np.any(pred != obs, axis=1)))
        n += b
    return f


def main():
    out = []
    for p, d, shots in POINTS:
        rounds = 3 * d                                              # three checks of d_Z rounds
        q = 0.5 * (1 - (1 - 2 * (2 * p / 3)) ** 3)                  # three CNOT layers, Z 2p/3 each
        t0 = time.time()
        f0 = fails(rep_circuit(d, rounds, p), shots, 1000 + d)
        f1 = fails(rep_op_circuit(d, rounds, p, d, q), shots, 2000 + d)
        # ratio of two Poisson counts: 95 % interval from the conditional binomial (Clopper-Pearson-like
        # via the normal approximation on log)
        r = f1 / f0 if f0 else float("nan")
        se = (1 / max(f1, 1) + 1 / max(f0, 1)) ** 0.5
        rec = dict(p=p, d=d, rounds=rounds, shots=shots, fails_plain=f0, fails_op=f1, ratio=r,
                   ratio_lo=r * np.exp(-1.96 * se), ratio_hi=r * np.exp(1.96 * se), seconds=time.time() - t0)
        print(json.dumps(rec), flush=True)
        out.append(rec)
    # pooled over the points: the log-ratio weighted by its inverse variance
    lr = np.array([np.log(x["ratio"]) for x in out])
    wt = np.array([1 / (1 / x["fails_op"] + 1 / x["fails_plain"]) for x in out])
    mu = float((lr * wt).sum() / wt.sum())
    se = float(wt.sum() ** -0.5)
    low_p = [x for x in out if x["p"] <= 1e-3]
    lr2 = np.array([np.log(x["ratio"]) for x in low_p])
    wt2 = np.array([1 / (1 / x["fails_op"] + 1 / x["fails_plain"]) for x in low_p])
    mu2 = float((lr2 * wt2).sum() / wt2.sum())
    se2 = float(wt2.sum() ** -0.5)
    res = dict(points=out, pooled=dict(ratio=float(np.exp(mu)), lo=float(np.exp(mu - 1.96 * se)),
                                       hi=float(np.exp(mu + 1.96 * se))),
               pooled_p1e3=dict(ratio=float(np.exp(mu2)), lo=float(np.exp(mu2 - 1.96 * se2)),
                                hi=float(np.exp(mu2 + 1.96 * se2))))
    json.dump(res, open(os.path.join(ROOT, "results", "op_noise_penalty.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "points"}))


if __name__ == "__main__":
    main()
