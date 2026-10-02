"""Second-priority task list (tasks/tier_b.jsonl): the subsets of the extended task files that the
analysis needs beyond the core list (tasks/core_local.jsonl), in priority order.  Every line is
copied verbatim from its source file (same spec, same task id), with its output directory.

Kept: transfer checks in d_Z (main, d_Z = 17, 19), the Hamming alternatives at d_Z = 15 (and
[63,57,3] at 13, 15), bias transfer checks at the ends of the eta range, false flags and the
heralded-flag variant at d_Z = 15, the literal-reading subset, the remaining p_Z = 1e-2 settings,
[16,3,8] at low bias and the rest of the held-out validation.  Everything else is covered by the
validated transfers (docs/methods.md)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from elevator.tasks import task_id  # noqa: E402

ALLC = ["idle", "gate", "prep", "meas"]


def load(name, outdir):
    out = []
    for line in open(os.path.join(ROOT, "tasks", name)):
        if line.strip():
            t = json.loads(line)
            t.setdefault("outdir", outdir)
            out.append(t)
    return out


def fl(t):
    f = t["flag"]
    return f["f"], tuple(f["classes"]), f["window"], f.get("false_rate", 0.0), f.get("mode", "erasure")


def pick():
    core = set()
    for t in load("core_local.jsonl", None):
        t = dict(t); t.pop("outdir", None); core.add(task_id(t))
    G = {}
    A, I = tuple(ALLC), ("idle",)
    # 1. d_Z transfer checks (main grid at d_Z = 17, 19)
    keep = {(0.0, I, 0), (0.99, A, 0), (0.99, I, 0), (0.99, A, 64), (1.0, A, 4096), (0.9, A, 0)}
    G["dcheck"] = [t for t in load("flag_main.jsonl", "results/flag_main")
                   if t["d"] in (17, 19) and fl(t)[:3] in keep and fl(t)[3] == 0]
    # 2. Hamming alternatives at d_Z = 15
    keep_alt = ({(f, A, 0) for f in [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 1.0]}
                | {(0.0, I, 0)} | {(f, I, 0) for f in [0.9, 0.99, 1.0]}
                | {(0.99, A, w) for w in [1, 16, 64, 256, 1024, 4096]} | {(1.0, A, w) for w in [64, 4096]})
    G["alt"] = [t for t in load("flag_alt.jsonl", "results/flag_alt") if t["d"] == 15 and fl(t)[:3] in keep_alt]
    # ([63,57,3] needs ~1.5 GB per process: run separately with fewer processes)
    # 3. bias: transfer checks at the two ends of the eta range
    keep_b = {(0.0, I, 0), (0.99, A, 0), (0.99, I, 0)}
    G["bias"] = [t for t in load("flag_bias_trim.jsonl", "results/flag_bias")
                 if t["d"] == 15 and t["p_x"] in (2.5e-8, 1e-10) and fl(t)[:3] in keep_b]
    # 4. [16,3,8] flag-free at low bias (Fig. 1 below eta ~ 7e4)
    G["bias"] += load("flag_16_3_8.jsonl", "results/flag_16_3_8")
    # 5. p_Z = 1e-2 beyond the core settings
    G["pz1e2"] = [t for t in load("flag_pz1e2.jsonl", "results/flag_pz1e2") if t["d"] in (17, 25)]
    G["pz1e2"] += [t for t in load("flag_pz1e2.jsonl", "results/flag_pz1e2")
                   if t["d"] == 33 and fl(t)[:3] in {(0.0, I, 0), (0.99, A, 0), (1.0, A, 0)}]
    # 6. false flags and heralded flags at d_Z = 15
    G["false"] = [t for t in load("flag_falseflag.jsonl", "results/flag_falseflag") if t["d"] == 15]
    G["herald"] = [t for t in load("flag_herald_trim.jsonl", "results/flag_herald") if t["d"] == 15]
    # 7. literal reading subset
    keep_l = {(0.0, I, 0)} | {(f, I, 0) for f in [0.9, 0.99, 1.0]} | {(f, A, 0) for f in [0.9, 0.99, 1.0]} \
        | {(0.99, A, 64), (0.99, A, 1024)}
    G["literal"] = [t for t in load("flag_literal.jsonl", "results/flag_literal") if fl(t)[:3] in keep_l]
    # 8. rest of the validation
    G["validation"] = load("flag_validation.jsonl", "results/flag_validation")
    # 9. flag-free reproduction and phase-flip points still missing
    # (X memory at the paper's sampled points: the min-sum BP+LSD runs of phase_xlow / phase_ancdiag
    #  cover them; the one missing point is tasks/phase_xrepro.jsonl.  The product-sum repro_x runs
    #  cost ~3 s per shot and are not continued beyond d_Z = 9.)
    G["repro"] = load("phase_xrepro.jsonl", "results/phase_xlow") + load("repro_16_3_8.jsonl", "results/repro_16_3_8")
    G["phase"] = load("phase_xlarge.jsonl", "results/phase_xlarge") + load("phase_rep_literal.jsonl", "results/phase_rep_literal")
    order = ["pz1e2", "repro", "alt", "validation", "bias", "dcheck", "phase", "false", "herald", "literal"]
    out = [t for g in order for t in G[g]]
    seen, res = set(core), []
    for t in out:
        s = dict(t); s.pop("outdir", None)
        k = task_id(s)
        if k in seen:
            continue
        seen.add(k)
        res.append(t)
    return res


if __name__ == "__main__":
    ts = pick()
    for name, seq in [("tier_b.jsonl", ts), ("tier_b_back.jsonl", ts[::-1])]:
        with open(os.path.join(ROOT, "tasks", name), "w") as fh:
            for t in seq:
                fh.write(json.dumps(t) + "\n")
    import collections
    print(len(ts), collections.Counter(t["outdir"] for t in ts))
