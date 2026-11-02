"""Per-class sums of X probabilities (per unit p_X) for each code and d_Z: results/summary/class_sums.json.

For every location class c the file stores [sum of X probabilities of locations whose flip has an
effect, sum over all locations]; with them the fault intensities U and S of any flag setting at any
p_X follow exactly (transfer of the stratum failure fractions F(a, b) across d_Z and p_X).
For d_Z >= 17 the sums are exact quadratics in d_Z (checked: 1e-9 relative at d_Z = 37 ... 61 from
a fit on 17 ... 33), which the analysis uses beyond the computed distances.

  python scripts/class_sums.py [config ...]     config = code:n_anc[:n_outer][:lit], default: all
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from elevator.blocklevel import BlockModel, class_sums  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.schedule import ElevatorSchedule  # noqa: E402

DEFAULT = ["15_9_3:1", "15_6_5:1", "15_6_5:2", "ham15:1", "ham31:1", "xham16:1", "ham63:1:3", "16_3_8:1",
           "15_9_3:1:lit", "15_6_5:1:lit", "15_6_5:2:lit"]
DS = [13, 15, 17, 19, 21, 25, 29, 33, 37, 41, 45, 51, 57, 61]
PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "summary", "class_sums.json")


def key(nm, na, d, n_outer, literal=False):
    return f"{nm}:a{na}:d{d}" + ("" if n_outer == 5 else f":o{n_outer}") + (":lit" if literal else "")


def main():
    cfgs = sys.argv[1:] or DEFAULT
    out = json.load(open(PATH)) if os.path.exists(PATH) else {}
    for cfg in cfgs:
        parts = cfg.split(":")
        literal = parts[-1] == "lit"
        if literal:
            parts = parts[:-1]
        nm, na = parts[0], int(parts[1])
        n_outer = int(parts[2]) if len(parts) > 2 else 5
        code = load_code(nm)
        ds = DS if code.n <= 31 else [13, 15, 17, 19, 21, 25, 29, 33]
        for d in ds:
            k = key(nm, na, d, n_outer, literal)
            if k in out:
                continue
            t = time.time()
            s = ElevatorSchedule(code, d, n_anc=na, n_outer=n_outer)
            ctx = ("edge", "cnot", "op") if literal else ("edge", "cnot")
            bm = BlockModel(s, 1.0, idle_ctx=ctx)   # p = 1: sums are per unit p
            cs = class_sums(bm)
            out[k] = dict(sums=cs, rounds=s.n_rounds, k=code.k)
            print(nm, na, n_outer, d, s.n_rounds, {c: round(v[0]) for c, v in cs.items()}, f"{time.time() - t:.1f}s", flush=True)
            del bm
            json.dump(out, open(PATH, "w"), indent=1)


if __name__ == "__main__":
    main()
