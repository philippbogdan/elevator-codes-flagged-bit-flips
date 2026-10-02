"""Hamming [127,120,3], pushing the overhead frontier: at p_Z = 1e-3 its phase-flip floor is d_Z = 15 in
both phase-flip models (30.9 qubits per logical qubit against 32.6 for [63,57,3]); whether its bit flips
allow it, and at which flag efficiency.  Three outer rounds (as for [63,57,3]), p_X = 1e-9.

    python scripts/make_ham127_tasks.py      # writes tasks/ham127.jsonl
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ["idle", "gate", "prep", "meas"]
SETTINGS = [(0.0, ["idle"], 0), (0.99, ALL, 0), (0.995, ALL, 0), (0.999, ALL, 0), (1.0, ALL, 0), (0.995, ALL, 64)]


def main():
    out = []
    seed = 750001
    for f, cls, w in SETTINGS:
        out.append(dict(kind="strata", code="ham127", n_anc=1, d=15, mode="full", compress=False,
                        idle_ctx=["edge", "cnot"], n_outer=3, p_x=1e-9,
                        flag=dict(f=f, classes=cls, window=w, false_rate=0.0), decoder="mle_excl",
                        kmax=5, budget=20000, n1=400, rel_tol=0.15, seed=seed, tag="ham127",
                        outdir="results/flag_alt"))
        seed += 1
    fn = os.path.join(ROOT, "tasks", "ham127.jsonl")
    with open(fn, "w") as fh:
        for s in out:
            fh.write(json.dumps(s) + "\n")
    print(fn, len(out))


if __name__ == "__main__":
    main()
