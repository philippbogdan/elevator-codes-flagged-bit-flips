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

import scipy.sparse as sp
from ldpc import BpOsdDecoder
from scipy.optimize import Bounds, LinearConstraint, milp

from .blocklevel import BlockModel
from .mle import mle_solve


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
        self.E = float(self.cum_e[-1])     # total from the cumulative sum (sampling-safe)
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
        o = dict(bp_method="product_sum", max_iter=100, osd_method="osd_cs", osd_order=7)
        o.update(opts)
        self.fm = fm
        H = fm.bm.col_D.astype(np.uint8)
        self.L = fm.bm.col_L.astype(np.uint8)
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


class MleFlagDecoder:
    """Exact most-likely-error decoder (integer program, HiGHS via scipy) on the merged
    block-level DEM with per-shot flag posteriors: min sum_j w_j x_j  s.t.  H x = s (mod 2),
    w_j = log((1 - p_j) / p_j).  Used to check the optimality of BP+OSD."""

    def __init__(self, fm: FlagModel):
        self.fm = fm
        self.H = sp.csr_matrix(fm.bm.col_D.astype(np.int64))
        self.L = fm.bm.col_L.astype(np.uint8)
        self.colw = np.asarray(fm.bm.col_D.sum(axis=0)).ravel()

    def decode(self, det, wins):
        if not det.any():
            return np.zeros(self.L.shape[0], np.uint8)
        p = self.fm.column_probs(wins) if wins else self.fm.col_bg
        p = np.clip(p, 1e-300, 0.5)
        w = np.log((1 - p) / p)
        nd, nc = self.H.shape
        # variables: x (nc binary), z (nd integer >= 0):  H x - 2 z = det
        A = sp.hstack([self.H, -2 * sp.identity(nd, format="csr")]).tocsr()
        c = np.concatenate([w, np.zeros(nd)])
        zmax = np.asarray(self.H.sum(axis=1)).ravel() // 2 + 1
        lb = np.zeros(nc + nd)
        ub = np.concatenate([np.ones(nc), zmax])
        integrality = np.ones(nc + nd)
        res = milp(c, constraints=LinearConstraint(A, det.astype(float), det.astype(float)),
                   integrality=integrality, bounds=Bounds(lb, ub), options=dict(disp=False))
        if res.x is None:
            raise RuntimeError("MLE infeasible")
        x = np.round(res.x[:nc]).astype(np.uint8)
        return (self.L @ x) & 1


def _slot_probs_given(fm: FlagModel, wins) -> np.ndarray:
    """Slot flip probabilities given flagged windows (same posteriors as column_probs)."""
    if not wins:
        return 0.5 * (1 - np.exp(fm.lg_slot_bg))
    lg_slot = fm.lg_slot_bg.copy()
    r = fm.r_win
    for w in wins:
        k = np.searchsorted(fm.uwin, w)
        if k >= len(fm.uwin) or fm.uwin[k] != w:
            continue
        ids = fm.order[fm.wstart[k]:fm.wend[k]]
        ef = fm.e[ids] * fm.f[ids]
        log_no = np.log1p(-ef)
        tot_no = log_no.sum() + np.log1p(-r)
        p_flag = -np.expm1(tot_no)
        if p_flag <= 0:
            continue
        p_others = -np.expm1(tot_no - log_no)
        post_x = np.minimum(0.5 * fm.e[ids] * (fm.f[ids] + (1 - fm.f[ids]) * p_others) / p_flag, 0.5 - 1e-12)
        sl = fm.slot[ids]
        ok = sl >= 0
        old = np.log1p(-2 * np.minimum(fm.x_bg[ids][ok], 0.5 - 1e-15))
        np.add.at(lg_slot, sl[ok], np.log1p(-2 * post_x[ok]) - old)
    return 0.5 * (1 - np.exp(lg_slot))


