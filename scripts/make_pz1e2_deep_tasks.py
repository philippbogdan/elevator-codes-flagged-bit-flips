"""Deeper stratified runs at p_Z = 1e-2 (p_X = 1e-8) for [15,6,5] with exactly timed flags, at d_Z = 33,
the reference for every transfer to the large d_Z where the p_Z = 1e-2 floors lie.  The analytic bounds
of scripts/strata_caps.py remove the strata they bound by 0; the budget goes to the strata that decide
the 95 % upper bounds there ((1,3), (2,1), (1,4), (2,2), ...).  The analysis pools these runs with the
earlier ones of the same setting (independent seeds).

    python scripts/make_pz1e2_deep_tasks.py      # writes tasks/pz1e2_deep.jsonl
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ["idle", "gate", "prep", "meas"]
SETTINGS = [(0.0, ["idle"]), (0.9, ["idle"]), (0.99, ["idle"]), (0.9, ALL), (0.99, ALL), (0.99, ["idle", "gate"])]


def main():
    out = []
    seed = 710001
    for n_anc in (1, 2):
        for f, cls in SETTINGS:
            out.append(dict(kind="strata", code="15_6_5", n_anc=n_anc, d=33, mode="full", compress=False,
                            idle_ctx=["edge", "cnot"], n_outer=5, p_x=1e-8,
                            flag=dict(f=f, classes=cls, window=0, false_rate=0.0), decoder="mle_excl",
                            kmax=7, budget=500000, n1=10000, lo_order=5, rel_tol=0.02, abs_tol=1e-22,
                            analytic_caps=True, seed=seed, tag="pz1e2-deep", outdir="results/flag_pz1e2"))
            seed += 1
    fn = os.path.join(ROOT, "tasks", "pz1e2_deep.jsonl")
    with open(fn, "w") as fh:
        for s in out:
            fh.write(json.dumps(s) + "\n")
    print(fn, len(out))


if __name__ == "__main__":
    main()
