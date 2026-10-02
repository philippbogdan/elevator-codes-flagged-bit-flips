"""The p_Z = 1e-2 (p_X = 1e-8) flag settings that complete the grid of p_Z = 1e-3: efficiencies 0.5 to
0.999 with exact timing, windows from one CNOT layer to 4096 ticks (longer than an outer round at the
d_Z of the p_Z = 1e-2 floors), idle-only flags at f = 1 and with coarse windows; for [15,9,3] and
[15,6,5] with one and two ancillas at d_Z = 17, 25, 33 (the transfer references).

    python scripts/make_pz1e2_grid_tasks.py      # writes tasks/pz1e2_grid.jsonl
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ["idle", "gate", "prep", "meas"]
SETTINGS = ([(f, ALL, 0) for f in (0.5, 0.8, 0.95, 0.999)]
            + [(0.99, ALL, w) for w in (1, 4, 16, 256, 4096)]
            + [(0.9, ALL, 4096), (1.0, ["idle"], 0), (0.99, ["idle"], 4096)])
CODES = [("15_9_3", 1), ("15_6_5", 1), ("15_6_5", 2)]


def main():
    out = []
    seed = 720001
    for code, n_anc in CODES:
        kmax = 6 if code == "15_9_3" else 7
        for d in (17, 25, 33):
            for f, cls, w in SETTINGS:
                out.append(dict(kind="strata", code=code, n_anc=n_anc, d=d, mode="full", compress=False,
                                idle_ctx=["edge", "cnot"], n_outer=5, p_x=1e-8,
                                flag=dict(f=f, classes=cls, window=w, false_rate=0.0), decoder="mle_excl",
                                kmax=kmax, budget=40000, n1=400, rel_tol=0.15, analytic_caps=True, seed=seed,
                                tag="pz1e2-grid", outdir="results/flag_pz1e2"))
                seed += 1
    fn = os.path.join(ROOT, "tasks", "pz1e2_grid.jsonl")
    with open(fn, "w") as fh:
        for s in out:
            fh.write(json.dumps(s) + "\n")
    print(fn, len(out))


if __name__ == "__main__":
    main()
