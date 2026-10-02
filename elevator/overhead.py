"""Qubit overhead from logical-error models (arXiv:2601.10786, Appendix B).

Overheads (physical qubits incl. ancillas per logical qubit):
  concatenated (elevator): n_b (2 d_Z - 1) / k
  repetition code:         2 d_Z - 1
  thin rotated surface:    2 d_X d_Z - 1
  thin XZZX (unrotated):   (2 d_X - 1)(2 d_Z - 1)
Logical error rates are per (inner) round and per logical qubit, p_L = p_XL + p_ZL.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

# Table II (Z-type memory fits): p_XL = d^c (a p_X)^b
ELEVATOR_PXL = {
    ("15_9_3", 1): (37.18, 1.94, 2.33),
    ("15_6_5", 1): (115.14, 2.76, 3.73),
    ("15_6_5", 2): (88.47, 2.86, 3.89),
    ("16_3_8", 1): (61.99, 3.57, 5.74),
}
ELEVATOR_NK = {"15_9_3": (15, 9), "15_6_5": (15, 6), "16_3_8": (16, 3), "ham7": (7, 4), "ham15": (15, 11),
               "ham31": (31, 26), "ham63": (63, 57), "xham16": (16, 11), "xham32": (32, 26)}


def paper_pxl(code: str, n_anc: int, d: int, px: float) -> float:
    a, b, c = ELEVATOR_PXL[(code, n_anc)]
    return d ** c * (a * px) ** b


def paper_pzl(code: str, n_anc: int, d: int, pz: float) -> float:
    n, k = ELEVATOR_NK[code]
    nb = n + n_anc
    return (nb / 16) * (9 / k) * 0.12 * (34.4 * pz) ** (0.94 * (d + 1) / 2)


def rep_pl(d: int, pz: float, px: float) -> float:
    return 0.13 * (25.02 * pz) ** (0.99 * (d + 1) / 2) + 3.88 * px * d


# Table III / IV (thin surface, XZZX)
SURF_PZL = {("rot", 3, "1e-2"): (0.05, 4.23, 0.08), ("rot", 5, "1e-2"): (0.04, 2.18, 0.03),
            ("rot", 3, "lt"): (0.14, 72.66, 0.97), ("rot", 5, "lt"): (0.16, 84.69, 0.94),
            ("xzzx", 3, "lt"): (0.36, 30.60, 1.00), ("xzzx", 5, "lt"): (0.64, 28.92, 1.01)}
SURF_PXL = {("rot", 3): (1.06, 19.30, 2.00), ("rot", 5): (1.19, 19.30, 2.97),
            ("xzzx", 3): (1.03, 0.97, 1.99), ("xzzx", 5): (1.06, 12.38, 2.93)}


def surf_pl(kind: str, dx: int, dz: int, pz: float, px: float) -> float:
    key = "1e-2" if (kind == "rot" and abs(pz - 1e-2) < 1e-12) else "lt"
    a, b, c = SURF_PZL[(kind, dx, key)]
    pzl = a * (b * pz) ** (c * (dz + 1) / 2)
    a2, b2, c2 = SURF_PXL[(kind, dx)]
    pxl = dz ** a2 * (b2 * px) ** c2
    return pzl + pxl


@dataclass
class Candidate:
    family: str
    label: str
    overhead: float
    pl: float
    d: int


def candidates(pz: float, eta: float, d_range=range(3, 202, 2), families=("elevator", "rep", "rot", "xzzx"),
               elevator_models: dict | None = None) -> list[Candidate]:
    """All (code, d) candidates with their p_L and overhead.

    elevator_models: optional {(code, n_anc): (pxl_fn(d, px), pzl_fn(d, pz))} overriding the
    paper's fits (used for flagged / re-simulated models)."""
    px = pz / eta
    out: list[Candidate] = []
    if "elevator" in families:
        models = elevator_models
        if models is None:
            models = {key: (lambda d, x, key=key: paper_pxl(key[0], key[1], d, x),
                            lambda d, z, key=key: paper_pzl(key[0], key[1], d, z))
                      for key in ELEVATOR_PXL}
        for (code, n_anc), (fx, fz) in models.items():
            n, k = ELEVATOR_NK[code]
            nb = n + n_anc
            for d in d_range:
                pl = fx(d, px) + fz(d, pz)
                out.append(Candidate("elevator", f"[{n},{k}] {code} a{n_anc}", nb * (2 * d - 1) / k, pl, d))
    if "rep" in families:
        for d in d_range:
            out.append(Candidate("rep", "repetition", 2 * d - 1, rep_pl(d, pz, px), d))
    for kind in ("rot", "xzzx"):
        if kind in families:
            for dx in (3, 5):
                for d in d_range:
                    oh = 2 * dx * d - 1 if kind == "rot" else (2 * dx - 1) * (2 * d - 1)
                    out.append(Candidate(kind, f"{kind} dX={dx}", oh, surf_pl(kind, dx, d, pz, px), d))
    return out


def min_overhead(target: float, cands: list[Candidate], family: str | None = None) -> Candidate | None:
    ok = [c for c in cands if c.pl <= target and (family is None or c.family == family)]
    if not ok:
        return None
    return min(ok, key=lambda c: (c.overhead, c.pl))


def floor_pl(cands: list[Candidate], family: str) -> Candidate | None:
    fam = [c for c in cands if c.family == family]
    return min(fam, key=lambda c: c.pl) if fam else None
