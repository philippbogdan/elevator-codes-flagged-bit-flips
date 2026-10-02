"""Task files for the phase-flip (X-memory) side.

  rep   : isolated repetition code (elevator inner round), PyMatching, p in [1e-3, 1e-2]
  xlow  : elevator X memory (noop reading, full sweep), BP+LSD (min-sum 30), lower p / larger d
"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPLSD = dict(name="bplsd", bp_method="minimum_sum", ms_scaling_factor=0.9, max_iter=30, lsd_method="lsd_cs", lsd_order=4)


def rep_rate_guess(d, p):
    return 0.13 * (25.02 * p) ** (0.99 * (d + 1) / 2)


def rep_tasks():
    ts = []
    seed = 7000
    for p in [1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2]:
        for d in range(5, 60, 2):
            r = rep_rate_guess(d, p)
            if r < 4e-10 or r > 0.05:
                continue
            rounds = max(100, 10 * d)
            shots = int(min(3e10, math.ceil(250 / (r * rounds))))
            seed += 1
            ts.append(dict(kind="rep", d=d, p_z=p, rounds=rounds, extra_idle=0.0, shots=shots,
                           max_fail=200, seed=seed, shard=int(min(2e8, max(1e5, shots / 64)))))
    return ts


def xlow_tasks():
    ts = []
    seed = 9000
    pts = [(1e-2, [13, 17, 21]), (7e-3, [11, 13, 15, 17]), (5e-3, [11, 13, 15]), (3e-3, [9, 11]),
           (2e-3, [7, 9]), (1e-3, [5, 7])]
    for p, ds in pts:
        for d in ds:
            seed += 1
            ts.append(dict(kind="phys", code="15_9_3", d=d, memory="X", p_x=0.0, p_z=p, n_anc=1, mode="full",
                           compress=False, n_outer=1, idle_ctx=["edge", "cnot"], decoder=BPLSD,
                           shots=3_000_000, max_fail=150, seed=seed, shard=400, variant="full/noop"))
    for p, d in [(7e-3, 9), (7e-3, 13), (5e-3, 11)]:
        seed += 1
        ts.append(dict(kind="phys", code="15_6_5", d=d, memory="X", p_x=0.0, p_z=p, n_anc=1, mode="full",
                       compress=False, n_outer=1, idle_ctx=["edge", "cnot"], decoder=BPLSD,
                       shots=3_000_000, max_fail=150, seed=seed, shard=400, variant="full/noop"))
    return ts


if __name__ == "__main__":
    which = sys.argv[1]
    ts = {"rep": rep_tasks, "xlow": xlow_tasks}[which]()
    path = os.path.join(ROOT, "tasks", f"phase_{which}.jsonl")
    with open(path, "w") as fh:
        for t in ts:
            fh.write(json.dumps(t) + "\n")
    print(path, len(ts))
