"""Per-class sums of X probabilities (per unit p_X) for each code and d_Z: results/summary/class_sums.json."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from elevator.codes import load_code
from elevator.schedule import ElevatorSchedule
from elevator.blocklevel import BlockModel, class_sums
out = {}
for nm, na in [("15_9_3",1),("15_6_5",1),("15_6_5",2),("ham15",1),("ham31",1),("xham16",1)]:
    code = load_code(nm)
    for d in [13,15,17,19,21,25,29,33,37,41,45,51,57,61]:
        t=time.time()
        s = ElevatorSchedule(code, d, n_anc=na, n_outer=5)
        bm = BlockModel(s, 1.0, idle_ctx=("edge","cnot"))   # p = 1: sums are per unit p
        cs = class_sums(bm)
        out[f"{nm}:a{na}:d{d}"] = dict(sums=cs, rounds=s.n_rounds, k=code.k)
        print(nm, na, d, s.n_rounds, {k: round(v[0]) for k,v in cs.items()}, f"{time.time()-t:.1f}s", flush=True)
        del bm
json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "summary", "class_sums.json"), "w"), indent=1)
