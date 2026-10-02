"""Regenerate every table, figure and number from the stored raw results.

  python scripts/analyze.py            # writes results/summary/*
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from elevator import overhead as OH  # noqa: E402
from elevator.analysis import load_strata, overhead  # noqa: E402

OUT = os.path.join(ROOT, "results", "summary")
os.makedirs(OUT, exist_ok=True)
NUMBERS: dict = {}


def save_numbers():
    json.dump(NUMBERS, open(os.path.join(OUT, "numbers.json"), "w"), indent=1, default=float)


# ------------------------------------------------------------------ 1. reproduction
def repro_tables():
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from summarize_repro import load
    out = []
    for mem, dd in [("Z", "repro_z"), ("X", "repro_x")]:
        rows = load(os.path.join(ROOT, "results", dd))
        rows.sort(key=lambda r: (r["code"], r["n_anc"], r["variant"], r["d"], r["p"]))
        by_var = defaultdict(list)
        for r in rows:
            by_var[(r["code"], r["n_anc"], r["variant"])].append(r)
        out.append(f"\n### {mem}-type memory (flags off) vs arXiv:2601.10786 fits\n")
        out.append("| code | anc | reading | points within 2x / 95% CI | ratio range (this work / fit) |")
        out.append("|---|---|---|---|---|")
        for key, rs in sorted(by_var.items()):
            ok = sum(r["within"] for r in rs)
            rat = [r["ratio"] for r in rs]
            out.append(f"| {key[0]} | {key[1]} | {key[2]} | {ok}/{len(rs)} | {min(rat):.2f} - {max(rat):.2f} |")
            NUMBERS.setdefault("repro", {})[f"{mem}:{key[0]}:a{key[1]}:{key[2]}"] = dict(
                within=ok, n=len(rs), ratio_min=min(rat), ratio_max=max(rat))
        out.append("")
        out.append("| code | anc | reading | d | p | fails/shots | p_L this work [95% CI] | fit | ratio |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            out.append(f"| {r['code']} | {r['n_anc']} | {r['variant']} | {r['d']} | {r['p']:.1e} | "
                       f"{r['fails']}/{r['shots']} | {r['pL']:.2e} [{r['lo']:.2e}, {r['hi']:.2e}] | "
                       f"{r['fit']:.2e} | {r['ratio']:.2f}{'' if r['within'] else ' (outside)'} |")
    open(os.path.join(OUT, "reproduction.md"), "w").write("\n".join(out) + "\n")


def figures_from_fits():
    """Figures 1 and 2 of arXiv:2601.10786 recomputed from its own fitted models."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    etas = np.logspace(np.log10(4e4), 7, 300)
    fam = {"elevator": [], "rot": [], "xzzx": []}
    for eta in etas:
        cs = OH.candidates(1e-3, eta)
        for f in fam:
            c = OH.min_overhead(1e-12, cs, f)
            fam[f].append(c.overhead if c else np.nan)
    fig, ax = plt.subplots(figsize=(5, 4))
    for f, lab in [("elevator", "Concatenated (fits)"), ("rot", "Thin surface (fits)"), ("xzzx", "Thin XZZX (fits)")]:
        ax.step(etas, fam[f], where="post", label=lab)
    ax.set_xscale("log"); ax.set_xlabel("noise bias eta"); ax.set_ylabel("qubit overhead"); ax.set_ylim(50, 250)
    ax.legend(); ax.set_title("Fig. 1 of arXiv:2601.10786 from its fits")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig1_from_paper_fits.png"), dpi=130); plt.close(fig)
    # key numbers
    key = {}
    for eta in [5e4, 1e5, 1e6, 2e6, 1e7]:
        cs = OH.candidates(1e-3, eta)
        key[f"eta={eta:g}"] = {f: (OH.min_overhead(1e-12, cs, f).overhead if OH.min_overhead(1e-12, cs, f) else None)
                               for f in ["elevator", "rot", "xzzx"]}
    NUMBERS["fig1_from_fits"] = key
    # transitions
    prev, trans = None, []
    for eta in np.logspace(np.log10(4e4), 7, 2000):
        c = OH.min_overhead(1e-12, OH.candidates(1e-3, eta), "elevator")
        lab = (round(c.overhead, 2), c.label) if c else None
        if lab != prev:
            trans.append(dict(eta=float(eta), overhead=lab[0] if lab else None, code=lab[1] if lab else None))
            prev = lab
    NUMBERS["fig1_elevator_steps"] = trans
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    for ax, pz in zip(axs, [1e-3, 1e-2]):
        cs = OH.candidates(pz, 1e6)
        targets = np.logspace(-17 if pz == 1e-3 else -12, -5 if pz == 1e-3 else -3, 400)
        for f, lab in [("rep", "Repetition"), ("elevator", "Concatenated"), ("rot", "Thin surface"), ("xzzx", "XZZX")]:
            ys = [(OH.min_overhead(t, cs, f).overhead if OH.min_overhead(t, cs, f) else np.nan) for t in targets]
            ax.step(targets, ys, where="post", label=lab)
        ax.set_xscale("log"); ax.set_ylim(0, 380); ax.set_xlabel("logical error rate"); ax.set_ylabel("qubit overhead")
        ax.set_title(f"p_Z={pz:g}, eta=1e6 (from fits)")
        fl = {lab: OH.floor_pl([c for c in cs if c.label == lab], "elevator") for lab in sorted(set(c.label for c in cs if c.family == "elevator"))}
        NUMBERS.setdefault("fig2_from_fits_floors", {})[f"pz={pz:g}"] = {k: dict(pl=v.pl, d=v.d, overhead=v.overhead) for k, v in fl.items()}
    axs[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_from_paper_fits.png"), dpi=130); plt.close(fig)


# ------------------------------------------------------------------ 2. phase-flip model
PHASE = {}


def phase_model():
    """Fit p_rep(d, p) (isolated repetition code) and the elevator/rep ratio c; held-out checks."""
    from elevator.phasemodel import RepModel, fit_ratio, load_elev_x, load_rep
    rows = load_rep(os.path.join(ROOT, "results", "phase_rep"))
    if len(rows) < 8:
        return None
    byp = defaultdict(list)
    for r in rows:
        byp[r["p"]].append(r)
    held, train = [], []
    for p, rs in byp.items():
        rs.sort(key=lambda r: r["d"])
        if len(rs) >= 3:
            held.append(rs[-1]); train += rs[:-1]
        else:
            train += rs
    m_tr = RepModel(train)
    lines = ["\n## Phase-flip model\n", "### Isolated repetition code (elevator inner round, PyMatching)\n",
             "Model: log p_rep = a0 + a1 log p + h (b0 + b1 log p + b2 log^2 p), h = (d_Z + 1)/2, weighted by failures.\n",
             "Held-out test: the lowest-rate (largest d_Z) point at each p is left out of the fit and predicted.\n",
             "| p_Z | d_Z | measured per round [95% CI] | failures | predicted (held out) | ratio |", "|---|---|---|---|---|---|"]
    ho = []
    for r in sorted(held, key=lambda r: (r["p"], r["d"])):
        mu, sd = m_tr.log_predict(r["d"], r["p"])
        pred = float(np.exp(mu[0]))
        inside = r["lo"] <= pred * math.exp(2 * sd[0]) and r["hi"] >= pred * math.exp(-2 * sd[0])
        ho.append(dict(p=r["p"], d=r["d"], y=r["y"], lo=r["lo"], hi=r["hi"], pred=pred, ratio=r["y"] / pred, inside=inside))
        lines.append(f"| {r['p']:.1e} | {r['d']} | {r['y']:.2e} [{r['lo']:.2e}, {r['hi']:.2e}] | {r['fails']} | {pred:.2e} | {r['y']/pred:.2f} |")
    m = RepModel(rows)
    PHASE["rep"] = m
    NUMBERS["phase_rep_fit"] = dict(coef=list(m.coef), rms_log=m.rms, n=len(rows), heldout=ho)
    # paper comparison for the repetition code
    lines.append("\nAll points against the paper's repetition-code fit 0.13 (25.02 p)^(0.99 (d+1)/2):\n")
    lines.append("| p_Z | d_Z | this work | paper fit | ratio |")
    lines.append("|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r["p"], r["d"])):
        fit = 0.13 * (25.02 * r["p"]) ** (0.99 * (r["d"] + 1) / 2)
        lines.append(f"| {r['p']:.1e} | {r['d']} | {r['y']:.2e} | {fit:.2e} | {r['y']/fit:.2f} |")
    # elevator / rep ratio
    elev = [r for r in load_elev_x([os.path.join(ROOT, "results", d) for d in ("repro_x", "phase_xlow")])
            if r["idle"] == "edge,cnot" and not r["compress"]]
    NBK = {(c, a): (OH.ELEVATOR_NK[c][0] + a) / OH.ELEVATOR_NK[c][1] for c in OH.ELEVATOR_NK for a in (1, 2)}
    if len(elev) >= 4:
        coef, cov, resid = fit_ratio(elev, m, NBK)
        PHASE["c"] = (coef, cov)
        lines.append("\n### Elevator X memory (noop reading, full sweep, BP+LSD) over (n_b/k) p_rep\n")
        lines.append(f"log c = {coef[0]:.3f} + {coef[1]:.3f} log p + {coef[2]:.3f} h\n")
        lines.append("| code | d_Z | p_Z | p_ZL measured [95% CI] | (n_b/k) p_rep | c |")
        lines.append("|---|---|---|---|---|---|")
        for r in sorted(elev, key=lambda r: (r["code"], r["p"], r["d"])):
            pr = float(m.predict(r["d"], r["p"])) * NBK[(r["code"], r["n_anc"])]
            lines.append(f"| {r['code']} | {r['d']} | {r['p']:.1e} | {r['y']:.2e} [{r['lo']:.2e}, {r['hi']:.2e}] | {pr:.2e} | {r['y']/pr:.2f} |")
        NUMBERS["phase_ratio_fit"] = dict(coef=list(coef), n=len(elev))
    open(os.path.join(OUT, "phase_model.md"), "w").write("\n".join(lines) + "\n")
    return m


def pzl_model(code, n_anc, d, pz, conservative=False):
    """This work's phase-flip model: (n_b/k) c(d,p) p_rep(d,p)."""
    m = PHASE["rep"]
    n, k = OH.ELEVATOR_NK[code]
    mu, sd = m.log_predict(d, pz)
    val = float(np.exp(mu[0] + (2 * sd[0] if conservative else 0.0)))
    if "c" in PHASE:
        coef, cov = PHASE["c"]
        x = np.array([1.0, math.log(pz), (d + 1) / 2])
        lc = float(x @ coef)
        if conservative:
            lc += 2 * math.sqrt(max(float(x @ cov @ x), 0.0))
        val *= math.exp(lc)
    else:
        val *= 2.0          # placeholder until the elevator/rep ratio is measured
    return (n + n_anc) / k * val


# ------------------------------------------------------------------ 2b. transfer of F(a,b) across d_Z
CLASS_LIST = ["idle", "gate", "prep", "meas"]
CLASSES_OF = {"none": [], "idle": ["idle"], "idle+gate": ["idle", "gate"], "all": CLASS_LIST}


def class_sums_table():
    fn = os.path.join(OUT, "class_sums.json")
    return json.load(open(fn)) if os.path.exists(fn) else {}


def transfer_pxl(row, d_target, p_x=None):
    """p_XL (per round per logical qubit) at d_target from the stratum failure fractions of `row`
    (computed at row['d']) and exact fault intensities U, S at d_target (class sums).
    Returns (central, lo, hi)."""
    from elevator.decode import wilson
    from elevator.strata import pois
    sums = class_sums_table().get(f"{row['code']}:a{row['n_anc']}:d{d_target}")
    if sums is None:
        return None
    p_x = row["p_x"] if p_x is None else p_x
    eff = {c: (row["f"] if c in CLASSES_OF[row["classes"]] else 0.0) for c in CLASS_LIST}
    U = p_x * sum((1 - eff[c]) * sums["sums"][c][0] for c in CLASS_LIST)
    S = p_x * sum(2 * eff[c] * sums["sums"][c][1] for c in CLASS_LIST)
    est = lo = hi = 0.0
    kmax = 0
    for key, (f, n) in row["strata"].items():
        a, b = map(int, key.split(","))
        kmax = max(kmax, a + b)
        w = pois(a, U) * pois(b, S)
        if key in row["exact"]:
            v = row["exact"][key]
            est += w * v; lo += w * v; hi += w * v
            continue
        if n == 0:
            continue
        l, h = wilson(f, n)
        est += w * f / n; lo += w * l; hi += w * h
    tail = 1.0 - sum(pois(a, U) * pois(t - a, S) for t in range(kmax + 1) for a in range(t + 1))
    R, k = sums["rounds"], sums["k"]
    return est / (R * k), lo / (R * k), (hi + max(tail, 0.0)) / (R * k)


# ------------------------------------------------------------------ 3. flag study
CODES_MAIN = [("15_9_3", 1), ("15_6_5", 1), ("15_6_5", 2)]
CODE_LABEL = {("15_9_3", 1): "[15,9,3]", ("15_6_5", 1): "[15,6,5]", ("15_6_5", 2): "[15,6,5] 2 anc",
              ("ham15", 1): "Hamming [15,11,3]", ("ham31", 1): "Hamming [31,26,3]", ("xham16", 1): "ext. Hamming [16,11,4]"}


def pzl_paper(code, n_anc, d, pz):
    return OH.paper_pzl(code, n_anc, d, pz)


def flag_rows(dirs):
    rows = []
    for dd in dirs:
        p = os.path.join(ROOT, "results", dd)
        if os.path.isdir(p):
            rows += load_strata(p)
    return rows


def select(rows, **kw):
    out = []
    for r in rows:
        if all((r.get(k) == v) if not callable(v) else v(r.get(k)) for k, v in kw.items()):
            out.append(r)
    return out


def best_overhead(rows_by_cd, pz, target, pzl_fn, use="pL", codes=CODES_MAIN):
    """rows_by_cd: {(code, n_anc, d): row}; cheapest admissible (code, d)."""
    best = None
    for (code, n_anc, d), r in rows_by_cd.items():
        if (code, n_anc) not in codes:
            continue
        tot = r[use] + pzl_fn(code, n_anc, d, pz)
        if tot <= target:
            oh = overhead(code, n_anc, d)
            if best is None or oh < best[0]:
                best = (oh, code, n_anc, d, r[use], tot)
    return best


def flag_tables(pzl_fn=pzl_paper, tag="paper-pZL", dirs=("flag_main",), idle="edge,cnot", px=1e-9,
                codes=CODES_MAIN, label="main"):
    rows = select(flag_rows(dirs), idle=idle, p_x=px)
    if not rows:
        return
    lines = [f"\n## Flagged bit flips, p_X = {px:g} (reading: idle={idle}); phase flips from {tag}\n"]
    # f = 0 rows apply to every class and window
    f0 = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["f"] == 0}
    settings = sorted({(r["classes"], r["window"], r["f"], r["r"]) for r in rows if r["f"] > 0})
    res = {}
    for (cls, w, f, rr) in [("none", 0, 0.0, 0.0)] + settings:
        if f == 0:
            byc = f0
        else:
            byc = {(r["code"], r["n_anc"], r["d"]): r for r in rows
                   if r["classes"] == cls and r["window"] == w and r["f"] == f and r["r"] == rr}
        for use in ("pL", "hi"):
            b = best_overhead(byc, 1e-3, 1e-12, pzl_fn, use, codes)
            res[(cls, w, f, rr, use)] = b
        per_code = {}
        for code in codes:
            sub = {k: v for k, v in byc.items() if (k[0], k[1]) == code}
            b = best_overhead(sub, 1e-3, 1e-12, pzl_fn, "pL", [code])
            per_code[code] = b
        res[(cls, w, f, rr, "per_code")] = per_code
    # table: overhead vs f (exact timing)
    lines.append("### Minimum qubit overhead at p_Z = 1e-3, eta = 1e6, target 1e-12 per round per logical qubit\n")
    lines.append("Central estimate (conservative: bit-flip rate at its 95% upper bound) and the chosen code/d_Z.\n")
    lines.append("| flags on | window (ticks) | f | false flags /qubit/tick | overhead (central) | code, d_Z | p_XL | overhead (conservative) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for key in [("none", 0, 0.0, 0.0)] + settings:
        b = res[key + ("pL",)]
        bh = res[key + ("hi",)]
        cell = (f"{b[0]:.1f} | {CODE_LABEL[(b[1], b[2])]}, {b[3]} | {b[4]:.2e}" if b else "not reached | - | -")
        cellh = f"{bh[0]:.1f}" if bh else "not reached"
        lines.append(f"| {key[0]} | {'exact' if key[1] == 0 else key[1]} | {key[2]} | {key[3]:g} | {cell} | {cellh} |")
    open(os.path.join(OUT, f"flags_{label}_{tag}.md"), "w").write("\n".join(lines) + "\n")
    NUMBERS.setdefault("flags", {})[f"{label}:{tag}"] = {
        f"{k[0]}|w{k[1]}|f{k[2]}|r{k[3]}|{k[4]}": (None if v is None else (v if k[4] != "per_code" else
                                                     {CODE_LABEL[c]: (None if bb is None else bb[0]) for c, bb in v.items()}))
        for k, v in res.items()}
    return res, rows


# ------------------------------------------------------------------ 4. validation (held-out direct MC)
def validation_table():
    from elevator.decode import wilson
    vdir = os.path.join(ROOT, "results", "flag_validation")
    if not os.path.isdir(vdir):
        return
    strata = {}
    direct = {}
    import glob as _g
    for fn in _g.glob(os.path.join(vdir, "*.json")):
        r = json.load(open(fn))
        sp = r["spec"]
        key = (sp["code"], sp["n_anc"], sp["d"], sp["p_x"], sp["flag"]["f"], tuple(sp["flag"]["classes"]), sp["flag"]["window"])
        if sp["kind"] == "strata":
            strata[key] = r
        elif r.get("shots"):
            direct[key] = r
    lines = ["\n## Held-out check of the stratified estimator under flags\n",
             "Same configuration, two estimators: direct Monte Carlo (all events sampled) and the stratified "
             "estimator used at p_X = 1e-9 (truncated at a+b <= kmax).  Per shot, 95% intervals.\n",
             "| code | p_X | f | flags on | window | direct P_fail [95% CI] | stratified [95% CI] | agree |",
             "|---|---|---|---|---|---|---|---|"]
    agree = 0
    total = 0
    for key in sorted(set(strata) & set(direct)):
        s_, d_ = strata[key], direct[key]
        P = d_["fails"] / d_["shots"]
        lo, hi = wilson(d_["fails"], d_["shots"])
        ok = not (s_["hi"] < lo or s_["lo"] > hi)
        agree += ok
        total += 1
        cls = {1: "idle", 2: "idle+gate", 4: "all"}.get(len(key[5]), "?") if key[4] > 0 else "-"
        lines.append(f"| {CODE_LABEL[(key[0], key[1])]} | {key[3]:.0e} | {key[4]} | {cls} | {key[6] or 'exact'} | "
                     f"{P:.3e} [{lo:.2e}, {hi:.2e}] | {s_['P']:.3e} [{s_['lo']:.2e}, {s_['hi']:.2e}] | {'yes' if ok else 'NO'} |")
    lines.append(f"\n{agree} of {total} configurations agree within the 95% intervals.\n")
    NUMBERS["validation"] = dict(agree=agree, total=total)
    open(os.path.join(OUT, "validation.md"), "w").write("\n".join(lines) + "\n")


# ------------------------------------------------------------------ 5. bias sweep
ETAS = {2.5e-8: 4e4, 1e-8: 1e5, 4e-9: 2.5e5, 2e-9: 5e5, 1e-9: 1e6, 5e-10: 2e6, 2e-10: 5e6, 1e-10: 1e7}


def bias_sweep(pzl_fn, tag, codes=CODES_MAIN, label="bias"):
    rows = [r for r in flag_rows(("flag_main", "flag_bias", "flag_alt")) if r["idle"] == "edge,cnot"]
    settings = [("none", 0, 0.0), ("all", 0, 0.9), ("all", 0, 0.99), ("all", 0, 1.0), ("idle", 0, 0.9),
                ("idle", 0, 0.99), ("all", 64, 0.99), ("all", 1024, 0.99)]
    lines = [f"\n## Overhead vs noise bias at p_Z = 1e-3, target 1e-12 (phase flips: {tag})\n",
             "| eta | p_X | " + " | ".join(f"{c} f={f} w={w or 'exact'}" for c, w, f in settings) + " |",
             "|---|---|" + "---|" * len(settings)]
    out = {}
    for px, eta in sorted(ETAS.items(), key=lambda kv: kv[1]):
        cells = []
        for (cls, w, f) in settings:
            if f == 0:
                byc = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["p_x"] == px and r["f"] == 0 and r["r"] == 0}
            else:
                byc = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["p_x"] == px and r["f"] == f
                       and r["classes"] == cls and r["window"] == w and r["r"] == 0}
            b = best_overhead(byc, 1e-3, 1e-12, pzl_fn, "pL", codes)
            out[(eta, cls, w, f)] = b
            cells.append(f"{b[0]:.1f} ({CODE_LABEL[(b[1], b[2])]}, {b[3]})" if b else ("-" if not byc else "not reached"))
        lines.append(f"| {eta:.1e} | {px:.1e} | " + " | ".join(cells) + " |")
    open(os.path.join(OUT, f"{label}_{tag}.md"), "w").write("\n".join(lines) + "\n")
    NUMBERS.setdefault("bias", {})[f"{label}:{tag}"] = {f"{k[0]:g}|{k[1]}|w{k[2]}|f{k[3]}": (None if v is None else v[0]) for k, v in out.items()}
    return out


if __name__ == "__main__":
    repro_tables()
    figures_from_fits()
    flag_tables()
    validation_table()
    bias_sweep(pzl_paper, "paper-pZL")
    if phase_model() is not None:
        flag_tables(pzl_fn=pzl_model, tag="this-work-pZL")
        bias_sweep(pzl_model, "this-work-pZL")
    save_numbers()
    print("wrote", OUT)
