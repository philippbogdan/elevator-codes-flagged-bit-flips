"""Run the known-answer checks and write results/known_answers.json.

  python scripts/known_answers.py [--quick]
"""
import argparse
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from elevator.codes import load_code  # noqa: E402
from elevator.known_answers import (circuit_erasure_blocks, circuit_random_flagged,  # noqa: E402
                                    code_capacity_erasures, repetition_code)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="results/known_answers.json")
    a = ap.parse_args()
    t0 = time.time()
    res = {}
    # KA1: repetition codes at code capacity
    for d in ([3, 5] if a.quick else [3, 5, 7, 9]):
        r = code_capacity_erasures(repetition_code(d), d)
        res[f"KA1_code_capacity_rep{d}"] = r
        assert all(r[s]["failures"] == 0 for s in range(d)), r
        assert r[d]["failures"] * 2 == r[d]["patterns"], r
        print("KA1 rep", d, "ok", flush=True)
    # KA1 at circuit level: elevator memory with a [d,1,d] repetition outer code
    for d in ([3] if a.quick else [3, 5]):
        code = repetition_code(d)
        out = {}
        for k in range(1, d + 1):
            out[k] = circuit_random_flagged(code, 3, k, 300 if a.quick else 2000, seed=k)
        res[f"KA1_circuit_rep{d}"] = out
        assert all(out[k]["failures"] == 0 for k in range(1, d)), out
        print("KA1 circuit rep", d, {k: v["failures"] for k, v in out.items()}, flush=True)
    # KA2: outer codes, code capacity, every erasure pattern up to d (d only for tightness)
    for nm in ["15_9_3", "15_6_5"]:
        code = load_code(nm)
        r = code_capacity_erasures(code, code.d if not a.quick or nm == "15_9_3" else code.d - 1)
        res[f"KA2_code_capacity_{nm}"] = r
        assert all(r[s]["failures"] == 0 for s in range(code.d)), r
        if code.d in r:
            wd = code.weight_distribution()
            assert r[code.d]["sets_with_failure"] == wd[code.d], (r[code.d], wd)
        print("KA2 code capacity", nm, "ok", flush=True)
    # KA2 at circuit level: every subset of up to d-1 data blocks erased in one round
    for nm in ["15_9_3", "15_6_5"]:
        code = load_code(nm)
        if a.quick and nm == "15_6_5":
            continue
        r = circuit_erasure_blocks(code, d_inner=3, max_size=code.d - 1,
                                   rounds_frac=(0.5,) if a.quick else (0.2, 0.5, 0.8))
        res[f"KA2_circuit_{nm}"] = r
        assert all(v["failures"] == 0 for v in r.values()), r
        print("KA2 circuit", nm, {s: (v["sets"], v["failures"]) for s, v in r.items()}, flush=True)
    res["seconds"] = time.time() - t0
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1, default=str)
    print("all known-answer checks passed", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
