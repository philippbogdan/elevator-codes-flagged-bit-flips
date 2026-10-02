"""Result files whose spec is not in any task file (so ./reproduce.sh all would not recreate them).

  python scripts/orphans.py            # list (tasks/legacy.jsonl counts as a task file)
  python scripts/orphans.py --write    # collect the specs no other task file has into tasks/legacy.jsonl
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from elevator.tasks import task_id  # noqa: E402

known = set()
for fn in glob.glob(os.path.join(ROOT, "tasks", "*.jsonl")):
    if fn.endswith("legacy.jsonl") and "--write" in sys.argv:     # regenerating legacy.jsonl itself
        continue
    for line in open(fn):
        if line.strip():
            t = json.loads(line)
            t.pop("outdir", None)
            known.add(task_id(t))
orph = []
for fn in sorted(glob.glob(os.path.join(ROOT, "results", "*", "*.json"))):
    try:
        r = json.load(open(fn))
    except Exception:
        continue
    sp = r.get("spec") if isinstance(r, dict) else None
    if not sp:
        continue
    sp = {k: v for k, v in sp.items() if k != "outdir"}
    if task_id(sp) not in known:
        orph.append((fn, sp))
for fn, sp in orph:
    print(os.path.relpath(fn, ROOT), sp.get("kind"), sp.get("code"), sp.get("d"), sp.get("tag", ""))
print(len(orph), "orphans")
if "--write" in sys.argv:
    with open(os.path.join(ROOT, "tasks", "legacy.jsonl"), "w") as fh:
        for fn, sp in orph:
            t = dict(sp)
            t["outdir"] = os.path.relpath(os.path.dirname(fn), ROOT)
            fh.write(json.dumps(t) + "\n")
