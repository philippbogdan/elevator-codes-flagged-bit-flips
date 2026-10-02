"""Count finished tasks of task files (by task_id and matching spec).  python scripts/progress.py tasks/*.jsonl"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from elevator.tasks import task_id  # noqa: E402

DEFAULT_OUT = {}
for fn in sys.argv[1:]:
    done = tot = 0
    by = {}
    for line in open(fn):
        if not line.strip():
            continue
        s = json.loads(line)
        od = s.pop("outdir", None) or DEFAULT_OUT.get(fn)
        tot += 1
        tag = s.get("tag", s.get("kind"))
        ok = False
        if od:
            p = os.path.join(od, task_id(s) + ".json")
            ok = os.path.exists(p)
        else:
            for d in os.listdir("results"):
                if os.path.exists(os.path.join("results", d, task_id(s) + ".json")):
                    ok = True
                    break
        done += ok
        b = by.setdefault(tag, [0, 0])
        b[0] += ok
        b[1] += 1
    print(f"{fn}: {done}/{tot}  " + "  ".join(f"{k} {v[0]}/{v[1]}" for k, v in by.items()))
