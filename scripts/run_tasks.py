"""Run the tasks of a JSONL task file (one JSON spec per line).

  python scripts/run_tasks.py TASKS.jsonl OUTDIR [--procs N]

Under gpurun --tasks N, task line i is run by GPURUN_TASK == i mod GPURUN_NTASKS.
Each task writes OUTDIR/<task_id>.json (checkpointed; reruns resume or skip).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elevator.tasks import run_task, task_id  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks")
    ap.add_argument("outdir")
    # default: the cores allocated by gpurun (exported as OMP_NUM_THREADS), not the machine's
    ap.add_argument("--procs", type=int, default=int(os.environ.get("OMP_NUM_THREADS", os.cpu_count())))
    ap.add_argument("--shard", type=int, default=None)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    me = int(os.environ.get("GPURUN_TASK", "0"))
    nt = int(os.environ.get("GPURUN_NTASKS", "1"))
    specs = [json.loads(line) for line in open(a.tasks) if line.strip()]
    for i, spec in enumerate(specs):
        if i % nt != me:
            continue
        out = os.path.join(a.outdir, task_id(spec) + ".json")
        if spec["kind"] == "strata":
            from elevator.flagstudy import run_strata
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
