"""Summarize reproduction results against arXiv:2601.10786 fits."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from elevator.decode import wilson

FITX = {("15_9_3", 1): (37.18, 1.94, 2.33), ("15_6_5", 1): (115.14, 2.76, 3.73), ("15_6_5", 2): (88.47, 2.86, 3.89),
        ("16_3_8", 1): (61.99, 3.57, 5.74)}


def fit_z(code, n_anc, d, p):
    a, b, c = FITX[(code, n_anc)]
    return d ** c * (a * p) ** b


def fit_x(code, n_anc, d, p, k):
    n_b = (15 if code != "16_3_8" else 16) + n_anc
    return (n_b / 16) * (9 / k) * 0.12 * (34.4 * p) ** (0.94 * (d + 1) / 2)


def per_round(f, n, R, k):
    if n == 0:
        return float("nan")
    P = f / n
    return 1 - (1 - P) ** (1 / (R * k)) if P < 1 else float("nan")


def load(dirpath):
    rows = []
    for fn in glob.glob(os.path.join(dirpath, "*.json")):
        st = json.load(open(fn))
        sp = dict(st["spec"])
        if sp.get("kind") == "direct_block":      # block-level sampler (equivalent to the physical circuit)
            sp.setdefault("memory", "Z")
            sp.setdefault("p_z", 0.0)
            sp["variant"] = "full/noop" if sp.get("idle_ctx") == ["edge", "cnot"] else "full/all"
        R, k = st["rounds"], st["k"]
        if not st["shots"]:
            continue
        pl = per_round(st["fails"], st["shots"], R, k)
        lo, hi = wilson(st["fails"], st["shots"])
        pl_lo, pl_hi = per_round(lo * st["shots"], st["shots"], R, k), per_round(hi * st["shots"], st["shots"], R, k)
        p = sp["p_x"] if sp["memory"] == "Z" else sp["p_z"]
        fit = fit_z(sp["code"], sp["n_anc"], sp["d"], p) if sp["memory"] == "Z" else fit_x(sp["code"], sp["n_anc"], sp["d"], p, k)
        dec = sp.get("decoder")
        dname = dec if isinstance(dec, str) else (dec or {}).get("name", "?") + (
            "-minsum" if isinstance(dec, dict) and dec.get("bp_method") == "minimum_sum" else "")
        rows.append(dict(code=sp["code"], n_anc=sp["n_anc"], mem=sp["memory"], d=sp["d"], p=p, variant=sp.get("variant"),
                         anc_scale=float(sp.get("anc_scale", 1.0)), n_outer=sp.get("n_outer"), decoder=dname,
                         fails=st["fails"], shots=st["shots"], R=R, k=k, pL=pl, lo=pl_lo, hi=pl_hi, fit=fit,
                         ratio=pl / fit, within=(pl_lo <= 2 * fit and pl_hi >= fit / 2)))
    return rows


if __name__ == "__main__":
    for d_ in sys.argv[1:]:
        rows = load(d_)
        rows.sort(key=lambda r: (r["code"], r["n_anc"], r["variant"], r["d"], r["p"]))
        for r in rows:
            print(f"{r['code']} a{r['n_anc']} {r['mem']} {r['variant']:14s} d={r['d']:2d} p={r['p']:.1e} {r['fails']:5d}/{r['shots']:<8d} pL={r['pL']:.2e} [{r['lo']:.2e},{r['hi']:.2e}] fit={r['fit']:.2e} ratio={r['ratio']:.2f} {'ok' if r['within'] else 'X'}")
