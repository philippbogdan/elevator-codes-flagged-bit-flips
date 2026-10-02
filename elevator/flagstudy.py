"""Stratified estimation of the flagged bit-flip logical error rate (cluster task 'strata').

spec = dict(kind='strata', code, n_anc, d, mode, compress, idle_ctx, n_outer, p_x,
            flag=dict(f, classes, window, false_rate), decoder='mle'|'bposd',
            kmax, budget, n1, seed,
            ff_caps (analytic false-flag bounds), analytic_caps (scripts/strata_caps.py),
            lo_order (strata with a + b <= lo_order get n1 samples first))
Result: per-stratum (fails, n), U, S, rounds, k and the combined estimate.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import zlib
from multiprocessing import Pool

import numpy as np

from .blocklevel import BlockModel
from .codes import load_code
from .decode import wilson
from .flags import BpOsdFlagDecoder, ExclusiveMleDecoder, FlagConfig, FlagModel, MleFlagDecoder
from .schedule import ElevatorSchedule
from .strata import StrataSampler, min_logical_weight_le2, pois, single_unflagged_exact

_W = {}


def _build(spec):
    code = load_code(spec["code"])
    sched = ElevatorSchedule(code, spec["d"], n_anc=spec.get("n_anc", 1), mode=spec.get("mode", "full"),
                             n_outer=spec.get("n_outer", 5), compress=bool(spec.get("compress", False)))
    bm = BlockModel(sched, spec["p_x"], idle_ctx=tuple(spec.get("idle_ctx", ("edge", "cnot", "op"))))
    fl = spec["flag"]
    cfg = FlagConfig.make(fl["f"], classes=tuple(fl.get("classes", ["idle"])),
                          false_rate=fl.get("false_rate", 0.0), window=fl.get("window", 0),
                          mode=fl.get("mode", "erasure"))
    fm = FlagModel(bm, cfg)
    dname = spec.get("decoder", "mle_excl")
    if dname == "mle_excl":
        dec = ExclusiveMleDecoder(fm)
    elif dname == "mle":
        dec = MleFlagDecoder(fm)
    else:
        dec = BpOsdFlagDecoder(fm)
    return code, sched, bm, fm, dec, StrataSampler(fm)


def _init(spec):
    _W["spec"] = spec
    _W["obj"] = _build(spec)


def _work(args):
    a, b, n, seed, max_fail = args
    code, sched, bm, fm, dec, ss = _W["obj"]
    r = ss.estimate_F(dec, a, b, n, seed, max_fail=max_fail)
    return (a, b, r["fails"], r["n"])


def strata_list(kmax: int):
    return [(a, t - a) for t in range(1, kmax + 1) for a in range(t + 1)]


def run_strata(spec: dict, procs: int, out_path: str | None = None) -> dict:
    t0 = time.time()
    code, sched, bm, fm, dec, ss = _build(spec)
    U, S = ss.U, ss.S
    kmax = int(spec.get("kmax", (code.d + 1)))
    strata = strata_list(kmax)
    weights = {st: pois(st[0], U) * pois(st[1], S) for st in strata}
    counts = {st: [0, 0] for st in strata}
    exact = {}
    r_false = float(spec["flag"].get("false_rate", 0.0))
    if r_false == 0.0 and spec.get("decoder", "mle_excl").startswith("mle"):
        # single-event strata exactly: F(1,0) by enumeration; F(0,1) = 0 when the merged
        # DEM has no logical of weight <= 2 (one flagged event is always resolved).
        f10, nf10, ncol = single_unflagged_exact(fm, dec)
        exact[(1, 0)] = f10
        assert not min_logical_weight_le2(bm), "DEM has a logical of weight <= 2"
        exact[(0, 1)] = 0.0
        if int(spec["flag"].get("window", 0)) == 0:
            # exactly timed flags: b < d erasures of single mechanisms cannot contain a logical
            # (circuit distance = code distance, checked with Stim for every outer code used)
            for b in range(2, code.d):
                if (0, b) in weights:
                    exact[(0, b)] = 0.0
    # analytic caps on single/two-event strata with false flags (scripts/false_flag_bounds.py): the
    # allocation then spends its budget where the upper bound is really decided
    caps = {}
    capped0 = set()
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    if spec.get("ff_caps") and r_false > 0:
        from false_flag_bounds import bounds_for
        b = bounds_for(dict(spec))
        if b:
            caps = {tuple(map(int, k.split(","))): v for k, v in b.items() if k in ("1,0", "0,1", "0,2")}
    # analytic bounds from the code distance and the decoder's costs (scripts/strata_caps.py; exactly
    # timed erasure flags, no false flags): strata bounded by 0 are not sampled, the others' bounds
    # steer the allocation
    if (spec.get("analytic_caps") and r_false == 0.0 and int(spec["flag"].get("window", 0)) == 0
            and spec["flag"].get("mode", "erasure") == "erasure" and spec.get("decoder", "mle_excl").startswith("mle")
            and spec.get("mode", "full") == "full" and not spec.get("compress")):
        import strata_caps as SC
        rec = SC.record_for(spec["code"], spec.get("n_anc", 1), spec.get("n_outer", 5),
                            ",".join(spec.get("idle_ctx", ("edge", "cnot", "op"))))
        if rec is not None:
            names = ["idle", "gate", "prep", "meas"]
            eff = [float(spec["flag"]["f"]) if nm in spec["flag"].get("classes", ["idle"]) else 0.0 for nm in names]
            for k_, v in SC.caps_for(rec, spec["d"], spec["p_x"], eff, strata).items():
                st = tuple(map(int, k_.split(",")))
                if st in exact:
                    continue
                caps[st] = v
                if v == 0.0:
                    capped0.add(st)
    budget = int(spec.get("budget", 100000))
    n1 = int(spec.get("n1", 1000))
    rel_tol = float(spec.get("rel_tol", 0.15))
    abs_tol = float(spec.get("abs_tol", 1e-13))
    base = int(spec.get("seed", 0)) * 7919
    used = 0
    sampled = [st for st in strata if st not in exact and st not in capped0 and weights[st] > 0]
    with Pool(procs, initializer=_init, initargs=(spec,)) as pool:
        def run_alloc(alloc, tag):
            nonlocal used
            jobs = []
            for st, n in alloc.items():
                if n <= 0:
                    continue
                chunks = max(1, min(procs, n // 100))
                per = -(-n // chunks)
                for c in range(chunks):
                    jobs.append((st[0], st[1], per, (base + zlib.crc32(repr((st, tag, c)).encode())) % 2147483647, None))
            for a, b, f, n in pool.imap_unordered(_work, jobs):
                counts[(a, b)][0] += f
                counts[(a, b)][1] += n
                used += n

        # phase 1: low orders first; higher orders only if their weight can matter
        t_lead = (code.d + 1) // 2
        lo_cut = int(spec.get("lo_order", t_lead + 1))
        lo_ord = [st for st in sampled if sum(st) <= lo_cut]
        hi_ord = [st for st in sampled if sum(st) > lo_cut]
        run_alloc({st: n1 for st in lo_ord}, "p1")
        est0 = sum(weights[st] * counts[st][0] / max(counts[st][1], 1) for st in lo_ord)
        est0 += sum(weights[st] * exact[st] for st in exact)
        skipped = []
        keep_hi = []
        for st in hi_ord:
            if est0 > 0 and weights[st] < 1e-3 * est0:
                skipped.append(st)
            else:
                keep_hi.append(st)
        run_alloc({st: n1 for st in keep_hi}, "p1b")
        sampled = lo_ord + keep_hi
        it = 0
        while used < budget and it < 12:
            it += 1
            est = sum(weights[st] * counts[st][0] / max(counts[st][1], 1) for st in sampled)
            est += sum(weights[st] * exact[st] for st in exact)
            widths = {}
            for st in sampled:
                f, n = counts[st]
                lo, hi = wilson(f, n)
                if st in caps:
                    hi = min(hi, max(caps[st], f / max(n, 1)))
                widths[st] = weights[st] * max(hi - lo, 0.0)
            tot = sum(widths.values())
            if est > 0 and tot < rel_tol * est:
                break
            # absolute stop: 95% upper bound (per round per logical qubit) below abs_tol
            hi_tot = sum(weights[st] * (min(wilson(*counts[st])[1], max(caps[st], counts[st][0] / counts[st][1]))
                                        if st in caps else wilson(*counts[st])[1]) for st in sampled if counts[st][1])
            hi_tot += sum(weights[st] * exact[st] for st in exact) + sum(weights[st] for st in skipped)
            if hi_tot / (sched.n_rounds * code.k) < abs_tol:
                break
            mx = max(widths.values()) if widths else 0
            if mx <= 0:
                break
            chunk = min(budget - used, max(4 * procs * 100, (budget - used) // 3))
            sel = {st: wd for st, wd in widths.items() if wd >= 0.05 * mx}
            sw = sum(sel.values())
            run_alloc({st: max(100, int(chunk * wd / sw)) for st, wd in sel.items()}, f"it{it}")
    res = summarize(counts, weights, exact)
    if caps:
        res["caps"] = {f"{a},{b}": v for (a, b), v in caps.items()}
    skip_w = sum(weights[st] for st in skipped)
    res["hi"] += skip_w                      # skipped strata contribute at most their weight
    res["skipped_weight"] = skip_w
    res.update(dict(exact={f"{a},{b}": v for (a, b), v in exact.items()},spec=spec, U=U, S=S, rounds=sched.n_rounds, k=code.k,
                    strata={f"{a},{b}": counts[(a, b)] for (a, b) in strata},
                    weights={f"{a},{b}": weights[(a, b)] for (a, b) in strata},
                    seconds=time.time() - t0, decodes=used))
    R, k = sched.n_rounds, code.k
    for key in ("P", "lo", "hi"):
        res["pL_" + key] = res[key] / (R * k)
    # truncation bound: probability of more than kmax events
    tail = 1.0 - sum(pois(a, U) * pois(t - a, S) for t in range(0, kmax + 1) for a in range(t + 1))
    res["tail_bound"] = max(tail, 0.0)
    res["hi"] += res["tail_bound"]          # truncated strata contribute at most this
    res["pL_hi"] = res["hi"] / (R * k)
    if out_path:
        tmp = out_path + ".tmp"
        json.dump(res, open(tmp, "w"))
        os.replace(tmp, out_path)
    return res


def summarize(counts, weights, exact=None):
    est = lo = hi = 0.0
    for st, v in (exact or {}).items():
        est += weights[st] * v
        lo += weights[st] * v
        hi += weights[st] * v
    for st, (f, n) in counts.items():
        if n == 0 or (exact and st in exact):
            continue
        w = weights[st]
        l, h = wilson(f, n)
        est += w * f / n
        lo += w * l
        hi += w * h
    return dict(P=est, lo=lo, hi=hi)
