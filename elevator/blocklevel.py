"""Exact block-level reduction of the Z-type (bit-flip) memory, with physical flag locations.

Every physical X fault of the circuits in circuits.py (memory='Z') flips the logical
bit of one row (block position) in one *slot*: a maximal time interval in which the
row takes part in no block-level operation (transversal CNOT tick, ancilla reset,
measurement).  Faults with no logical effect are kept (slot = -1): they can still
raise a flag.

Event model for flags (arXiv:2607.01375): a bit-flip *event* on a cat qubit leaves
its bit randomised, so an X results with probability 1/2.  To keep the Pauli
marginals of arXiv:2601.10786 (Table I) the event probability of a location is
twice its X probability.  For a CNOT the control's X faults are split into a
'before' sub-location (X propagates to the target: XX) and an 'after' one (XI); the
target's (IX) is a third sub-location; each has X probability p/3.

Location classes: 0 idle, 1 gate (inner or transversal CNOT), 2 prep (R_Z), 3 meas (M_Z).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .schedule import ElevatorSchedule, op_cnots

IDLE, GATE, PREP, MEAS = 0, 1, 2, 3
CLASS_NAMES = ["idle", "gate", "prep", "meas"]


@dataclass
class Locations:
    qubit: np.ndarray    # physical qubit id (same numbering as circuits.py)
    tick: np.ndarray     # tick index
    sub: np.ndarray      # 0 = before / only, 1 = after (for a CNOT control), 2 = target
    cls: np.ndarray      # location class
    xprob: np.ndarray    # Pauli X probability (Table I)
    slot: np.ndarray     # slot id flipped by an X here, -1 if none


class BlockModel:
    """Block-level Z-memory model built from an ElevatorSchedule."""

    def __init__(self, sched: ElevatorSchedule, p: float, idle_ctx=("edge", "cnot", "op")):
        self.s = sched
        self.d = sched.d
        self.P = sched.P
        self.p = p
        self.idle_ctx = set(idle_ctx)
        self.W = 2 * self.d - 1
        self._build()

    # ------------------------------------------------------------------ qubit ids
    def dq(self, r, j):
        return r * self.W + 2 * j

    def aq(self, r, j):
        return r * self.W + 2 * j + 1

    # ------------------------------------------------------------------ build
    def _build(self):
        s, d, P, p = self.s, self.d, self.P, self.p
        q_l, t_l, sub_l, c_l, x_l, sl_l = [], [], [], [], [], []
        # slot bookkeeping
        cur = [0] * P              # current slot id of each row
        nslot = 0
        slot_row = []
        slot_start = []

        def new_slot(r, tick):
            nonlocal nslot
            cur[r] = nslot
            slot_row.append(r)
            slot_start.append(tick)
            nslot += 1

        # block-level op log for symptom propagation: ('R', r) ('M', r, meas_id) ('CX', c, t)
        # and ('SLOT', r, slot) markers in time order
        self.ops = []
        for r in range(P):
            new_slot(r, 0)
            self.ops.append(("SLOT", r, cur[r]))
        meas_info = []             # (meas_id, kind, data): kind 'check' (chk, outer) or 'final' (row)

        def add(qs, tick, sub, cls, xp, slots):
            n = len(qs)
            q_l.append(np.asarray(qs, dtype=np.int32))
            t_l.append(np.full(n, tick, dtype=np.int32))
            sub_l.append(np.full(n, sub, dtype=np.int8))
            c_l.append(np.full(n, cls, dtype=np.int8))
            x_l.append(np.full(n, xp, dtype=np.float64))
            sl_l.append(np.asarray(slots, dtype=np.int32))

        tick = 0
        first = True
        content0 = s.initial_content
        data_rows0 = {r for r in range(P) if content0[r][0] == "D"}
        for seg, content in s.iter_contents():
            if seg[0] == "round":
                _, ridx, resets, measures = seg
                mrows = {m[0]: m for m in measures}
                # t0
                for r in range(P):
                    qs = [self.dq(r, j) for j in range(d)]
                    if r in resets:
                        self.ops.append(("R", r))
                        new_slot(r, tick)
                        self.ops.append(("SLOT", r, cur[r]))
                        add(qs, tick, 0, PREP, p, [cur[r]] * d)
                    elif first and r in data_rows0:
                        add(qs, tick, 0, PREP, p, [cur[r]] * d)
                    elif "edge" in self.idle_ctx:
                        add(qs, tick, 0, IDLE, p, [cur[r]] * d)
                first = False
                tick += 1
                # t1: CNOT A_j -> D_j ; D_{d-1} idle
                for r in range(P):
                    A = [self.aq(r, j) for j in range(d - 1)]
                    D = [self.dq(r, j) for j in range(d - 1)]
                    add(A, tick, 0, GATE, p / 3, [-1] * (d - 1))        # XX: X on A_j and D_j -> even
                    add(A, tick, 1, GATE, p / 3, [cur[r]] * (d - 1))    # XI: A_j -> D_{j+1} at t2
                    add(D, tick, 2, GATE, p / 3, [cur[r]] * (d - 1))    # IX
                    if "cnot" in self.idle_ctx:
                        add([self.dq(r, d - 1)], tick, 0, IDLE, p, [cur[r]])
                tick += 1
                # t2: CNOT A_j -> D_{j+1} ; D_0 idle
                for r in range(P):
                    A = [self.aq(r, j) for j in range(d - 1)]
                    D = [self.dq(r, j + 1) for j in range(d - 1)]
                    add(A, tick, 0, GATE, p / 3, [cur[r]] * (d - 1))    # XX: D_{j+1} flipped
                    add(A, tick, 1, GATE, p / 3, [-1] * (d - 1))        # XI: A_j only (measured in X)
                    add(D, tick, 2, GATE, p / 3, [cur[r]] * (d - 1))    # IX
                    if "cnot" in self.idle_ctx:
                        add([self.dq(r, 0)], tick, 0, IDLE, p, [cur[r]])
                tick += 1
                # t3: data idle / ancilla readout
                for r in range(P):
                    qs = [self.dq(r, j) for j in range(d)]
                    if r in mrows:
                        add(qs, tick, 0, MEAS, p, [cur[r]] * d)
                    elif "edge" in self.idle_ctx:
                        add(qs, tick, 0, IDLE, p, [cur[r]] * d)
                for r in sorted(mrows):
                    _, aid, chk, outer = mrows[r]
                    mid = len(meas_info)
                    meas_info.append((mid, "check", (chk, outer)))
                    self.ops.append(("M", r, mid))
                    new_slot(r, tick + 1)
                    self.ops.append(("SLOT", r, cur[r]))
                tick += 1
            else:
                ops = seg[1]
                if not ops:
                    continue
                layers = [op_cnots(kind, ar, dr) for kind, ar, dr in ops]
                nl = max(len(L) for L in layers)
                for t in range(nl):
                    active = set()
                    pairs = []
                    for L in layers:
                        if t < len(L):
                            pairs.append(L[t])
                            active.update(L[t])
                    for (cr, tr) in pairs:
                        Cq = [self.dq(cr, j) for j in range(d)]
                        Tq = [self.dq(tr, j) for j in range(d)]
                        add(Cq, tick, 0, GATE, p / 3, [cur[cr]] * d)    # XX == X on control before
                    # block-level CNOTs: end slots, propagate, start new slots
                    for (cr, tr) in pairs:
                        self.ops.append(("CX", cr, tr))
                        new_slot(cr, tick + 1)
                        self.ops.append(("SLOT", cr, cur[cr]))
                        new_slot(tr, tick + 1)
                        self.ops.append(("SLOT", tr, cur[tr]))
                    for (cr, tr) in pairs:
                        Cq = [self.dq(cr, j) for j in range(d)]
                        Tq = [self.dq(tr, j) for j in range(d)]
                        add(Cq, tick, 1, GATE, p / 3, [cur[cr]] * d)    # XI
                        add(Tq, tick, 2, GATE, p / 3, [cur[tr]] * d)    # IX
                    if "op" in self.idle_ctx:
                        for r in range(P):
                            if r not in active:
                                add([self.dq(r, j) for j in range(d)], tick, 0, IDLE, p, [cur[r]] * d)
                    tick += 1
        # final data readout (one tick)
        content = s.final_content
        drows = [r for r in range(P) if content[r][0] == "D"]
        for r in drows:
            add([self.dq(r, j) for j in range(d)], tick, 0, MEAS, p, [cur[r]] * d)
        for r in drows:
            mid = len(meas_info)
            meas_info.append((mid, "final", r))
            self.ops.append(("M", r, mid))
        tick += 1
        self.n_ticks = tick
        self.loc = Locations(np.concatenate(q_l), np.concatenate(t_l), np.concatenate(sub_l),
                             np.concatenate(c_l), np.concatenate(x_l), np.concatenate(sl_l))
        self.n_slots = nslot
        self.slot_row = np.array(slot_row, dtype=np.int32)
        self.slot_start = np.array(slot_start, dtype=np.int32)
        self.meas_info = meas_info
        self._symptoms(drows)

    # ------------------------------------------------------------------ symptoms
    def _symptoms(self, drows):
        s, P = self.s, self.P
        code = s.code
        mask = [0] * P
        meas_mask = {}
        for op in self.ops:
            if op[0] == "SLOT":
                mask[op[1]] |= (1 << op[2])
            elif op[0] == "R":
                mask[op[1]] = 0
            elif op[0] == "M":
                meas_mask[op[2]] = mask[op[1]]
            elif op[0] == "CX":
                mask[op[2]] ^= mask[op[1]]
        # detectors (same definitions and order as circuits.py, memory='Z')
        dets = []
        last = {}
        check_meas = [m for m in self.meas_info if m[1] == "check"]
        for mid, _, (chk, outer) in check_meas:
            v = meas_mask[mid]
            if chk in last:
                v ^= meas_mask[last[chk]]
            dets.append(v)
            last[chk] = mid
        final = {m[2]: m[0] for m in self.meas_info if m[1] == "final"}
        content = s.final_content
        row_of_block = {content[r][1]: r for r in drows}
        for chk in range(code.m):
            v = meas_mask[last[chk]]
            for b in np.nonzero(code.H[chk])[0]:
                v ^= meas_mask[final[row_of_block[int(b)]]]
            dets.append(v)
        obs = [meas_mask[final[row_of_block[b]]] for b in code.info_set]
        self.n_det = len(dets)
        self.n_obs = len(obs)
        ns = self.n_slots
        D = np.zeros((self.n_det, ns), dtype=np.uint8)
        L = np.zeros((self.n_obs, ns), dtype=np.uint8)
        for i, v in enumerate(dets):
            D[i] = _bits(v, ns)
        for i, v in enumerate(obs):
            L[i] = _bits(v, ns)
        self.slot_D = D
        self.slot_L = L
        # merge slots by symptom -> columns
        key = np.concatenate([D, L], axis=0).T          # (ns, n_det+n_obs)
        packed = np.packbits(key, axis=1)
        uniq, inv = np.unique(packed, axis=0, return_inverse=True)
        inv = inv.ravel()
        nonzero = np.array([bool(u.any()) for u in uniq])
        col_of_uniq = -np.ones(len(uniq), dtype=np.int64)
        col_of_uniq[nonzero] = np.arange(nonzero.sum())
        self.slot_col = col_of_uniq[inv]                 # -1: slot with no effect
        ncol = int(nonzero.sum())
        self.n_col = ncol
        first_slot = np.full(ncol, -1, dtype=np.int64)
        for sidx in range(ns):
            c = self.slot_col[sidx]
            if c >= 0 and first_slot[c] < 0:
                first_slot[c] = sidx
        self.col_D = D[:, first_slot]
        self.col_L = L[:, first_slot]

    # ------------------------------------------------------------------ probabilities
    def slot_probs(self, xprob: np.ndarray | None = None) -> np.ndarray:
        """XOR-combine location X probabilities into slot flip probabilities."""
        x = self.loc.xprob if xprob is None else xprob
        ok = self.loc.slot >= 0
        lg = np.zeros(self.n_slots)
        np.add.at(lg, self.loc.slot[ok], np.log1p(-2 * np.minimum(x[ok], 0.5 - 1e-15)))
        return 0.5 * (1 - np.exp(lg))

    def col_probs(self, sp: np.ndarray) -> np.ndarray:
        ok = self.slot_col >= 0
        lg = np.zeros(self.n_col)
        np.add.at(lg, self.slot_col[ok], np.log1p(-2 * np.minimum(sp[ok], 0.5 - 1e-15)))
        return 0.5 * (1 - np.exp(lg))

    def dem_text(self, sp: np.ndarray | None = None) -> str:
        cp = self.col_probs(self.slot_probs() if sp is None else sp)
        lines = []
        for c in range(self.n_col):
            ts = [f"D{i}" for i in np.nonzero(self.col_D[:, c])[0]]
            ts += [f"L{i}" for i in np.nonzero(self.col_L[:, c])[0]]
            lines.append(f"error({float(cp[c])!r}) " + " ".join(ts))
        return "\n".join(lines)


def _bits(v: int, n: int) -> np.ndarray:
    b = np.frombuffer(v.to_bytes((n + 7) // 8, "little"), dtype=np.uint8)
    return np.unpackbits(b, bitorder="little")[:n]
