"""Stratified (fixed-event-count) estimation of the bit-flip logical error rate.

Events form independent Poisson processes:
  unflagged X errors   intensity u_l = x_l (1 - f_l)           (only those with an effect)
  flagged events       intensity s_l = 2 x_l f_l, X with prob 1/2
  false flags          r per qubit per tick
so P(a unflagged, b flagged) = Pois(a; U) Pois(b; S) and

  P_fail(shot) = sum_{a,b} Pois(a; U) Pois(b; S) F(a, b),

where F(a, b) = P(decoder fails | a, b) is estimated by sampling exactly a and b
events (positions drawn proportionally to u_l and s_l) plus the false flags.  F
does not depend on p except through the decoder's priors, so the sum gives p_XL at
rates far below direct sampling; the truncation at a + b <= K is checked against
direct Monte Carlo where both are available.
"""
from __future__ import annotations

import math

import numpy as np

from .flags import FlagModel


class StrataSampler:
    def __init__(self, fm: FlagModel):
        self.fm = fm
        L = fm.bm.loc
        u = fm.x * (1.0 - fm.f)
        u = np.where(L.slot >= 0, u, 0.0)
        s = fm.e * fm.f
        self.cum_u = np.cumsum(u)
        self.cum_s = np.cumsum(s)
        self.U = float(self.cum_u[-1])     # totals from the cumulative sums (sampling-safe)
        self.S = float(self.cum_s[-1])

    def sample(self, a: int, b: int, rng):
        fm = self.fm
        if (a and self.U <= 0) or (b and self.S <= 0):
            raise ValueError("stratum with zero weight")
        iu = np.searchsorted(self.cum_u, rng.random(a) * self.U, side="right") if a else np.zeros(0, int)
        isf = np.searchsorted(self.cum_s, rng.random(b) * self.S, side="right") if b else np.zeros(0, int)
        flips_u = fm.slot[iu]
        # flagged events (X with prob 1/2) + false flags
        flips_s, wins = fm._realise(isf, rng, force_flag=np.ones(b, bool))
        flips = np.concatenate([flips_u[flips_u >= 0], flips_s])
        return flips, wins

    def estimate_F(self, decoder, a: int, b: int, n: int, seed: int, max_fail: int | None = None) -> dict:
        rng = np.random.default_rng(seed)
        fails = done = 0
        for _ in range(n):
            flips, wins = self.sample(a, b, rng)
            det, obs = self.fm.syndrome(flips)
            done += 1
            if not det.any() and not obs.any():
                continue
            pred = decoder.decode(det, wins)
            if np.any(pred != obs):
                fails += 1
                if max_fail is not None and fails >= max_fail:
                    break
        return dict(a=a, b=b, n=done, fails=fails)


def pois(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def combine(U: float, S: float, Fs: dict) -> dict:
    """Fs: {(a,b): (fails, n)} -> P_fail estimate with a 95% interval (Wilson per stratum,
    combined by adding the per-stratum bounds weighted by the Poisson probabilities)."""
    from .decode import wilson
    est = lo = hi = 0.0
    for (a, b), (fails, n) in Fs.items():
        w = pois(a, U) * pois(b, S)
        if n == 0:
            continue
        f = fails / n
        l, h = wilson(fails, n)
        est += w * f
        lo += w * l
        hi += w * h
    return dict(P=est, lo=lo, hi=hi)


def single_unflagged_exact(fm, decoder) -> tuple[float, int, int]:
    """Exact F(1,0) (no false flags): decode every merged mechanism alone.
    Returns (F, n_columns_failing, n_columns)."""
    bm = fm.bm
    L = bm.loc
    u = fm.x * (1.0 - fm.f)
    ok = L.slot >= 0
    cols = bm.slot_col[L.slot[ok]]
    good = cols >= 0
    mass = np.bincount(cols[good], weights=u[ok][good], minlength=bm.n_col)
    U = float(u[ok].sum())
    fail_mass = 0.0
    nfail = 0
    for c in range(bm.n_col):
        if mass[c] <= 0:
            continue
        det = bm.col_D[:, c].astype(np.uint8)
        obs = bm.col_L[:, c].astype(np.uint8)
        pred = decoder.decode(det, set()) if det.any() else np.zeros_like(obs)
        if np.any(pred != obs):
            fail_mass += mass[c]
            nfail += 1
    return (fail_mass / U if U > 0 else 0.0), nfail, int((mass > 0).sum())


def min_logical_weight_le2(bm) -> bool:
    """True if the merged DEM has an undetectable logical of weight <= 2."""
    D = bm.col_D.T
    Lm = bm.col_L.T
    if np.any((~D.any(axis=1)) & Lm.any(axis=1)):
        return True
    key = {}
    for c in range(D.shape[0]):
        k = D[c].tobytes()
        if k in key and not np.array_equal(Lm[key[k]], Lm[c]):
            return True
        key.setdefault(k, c)
    return False