class TrellisMLDecoder:
    """Exact maximum-likelihood (coset) decoder for the block-level Z memory: forward
    algorithm over the 2^P error frames of the rows, with independent slot flips.
    Exact for the flag model whenever every flagged window covers a single slot."""

    def __init__(self, fm: FlagModel):
        bm = fm.bm
        self.fm = fm
        self.bm = bm
        self.P = bm.P
        self.N = 1 << self.P
        idx = np.arange(self.N, dtype=np.int64)
        self.idx = idx
        self._cx = {}
        s = bm.s
        code = s.code
        # measurement ids of checks (in detector order) and final rows
        self.check_mids = [m[0] for m in bm.meas_info if m[1] == "check"]
        self.check_of_mid = {m[0]: m[2][0] for m in bm.meas_info if m[1] == "check"}
        content = s.final_content
        self.final_rows = [r for r in range(self.P) if content[r][0] == "D"]
        row_of_block = {content[r][1]: r for r in self.final_rows}
        self.check_rows = [[row_of_block[int(b)] for b in np.nonzero(code.H[c])[0]] for c in range(code.m)]
        self.info_rows = [row_of_block[b] for b in code.info_set]
        self.m = code.m

    def _perm(self, c, t):
        key = (c, t)
        if key not in self._cx:
            i = self.idx
            self._cx[key] = i ^ (((i >> c) & 1) << t)
        return self._cx[key]

    def decode(self, det, wins, return_probs=False):
        bm, P, N = self.bm, self.P, self.N
        sp = _slot_probs_given(self.fm, wins)
        v = np.zeros(N)
        v[0] = 1.0
        # raw check outcomes from detectors (cumulative per check)
        last = {}
        raw = {}
        for di, mid in enumerate(self.check_mids):
            c = self.check_of_mid[mid]
            raw[mid] = int(det[di]) ^ last.get(c, 0)
            last[c] = raw[mid]
        nd_checks = len(self.check_mids)
        for op in bm.ops:
            kind = op[0]
            if kind == "SLOT":
                r, sl = op[1], op[2]
                q = sp[sl]
                if q > 0:
                    v3 = v.reshape(N >> (r + 1), 2, 1 << r)
                    a0 = v3[:, 0, :].copy()
                    a1 = v3[:, 1, :]
                    v3[:, 0, :] = (1 - q) * a0 + q * a1
                    v3[:, 1, :] = (1 - q) * a1 + q * a0
            elif kind == "CX":
                v = v[self._perm(op[1], op[2])]
            elif kind == "R":
                r = op[1]
                v3 = v.reshape(N >> (r + 1), 2, 1 << r)
                v3[:, 0, :] += v3[:, 1, :]
                v3[:, 1, :] = 0.0
            elif kind == "M":
                r, mid = op[1], op[2]
                if mid in raw:
                    v3 = v.reshape(N >> (r + 1), 2, 1 << r)
                    v3[:, 1 - raw[mid], :] = 0.0
                    s_ = v.sum()
                    if s_ > 0:
                        v /= s_
        # final: parity constraints on data rows, then group by info-set bits
        i = self.idx
        ok = np.ones(N, bool)
        for c in range(self.m):
            par = np.zeros(N, dtype=np.int64)
            for r in self.check_rows[c]:
                par ^= (i >> r) & 1
            want = int(det[nd_checks + c]) ^ last.get(c, 0)
            ok &= (par == want)
        cls = np.zeros(N, dtype=np.int64)
        for j, r in enumerate(self.info_rows):
            cls |= ((i >> r) & 1) << j
        probs = np.bincount(cls[ok], weights=v[ok], minlength=1 << len(self.info_rows))
        best = int(np.argmax(probs))
        pred = np.array([(best >> j) & 1 for j in range(len(self.info_rows))], dtype=np.uint8)
        return (pred, probs) if return_probs else pred


class ExclusiveMleDecoder:
    """Most-likely-error decoder for the flag model with at most one event per flagged
    window (exact up to O(E_W) corrections, E_W = event probability of a window).

    Variables: x_c (unflagged flip of merged column c, prior from the no-flag posterior of
    locations outside flagged windows) and y_{W,c} (the event behind flag W flipped column
    c).  Costs: w_c = log((1-q_c)/q_c);  v_{W,c} = log(pi_{W,0} / pi_{W,c}) with
    pi_{W,c} = P(the window's event flipped column c | flag) and pi_{W,0} = P(no flip | flag).
    Constraints: H (x + sum_W y_W) = s (mod 2),  sum_c y_{W,c} <= 1."""

    def __init__(self, fm: FlagModel):
        self.fm = fm
        bm = fm.bm
        self.H = sp.csc_matrix(bm.col_D.astype(np.int64))
        self.L = bm.col_L.astype(np.uint8)
        self.nd, self.nc = self.H.shape
        self.lg_col_bg = np.log1p(-2 * np.minimum(fm.col_bg, 0.5 - 1e-15))
        self.zmax = np.asarray(self.H.sum(axis=1)).ravel() // 2 + 2

    def _window_terms(self, wins):
        """For each flagged window: (columns, pi_c) and the location ids (to remove from bg)."""
        fm = self.fm
        out = []
        for w in wins:
            k = np.searchsorted(fm.uwin, w)
            if k >= len(fm.uwin) or fm.uwin[k] != w:
                continue
            ids = fm.order[fm.wstart[k]:fm.wend[k]]
            ef = fm.e[ids] * fm.f[ids]
            tot = ef.sum()
            r = fm.r_win
            denom = r + tot
            if denom <= 0:
                continue
            cols = fm.bm.slot_col[np.maximum(fm.slot[ids], 0)]
            cols = np.where(fm.slot[ids] >= 0, cols, -1)
            ok = cols >= 0
            # P(event at l and X) given exactly one event-or-false-flag explains the flag
            pl = 0.5 * ef / denom
            uc, inv = np.unique(cols[ok], return_inverse=True)
            pc = np.bincount(inv, weights=pl[ok], minlength=len(uc))
            p0 = 1.0 - pc.sum()
            out.append((uc, pc, max(p0, 1e-300), ids))
        return out

    def decode(self, det, wins):
        if not det.any():
            return np.zeros(self.L.shape[0], np.uint8)
        fm = self.fm
        terms = self._window_terms(wins) if wins else []
        lg = self.lg_col_bg.copy()
        # remove the flagged windows' locations from the background columns
        for (uc, pc, p0, ids) in terms:
            sl = fm.slot[ids]
            okk = sl >= 0
            if okk.any():
                cols = fm.bm.slot_col[sl[okk]]
                good = cols >= 0
                np.add.at(lg, cols[good], -np.log1p(-2 * np.minimum(fm.x_bg[ids][okk][good], 0.5 - 1e-15)))
        q = np.clip(0.5 * (1 - np.exp(lg)), 1e-300, 0.5)
        w = np.log((1 - q) / q)
        ycols = []
        ycost = []
        ywin = []
        for wi, (uc, pc, p0, ids) in enumerate(terms):
            for c, pcv in zip(uc, pc):
                if pcv <= 0:
                    continue
                ycols.append(c)
                ycost.append(np.log(p0 / pcv))
                ywin.append(wi)
        x = mle_solve(self.H, w, det, ycols, ycost, ywin)
        return (self.L @ x) & 1
