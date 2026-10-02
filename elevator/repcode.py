"""Isolated phase-flip repetition code with the elevator's inner round (X-basis memory).

Same tick structure and noise as one row of circuits.py (memory='X'):
  t0 R_X inner ancillas (Z err p), data idle (Z p)
  t1 CNOT A_j -> D_j, D_{d-1} idle;  t2 CNOT A_j -> D_{j+1}, D_0 idle
  t3 M_X inner ancillas (Z err p), data idle
optionally followed by `extra_idle` idle ticks per round (the elevator's logical-op
layers under the literal noise reading).  Decoded with PyMatching (the DEM is graphlike).
"""
from __future__ import annotations

import numpy as np
import stim


def rep_circuit(d: int, rounds: int, p: float, extra_idle: float = 0.0) -> stim.Circuit:
    D = [2 * j for j in range(d)]
    A = [2 * j + 1 for j in range(d - 1)]
    L = []
    L.append("RX " + " ".join(map(str, D)))
    L.append(f"Z_ERROR({p}) " + " ".join(map(str, D)))
    nA = d - 1
    for r in range(rounds):
        L.append("RX " + " ".join(map(str, A)))
        L.append(f"Z_ERROR({p}) " + " ".join(map(str, A)))
        if r > 0:
            L.append(f"Z_ERROR({p}) " + " ".join(map(str, D)))
        L.append("TICK")
        L.append("CX " + " ".join(f"{A[j]} {D[j]}" for j in range(d - 1)))
        L.append(f"PAULI_CHANNEL_2(0,0,{p/3},0,0,0,0,0,0,0,0,{p/3},0,0,{p/3}) " + " ".join(f"{A[j]} {D[j]}" for j in range(d - 1)))
        L.append(f"Z_ERROR({p}) {D[d - 1]}")
        L.append("TICK")
        L.append("CX " + " ".join(f"{A[j]} {D[j + 1]}" for j in range(d - 1)))
        L.append(f"PAULI_CHANNEL_2(0,0,{p/3},0,0,0,0,0,0,0,0,{p/3},0,0,{p/3}) " + " ".join(f"{A[j]} {D[j + 1]}" for j in range(d - 1)))
        L.append(f"Z_ERROR({p}) {D[0]}")
        L.append("TICK")
        L.append(f"Z_ERROR({p}) " + " ".join(map(str, A)))
        L.append("MX " + " ".join(map(str, A)))
        L.append(f"Z_ERROR({p}) " + " ".join(map(str, D)))
        for j in range(nA):
            if r == 0:
                L.append(f"DETECTOR({2*j+1},{r}) rec[{-nA + j}]")
            else:
                L.append(f"DETECTOR({2*j+1},{r}) rec[{-nA + j}] rec[{-2 * nA + j}]")
        if extra_idle > 0:
            # extra idle ticks folded into one channel with the same total Z probability
            q = 0.5 * (1 - (1 - 2 * p) ** extra_idle)
            L.append(f"Z_ERROR({q}) " + " ".join(map(str, D)))
        L.append("TICK")
    L.append(f"Z_ERROR({p}) " + " ".join(map(str, D)))
    L.append("MX " + " ".join(map(str, D)))
    for j in range(nA):
        L.append(f"DETECTOR({2*j+1},{rounds}) rec[{-d + j}] rec[{-d + j + 1}] rec[{-d - nA + j}]")
    L.append("OBSERVABLE_INCLUDE(0) rec[-1]")
    return stim.Circuit("\n".join(L))


def sample_rep(d: int, rounds: int, p: float, shots: int, seed: int, extra_idle: float = 0.0,
               batch: int = 100000) -> dict:
    import pymatching
    c = rep_circuit(d, rounds, p, extra_idle)
    dem = c.detector_error_model(decompose_errors=True, approximate_disjoint_errors=True)
    m = pymatching.Matching.from_detector_error_model(dem)
    smp = c.compile_detector_sampler(seed=seed)
    fails = done = 0
    while done < shots:
        b = min(batch, shots - done)
        det, obs = smp.sample(b, separate_observables=True, bit_packed=True)
        pred = m.decode_batch(det, bit_packed_shots=True, bit_packed_predictions=True)
        fails += int(np.count_nonzero(np.any(pred != obs, axis=1)))
        done += b
    return dict(shots=done, fails=fails, rounds=rounds)
