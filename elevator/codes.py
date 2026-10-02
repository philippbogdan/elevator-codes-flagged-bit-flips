"""Outer (bit-flip) codes of the Elevator-code memory and GF(2) helpers.

The [15,9,3] and [15,6,5] parity-check matrices are read from data/outer-codes/
(transcribed from Appendix C of arXiv:2601.10786v2).  The [16,3,8] matrix, needed
only to redraw the published Figure 1 at low bias, is transcribed here from the
same appendix (apssamp.tex, figure "fig:parity-check-16-3-8").
"""
from __future__ import annotations

import itertools
import os
from dataclasses import dataclass, field

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

H_16_3_8 = """
1 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0
1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0
0 0 0 0 0 0 1 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
"""


def _parse(text: str) -> np.ndarray:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rows.append([int(x) for x in line.split()])
    return np.array(rows, dtype=np.uint8)


def gf2_rank(M: np.ndarray) -> int:
    A = (np.array(M, dtype=np.uint8) % 2).copy()
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
        if r == rows:
            break
    return r


def gf2_nullspace(H: np.ndarray) -> np.ndarray:
    """Basis (rows) of {x : H x = 0 mod 2}."""
    H = (np.array(H, dtype=np.uint8) % 2).copy()
    m, n = H.shape
    A = H.copy()
    pivots = []
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(m):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        pivots.append(c)
        r += 1
        if r == m:
            break
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        x = np.zeros(n, dtype=np.uint8)
        x[f] = 1
        for i, pc in enumerate(pivots):
            if A[i, f]:
                x[pc] = 1
        basis.append(x)
    return np.array(basis, dtype=np.uint8).reshape(len(basis), n)


def information_set(G: np.ndarray) -> list[int]:
    """Columns I with G[:, I] invertible (greedy, lowest indices first)."""
    k, n = G.shape
    chosen: list[int] = []
    for c in range(n):
        if gf2_rank(G[:, chosen + [c]]) == len(chosen) + 1:
            chosen.append(c)
        if len(chosen) == k:
            break
    assert len(chosen) == k
    return chosen


@dataclass
class OuterCode:
    name: str
    H: np.ndarray
    G: np.ndarray = field(init=False)
    n: int = field(init=False)
    k: int = field(init=False)
    d: int = field(init=False)
    m: int = field(init=False)
    info_set: list[int] = field(init=False)

    def __post_init__(self):
        self.H = (np.array(self.H, dtype=np.uint8) % 2)
        self.m, self.n = self.H.shape
        self.G = gf2_nullspace(self.H)
        self.k = self.G.shape[0]
        assert self.k == self.n - gf2_rank(self.H)
        self.d = self.min_distance()
        self.info_set = information_set(self.G)

    def codewords(self) -> np.ndarray:
        words = []
        for coeffs in itertools.product([0, 1], repeat=self.k):
            c = np.array(coeffs, dtype=np.uint8) @ self.G % 2
            words.append(c)
        return np.array(words, dtype=np.uint8)

    def min_distance(self) -> int:
        w = self.codewords().sum(axis=1)
        return int(w[w > 0].min())

    def weight_distribution(self) -> dict[int, int]:
        w = self.codewords().sum(axis=1)
        out: dict[int, int] = {}
        for x in w:
            out[int(x)] = out.get(int(x), 0) + 1
        return dict(sorted(out.items()))

    @property
    def label(self) -> str:
        return f"[{self.n},{self.k},{self.d}]"


def load_code(name: str) -> OuterCode:
    """name in {'15_9_3', '15_6_5', '16_3_8'} (also accepts '[15,9,3]' style)."""
    key = name.strip("[]").replace(",", "_")
    if key == "16_3_8":
        return OuterCode("16_3_8", _parse(H_16_3_8))
    path = os.path.join(ROOT, "data", "outer-codes", f"H_{key}.txt")
    with open(path) as fh:
        return OuterCode(key, _parse(fh.read()))


if __name__ == "__main__":
    for nm in ["15_9_3", "15_6_5", "16_3_8"]:
        c = load_code(nm)
        print(nm, c.label, "m =", c.m, "rank =", gf2_rank(c.H), "weights", c.weight_distribution(),
              "info set", c.info_set)
