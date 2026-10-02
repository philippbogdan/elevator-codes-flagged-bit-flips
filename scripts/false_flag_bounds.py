"""Rigorous upper bounds on the strata F(1, 0), F(0, 1) and (exact timing) F(0, 2) when false flags are
present (r > 0), for codes whose merged block-level DEM has distance 3.  Without them these strata, which
carry most of the Poisson weight, would enter the 95 % upper bounds at their Wilson bounds (~1/n).

The decoder (exclusive-window MLE, elevator/flags.py) minimises the cost of an explanation: w_c for an
unflagged column c (background no-flag posterior), v_{W,c} = log(pi_{W,0} / pi_{W,c}) for column c of a
flagged window W (the false-flag rate enters pi), 0 for "no event" in W.  Let t be the cost of the true
explanation.  The decoder fails only if its explanation differs from the truth by a nontrivial logical
z (>= 3 columns: the DEM has no logical of <= 2 columns); z consists of true columns the decoder drops
or swaps and of an alternative set E' of n_x unflagged columns and n_f columns of falsely flagged
windows, and the decoder's cost of E' is at most t + eps (what it drops is saved).  With v(c) the
cheapest false-flag cost of column c, P(c) <= r_W N_W(c) the probability that a window holding c is
falsely flagged, w_min the cheapest unflagged column and v_min the cheapest false-flag column, every
structure that the costs allow is bounded (c0: the true column(s), as one combined signature):

    (n_x, n_f) = (1, 1):  sum_c1 P(c1) [a column c with c0 + c1 + c logical, w_c + v(c1) <= t]
                 (0, 2):  sum_{c1<c2} P(c1) P(c2) [c0 + c1 + c2 logical]
                 (1, 2):  sum_{c1<c2} P(c1) P(c2) [a column c with c0 + c1 + c2 + c logical,
                                                   w_c + v(c1) + v(c2) <= t]
                 (0, 3):  sum_{c1<c2<c3} P1 P2 P3 [c0 + c1 + c2 + c3 logical, v1 + v2 + v_min <= t]
    other (n_x, n_f) with n_x w_min + n_f v_min <= t:  P(N >= n_f) for N ~ Poisson(Lambda), all false
    flags; n_x >= 2 must be impossible (2 w_min > t), otherwise no bound is returned.

F(1, 0): the true unflagged column's cost is taken with its three largest window contributions removed
(flagged windows leave the background), plus the probability that four or more false flags hit it.
F(0, 1): the true flagged event (window W0, column c0, cost v_{W0,c0}, X with probability 1/2); for a
window with several columns also the switch to another of its columns, completed by one more column (or
more, through the Poisson tail).  With exact timing and 2 min(v_min, w_min) > max t it is 0 (cost rule).
F(0, 2), exact timing: both true events (X with probability 1/2 each) dropped, kept or used, completed
as above.  The bounds use no decoding; their inputs are the decoder's own costs.  Writes
results/false_flag_bounds.json keyed by the setting (code, n_anc, d, p_X, f, classes, window, r, ...).

  python scripts/false_flag_bounds.py
"""
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from elevator.flagstudy import _build  # noqa: E402

CLASS_TAG = {("idle",): "idle", ("idle", "gate"): "idle+gate", ("idle", "gate", "prep", "meas"): "all"}
U64 = np.uint64


def setting_key(spec):
    fl = spec["flag"]
    return "|".join(str(x) for x in (spec["code"], spec.get("n_anc", 1), spec["d"], spec["p_x"], fl["f"],
                                       CLASS_TAG[tuple(fl.get("classes", ["idle"]))], fl.get("window", 0),
                                       fl["false_rate"], ",".join(spec.get("idle_ctx", [])),
                                       spec.get("n_outer", 5)))


def _pack(M):
    assert M.shape[0] <= 63
    w = (U64(1) << np.arange(M.shape[0], dtype=U64))
    return (M.astype(U64) * w[:, None]).sum(axis=0).astype(U64)


def _pois_tail(lam, n):
    """P(Poisson(lam) >= n)"""
    if n is None:
        return 0.0
    if n <= 0:
        return 1.0
    return max(0.0, 1.0 - sum(math.exp(-lam) * lam ** k / math.factorial(k) for k in range(n)))


def _eps(t):
    return 1e-3 * abs(t) + 1e-3


class Lookup:
    """sorted keys with values; vectorised lookup returning a default where absent"""

    def __init__(self, keys, vals):
        o = np.argsort(keys, kind="stable")
        self.k, self.v = keys[o], vals[o]

    def __call__(self, q, default):
        i = np.searchsorted(self.k, q)
        i = np.minimum(i, len(self.k) - 1) if len(self.k) else i
        hit = (len(self.k) > 0) & (self.k[i] == q) if len(self.k) else np.zeros(len(q), bool)
        return np.where(hit, self.v[i] if len(self.k) else default, default)


