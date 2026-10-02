"""Physical Stim circuits of the Elevator-code memory (arXiv:2601.10786 noise model).

Row r holds d data qubits D[r][j] and d-1 inner ancillas A[r][j] (between D[r][j]
and D[r][j+1]); qubit index r*(2d-1) + 2j (data) and r*(2d-1) + 2j + 1 (ancilla).

Inner round (4 ticks, every row):
  t0  R_X inner ancillas (Z err p_Z); data idle; a logical ancilla being started
      has its data qubits prepared with R_Z (X err p_X) instead of idling.
  t1  CNOT A[j] -> D[j]
  t2  CNOT A[j] -> D[j+1]
  t3  M_X inner ancillas (Z err p_Z); data idle; a logical ancilla being read out
      has its data qubits measured with M_Z (X err p_X) instead of idling.
Logical-op layer: transversal CNOT layers between data qubits of two rows; every
other data qubit idles for each such tick.  Inner ancillas carry no noise between
their M_X and the next R_X (they are reset).

Noise (Table I): prep/meas in Z: X at p_X; prep/meas in X: Z at p_Z; idle: X p_X,
Z p_Z; CNOT: IZ, ZI, ZZ at p_Z/3, IX, XI, XX at p_X/3.

memory='Z': data prepared in |0>, observables = Z_L of an information set of the
outer code; detectors = outer-check comparisons.  Only X noise matters.
memory='X': data prepared in |+>, observables = X-bar of a basis of outer
codewords; detectors = inner X-stabiliser comparisons.  Only Z noise matters.
"""
from __future__ import annotations

import numpy as np
import stim

from .codes import OuterCode
from .schedule import ElevatorSchedule, op_cnots


class _TextCircuit:
    """Minimal stand-in for stim.Circuit.append (which is ~3 ms per call in stim 1.16)."""

    def __init__(self):
        self.lines: list[str] = []

    def append(self, name, targets=(), args=None):
        if isinstance(targets, int):
            targets = [targets]
        if args is None or (isinstance(args, (list, tuple)) and len(args) == 0):
            a = ""
        elif isinstance(args, (list, tuple)):
            a = "(" + ",".join(repr(float(x)) for x in args) + ")"
        else:
            a = f"({float(args)!r})"
        self.lines.append(name + a + (" " + " ".join(str(int(t)) for t in targets) if len(targets) else ""))


class Frames:
    """XOR-sets of measurement indices plus random-variable ids (frozenset pairs)."""

    def __init__(self):
        self.next_rv = 0

    def fresh(self):
        self.next_rv += 1
        return (frozenset(), frozenset([self.next_rv]))

    @staticmethod
    def xor(a, b):
        return (a[0] ^ b[0], a[1] ^ b[1])

    @staticmethod
    def zero():
        return (frozenset(), frozenset())


