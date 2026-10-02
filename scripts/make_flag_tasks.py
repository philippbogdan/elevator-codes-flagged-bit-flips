"""Task files for the flagged bit-flip (Z-memory) study.

  python scripts/make_flag_tasks.py main      -> tasks/flag_main.jsonl   (p_X = 1e-9)
  python scripts/make_flag_tasks.py literal   -> tasks/flag_literal.jsonl
  python scripts/make_flag_tasks.py bias      -> tasks/flag_bias.jsonl
  python scripts/make_flag_tasks.py pz1e2     -> tasks/flag_pz1e2.jsonl  (p_X = 1e-8, large d)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = [("15_9_3", 1), ("15_6_5", 1), ("15_6_5", 2)]
CLASSES = {"idle": ["idle"], "idlegate": ["idle", "gate"], "all": ["idle", "gate", "prep", "meas"]}
F_SWEEP = [0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 1.0]
WINDOWS = [1, 4, 16, 64, 256, 1024, 4096]
NOOP = ["edge", "cnot"]
ALL = ["edge", "cnot", "op"]


def spec(code, n_anc, d, p_x, f, classes, window, r=0.0, idle_ctx=NOOP, seed=0, budget=30000, tag=""):
    dist = {"15_9_3": 3, "15_6_5": 5, "ham15": 3, "ham31": 3, "xham16": 4, "16_3_8": 8}[code]
    return dict(kind="strata", code=code, n_anc=n_anc, d=d, mode="full", compress=False,
                idle_ctx=idle_ctx, n_outer=5, p_x=p_x,
                flag=dict(f=f, classes=CLASSES[classes], window=window, false_rate=r),
                decoder="mle_excl", kmax=dist + 1, budget=budget, n1=400,
                rel_tol=0.15, seed=seed, tag=tag)


def flag_settings(windows=True, false_flags=False):
    out = [(0.0, "idle", 0, 0.0)]
    for cls in CLASSES:
        for f in F_SWEEP:
            out.append((f, cls, 0, 0.0))
    if windows:
        for cls in ["idle", "all"]:
            for f in [0.9, 0.99, 1.0]:
                for w in WINDOWS:
                    out.append((f, cls, w, 0.0))
    if false_flags:
        for w in [0, 64]:
            for r in [1e-10, 1e-9, 1e-8, 1e-7, 1e-6]:
                out.append((0.99, "all", w, r))
    return out


def main_tasks():
    ts = []
    seed = 0
    for code, n_anc in CODES:
        for d in [15, 17, 19]:
            for (f, cls, w, r) in flag_settings(windows=True, false_flags=(d == 17)):
                seed += 1
                ts.append(spec(code, n_anc, d, 1e-9, f, cls, w, r, seed=seed, tag="main"))
    return ts


def literal_tasks():
    ts = []
    seed = 50000
    for code, n_anc in CODES:
        for (f, cls, w, r) in flag_settings(windows=False):
            if cls == "idlegate":
                continue
            seed += 1
            ts.append(spec(code, n_anc, 17, 1e-9, f, cls, w, r, idle_ctx=ALL, seed=seed, tag="literal"))
        for w in WINDOWS:
            seed += 1
            ts.append(spec(code, n_anc, 17, 1e-9, 0.99, "all", w, 0.0, idle_ctx=ALL, seed=seed, tag="literal"))
    return ts


def alt_tasks():
    """Alternative outer codes tried for the frontier (Hamming family), p_X = 1e-9."""
    ts = []
    seed = 200000
    for code, n_anc in [("ham15", 1), ("ham31", 1), ("xham16", 1)]:
        for d in ([13, 15, 17] if code != "xham16" else [15, 17]):
            for (f, cls, w, r) in flag_settings(windows=True, false_flags=False):
                seed += 1
                ts.append(spec(code, n_anc, d, 1e-9, f, cls, w, r, seed=seed, tag="alt"))
    return ts


def bias_tasks():
    """p_X grid for the bias sweep at p_Z = 1e-3 (eta = 4e4 ... 1e7)."""
    ts = []
    seed = 100000
    pxs = [2.5e-8, 1e-8, 4e-9, 2e-9, 5e-10, 2e-10, 1e-10]
    for code, n_anc in CODES + [("ham15", 1)]:
        for d in [15, 17, 19]:
            for px in pxs:
                for (f, cls, w) in [(0.0, "idle", 0), (0.9, "all", 0), (0.99, "all", 0), (1.0, "all", 0),
                                    (0.9, "idle", 0), (0.99, "idle", 0), (0.99, "all", 64), (0.99, "all", 1024)]:
                    seed += 1
                    ts.append(spec(code, n_anc, d, px, f, cls, w, seed=seed, tag="bias"))
    return ts


def pz1e2_tasks():
    """p_Z = 1e-2, eta = 1e6 (p_X = 1e-8): bit-flip side at larger d_Z."""
    ts = []
    seed = 300000
    settings = [(0.0, "idle", 0), (0.9, "all", 0), (0.99, "all", 0), (1.0, "all", 0), (0.9, "idle", 0),
                (0.99, "idle", 0), (0.99, "idlegate", 0), (0.99, "all", 64), (0.99, "all", 1024)]
    for code, n_anc in CODES + [("ham15", 1)]:
        for d in [17, 25, 33]:
            for (f, cls, w) in settings:
                seed += 1
                ts.append(spec(code, n_anc, d, 1e-8, f, cls, w, seed=seed, tag="pz1e2"))
    return ts


def validation_tasks():
    """Held-out check of the stratified estimator: direct sampling vs strata at p_X where both work."""
    ts = []
    seed = 400000
    settings = [(0.0, "idle", 0), (0.9, "all", 0), (0.99, "all", 64), (0.99, "idle", 0), (1.0, "all", 1024)]
    for code, n_anc in CODES:
        for px in [3e-7, 1e-6]:
            for (f, cls, w) in settings:
                seed += 1
                st = spec(code, n_anc, 15, px, f, cls, w, seed=seed, tag="validate", budget=40000)
                st["kmax"] = 9 if px >= 1e-6 else 7
                st["rel_tol"] = 0.05
                ts.append(st)
                dr = {k: v for k, v in st.items() if k not in ("kmax", "budget", "n1", "rel_tol")}
                dr.update(kind="direct_block", shots=400000, max_fail=400, shard=2000, seed=seed + 50000)
                ts.append(dr)
    return ts


def supp_tasks():
    """Fill the efficiency x timing map (classes 'all' and 'idle') at d_Z = 15, 17 and the
    false-flag sweep at d_Z = 15."""
    ts = []
    seed = 500000
    for code, n_anc in CODES:
        for d in [15, 17]:
            for cls in ["all", "idle"]:
                for f in [0.5, 0.8, 0.95, 0.98, 0.995]:
                    for w in [4, 64, 1024, 4096]:
                        seed += 1
                        ts.append(spec(code, n_anc, d, 1e-9, f, cls, w, seed=seed, tag="supp"))
        for w in [0, 64]:
            for r in [1e-10, 1e-9, 1e-8, 1e-7, 1e-6]:
                seed += 1
                ts.append(spec(code, n_anc, 15, 1e-9, 0.99, "all", w, r, seed=seed, tag="supp"))
                seed += 1
                ts.append(spec(code, n_anc, 15, 1e-9, 0.99, "idle", w, r, seed=seed, tag="supp"))
    return ts


if __name__ == "__main__":
    which = sys.argv[1]
    ts = {"main": main_tasks, "literal": literal_tasks, "bias": bias_tasks, "alt": alt_tasks,
          "pz1e2": pz1e2_tasks, "validation": validation_tasks,
          "supp": supp_tasks}[which]()
    os.makedirs(os.path.join(ROOT, "tasks"), exist_ok=True)
    path = os.path.join(ROOT, "tasks", f"flag_{which}.jsonl")
    with open(path, "w") as fh:
        for t in ts:
            fh.write(json.dumps(t) + "\n")
    print(path, len(ts))
