"""Deeper false-flag runs for [15,9,3] (d_Z = 15, p_X = 1e-9) at r = 1e-7 and 1e-6, the rates where the
95 % upper bounds of the windowed settings are still set by sampling (strata (0,2), (1,0), (1,1)); the
analytic bounds of scripts/false_flag_bounds.py steer the allocation.  Pooled with the earlier runs of
the same settings (independent seeds).

    python scripts/make_ff_deep_tasks.py      # writes tasks/ff_deep.jsonl
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ["idle", "gate", "prep", "meas"]
SETTINGS = [(0.99, ALL, 64), (0.8, ALL, 4), (0.8, ALL, 16), (0.9, ALL, 4), (0.9, ALL, 16), (0.99, ["idle"], 64),
            (0.99, ["idle"], 0)]


def main():
    out = []
    seed = 730001
    for r in (1e-7, 1e-6):
        for f, cls, w in SETTINGS:
            out.append(dict(kind="strata", code="15_9_3", n_anc=1, d=15, mode="full", compress=False,
                            idle_ctx=["edge", "cnot"], n_outer=5, p_x=1e-9,
                            flag=dict(f=f, classes=cls, window=w, false_rate=r), decoder="mle_excl",
                            kmax=4, budget=200000, n1=2000, rel_tol=0.05, ff_caps=True, seed=seed,
                            tag="ff-deep", outdir="results/flag_falseflag"))
            seed += 1
    fn = os.path.join(ROOT, "tasks", "ff_deep.jsonl")
    with open(fn, "w") as fh:
        for s in out:
            fh.write(json.dumps(s) + "\n")
    print(fn, len(out))


if __name__ == "__main__":
    main()