class CircuitBuilder:
    def __init__(self, sched: ElevatorSchedule, memory: str, p_x: float = 0.0, p_z: float = 0.0,
                 noise_classes=None):
        assert memory in ("X", "Z")
        self.s = sched
        self.memory = memory
        self.d = sched.d
        self.P = sched.P
        self.p_x = p_x
        self.p_z = p_z
        self.W = 2 * self.d - 1
        self.c = _TextCircuit()
        self.nmeas = 0
        self.tick = 0

    # ---- indexing
    def dq(self, r, j):
        return r * self.W + 2 * j

    def aq(self, r, j):
        return r * self.W + 2 * j + 1

    def row_data(self, r):
        return [self.dq(r, j) for j in range(self.d)]

    def row_anc(self, r):
        return [self.aq(r, j) for j in range(self.d - 1)]

    # ---- noise helpers
    def idle(self, qs):
        if not qs:
            return
        px, pz = self.p_x, self.p_z
        if px > 0 or pz > 0:
            self.c.append("PAULI_CHANNEL_1", qs, [px, 0, pz])

    def cnot(self, pairs):
        if not pairs:
            return
        flat = [q for pr in pairs for q in pr]
        self.c.append("CX", flat)
        px, pz = self.p_x / 3, self.p_z / 3
        if px > 0 or pz > 0:
            # order: IX IY IZ XI XX XY XZ YI YX YY YZ ZI ZX ZY ZZ
            self.c.append("PAULI_CHANNEL_2", flat,
                          [px, 0, pz, px, px, 0, 0, 0, 0, 0, 0, pz, 0, 0, pz])

    def meas(self, gate, qs, err):
        """Measure qs; returns list of record indices."""
        if err[1] > 0:
            self.c.append(err[0], qs, err[1])
        self.c.append(gate, qs)
        idx = list(range(self.nmeas, self.nmeas + len(qs)))
        self.nmeas += len(qs)
        return idx

    def end_tick(self):
        self.c.append("TICK")
        self.tick += 1

    # ---- build
    def build(self) -> stim.Circuit:
        s, d, P = self.s, self.d, self.P
        c = self.c
        for r in range(P):
            for j in range(d):
                c.append("QUBIT_COORDS", [self.dq(r, j)], [2 * j, r])
            for j in range(d - 1):
                c.append("QUBIT_COORDS", [self.aq(r, j)], [2 * j + 1, r])
        F = Frames()
        X_mem = self.memory == "X"
        # frames: memory Z -> per-row Z_L frame;  memory X -> per-row X_L and S_j frames
        zl = [Frames.zero() for _ in range(P)]
        xl = [Frames.zero() for _ in range(P)]
        sf = [[Frames.zero() for _ in range(d - 1)] for _ in range(P)]
        content0 = s.initial_content
        anc_rows_initial = [r for r in range(P) if content0[r][0] == "A"]
        # initial preparation of data rows (ancilla rows are reset at their first round)
        data_rows = [r for r in range(P) if content0[r][0] == "D"]
        dq_all = [q for r in data_rows for q in self.row_data(r)]
        if X_mem:
            c.append("RX", dq_all)
            if self.p_z > 0:
                c.append("Z_ERROR", dq_all, self.p_z)
            for r in anc_rows_initial:
                xl[r] = F.fresh()
                sf[r] = [F.fresh() for _ in range(d - 1)]
        else:
            c.append("R", dq_all)
            if self.p_x > 0:
                c.append("X_ERROR", dq_all, self.p_x)
        # (data preparation shares tick t0 of the first round)
        self.det_list = []     # list of (list of meas idx, coords)
        self.check_meas = []   # (check, outer, meas idx list) for Z memory
        last_check_meas = {}
        first_round = True
        for seg, content in s.iter_contents():
            if seg[0] == "round":
                _, ridx, resets, measures = seg
                meas_rows = {m[0]: m for m in measures}
                # t0
                all_anc = [q for r in range(P) for q in self.row_anc(r)]
                c.append("RX", all_anc)
                if self.p_z > 0:
                    c.append("Z_ERROR", all_anc, self.p_z)
                if resets:
                    rq = [q for r in resets for q in self.row_data(r)]
                    c.append("R", rq)
                    if self.p_x > 0:
                        c.append("X_ERROR", rq, self.p_x)
                    for r in resets:
                        if X_mem:
                            xl[r] = F.fresh()
                            sf[r] = [F.fresh() for _ in range(d - 1)]
                        else:
                            zl[r] = Frames.zero()
                idle_rows = [r for r in range(P) if r not in resets]
                if not first_round:
                    self.idle([q for r in idle_rows for q in self.row_data(r)])
                first_round = False
                self.end_tick()
                # t1
                pairs = [(self.aq(r, j), self.dq(r, j)) for r in range(P) for j in range(d - 1)]
                self.cnot(pairs)
                self.idle([self.dq(r, d - 1) for r in range(P)])
                self.end_tick()
                # t2
                pairs = [(self.aq(r, j), self.dq(r, j + 1)) for r in range(P) for j in range(d - 1)]
                self.cnot(pairs)
                self.idle([self.dq(r, 0) for r in range(P)])
                self.end_tick()
                # t3: inner ancilla X measurement (+ logical ancilla Z readout)
                midx = self.meas("MX", all_anc, ("Z_ERROR", self.p_z))
                k = 0
                for r in range(P):
                    for j in range(d - 1):
                        m = midx[k]
                        k += 1
                        if X_mem:
                            fr = sf[r][j]
                            if not fr[1]:
                                self.det_list.append((sorted(fr[0] ^ {m}), (2 * j + 1, r, ridx)))
                            sf[r][j] = (frozenset([m]), frozenset())
                if meas_rows:
                    mq = [q for r in sorted(meas_rows) for q in self.row_data(r)]
                    midx2 = self.meas("M", mq, ("X_ERROR", self.p_x))
                    k = 0
                    for r in sorted(meas_rows):
                        idxs = midx2[k:k + d]
                        k += d
                        _, aid, chk, outer = meas_rows[r]
                        if not X_mem:
                            # check value = parity of the d results; frame zl[r] must be trivial
                            assert not zl[r][1]
                            prev = last_check_meas.get(chk)
                            det = set(idxs) ^ set(zl[r][0])
                            if prev is not None:
                                det ^= set(prev)
                            self.det_list.append((sorted(det), (-1, chk, outer)))
                            last_check_meas[chk] = idxs
                            self.check_meas.append((chk, outer, idxs))
                        else:
                            xl[r] = F.fresh()
                            sf[r] = [F.fresh() for _ in range(d - 1)]
                    other = [q for r in range(P) if r not in meas_rows for q in self.row_data(r)]
                    self.idle(other)
                else:
                    self.idle([q for r in range(P) for q in self.row_data(r)])
                self.end_tick()
            else:
                ops = seg[1]
                if not ops:
                    continue
                layers = [op_cnots(kind, ar, dr) for kind, ar, dr in ops]
                nl = max(len(L) for L in layers)
                for t in range(nl):
                    pairs = []
                    active = set()
                    for L in layers:
                        if t < len(L):
                            cr, tr = L[t]
                            pairs += [(self.dq(cr, j), self.dq(tr, j)) for j in range(d)]
                            active.update([cr, tr])
                            if X_mem:
                                xl[cr] = Frames.xor(xl[cr], xl[tr])
                                sf[cr] = [Frames.xor(sf[cr][j], sf[tr][j]) for j in range(d - 1)]
                            else:
                                zl[tr] = Frames.xor(zl[tr], zl[cr])
                    self.cnot(pairs)
                    self.idle([q for r in range(P) if r not in active for q in self.row_data(r)])
                    self.end_tick()
        # ---- final data readout
        content = s.final_content
        drows = [r for r in range(P) if content[r][0] == "D"]
        block_of_row = {r: content[r][1] for r in drows}
        row_of_block = {b: r for r, b in block_of_row.items()}
        fq = [q for r in drows for q in self.row_data(r)]
        if X_mem:
            midx = self.meas("MX", fq, ("Z_ERROR", self.p_z))
        else:
            midx = self.meas("M", fq, ("X_ERROR", self.p_x))
        res = {}
        for i, r in enumerate(drows):
            res[r] = midx[i * self.d:(i + 1) * self.d]
        self.observables = []
        code = s.code
        if X_mem:
            for r in drows:
                for j in range(d - 1):
                    fr = sf[r][j]
                    assert not fr[1], "final stabiliser frame not deterministic"
                    det = set(fr[0]) ^ {res[r][j], res[r][j + 1]}
                    self.det_list.append((sorted(det), (2 * j + 1, r, s.n_rounds)))
            for wi, w in enumerate(code.G):
                obs = set()
                rv = frozenset()
                for b in np.nonzero(w)[0]:
                    r = row_of_block[int(b)]
                    obs ^= {res[r][0]}
                    obs ^= set(xl[r][0])
                    rv = rv ^ xl[r][1]
                assert not rv, "observable frame not deterministic"
                self.observables.append(sorted(obs))
        else:
            for chk in range(code.m):
                det = set()
                for b in np.nonzero(code.H[chk])[0]:
                    det ^= set(res[row_of_block[int(b)]])
                det ^= set(last_check_meas[chk])
                self.det_list.append((sorted(det), (-1, chk, s.n_outer)))
            for b in code.info_set:
                self.observables.append(sorted(res[row_of_block[b]]))
        # append detectors / observables
        n = self.nmeas
        for idxs, coords in self.det_list:
            c.lines.append("DETECTOR(" + ",".join(str(x) for x in coords) + ") "
                           + " ".join(f"rec[{i - n}]" for i in idxs))
        for oi, idxs in enumerate(self.observables):
            c.lines.append(f"OBSERVABLE_INCLUDE({oi}) " + " ".join(f"rec[{i - n}]" for i in idxs))
        return stim.Circuit("\n".join(c.lines))


def build_circuit(code: OuterCode, d: int, memory: str, p_x: float = 0.0, p_z: float = 0.0,
                  n_anc: int = 1, mode: str = "full", n_outer: int | None = None,
                  r_min: int | None = None) -> tuple[stim.Circuit, ElevatorSchedule]:
    if n_outer is None:
        n_outer = 5 if memory == "Z" else 1
    sched = ElevatorSchedule(code, d, n_anc=n_anc, mode=mode, n_outer=n_outer, r_min=r_min)
    b = CircuitBuilder(sched, memory, p_x=p_x, p_z=p_z)
    return b.build(), sched
