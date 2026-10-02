"""Stratified estimation of the flagged bit-flip logical error rate (cluster task 'strata').

spec = dict(kind='strata', code, n_anc, d, mode, compress, idle_ctx, n_outer, p_x,
            flag=dict(f, classes, window, false_rate), decoder='mle'|'bposd',
            kmax, budget, n1, seed)
Result: per-stratum (fails, n), U, S, rounds, k and the combined estimate.
"""
from __future__ import annotations

import math
import os
import time

import numpy as np

from .blocklevel import BlockModel
from .codes import load_code
from .decode import wilson
from .flags import BpOsdFlagDecoder, FlagConfig, FlagModel, MleFlagDecoder
from .schedule import ElevatorSchedule
from .strata import StrataSampler, pois

_W = {}


def _build(spec):
    code = load_code(spec["code"])
    sched = ElevatorSchedule(code, spec["d"], n_anc=spec.get("n_anc", 1), mode=spec.get("mode", "full"),
                             n_outer=spec.get("n_outer", 5), compress=bool(spec.get("compress", False)))
    bm = BlockModel(sched, spec["p_x"], idle_ctx=tuple(spec.get("idle_ctx", ("edge", "cnot", "op"))))
    fl = spec["flag"]
    cfg = FlagConfig.make(fl["f"], classes=tuple(fl.get("classes", ["idle"])),
                          false_rate=fl.get("false_rate", 0.0), window=fl.get("window", 0))
    fm = FlagModel(bm, cfg)
    if spec.get("decoder", "mle") == "mle":
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
    from multiprocessing import Pool
    t0 = time.time()
    code, sched, bm, fm, dec, ss = _build(spec)
    U, S = ss.U, ss.S
    kmax = int(spec.get("kmax", (code.d + 1)))
    strata = strata_list(kmax)
    weights = {st: pois(st[0], U) * pois(st[1], S) for st in strata}
    counts = {st: [0, 0] for st in strata}
    budget = int(spec.get("budget", 100000))
    n1 = int(spec.get("n1", 1000))
    base = int(spec.get("seed", 0)) * 7919
    used = 0
    with Pool(procs, initializer=_init, initargs=(spec,)) as pool:
        def run_alloc(alloc, tag):
            nonlocal used
            jobs = []
            for st, n in alloc.items():
                if n <= 0:
                    continue
                chunks = max(1, min(procs, n // 200))
                per = -(-n // chunks)
                for c in range(chunks):
                    jobs.append((st[0], st[1], per, base + hash((st, tag, c)) % 1000003, None))
            for a, b, f, n in pool.imap_unordered(_work, jobs):
                counts[(a, b)][0] += f
                counts[(a, b)][1] += n
                used += n

        # phase 1: every stratum with a non-negligible weight
        run_alloc({st: n1 for st in strata if weights[st] > 0}, "p1")
        # phase 2: Neyman allocation of the remaining budget
        for it in range(3):
            rem = budget - used
            if rem <= 0:
                break
            est = sum(weights[st] * counts[st][0] / max(counts[st][1], 1) for st in strata)
            scores = {}
            for st in strata:
                f, n = counts[st]
                if n == 0 or weights[st] == 0:
                    continue
                lo, hi = wilson(f, n)
                upper = weights[st] * hi
                if upper < 1e-3 * max(est, 1e-300) and f == 0:
                    continue
                fh = max(f / n, hi / 3)
                scores[st] = weights[st] * math.sqrt(fh * (1 - fh))
            tot = sum(scores.values())
            if tot <= 0:
                break
            alloc = {st: int(rem / 3 * sc / tot) for st, sc in scores.items()}
            run_alloc(alloc, f"p2{it}")
    res = summarize(counts, weights)
    res.update(dict(spec=spec, U=U, S=S, rounds=sched.n_rounds, k=code.k,
                    strata={f"{a},{b}": counts[(a, b)] for (a, b) in strata},
                    weights={f"{a},{b}": weights[(a, b)] for (a, b) in strata},
                    seconds=time.time() - t0, decodes=used))
    R, k = sched.n_rounds, code.k
    for key in ("P", "lo", "hi"):
        res["pL_" + key] = res[key] / (R * k)
    # truncation bound: probability of more than kmax events
    tail = 1.0 - sum(pois(a, U) * pois(t - a, S) for t in range(0, kmax + 1) for a in range(t + 1))
    res["tail_bound"] = max(tail, 0.0)
    if out_path:
        import json
        tmp = out_path + ".tmp"
        json.dump(res, open(tmp, "w"))
        os.replace(tmp, out_path)
    return res


def summarize(counts, weights):
    est = lo = hi = 0.0
    for st, (f, n) in counts.items():
        if n == 0:
            continue
        w = weights[st]
        l, h = wilson(f, n)
        est += w * f / n
        lo += w * l
        hi += w * h
    return dict(P=est, lo=lo, hi=hi)
