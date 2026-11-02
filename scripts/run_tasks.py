"""Run one JSON specification per line using local CPU processes.

  python scripts/run_tasks.py TASKS.jsonl OUTDIR [--procs N]

Each task writes OUTDIR/<task_id>.json unless its spec overrides outdir.
Direct samples resume or skip at their stopping rule; matching stratified results skip.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elevator.flagstudy import run_strata  # noqa: E402
from elevator.tasks import run_task, task_id  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Run saved simulation specifications using local CPU processes.")
    ap.add_argument("tasks", help="JSONL file with one simulation specification per line")
    ap.add_argument("outdir", help="result directory, unless a specification supplies outdir")
    ap.add_argument("--procs", type=int, default=os.cpu_count(), help="sampling processes (default: detected CPU count)")
    ap.add_argument("--shard", type=int, default=None, help="shots per direct-sampling batch; does not affect stratified tasks")
    ap.add_argument("--part", type=int, default=0, help="zero-based part of the specification file to run")
    ap.add_argument("--nparts", type=int, default=1, help="number of interleaved parts into which the file is divided")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    me, nt = a.part, a.nparts
    specs = [json.loads(line) for line in open(a.tasks) if line.strip()]
    for i, spec in enumerate(specs):
        if i % nt != me:
            continue
        odir = spec.pop("outdir", a.outdir)
        os.makedirs(odir, exist_ok=True)
        out = os.path.join(odir, task_id(spec) + ".json")
        if spec["kind"] == "strata":
            if os.path.exists(out) and json.load(open(out)).get("spec") == spec:
                continue
            res = run_strata(spec, a.procs, out)
            print(json.dumps({k: res[k] for k in ("P", "lo", "hi", "pL_P", "seconds", "decodes")}),
                  json.dumps(spec), flush=True)
            continue
        if os.path.exists(out):
            st = json.load(open(out))
            mf = spec.get("max_fail")
            if st.get("spec") == spec and (st["shots"] >= spec["shots"] or (mf and st["fails"] >= mf)):
                continue
        st = run_task(spec, a.procs, out, a.shard)
        print(json.dumps({k: st[k] for k in ("shots", "fails", "rounds", "k", "seconds")}),
              json.dumps(spec), flush=True)


if __name__ == "__main__":
    main()
