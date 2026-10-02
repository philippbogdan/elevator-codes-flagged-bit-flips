"""Exact maximum-likelihood decoding of a detector error model with a syndrome trellis.

Mechanisms are processed in order of their first detector; the state is the parity of
the currently open detectors plus the observable bits.  A detector is closed (projected
onto its observed value) after the last mechanism that touches it.  Cost is
O(#mechanisms * 2^(width + #observables)); practical when the width (maximum number of
simultaneously open detectors) is <= ~16, e.g. a repetition code of distance <= 15.
"""
from __future__ import annotations

import numpy as np
import stim


class TrellisDecoder:
    def __init__(self, dem: stim.DetectorErrorModel):
        mechs = []
        for inst in dem.flattened():
            if inst.type != "error":
                continue
            p = inst.args_copy()[0]
            dets, obs = [], 0
            for t in inst.targets_copy():
                if t.is_relative_detector_id():
                    dets.append(t.val)
                elif t.is_logical_observable_id():
                    obs ^= 1 << t.val
            if dets or obs:
                mechs.append((p, sorted(set(dets)), obs))
        mechs.sort(key=lambda m: (m[1][0] if m[1] else 10 ** 9, m[1][-1] if m[1] else 0))
        self.mechs = mechs
        self.n_det = dem.num_detectors
        self.n_obs = dem.num_observables
        last = {}
        for i, (_, ds, _) in enumerate(mechs):
            for dd in ds:
                last[dd] = i
        self.close_after = {}
        for dd, i in last.items():
            self.close_after.setdefault(i, []).append(dd)
        # simulate bit allocation to find the width
        open_ = set()
        width = 0
        for i, (_, ds, _) in enumerate(mechs):
            open_.update(ds)
            width = max(width, len(open_))
            for dd in self.close_after.get(i, []):
                open_.discard(dd)
        self.width = width

    def decode(self, det: np.ndarray, return_probs: bool = False):
        nb = self.width
        no = self.n_obs
        size = 1 << (nb + no)
        v = np.zeros(size)
        v[0] = 1.0
        pos = {}
        free = list(range(nb))[::-1]
        idx = np.arange(size, dtype=np.int64)
        for i, (p, ds, obs) in enumerate(self.mechs):
            for dd in ds:
                if dd not in pos:
                    pos[dd] = free.pop()
            mask = obs << nb
            for dd in ds:
                mask |= 1 << pos[dd]
            if p > 0:
                v = (1 - p) * v + p * v[idx ^ mask]
            for dd in self.close_after.get(i, []):
                b = pos.pop(dd)
                bit = (idx >> b) & 1
                want = int(det[dd])
                v = np.where(bit == want, v, 0.0)
                # clear the bit: move mass to bit = 0 so the slot can be reused
                if want:
                    v = v[idx ^ (1 << b)] * ((idx >> b) & 1 == 0)
                free.append(b)
                s = v.sum()
                if s > 0:
                    v /= s
        probs = np.array([v[o << nb] for o in range(1 << no)])
        best = int(np.argmax(probs))
        pred = np.array([(best >> j) & 1 for j in range(no)], dtype=np.uint8)
        return (pred, probs) if return_probs else pred
