"""Block-level schedule of an Elevator-code memory.

A column of P = n + n_anc rows.  Each row holds one repetition-code block: a data
block ('D', b) or a logical ancilla ('A', a).  Time is a sequence of segments:

  ('round', resets, measures)   one inner repetition-code round on every row.
        resets   : rows whose data qubits are prepared in |0> (ancilla start, tick t0)
        measures : list of (row, anc, check, outer_round) measured in Z at tick t3
  ('ops', ops)                  one logical-operation layer between rounds.
        ops      : list of (kind, anc_row, data_row); kind 'CS' = CNOT+SWAP compiled
                   into two CNOT layers, 'S' = SWAP compiled into three.

Compiled CNOT order for an op between ancilla row a and data row b (positions):
    CS: CNOT(a->b), CNOT(b->a)            -> a holds the data, b holds anc xor data
    S : CNOT(a->b), CNOT(b->a), CNOT(a->b)

Modes for the ancilla path (the paper does not specify it):
  'full' : every check is measured during one sweep through the whole column
           (n logical operations), alternating down and up ("elevator").
  'span' : a check ends as soon as its last support block has been passed; the
           ancilla is reset in place and continues in the same direction,
           bouncing at the ends of the column.
  'local': the ancilla takes, among the checks left in the current outer round, the one
           with the shortest path from where it stands, heads for the nearer end of
           that check's support and sweeps it; reset in place (sensitivity case: the
           shortest path an ancilla moving by SWAPs can take).
Each check lasts max(R_min, n_ops + 1) rounds (R_min = d_Z in the paper).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .codes import OuterCode


@dataclass
class Ancilla:
    aid: int
    row: int
    direction: int
    checks: list[int]               # order of checks this ancilla measures (one cycle)
    queue: list[tuple[int, int]] = field(default_factory=list)   # (check, outer_round) remaining
    current: tuple[int, int] | None = None
    done: set = field(default_factory=set)
    passes: int = 0
    ops_this_check: int = 0
    rounds_since_prep: int = 0
    needs_reset: bool = True
    path_complete: bool = False
    active: bool = False            # prepared and running a check


class ElevatorSchedule:
    def __init__(self, code: OuterCode, d: int, n_anc: int = 1, mode: str = "full",
                 n_outer: int = 5, r_min: int | None = None, check_order=None,
                 anc_rows=None, compress: bool = False):
        self.code = code
        self.d = d
        self.n_anc = n_anc
        self.mode = mode
        self.compress = compress
        if compress:
            assert n_anc == 1 and mode == "full", "compressed schedule: one ancilla, full sweep"
        if mode == "local":
            assert n_anc == 1, "shortest-path schedule: one ancilla"
        self.n_outer = n_outer
        self.r_min = d if r_min is None else r_min
        self.P = code.n + n_anc
        self.supports = [set(np.nonzero(code.H[c])[0].tolist()) for c in range(code.m)]
        order = list(range(code.m)) if check_order is None else list(check_order)
        # initial layout: ancillas on top, data blocks below in index order
        if anc_rows is None:
            anc_rows = list(range(n_anc))
        content: list = [None] * self.P
        for a, r in enumerate(anc_rows):
            content[r] = ("A", a)
        b = 0
        for r in range(self.P):
            if content[r] is None:
                content[r] = ("D", b)
                b += 1
        self.initial_content = list(content)
        self.ancillas: list[Ancilla] = []
        for a, r in enumerate(anc_rows):
            mine = order[a::n_anc]
            anc = Ancilla(aid=a, row=r, direction=+1, checks=mine)
            anc.queue = [(c, t) for t in range(n_outer) for c in mine]
            self.ancillas.append(anc)
        self.segments: list = []
        self.check_records: list[dict] = []   # one per check measurement, in time order
        self._build(content)

    # ------------------------------------------------------------------ build
    def _build(self, content):
        P = self.P
        ancs = self.ancillas
        round_idx = 0
        guard = 0
        while any(a.queue or a.active for a in ancs):
            guard += 1
            if guard > 100000:
                raise RuntimeError("schedule did not terminate")
            # ---- inner round
            resets, measures = [], []
            for a in ancs:
                if a.needs_reset and a.queue:
                    if self.mode == "local":
                        self._pick_local(a, content)
                    a.current = a.queue.pop(0)
                    a.done = set()
                    a.passes = 0
                    a.ops_this_check = 0
                    a.rounds_since_prep = 0
                    a.path_complete = self._path_complete(a)
                    a.needs_reset = False
                    a.active = True
                    resets.append(a.row)
            for a in ancs:
                if a.active and a.path_complete and a.rounds_since_prep + 1 >= self.r_min:
                    c, t = a.current
                    measures.append((a.row, a.aid, c, t))
            self.segments.append(("round", round_idx, resets, measures))
            for a in ancs:
                if a.active:
                    a.rounds_since_prep += 1
            for (row, aid, c, t) in measures:
                a = ancs[aid]
                self.check_records.append(dict(round=round_idx, row=row, anc=aid, check=c,
                                               outer=t, ops=a.ops_this_check,
                                               rounds=a.rounds_since_prep))
                a.active = False
                a.needs_reset = True
                if self.mode == "full":
                    a.direction = -a.direction
                elif self.mode == "local":
                    pass
                else:
                    nxt = a.row + a.direction
                    if nxt < 0 or nxt >= P:
                        a.direction = -a.direction
            round_idx += 1
            if not any(a.queue or a.active for a in ancs):
                break
            # ---- logical operation layer(s)
            n_sub = 1
            if self.compress:
                a = ancs[0]
                if a.active and not a.path_complete:
                    gaps = max(1, self.r_min - 1)
                    g = a.rounds_since_prep - 1          # index of this gap (0-based)
                    n = self.code.n
                    base, extra = divmod(n, gaps)
                    n_sub = base + (1 if g < extra else 0)
                    n_sub = max(n_sub, 1)
            for _sub in range(n_sub):
                self.segments.append(("ops", self._op_layer(content, ancs)))
        self.final_content = list(content)
        self.n_rounds = round_idx

    def _op_layer(self, content, ancs) -> list:
        """One layer of logical operations (at most one per ancilla); updates content."""
        P = self.P
        ops = []
        busy = set()
        for a in ancs:
            if not a.active or a.path_complete:
                continue
            if self.mode == "local":
                c, _ = a.current
                left = [r for r in range(P) if content[r][0] == "D" and content[r][1] in self.supports[c] - a.done]
                if left and all(r < a.row for r in left):
                    a.direction = -1
                elif left and all(r > a.row for r in left):
                    a.direction = +1
            nxt = a.row + a.direction
            if nxt < 0 or nxt >= P:
                a.direction = -a.direction
                nxt = a.row + a.direction
            if content[nxt][0] == "A" or nxt in busy or a.row in busy:
                continue   # blocked by the other ancilla: wait this layer
            b = content[nxt][1]
            c, _ = a.current
            if b in self.supports[c] and b not in a.done:
                kind = "CS"
                a.done.add(b)
            else:
                kind = "S"
            ops.append((kind, a.row, nxt))
            busy.update([a.row, nxt])
        for kind, ar, dr in ops:
            content[ar], content[dr] = content[dr], content[ar]
        for a in ancs:
            for kind, ar, dr in ops:
                if ar == a.row:
                    a.row = dr
                    a.passes += 1
                    a.ops_this_check += 1
                    break
            if a.active:
                a.path_complete = self._path_complete(a)
        return ops

    def _pick_local(self, a: Ancilla, content) -> None:
        """'local' mode: move the cheapest check of the current outer round to the front of the
        queue (path: to the nearer end of its support rows, then across them) and aim at it."""
        t0 = a.queue[0][1]
        best, best_cost = 0, None
        for i, (c, t) in enumerate(a.queue):
            if t != t0:
                break
            rows = [r for r in range(self.P) if content[r][0] == "D" and content[r][1] in self.supports[c]]
            lo, hi = min(rows), max(rows)
            cost = min(abs(a.row - lo), abs(a.row - hi)) + (hi - lo)
            if best_cost is None or cost < best_cost:
                best, best_cost = i, cost
        a.queue.insert(0, a.queue.pop(best))
        c, _ = a.queue[0]
        rows = [r for r in range(self.P) if content[r][0] == "D" and content[r][1] in self.supports[c]]
        lo, hi = min(rows), max(rows)
        a.direction = -1 if abs(a.row - hi) < abs(a.row - lo) and hi <= a.row else (+1 if lo > a.row else
                                                                                     (-1 if hi < a.row else a.direction))

    def _path_complete(self, a: Ancilla) -> bool:
        c, _ = a.current
        if self.mode in ("span", "local"):
            return self.supports[c] <= a.done
        if self.mode == "full":
            return a.passes >= self.code.n and self.supports[c] <= a.done
        raise ValueError(self.mode)

    # --------------------------------------------------------------- queries
    def summary(self) -> dict:
        recs = self.check_records
        return dict(P=self.P, rounds=self.n_rounds, checks=len(recs),
                    rounds_per_outer=self.n_rounds / self.n_outer,
                    max_ops=max(r["ops"] for r in recs),
                    mean_rounds_per_check=float(np.mean([r["rounds"] for r in recs])),
                    op_layers=sum(1 for s in self.segments if s[0] == "ops" and s[1]))

    def iter_contents(self):
        """Yield (segment, content-before-segment)."""
        content = list(self.initial_content)
        for seg in self.segments:
            yield seg, list(content)
            if seg[0] == "ops":
                for kind, ar, dr in seg[1]:
                    content[ar], content[dr] = content[dr], content[ar]


def op_cnots(kind: str, ar: int, dr: int) -> list[tuple[int, int]]:
    """Row-level CNOT layers (control_row, target_row) of a compiled logical op."""
    if kind == "CS":
        return [(ar, dr), (dr, ar)]
    if kind == "S":
        return [(ar, dr), (dr, ar), (ar, dr)]
    raise ValueError(kind)


if __name__ == "__main__":
    from .codes import load_code
    for nm in ["15_9_3", "15_6_5"]:
        code = load_code(nm)
        for mode in ["full", "span"]:
            for n_anc in [1, 2]:
                for d in [9, 15, 17]:
                    s = ElevatorSchedule(code, d, n_anc=n_anc, mode=mode)
                    print(nm, mode, n_anc, d, s.summary())