def _group_sum(keys, vals):
    uk, inv = np.unique(keys, return_inverse=True)
    return Lookup(uk, np.bincount(inv, weights=vals))


class Tables:
    def __init__(self, spec):
        code, sched, bm, fm, dec, ss = _build(spec)
        self.d_code = code.d
        nc = bm.n_col
        self.nc = nc
        self.det = _pack(np.asarray(bm.col_D))
        self.obs = _pack(np.asarray(bm.col_L))
        self.nob = int(bm.col_L.shape[0])
        assert int(bm.col_D.shape[0]) + self.nob <= 63
        q = np.clip(0.5 * (1 - np.exp(dec.lg_col_bg)), 1e-300, 0.5)
        self.w = np.log((1 - q) / q)
        self.w_min = float(self.w.min())
        col = np.where(fm.slot >= 0, bm.slot_col[np.maximum(fm.slot, 0)], -1)
        ok = col >= 0
        ef = fm.e * fm.f
        self.r_win = float(fm.r_win)
        self.px = fm.px_event
        # per (window, column): flagged mass and background contribution; per window: all flagged mass
        key = fm.win[ok].astype(np.int64) * (nc + 1) + col[ok]
        uk, inv = np.unique(key, return_inverse=True)
        ef_wc = np.bincount(inv, weights=ef[ok])
        bg_wc = np.bincount(inv, weights=np.log1p(-2 * np.minimum(fm.x_bg[ok], 0.5 - 1e-15)))
        c_of = (uk % (nc + 1)).astype(np.int64)
        uw, invw = np.unique(fm.win, return_inverse=True)
        tot_w = np.bincount(invw, weights=ef)
        wi = np.searchsorted(uw, uk // (nc + 1))
        denom = self.r_win + tot_w[wi]
        pc = np.where(denom > 0, self.px * ef_wc / np.where(denom > 0, denom, 1.0), 0.0)
        p0 = np.maximum(1.0 - np.bincount(wi, weights=pc, minlength=len(uw))[wi], 1e-300)
        has = pc > 0
        v = np.full(len(pc), np.inf)
        v[has] = np.log(p0[has] / pc[has])
        self.wc_win, self.wc_col, self.wc_v, self.wc_ef = wi, c_of, v, ef_wc
        self.vmin = np.full(nc, np.inf)
        np.minimum.at(self.vmin, c_of[has], v[has])
        self.nw = np.bincount(c_of[has], minlength=nc).astype(float)
        self.P = np.minimum(1.0, self.r_win * self.nw)
        self.Lam = float(self.r_win * len(np.unique(wi[has])))
        live = np.isfinite(self.vmin) & (self.P > 0)
        self.live = np.nonzero(live)[0]
        self.v_gmin = float(self.vmin[live].min()) if live.any() else np.inf
        # truth cost of an unflagged column with its 3 largest window contributions removed
        rem = np.zeros(nc)
        o = np.lexsort((bg_wc, c_of))
        cs, bs = c_of[o], bg_wc[o]
        start = np.r_[0, np.nonzero(np.diff(cs))[0] + 1]
        for k in range(3):
            idx = start + k
            okk = idx < len(cs)
            okk[okk] = cs[idx[okk]] == cs[start[okk]]
            np.add.at(rem, cs[start[okk]], bs[idx[okk]])
        q3 = np.clip(0.5 * (1 - np.exp(dec.lg_col_bg - rem)), 1e-300, 0.5)
        self.w3 = np.log((1 - q3) / q3)
        u = fm.x * (1 - fm.f)
        self.u = np.bincount(col[ok], weights=u[ok], minlength=nc)
        self.S = float(ef.sum())
        # lookups: cheapest unflagged column per (det) and per (det, obs) -> "other observable" minimum
        dk = self.det
        do = (self.det << U64(self.nob)) | self.obs
        o2 = np.lexsort((self.w, dk))
        ud, first = np.unique(dk[o2], return_index=True)
        self.b1w = Lookup(ud, self.w[o2][first])
        self.b1o = Lookup(ud, self.obs[o2][first])
        # best among columns whose observable differs from the group's best one
        b1o_all = self.b1o(dk, U64(0))
        other = self.obs != b1o_all
        o3 = np.lexsort((self.w[other], dk[other]))
        ud2, first2 = np.unique(dk[other][o3], return_index=True)
        self.b2w = Lookup(ud2, self.w[other][o3][first2])
        # false-flag mass per det and per (det, obs) (no cost filter: upper bounds)
        L = self.live
        self.Qh = _group_sum(dk[L], self.P[L])
        self.Qho = _group_sum(do[L], self.P[L])
        # pairs of false-flag columns
        i1, i2 = np.triu_indices(len(L), 1)
        a, b = L[i1], L[i2]
        self.pd = dk[a] ^ dk[b]
        self.po = self.obs[a] ^ self.obs[b]
        self.pP = self.P[a] * self.P[b]
        self.pv = self.vmin[a] + self.vmin[b]
        self.PPh = _group_sum(self.pd, self.pP)
        self.PPho = _group_sum((self.pd << U64(self.nob)) | self.po, self.pP)

    # vectorised: cheapest unflagged column with detector key h and observable != l
    def min_w_other(self, h, l):
        w1 = self.b1w(h, np.inf)
        o1 = self.b1o(h, U64(0))
        w2 = self.b2w(h, np.inf)
        return np.where(o1 != l, w1, w2)

    def q_other(self, h, l):
        """sum of P over false-flag columns with detector key h and observable != l"""
        return np.maximum(self.Qh(h, 0.0) - self.Qho((h << U64(self.nob)) | l, 0.0), 0.0)

    def pp_other(self, h, l):
        """sum of P1 P2 over unordered false-flag column pairs completing (h, l) to a nontrivial logical"""
        return np.maximum(self.PPh(h, 0.0) - self.PPho((h << U64(self.nob)) | l, 0.0), 0.0)

    def completions(self, D0, O0, t):
        """probability bound for an alternative E' (|E'| >= 2) with D0/O0 + E' a nontrivial logical and
        cost(E') <= t + eps (structures (1,1), (0,2), (1,2), (0,3))"""
        T = t + _eps(t)
        tot = 0.0
        L = self.live
        if self.w_min + self.v_gmin <= T:                       # (1, 1)
            mw = self.min_w_other(D0 ^ self.det[L], O0 ^ self.obs[L])
            tot += float(self.P[L][mw + self.vmin[L] <= T].sum())
        if 2 * self.v_gmin <= T:                                 # (0, 2)
            tot += float(self.pp_other(np.array([D0], dtype=U64), np.array([O0], dtype=U64))[0])
        if self.w_min + 2 * self.v_gmin <= T:                   # (1, 2)
            sel = self.pv + self.w_min <= T
            mw = self.min_w_other(D0 ^ self.pd[sel], O0 ^ self.po[sel])
            tot += float(self.pP[sel][mw + self.pv[sel] <= T].sum())
        if 3 * self.v_gmin <= T:                                 # (0, 3)
            sel = self.pv + self.v_gmin <= T
            tot += float((self.pP[sel] * self.q_other(D0 ^ self.pd[sel], O0 ^ self.po[sel])).sum()) / 3.0
        return tot

    def tail_n(self, tmax):
        """smallest number of false flags of a structure not enumerated that the costs allow; None if none;
        -1 if two unflagged columns could be cheaper than the truth (no bound)"""
        T = tmax + _eps(tmax)
        if 2 * self.w_min <= T:
            return -1
        if self.w_min + 3 * self.v_gmin <= T:
            return 3
        if 4 * self.v_gmin <= T:
            return 4
        return None


def bounds_for(spec):
    from elevator.codes import load_code
    if load_code(spec["code"]).d != 3:
        return None
    T = Tables(spec)
    window = int(spec["flag"].get("window", 0))
    out = {"r_win": T.r_win, "v_min": T.v_gmin, "w_min": T.w_min, "Lambda": T.Lam}
    vfin = np.isfinite(T.wc_v)
    vmax_all = float(T.wc_v[vfin].max()) if vfin.any() else 0.0
    # ---------------- F(1, 0)
    cols = np.nonzero(T.u > 0)[0]
    t0 = np.maximum(T.w3, vmax_all)
    n = T.tail_n(float(t0[cols].max()))
    if n == -1:
        out["1,0"] = 1.0
    else:
        acc = sum(T.u[c] * (T.completions(T.det[c], T.obs[c], float(t0[c])) + _pois_tail(T.r_win * T.nw[c], 4))
                  for c in cols)
        out["1,0"] = min(1.0, acc / T.u[cols].sum() + _pois_tail(T.Lam, n))
        out["tail_10"] = n
    # ---------------- F(0, 1)
    real = vfin & (T.wc_ef > 0)
    tv, cv, wv, ev = T.wc_v[real], T.wc_col[real], T.wc_win[real], T.wc_ef[real]
    tmax = float(tv.max()) if len(tv) else 0.0
    if window == 0 and 2 * min(T.v_gmin, T.w_min) > tmax + _eps(tmax):
        out["0,1"] = 0.0
        out["cost_rule_01"] = True
    else:
        out["cost_rule_01"] = False
        n = T.tail_n(tmax)
        if n == -1:
            out["0,1"] = 1.0
        else:
            cache = {}
            acc = 0.0
            order = np.argsort(wv, kind="stable")
            wsrt = wv[order]
            bounds = np.r_[0, np.nonzero(np.diff(wsrt))[0] + 1, len(wsrt)]
            for s_, e_ in zip(bounds[:-1], bounds[1:]):
                ids = order[s_:e_]                                  # the (window, column) entries of one window
                for i in ids:
                    c0, t = int(cv[i]), float(tv[i])
                    k = (c0, round(t, 6))
                    if k not in cache:
                        cache[k] = T.completions(T.det[c0], T.obs[c0], t)
                    b = cache[k]
                    for j in ids:                                   # switch to another column of the window
                        if j == i:
                            continue
                        cp, vp = int(cv[j]), float(tv[j])
                        budget = t + _eps(t) - vp
                        if budget <= 0:
                            continue
                        D = np.array([T.det[c0] ^ T.det[cp]], dtype=U64)
                        O = np.array([T.obs[c0] ^ T.obs[cp]], dtype=U64)
                        if float(T.min_w_other(D, O)[0]) <= budget:
                            b = 1.0
                            break
                        if T.v_gmin <= budget:
                            b += float(T.q_other(D, O)[0])
                        if 2 * min(T.v_gmin, T.w_min) <= budget:
                            b += 1.0 if T.w_min <= budget else _pois_tail(T.Lam, 2)
                    acc += T.px * ev[i] * min(b, 1.0)
            out["0,1"] = min(1.0, acc / T.S + _pois_tail(T.Lam, n))
            out["tail_01"] = n
    # ---------------- F(0, 2), exact timing
    if window == 0 and len(tv):
        vmax = tmax
        if 2 * vmax + _eps(2 * vmax) >= T.w_min:
            out["0,2"] = 1.0
        else:
            # atoms (column, cost) of a true flagged event and their probabilities (over all events)
            ak = np.round(tv, 6)
            keys = cv.astype(np.int64) * 10 ** 7 + np.round(ak * 1e5).astype(np.int64)
            uk, inv = np.unique(keys, return_inverse=True)
            pa = np.bincount(inv, weights=ev) / T.S
            ca = (uk // 10 ** 7).astype(np.int64)
            ta = np.bincount(inv, weights=tv) / np.bincount(inv)
            single = np.array([T.completions(T.det[c], T.obs[c], float(t)) if 2 * T.v_gmin <= t + _eps(t) or
                               T.w_min + T.v_gmin <= t + _eps(t) else 0.0 for c, t in zip(ca, ta)])
            px = T.px
            A, B = np.meshgrid(np.arange(len(uk)), np.arange(len(uk)), indexing="ij")
            A, B = A.ravel(), B.ravel()
            p = pa[A] * pa[B]
            diff = ca[A] != ca[B]
            D = T.det[ca[A]] ^ T.det[ca[B]]
            O = T.obs[ca[A]] ^ T.obs[ca[B]]
            tt = ta[A] + ta[B]
            Ttt = tt + 1e-3 * tt + 1e-3
            one = np.where(diff & (T.v_gmin <= Ttt), T.q_other(D, O), 0.0)            # one false column
            two = np.where(diff & (2 * T.v_gmin <= Ttt), T.pp_other(D, O), 0.0)       # two false columns
            both = px * px * (one + two + single[A] + single[B])
            # one X (on the first event): dropped, the other event's flagged column used, one false column
            bud = ta[A] + 1e-3 * ta[A] + 1e-3 - ta[B]
            onex = px * (1 - px) * 2 * (single[A] + np.where(diff & (T.v_gmin <= bud), T.q_other(D, O), 0.0))
            b = np.minimum(both + onex, 1.0)
            n = T.tail_n(2 * vmax)
            out["0,2"] = 1.0 if n == -1 else min(1.0, float((p * b).sum()) + _pois_tail(T.Lam, n))
            out["tail_02"] = n
    return out


def main():
    out_path = os.path.join(ROOT, "results", "false_flag_bounds.json")
    out = {}
    seen = set()
    for fn in sorted(glob.glob(os.path.join(ROOT, "results", "flag_*", "*.json"))):
        try:
            r = json.load(open(fn))
        except Exception:
            continue
        sp = r.get("spec", {})
        if sp.get("kind") != "strata" or float(sp.get("flag", {}).get("false_rate", 0.0)) <= 0:
            continue
        if sp.get("flag", {}).get("mode", "erasure") != "erasure":
            continue
        key = setting_key(sp)
        if key in seen:
            continue
        seen.add(key)
        b = bounds_for(dict(sp))
        if b is None:
            continue
        out[key] = b
        print(key, {k: (f"{v:.2e}" if isinstance(v, float) else v) for k, v in b.items()}, flush=True)
        json.dump(out, open(out_path, "w"), indent=1)
    json.dump(out, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
