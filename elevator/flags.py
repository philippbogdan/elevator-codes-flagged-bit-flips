"""Flagged bit flips on the block-level Z memory: sampling and flag-aware decoding.

Flag model (parameters; every one is varied in the study):
  eff[c]      probability that an event at a location of class c (idle, gate, prep,
              meas) raises a flag (flag efficiency).  Baseline: idle only (the case
              established by arXiv:2607.01375), others 0 or equal to eff_idle.
  false_rate  probability of a false flag per physical qubit per tick (dark counts,
              emission without a flip).
  window      timing precision: a flag reports (qubit, window index) with windows of
              `window` ticks aligned to tick 0; window=0 means exact location
              (sub-tick: before/after a CNOT is known).

A flag on (q, W) makes the decoder replace the prior of every location of qubit q
in W by its exact posterior under independent events; locations outside flagged
windows get the posterior given 'no flag'.  Slot and column (merged mechanism)
probabilities are XOR-combinations of location posteriors.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .blocklevel import BlockModel


@dataclass
class FlagConfig:
    eff: tuple = (0.0, 0.0, 0.0, 0.0)     # idle, gate, prep, meas
    false_rate: float = 0.0               # per qubit per tick
    window: int = 0                       # ticks; 0 = exact location

    @staticmethod
    def make(f: float, classes=("idle",), false_rate: float = 0.0, window: int = 0):
        names = ["idle", "gate", "prep", "meas"]
        eff = tuple(f if n in classes else 0.0 for n in names)
        return FlagConfig(eff=eff, false_rate=false_rate, window=window)


class FlagModel:
    """Per-location event probabilities, flag efficiencies and index structures."""

    def __init__(self, bm: BlockModel, cfg: FlagConfig):
        self.bm = bm
        self.cfg = cfg
        L = bm.loc
        self.x = L.xprob                       # Pauli X probability
        self.e = 2.0 * L.xprob                 # event probability
        self.f = np.asarray(cfg.eff, dtype=float)[L.cls]
        self.n_qubits = bm.P * bm.W
        self.n_ticks = bm.n_ticks
        w = cfg.window
        # window id of every location: exact -> unique per location
        if w <= 0:
            self.win = np.arange(len(L.qubit), dtype=np.int64)
        else:
            self.win = L.qubit.astype(np.int64) * (self.n_ticks // w + 1) + L.tick // w
        order = np.argsort(self.win, kind="stable")
        self.order = order
        sw = self.win[order]
        self.win_sorted = sw
        # unique windows and their location ranges
        uw, start = np.unique(sw, return_index=True)
        self.uwin = uw
        self.wstart = start
        self.wend = np.append(start[1:], len(sw))
        # false-flag probability per window (per qubit per tick rate)
        r = cfg.false_rate
        if w <= 0:
            self.r_win = r            # interpreted per location for exact flags
        else:
            self.r_win = 1.0 - (1.0 - r) ** w
        # background (no-flag) posterior X probability
        ef = self.e * self.f
        self.x_bg = self.x * (1.0 - self.f) / (1.0 - ef)
        # cumulative weights for sampling
        self.cum_e = np.cumsum(self.e)
        self.E = float(self.cum_e[-1])
        self.slot = L.slot
        sp_bg = bm.slot_probs(self.x_bg)
        self.lg_slot_bg = np.log1p(-2 * np.minimum(sp_bg, 0.5 - 1e-15))
        self.col_bg = bm.col_probs(sp_bg)

    # ------------------------------------------------------------------ sampling
    def sample_poisson(self, rng):
        """Independent events at every location (direct Monte Carlo)."""
        n = rng.poisson(self.E)
        idx = np.searchsorted(self.cum_e, rng.random(n) * self.E, side="right")
        return self._realise(idx, rng)

    def _realise(self, idx, rng, force_flag=None, force_x=None):
        """Events at location indices idx -> (flipped slots, flagged window ids)."""
        n = len(idx)
        flagged = rng.random(n) < self.f[idx] if force_flag is None else force_flag
        xs = rng.random(n) < 0.5 if force_x is None else force_x
        sl = self.slot[idx]
        flips = sl[(xs) & (sl >= 0)]
        wins = set(self.win[idx[flagged]].tolist())
        # false flags
        r = self.cfg.false_rate
        if r > 0:
            if self.cfg.window <= 0:
                nf = rng.poisson(r * len(self.slot))
                fl = rng.integers(0, len(self.slot), nf)
                wins.update(self.win[fl].tolist())
            else:
                nwin_total = self.n_qubits * (self.n_ticks // self.cfg.window + 1)
                nf = rng.poisson(self.r_win * nwin_total)
                if nf:
                    qs = rng.integers(0, self.n_qubits, nf)
                    ws = rng.integers(0, self.n_ticks // self.cfg.window + 1, nf)
                    wins.update((qs.astype(np.int64) * (self.n_ticks // self.cfg.window + 1) + ws).tolist())
        return flips, wins

    def syndrome(self, flips):
        bm = self.bm
        if len(flips) == 0:
            return np.zeros(bm.n_det, np.uint8), np.zeros(bm.n_obs, np.uint8)
        cnt = np.bincount(flips, minlength=bm.n_slots) & 1
        nz = np.nonzero(cnt)[0]
        det = (bm.slot_D[:, nz].sum(axis=1) & 1).astype(np.uint8)
        obs = (bm.slot_L[:, nz].sum(axis=1) & 1).astype(np.uint8)
        return det, obs

    # ------------------------------------------------------------------ posteriors
    def column_probs(self, wins) -> np.ndarray:
        """Decoder column probabilities given the set of flagged window ids."""
        if not wins:
            return self.col_bg
        bm = self.bm
        lg_slot = self.lg_slot_bg.copy()
        r = self.r_win
        for w in wins:
            k = np.searchsorted(self.uwin, w)
            if k >= len(self.uwin) or self.uwin[k] != w:
                continue          # flag on a qubit/window without any location (no effect)
            ids = self.order[self.wstart[k]:self.wend[k]]
            ef = self.e[ids] * self.f[ids]
            log_no = np.log1p(-ef)
            tot_no = log_no.sum() + np.log1p(-r)
            p_flag = -np.expm1(tot_no)
            if p_flag <= 0:
                continue
            others_no = tot_no - log_no                   # log P(no flag from others)
            p_others = -np.expm1(others_no)
            post_e = self.e[ids] * (self.f[ids] + (1 - self.f[ids]) * p_others) / p_flag
            post_x = np.minimum(0.5 * post_e, 0.5 - 1e-12)
            sl = self.slot[ids]
            ok = sl >= 0
            if not ok.any():
                continue
            old = np.log1p(-2 * np.minimum(self.x_bg[ids][ok], 0.5 - 1e-15))
            new = np.log1p(-2 * post_x[ok])
            np.add.at(lg_slot, sl[ok], new - old)
        sp = 0.5 * (1 - np.exp(lg_slot))
        return bm.col_probs(sp)


class BpOsdFlagDecoder:
    """BP+OSD on the merged block-level DEM with per-shot flag posteriors."""

    def __init__(self, fm: FlagModel, **opts):
        from ldpc import BpOsdDecoder
        o = dict(bp_method="product_sum", max_iter=100, osd_method="osd_cs", osd_order=7)
        o.update(opts)
        self.fm = fm
        H = fm.bm.col_D.astype(np.uint8)
        self.L = fm.bm.col_L.astype(np.uint8)
        import scipy.sparse as sp
        self.dec = BpOsdDecoder(sp.csr_matrix(H), error_channel=list(fm.col_bg), **o)
        self._bg = True

    def decode(self, det, wins):
        if not det.any():
            return np.zeros(self.L.shape[0], np.uint8)
        if wins:
            self.dec.update_channel_probs(list(self.fm.column_probs(wins)))
            self._bg = False
        elif not self._bg:
            self.dec.update_channel_probs(list(self.fm.col_bg))
            self._bg = True
        e = self.dec.decode(det)
        return (self.L @ e) & 1


def direct_mc(fm: FlagModel, decoder, shots: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    fails = 0
    nflags = 0
    for _ in range(shots):
        flips, wins = fm.sample_poisson(rng)
        det, obs = fm.syndrome(flips)
        nflags += len(wins)
        if not det.any() and not obs.any():
            continue
        pred = decoder.decode(det, wins)
        if np.any(pred != obs):
            fails += 1
    return dict(shots=shots, fails=fails, mean_flags=nflags / shots)
