"""Task files for the flag-free reproduction of arXiv:2601.10786 (Appendix B sampled points).

Writes tasks/repro_z.jsonl and tasks/repro_x.jsonl.  Variants cover the two
unstated circuit details: schedule ('full' sweep with a round after every logical
operation vs 'compress' = exactly d_Z rounds per check) and idle noise on blocks
not taking part in a logical-operation tick ('all' vs 'noop').
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPOSD = dict(name="bposd", bp_method="product_sum", max_iter=100, osd_method="osd_cs", osd_order=7)
BPLSD = dict(name="bplsd", bp_method="product_sum", max_iter=100, lsd_method="lsd_cs", lsd_order=4)
IDLE = {"all": ["edge", "cnot", "op"], "noop": ["edge", "cnot"]}


def z_tasks():
    out = []
    seed = 1000
    for code, n_anc in [("15_9_3", 1), ("15_6_5", 1), ("15_6_5", 2)]:
        for d in [9, 11, 13, 15]:
            for p in [1e-6, 2e-6, 4.5e-6, 1e-5]:
                for sched in (["full", "compress"] if n_anc == 1 else ["full"]):
                    for idle in ["all", "noop"]:
                        seed += 1
                        out.append(dict(kind="phys", code=code, d=d, memory="Z", p_x=p, p_z=0.0,
                                        n_anc=n_anc, mode="full", compress=(sched == "compress"),
                                        n_outer=5, idle_ctx=IDLE[idle], decoder=BPOSD,
                                        shots=4_000_000, max_fail=400, seed=seed,
                                        variant=f"{sched}/{idle}"))
    return out


def x_tasks():
    out = []
    seed = 5000
    for d in [9, 11, 13]:
        for p in [5e-3, 7e-3, 1e-2]:
            for sched in ["full", "compress"]:
                for idle in ["all", "noop"]:
                    seed += 1
                    out.append(dict(kind="phys", code="15_9_3", d=d, memory="X", p_x=0.0, p_z=p,
                                    n_anc=1, mode="full", compress=(sched == "compress"), n_outer=1,
                                    idle_ctx=IDLE[idle], decoder=BPLSD, shots=200_000,
                                    max_fail=300, seed=seed, shard=500, variant=f"{sched}/{idle}"))
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "tasks"), exist_ok=True)
    for name, ts in [("repro_z", z_tasks()), ("repro_x", x_tasks())]:
        with open(os.path.join(ROOT, "tasks", name + ".jsonl"), "w") as fh:
            for t in ts:
                fh.write(json.dumps(t) + "\n")
        print(name, len(ts))
