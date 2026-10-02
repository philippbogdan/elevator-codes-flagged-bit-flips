"""Analysis of flag-study results: p_XL tables and minimum overheads."""
from __future__ import annotations

import glob
import json
import os
from collections import defaultdict

import numpy as np

from .overhead import ELEVATOR_NK, paper_pzl

CLASS_TAG = {("idle",): "idle", ("idle", "gate"): "idle+gate", ("idle", "gate", "prep", "meas"): "all"}


def overhead(code: str, n_anc: int, d: int) -> float:
    n, k = ELEVATOR_NK[code]
    return (n + n_anc) * (2 * d - 1) / k


def load_strata(dirs) -> list[dict]:
    if isinstance(dirs, str):
        dirs = [dirs]
    rows = []
    for dd in dirs:
        for fn in glob.glob(os.path.join(dd, "*.json")):
            r = json.load(open(fn))
            s = r["spec"]
            fl = s["flag"]
            rows.append(dict(code=s["code"], n_anc=s["n_anc"], d=s["d"], p_x=s["p_x"],
                             f=fl["f"], classes=CLASS_TAG[tuple(fl["classes"])] if fl["f"] > 0 else "none",
                             window=fl["window"], r=fl.get("false_rate", 0.0), mode=fl.get("mode", "erasure"),
                             idle=",".join(s.get("idle_ctx", [])), tag=s.get("tag", ""), n_outer=s.get("n_outer", 5),
                             pL=r["pL_P"], lo=r["pL_lo"], hi=r["pL_hi"], P=r["P"], U=r["U"], S=r["S"],
                             rounds=r["rounds"], k=r["k"], decodes=r["decodes"], strata=r["strata"],
                             exact=r.get("exact", {}), weights=r["weights"], file=fn))
    return rows


def flag_key(row) -> tuple:
    return (row["f"], row["classes"], row["window"], row["r"])


def index(rows):
    """{(flagkey, idle, p_x): {(code, n_anc, d): row}}"""
    out = defaultdict(dict)
    for r in rows:
        out[(flag_key(r), r["idle"], r["p_x"])][(r["code"], r["n_anc"], r["d"])] = r
    # f = 0 rows serve every class / window with f = 0
    return out


def min_overhead_for(table: dict, pz: float, target: float, pzl_fn=None, which: str = "pL",
                     codes=None) -> dict | None:
    """table: {(code, n_anc, d): row}.  Returns the cheapest (code, n_anc, d) meeting target."""
    if pzl_fn is None:
        pzl_fn = lambda code, n_anc, d, pz: paper_pzl(code, n_anc, d, pz)
    best = None
    for (code, n_anc, d), row in table.items():
        if codes and (code, n_anc) not in codes:
            continue
        pzl = pzl_fn(code, n_anc, d, pz)
        tot = row[which] + pzl
        if tot <= target:
            oh = overhead(code, n_anc, d)
            if best is None or oh < best["overhead"]:
                best = dict(code=code, n_anc=n_anc, d=d, overhead=oh, pXL=row[which], pZL=pzl, total=tot)
    return best
