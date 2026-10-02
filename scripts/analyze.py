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
    for mem, dds in [("Z", ["repro_z", "repro_16_3_8"]), ("X", ["repro_x", "phase_xlow", "phase_ancdiag"])]:
        rows = []
        for dd in dds:
            if os.path.isdir(os.path.join(ROOT, "results", dd)):
                rows += load(os.path.join(ROOT, "results", dd))
        if mem == "X":
            # the paper's sampled region of the X memory: [15,9,3], one outer round, d_Z = 9, 11, 13,
            # 5e-3 <= p_Z <= 1e-2 (runs of the phase-flip study at those points count as well)
            rows = [r for r in rows if r["anc_scale"] == 1.0 and r["d"] in (9, 11, 13) and 5e-3 <= r["p"] <= 1e-2]
            for r in rows:
                r["variant"] = f"{r['variant']} {r['decoder']}"
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
    NUMBERS["phase_rep_fit"] = dict(coef=list(m.coef), rms_log=m.rms, n=len(rows), heldout=ho, table=m.table())
    # paper comparison for the repetition code
    lines.append("\nAll points against the paper's repetition-code fit 0.13 (25.02 p)^(0.99 (d+1)/2):\n")
    lines.append("| p_Z | d_Z | this work | paper fit | ratio |")
    lines.append("|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r["p"], r["d"])):
        fit = 0.13 * (25.02 * r["p"]) ** (0.99 * (r["d"] + 1) / 2)
        lines.append(f"| {r['p']:.1e} | {r['d']} | {r['y']:.2e} | {fit:.2e} | {r['y']/fit:.2f} |")
    # elevator / rep ratio
    allx = [r for r in load_elev_x([os.path.join(ROOT, "results", d) for d in ("repro_x", "phase_xlow", "phase_ancdiag", "phase_xlarge")])
            if r["idle"] == "edge,cnot" and not r["compress"]]
    elev = [r for r in allx if r["anc_scale"] == 1.0]
    data_only = [r for r in allx if r["anc_scale"] == 0.0]
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
        if data_only:
            lines.append("\n### Ancilla diagnostic: logical-ancilla and logical-operation noise switched off\n")
            lines.append("| d_Z | p_Z | p_ZL ancilla noise off [95% CI] | (n_b/k) p_rep | c without ancilla noise |")
            lines.append("|---|---|---|---|---|")
            for r in sorted(data_only, key=lambda r: (r["p"], r["d"])):
                pr = float(m.predict(r["d"], r["p"])) * NBK[(r["code"], r["n_anc"])]
                lines.append(f"| {r['d']} | {r['p']:.1e} | {r['y']:.2e} [{r['lo']:.2e}, {r['hi']:.2e}] | {pr:.2e} | {r['y']/pr:.2f} |")
        from elevator.phasemodel import fit_two_component
        if len(elev) >= 5:
            NBK2 = {(c, a): OH.ELEVATOR_NK[c] for c in OH.ELEVATOR_NK for a in (1, 2)}
            # held-out test: fit on p_Z >= 3e-3, predict the p_Z <= 2e-3 points (the low-p regime)
            train = [r for r in elev if r["p"] >= 3e-3]
            held = [r for r in elev if r["p"] < 3e-3]
            if len(train) >= 5 and held:
                th0, cov0, tm0 = fit_two_component(train, m, NBK2, [r for r in data_only if r["p"] >= 3e-3])
                lines.append("\nHeld-out test of the two-component model (fit on p_Z >= 3e-3, predict p_Z < 3e-3):\n")
                lines.append("| code | d_Z | p_Z | measured [95% CI] | predicted | ratio |")
                lines.append("|---|---|---|---|---|---|")
                hos = []
                for r in sorted(held, key=lambda r: (r["p"], r["d"])):
                    pred = tm0(th0, r)
                    hos.append(dict(d=r["d"], p=r["p"], y=r["y"], lo=r["lo"], hi=r["hi"], pred=pred, ratio=r["y"] / pred))
                    lines.append(f"| {r['code']} | {r['d']} | {r['p']:.1e} | {r['y']:.2e} [{r['lo']:.2e}, {r['hi']:.2e}] | {pred:.2e} | {r['y']/pred:.2f} |")
                NUMBERS["phase_two_component_heldout"] = hos
            th, thcov, tmodel = fit_two_component(elev, m, NBK2, data_only)
            PHASE["two"] = (th, thcov, tmodel)
            lines.append(f"\nTwo-component model: p_ZL k = n a p_rep(d,p) + n_anc g s(d) p_rep(d, kappa p), s(d) = min(1, (n+1)/d), "
                         f"a = {math.exp(th[0]):.2f}, g = {math.exp(th[1]):.2f}, kappa = {math.exp(th[2]):.2f}\n")
            NUMBERS["phase_two_component"] = dict(a=math.exp(th[0]), g=math.exp(th[1]), kappa=math.exp(th[2]),
                                                   cov=thcov.tolist())
    open(os.path.join(OUT, "phase_model.md"), "w").write("\n".join(lines) + "\n")
    return m


def pzl_ideal(code, n_anc, d, pz):
    """Lower bound for the phase flips: data blocks exactly like isolated repetition codes decoded
    at the ML level (a = 1; matching = ML within statistics for the repetition code), the moving
    ancilla's term kept (it is the noise of the scheme's own logical operations)."""
    m = PHASE["rep"]
    n, k = OH.ELEVATOR_NK[code]
    from elevator.phasemodel import sweep_fraction
    th, thcov, tmodel = PHASE["two"]
    a, g, kap = np.exp(th)
    return float(n * 1.0 * m.predict(d, pz) + n_anc * g * sweep_fraction(n, d) * m.predict(d, kap * pz)) / k


def phase_floor_table():
    """Smallest d_Z whose phase-flip rate alone is below the target, per code (model and ideal bound)."""
    lines = ["\n## Phase-flip floor (flags cannot lower it)\n",
             "| code | p_Z | target | d_Z (this work's model) | overhead | d_Z (ideal decoder bound) | overhead |",
             "|---|---|---|---|---|---|---|"]
    out = {}
    for code in [("15_9_3", 1), ("15_6_5", 1), ("15_6_5", 2), ("ham15", 1), ("ham31", 1), ("ham63", 1)]:
        for pz, tgt in [(1e-3, 1e-12), (1e-3, 1e-15), (1e-2, 1e-9), (1e-2, 1e-12)]:
            dm = next((d for d in range(3, 202, 2) if pzl_model(code[0], code[1], d, pz) <= tgt), None)
            di = next((d for d in range(3, 202, 2) if pzl_ideal(code[0], code[1], d, pz) <= tgt), None)
            om = overhead(code[0], code[1], dm) if dm else None
            oi = overhead(code[0], code[1], di) if di else None
            out[f"{code[0]}|a{code[1]}|{pz:g}|{tgt:g}"] = dict(d_model=dm, oh_model=om, d_ideal=di, oh_ideal=oi)
            lines.append(f"| {CODE_LABEL[code]} | {pz:g} | {tgt:g} | {dm} | {om:.1f} | {di} | {oi:.1f} |" if dm and di
                         else f"| {CODE_LABEL[code]} | {pz:g} | {tgt:g} | {dm} | - | {di} | - |")
    NUMBERS["phase_floor"] = out
    open(os.path.join(OUT, "phase_floor.md"), "w").write("\n".join(lines) + "\n")


def pzl_model(code, n_anc, d, pz, conservative=False):
    """This work's phase-flip model: n a p_rep(d,p) + n_anc g p_rep(d, kappa p), per logical qubit;
    falls back to (n_b/k) c(d,p) p_rep(d,p) if the two-component fit is unavailable."""
    m = PHASE["rep"]
    n, k = OH.ELEVATOR_NK[code]
    if "two" in PHASE:
        th, thcov, tmodel = PHASE["two"]
        a, g, kap = np.exp(th)
        from elevator.phasemodel import sweep_fraction
        val = n * a * m.predict(d, pz) + n_anc * g * sweep_fraction(n, d) * m.predict(d, kap * pz)
        if conservative:
            val *= math.exp(2 * m.log_predict(d, kap * pz)[1][0])
        return float(val) / k
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


_CS = {}


def class_sums_table():
    if "t" not in _CS:
        fn = os.path.join(OUT, "class_sums.json")
        _CS["t"] = json.load(open(fn)) if os.path.exists(fn) else {}
    return _CS["t"]


def class_sums_for(code, n_anc, d, n_outer=5):
    """Exact per-class fault sums at d_Z; beyond the computed distances (d_Z >= 17) from the exact
    quadratic in d_Z through three computed distances (checked to 1e-9 at d_Z = 37 ... 61)."""
    t = class_sums_table()
    sfx = "" if n_outer == 5 else f":o{n_outer}"
    k = f"{code}:a{n_anc}:d{d}{sfx}"
    if k in t:
        return t[k]
    have = sorted(int(x.split(":")[2][1:]) for x in t
                  if x.startswith(f"{code}:a{n_anc}:d") and (x.endswith(sfx) if sfx else x.count(":") == 2))
    big = [x for x in have if x >= 17]
    if d < 17 or len(big) < 3:
        return None
    ds = big[-3:]
    rows = [t[f"{code}:a{n_anc}:d{x}{sfx}"] for x in ds]
    out = {"sums": {}, "k": rows[0]["k"]}
    for c in rows[0]["sums"]:
        out["sums"][c] = [float(np.polyval(np.polyfit(ds, [r["sums"][c][j] for r in rows], 2), d)) for j in (0, 1)]
    out["rounds"] = int(round(np.polyval(np.polyfit(ds, [r["rounds"] for r in rows], 1), d)))
    return out


def transfer_pxl(row, d_target, p_x=None):
    """p_XL (per round per logical qubit) at d_target from the stratum failure fractions of `row`
    (computed at row['d']) and exact fault intensities U, S at d_target (class sums).
    Returns (central, lo, hi)."""
    from elevator.decode import wilson
    from elevator.strata import pois
    sums = class_sums_for(row["code"], row["n_anc"], d_target, row.get("n_outer", 5))
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
        if key in row.get("hi_cap", {}):
            h = min(h, max(row["hi_cap"][key], f / n))
        est += w * f / n; lo += w * l; hi += w * h
    tail = 1.0 - sum(pois(a, U) * pois(t - a, S) for t in range(kmax + 1) for a in range(t + 1))
    R, k = sums["rounds"], sums["k"]
    return est / (R * k), lo / (R * k), (hi + max(tail, 0.0)) / (R * k)


# ------------------------------------------------------------------ 3. flag study
CODES_MAIN = [("15_9_3", 1), ("15_6_5", 1), ("15_6_5", 2)]
CODE_LABEL = {("15_9_3", 1): "[15,9,3]", ("15_6_5", 1): "[15,6,5]", ("15_6_5", 2): "[15,6,5] 2 anc",
              ("ham15", 1): "Hamming [15,11,3]", ("ham31", 1): "Hamming [31,26,3]", ("xham16", 1): "ext. Hamming [16,11,4]",
              ("ham63", 1): "Hamming [63,57,3]", ("16_3_8", 1): "[16,3,8]"}


def pzl_paper(code, n_anc, d, pz):
    return OH.paper_pzl(code, n_anc, d, pz)


_PERFECT = {}


def perfect_exact():
    """Exact F(0, b) for exactly timed perfect flags (scripts/perfect_flags_exact.py)."""
    if "t" not in _PERFECT:
        fn = os.path.join(ROOT, "results", "perfect_flags_exact.json")
        _PERFECT["t"] = json.load(open(fn)) if os.path.exists(fn) else []
    return _PERFECT["t"]


def apply_perfect_exact(r):
    """Rows with f = 1 on every class, exact timing, no false flags: replace the decoder-sampled F(0, b)
    by the decoding-free values of scripts/perfect_flags_exact.py at the nearest computed d_Z (U = 0,
    so these are the only strata).  They enter as sampled strata (round(F n) failures of n event
    sets), so their sampling uncertainty is carried into every interval and transfer."""
    if not (r["f"] == 1.0 and r["classes"] == "all" and r["window"] == 0 and r["r"] == 0
            and r.get("mode", "erasure") == "erasure" and r["U"] == 0):
        return r
    recs = [x for x in perfect_exact() if (x["code"], x["n_anc"], x["n_outer"]) == (r["code"], r["n_anc"], r.get("n_outer", 5))]
    if not recs:
        return r
    rec = min(recs, key=lambda x: abs(x["d"] - r["d"]))
    from elevator.decode import wilson
    from elevator.strata import pois
    r = dict(r)
    ex = {k: v for k, v in r["exact"].items() if not (k.startswith("0,") and k.split(",")[1] in rec["F"])}
    st = {k: v for k, v in r["strata"].items() if not k.startswith("0,")}
    n = int(rec["samples"])
    for b, v in rec["F"].items():
        st[f"0,{b}"] = [int(round(v["F"] * n)), n]
    r["exact"], r["strata"] = ex, st
    r["exact_F_source_d"] = rec["d"]
    est = lo = hi = 0.0
    for k, v in ex.items():
        a, b = map(int, k.split(","))
        w = pois(a, 0.0) * pois(b, r["S"])
        est += w * v; lo += w * v; hi += w * v
    bmax = 0
    for k, (fl, nn) in st.items():
        a, b = map(int, k.split(","))
        bmax = max(bmax, a + b)
        if nn == 0 or a > 0:
            continue
        w = pois(b, r["S"])
        l, h = wilson(fl, nn)
        est += w * fl / nn; lo += w * l; hi += w * h
    tail = 1.0 - sum(pois(b, r["S"]) for b in range(bmax + 1))
    R, k = r["rounds"], r["k"]
    r["P"] = est
    r["pL"], r["lo"], r["hi"] = est / (R * k), lo / (R * k), (hi + max(tail, 0.0)) / (R * k)
    return r


_FFB = {}


def apply_false_flag_bounds(r):
    """Rows with false flags (r > 0) of distance-3 codes: cap the upper end of the single-event strata
    (1,0) and (0,1) by the bounds of scripts/false_flag_bounds.py (results/false_flag_bounds.json)."""
    if r["r"] <= 0:
        return r
    if "t" not in _FFB:
        fn = os.path.join(ROOT, "results", "false_flag_bounds.json")
        _FFB["t"] = json.load(open(fn)) if os.path.exists(fn) else {}
    b = _FFB["t"].get(os.path.relpath(r["file"], ROOT)) or r.get("caps")
    if not b:
        return r
    from elevator.decode import wilson
    from elevator.strata import pois
    r = dict(r)
    r["hi_cap"] = {k: b[k] for k in ("1,0", "0,1", "0,2") if k in b}
    if r.get("caps"):              # caps applied during sampling are already in the stored bounds
        r["hi_cap"].update({k: v for k, v in r["caps"].items()})
    R, k = r["rounds"], r["k"]
    dh = 0.0
    for key, cap in r["hi_cap"].items():
        if key in r["exact"] or key not in r["strata"]:
            continue
        f, n = r["strata"][key]
        if n == 0:
            continue
        a, bb = map(int, key.split(","))
        w = pois(a, r["U"]) * pois(bb, r["S"])
        h = wilson(f, n)[1]
        dh += w * (h - min(h, max(cap, f / n)))
    r["hi"] = r["hi"] - dh / (R * k)
    return r


def flag_rows(dirs, transfers=True):
    rows = []
    for dd in dirs:
        p = os.path.join(ROOT, "results", dd)
        if os.path.isdir(p):
            rows += load_strata(p)
    rows = [apply_false_flag_bounds(apply_perfect_exact(r)) for r in rows]
    # several runs of the same setting (e.g. false-flag runs repeated with analytic caps): keep the
    # one with the tightest upper bound
    best = {}
    for r in rows:
        key = (r["code"], r["n_anc"], r["d"], r["p_x"], r["f"], r["classes"], r["window"], r["r"],
               r.get("mode", "erasure"), r["idle"], r.get("n_outer", 5))
        if key not in best or r["hi"] < best[key]["hi"]:
            best[key] = r
    rows = list(best.values())
    for r in rows:
        r.setdefault("transferred", False)
    if transfers:
        rows += synthesize(rows)
    return rows


TRANSFER_D = [13, 15, 17, 19, 21, 23, 25]
TRANSFER_P = [2.5e-8, 1e-8, 4e-9, 2e-9, 1e-9, 5e-10, 2e-10, 1e-10]


def synthesize(rows):
    """Rows for (d_Z, p_X) not simulated directly: stratum failure fractions from the closest simulated
    d_Z at the same p_X if any, else from p_X = 1e-9, with exact fault intensities (class sums)."""
    have = {}
    for r in rows:
        have[(r["code"], r["n_anc"], r["d"], r["p_x"], r["f"], r["classes"], r["window"], r["r"], r.get("mode", "erasure"), r["idle"])] = r
    out = []
    for (code, n_anc, d, px, f, cls, w, rr, mode, idle), src in list(have.items()):
        if rr != 0 or mode != "erasure":
            continue
        for d2 in TRANSFER_D:
            for p2 in TRANSFER_P:
                k2 = (code, n_anc, d2, p2, f, cls, w, rr, mode, idle)
                if k2 in have:
                    continue
                # prefer a source at the same p_X (any d), else the same d at 1e-9, else this one
                cand = [x for x in rows if (x["code"], x["n_anc"], x["p_x"], x["f"], x["classes"], x["window"], x["r"], x.get("mode", "erasure"), x["idle"]) ==
                        (code, n_anc, p2, f, cls, w, rr, mode, idle)]
                if not cand:
                    cand = [x for x in rows if (x["code"], x["n_anc"], x["p_x"], x["f"], x["classes"], x["window"], x["r"], x.get("mode", "erasure"), x["idle"]) ==
                            (code, n_anc, 1e-9, f, cls, w, rr, mode, idle)]
                if not cand:
                    continue
                srow = min(cand, key=lambda x: (abs(x["d"] - d2), x["transferred"]))
                if srow.get("transferred"):
                    continue
                t = transfer_pxl(srow, d2, p_x=p2)
                if t is None:
                    continue
                nr = dict(srow)
                nr.update(d=d2, p_x=p2, pL=t[0], lo=t[1], hi=t[2], transferred=True,
                          transferred_from=(srow["d"], srow["p_x"]))
                have[k2] = nr
                out.append(nr)
    return out


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
            # a decoder may always ignore the flags: codes without a run at this setting keep their
            # flag-free rate (marked in the per-code columns only by its value)
            for k_, v_ in f0.items():
                byc.setdefault(k_, v_)
        for use in ("pL", "hi"):
            b = best_overhead(byc, 1e-3, 1e-12, pzl_fn, use, codes)
            res[(cls, w, f, rr, use)] = b
        per_code = {}
        for code in codes:
            sub = {k: v for k, v in byc.items() if (k[0], k[1]) == code}
            b = best_overhead(sub, 1e-3, 1e-12, pzl_fn, "pL", [code])
            per_code[code] = b if b else ("n.r." if sub else "-")
        res[(cls, w, f, rr, "per_code")] = per_code
        # the simulated (not transferred) d_Z = 15 rows with their 95% intervals and failure counts
        sim = {}
        for code in codes:
            r15 = [r for r in byc.values() if (r["code"], r["n_anc"]) == code and r["d"] == 15 and not r.get("transferred")]
            if r15:
                r = r15[0]
                nf = sum(v[0] for k, v in r["strata"].items() if k not in r["exact"])
                sim[code] = (r["pL"], r["lo"], r["hi"], nf)
        res[(cls, w, f, rr, "sim15")] = sim
    # table: overhead vs f (exact timing)
    lines.append("### Minimum qubit overhead at p_Z = 1e-3, eta = 1e6, target 1e-12 per round per logical qubit\n")
    lines.append("Central estimate (conservative: bit-flip rate at its 95% upper bound) and the chosen code/d_Z.\n")
    hdr_codes = " | ".join(CODE_LABEL[c] for c in codes)
    lines.append("Per code: minimum overhead ('n.r.' = simulated but not reaching the target, '-' = not simulated), "
                 "then p_XL at d_Z = 15 per round per logical qubit [95% CI] (sampled logical failures behind it); "
                 "these p_X = 1e-9 values lie below direct-sampling reach and come from the stratified estimator "
                 "(model: Poisson strata, held-out check in validation.md).\n")
    lines.append(f"| flags on | window (ticks) | f | false flags /qubit/tick | best overhead (central) | code, d_Z | p_XL | best (conservative) | {hdr_codes} | "
                 + " | ".join(f"{CODE_LABEL[c]} p_XL(d=15)" for c in codes) + " |")
    lines.append("|---|---|---|---|---|---|---|---|" + "---|" * (2 * len(codes)))
    for key in [("none", 0, 0.0, 0.0)] + settings:
        b = res[key + ("pL",)]
        bh = res[key + ("hi",)]
        cell = (f"{b[0]:.1f} | {CODE_LABEL[(b[1], b[2])]}, {b[3]} | {b[4]:.2e}" if b else "not reached | - | -")
        cellh = f"{bh[0]:.1f}" if bh else "not reached"
        pc = res[key + ("per_code",)]
        cells = " | ".join((f"{pc[c][0]:.1f} (d={pc[c][3]})" if isinstance(pc.get(c), tuple) else pc.get(c, "-")) for c in codes)
        sim = res[key + ("sim15",)]
        cells2 = " | ".join((f"{sim[c][0]:.2e} [{sim[c][1]:.1e}, {sim[c][2]:.1e}] ({sim[c][3]})" if c in sim else "-") for c in codes)
        lines.append(f"| {key[0]} | {'exact' if key[1] == 0 else key[1]} | {key[2]} | {key[3]:g} | {cell} | {cellh} | {cells} | {cells2} |")
    open(os.path.join(OUT, f"flags_{label}_{tag}.md"), "w").write("\n".join(lines) + "\n")
    NUMBERS.setdefault("flags", {})[f"{label}:{tag}"] = {
        f"{k[0]}|w{k[1]}|f{k[2]}|r{k[3]}|{k[4]}": (None if v is None else (
            {CODE_LABEL[c]: (bb[0] if isinstance(bb, tuple) else bb) for c, bb in v.items()} if k[4] == "per_code" else
            ({CODE_LABEL[c]: list(bb) for c, bb in v.items()} if k[4] == "sim15" else v)))
        for k, v in res.items()}
    return res, rows


def required_f(pzl_fn, tag, dirs=("flag_main", "flag_supp"), codes=CODES_MAIN + [("ham15", 1), ("ham31", 1), ("ham63", 1)],
               target=1e-12, pz=1e-3, px=1e-9):
    """Minimum flag efficiency for each (code, d_Z, flag classes, window) to reach the target:
    log p_XL interpolated linearly in log(1 - f) between the bracketing simulated efficiencies (bit-flip
    upper bound used for the conservative column); the bracketing efficiencies are reported."""
    rows = [r for r in flag_rows(dirs + ("flag_alt", "flag_ham63")) if r["idle"] == "edge,cnot" and r["p_x"] == px and r["r"] == 0]
    groups = defaultdict(dict)
    zero = {}
    for r in rows:
        if r["f"] == 0:
            zero[(r["code"], r["n_anc"], r["d"])] = r
    for r in rows:
        if r["f"] > 0:
            groups[(r["code"], r["n_anc"], r["d"], r["classes"], r["window"])][r["f"]] = r
    lines = [f"\n## Minimum flag efficiency to reach {target:g} at p_Z = {pz:g}, eta = {pz/px:g} (phase flips: {tag})\n",
             "| code | d_Z | overhead | flags on | window | f required (central) | f required (95% upper bound on p_XL) |",
             "|---|---|---|---|---|---|---|"]
    out = {}
    for key in sorted(groups):
        code, n_anc, d, cls, w = key
        if (code, n_anc) not in codes:
            continue
        pts = dict(groups[key])
        if (code, n_anc, d) in zero:
            pts[0.0] = zero[(code, n_anc, d)]
        fs = sorted(pts)
        budget = target - pzl_fn(code, n_anc, d, pz)
        res = []
        for use in ("pL", "hi"):
            if budget <= 0:
                res.append("phase flips alone exceed target")
                continue
            val = None
            for i, f in enumerate(fs):
                if pts[f][use] <= budget:
                    if i == 0:
                        val = f
                    else:
                        # interpolate log p_XL linearly in log(1 - f) (p_XL ~ (1 - f)^k at small 1 - f)
                        f0, f1 = fs[i - 1], f
                        y0, y1 = math.log(max(pts[f0][use], 1e-300)), math.log(max(pts[f1][use], 1e-300))
                        yb = math.log(budget)
                        x0, x1 = math.log(1 - f0 + 1e-4), math.log(1 - f1 + 1e-4)
                        xb = x0 + (x1 - x0) * (y0 - yb) / (y0 - y1) if y0 != y1 else x1
                        val = 1 + 1e-4 - math.exp(xb)
                    break
            if val is None:
                res.append("not reached with f <= 1")
            else:
                j = fs.index(f)
                res.append(f"{val:.3f}" if j == 0 else f"{val:.3f} (between {fs[j - 1]:g} and {f:g})")
        out[f"{code}|a{n_anc}|d{d}|{cls}|w{w}"] = res
        lines.append(f"| {CODE_LABEL[(code, n_anc)]} | {d} | {overhead(code, n_anc, d):.1f} | {cls} | {w or 'exact'} | {res[0]} | {res[1]} |")
    NUMBERS.setdefault("required_f", {})[tag] = out
    open(os.path.join(OUT, f"required_f_{tag}.md"), "w").write("\n".join(lines) + "\n")


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
    # the p_X = 1e-9 estimates themselves, transferred to the validation p_X (intensities scale with p)
    from elevator.strata import pois
    main = {}
    for r in flag_rows(("flag_main",)):
        if r["p_x"] == 1e-9 and r["idle"] == "edge,cnot" and r["r"] == 0:
            main[(r["code"], r["n_anc"], r["d"], r["f"], r["classes"], r["window"])] = r
    lines += ["\n### The p_X = 1e-9 estimates predicting held-out direct samples\n",
              "Stratum failure fractions measured at p_X = 1e-9 (the numbers behind the overheads) with exact "
              "intensities at the held-out p_X; the upper bound adds the truncated strata.\n",
              "| code | p_X | f | flags on | window | direct P_fail [95% CI] | predicted from p_X = 1e-9 [lo, hi] | inside |",
              "|---|---|---|---|---|---|---|---|"]
    ins = tot2 = 0
    for key in sorted(direct):
        code, n_anc, d, px, f, cls_t, w = key
        cls = {1: "idle", 2: "idle+gate", 4: "all"}.get(len(cls_t), "?") if f > 0 else "none"
        r9 = main.get((code, n_anc, d, f, cls, w))
        if r9 is None:
            continue
        U, S = r9["U"] * px / 1e-9, r9["S"] * px / 1e-9
        est = lo = hi = 0.0
        kmax = 0
        for k2, (fa, n) in r9["strata"].items():
            a, b = map(int, k2.split(","))
            kmax = max(kmax, a + b)
            wgt = pois(a, U) * pois(b, S)
            if k2 in r9["exact"]:
                v = r9["exact"][k2]; est += wgt * v; lo += wgt * v; hi += wgt * v
            elif n:
                l, h = wilson(fa, n); est += wgt * fa / n; lo += wgt * l; hi += wgt * h
        tail = 1 - sum(pois(a, U) * pois(t - a, S) for t in range(kmax + 1) for a in range(t + 1))
        hi += max(tail, 0)
        d_ = direct[key]
        P = d_["fails"] / d_["shots"]
        dlo, dhi = wilson(d_["fails"], d_["shots"])
        ok = not (hi < dlo or lo > dhi)
        ins += ok
        tot2 += 1
        lines.append(f"| {CODE_LABEL[(code, n_anc)]} | {px:.0e} | {f} | {cls} | {w or 'exact'} | {P:.3e} [{dlo:.2e}, {dhi:.2e}] | "
                     f"{est:.3e} [{lo:.2e}, {hi:.2e}] | {'yes' if ok else 'NO'} |")
    lines.append(f"\n{ins} of {tot2} held-out direct-sampling points are inside the predicted interval.\n")
    NUMBERS["validation_transfer"] = dict(inside=ins, total=tot2)
    open(os.path.join(OUT, "validation.md"), "w").write("\n".join(lines) + "\n")


def transfer_check_main():
    """d_Z transfer at p_X = 1e-9: prediction from the d_Z = 15 failure fractions vs direct runs at 17, 19."""
    rows = [r for r in flag_rows(("flag_main", "flag_supp", "flag_alt", "flag_ham63"), transfers=False)
            if r["idle"] == "edge,cnot" and r["p_x"] == 1e-9]
    by = defaultdict(dict)
    for r in rows:
        by[(r["code"], r["n_anc"], r["f"], r["classes"], r["window"], r["r"], r.get("mode", "erasure"))][r["d"]] = r
    lines = ["\n## Transfer in d_Z at p_X = 1e-9: prediction from d_Z = 15 vs direct stratified runs\n",
             "| code | flags | d_Z | direct p_XL [95% CI] | from d_Z = 15 [95% CI] | intervals overlap | ratio |",
             "|---|---|---|---|---|---|---|"]
    ok = tot = 0
    for key, byd in sorted(by.items(), key=str):
        if 15 not in byd:
            continue
        for d2 in sorted(byd):
            if d2 == 15:
                continue
            t = transfer_pxl(byd[15], d2)
            if t is None:
                continue
            r = byd[d2]
            agree = not (t[2] < r["lo"] or t[1] > r["hi"])
            ok += agree
            tot += 1
            ratio = (t[0] / r["pL"]) if r["pL"] > 0 and t[0] > 0 else float("nan")
            fl = "none" if key[2] == 0 else f"f={key[2]} {key[3]} w={key[4] or 'exact'}" + (f" r={key[5]:g}" if key[5] else "")
            lines.append(f"| {CODE_LABEL[key[:2]]} | {fl} | {d2} | {r['pL']:.2e} [{r['lo']:.1e}, {r['hi']:.1e}] | "
                         f"{t[0]:.2e} [{t[1]:.1e}, {t[2]:.1e}] | {'yes' if agree else 'NO'} | {ratio:.2f} |")
    lines.append(f"\n{ok} of {tot} direct runs at d_Z = 17, 19 are consistent with the transfer from d_Z = 15.\n")
    NUMBERS["transfer_check_main"] = dict(agree=ok, total=tot)
    open(os.path.join(OUT, "transfer_check.md"), "w").write("\n".join(lines) + "\n")


def assumptions_table(pzl_fn=None, tag="this-work-pZL"):
    """Each assumption of the flag model with its measured effect: p_XL of every main code at d_Z = 15
    (p_X = 1e-9) and the minimum overhead at p_Z = 1e-3, eta = 1e6, 1e-12, for the alternatives tried."""
    pzl_fn = pzl_fn or pzl_model
    dirs = ("flag_main", "flag_supp", "flag_falseflag", "flag_herald", "flag_literal")
    rows = [r for r in flag_rows(dirs) if r["p_x"] == 1e-9]

    def cell(code, d, f, cls, w, rr=0.0, mode="erasure", idle="edge,cnot"):
        c = [r for r in rows if (r["code"], r["n_anc"]) == code and r["d"] == d and r["f"] == f
             and (f == 0 or (r["classes"] == cls and r["window"] == w)) and r["r"] == rr
             and r.get("mode", "erasure") == mode and r["idle"] == idle]
        if not c:
            return None
        return min(c, key=lambda r: r.get("transferred", False))

    def best(f, cls, w, rr=0.0, mode="erasure", idle="edge,cnot"):
        byc = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["f"] == f
               and (f == 0 or (r["classes"] == cls and r["window"] == w)) and r["r"] == rr
               and r.get("mode", "erasure") == mode and r["idle"] == idle}
        b = best_overhead(byc, 1e-3, 1e-12, pzl_fn, "pL", CODES_MAIN)
        return f"{b[0]:.1f} ({CODE_LABEL[(b[1], b[2])]}, d={b[3]})" if b else ("not reached" if byc else "-")

    groups = [
        ("flag classes (which locations raise flags)", [("idle", 0, 0.99), ("idle+gate", 0, 0.99), ("all", 0, 0.99),
                                                         ("idle", 0, 0.9), ("idle+gate", 0, 0.9), ("all", 0, 0.9)], {}),
        ("timing window (ticks; one inner round = 4, one outer round ~600-1100)",
         [("all", w, 0.99) for w in (0, 1, 4, 16, 64, 256, 1024, 4096)] + [("idle", w, 0.99) for w in (0, 64, 4096)], {}),
        ("event model: erasure (X with prob. 1/2) vs heralded X", [("idle", 0, 0.99), ("all", 0, 0.99), ("all", 64, 0.99)],
         {"mode": "herald"}),
        ("false flags per qubit per tick (f = 0.99, flags on all locations, exact / 64 ticks)",
         [("all", 0, 0.99, r) for r in (0.0, 1e-10, 1e-8, 1e-6)] + [("all", 64, 0.99, r) for r in (0.0, 1e-10, 1e-8, 1e-6)], {}),
        ("false flags at the operating point of arXiv:2607.01375 (f = 0.8-0.9, windows 4-16 ticks)",
         [(cls, w, f, r) for cls in ("idle", "all") for f in (0.8,) for w in (4,) for r in (1e-9, 1e-7, 1e-6)], {}),
    ]
    lines = [f"\n## Assumptions of the flag model and their measured effect (phase flips: {tag})\n",
             "p_XL per round per logical qubit at d_Z = 15, p_X = 1e-9 (stratified estimate), and the minimum overhead "
             "at p_Z = 1e-3, eta = 1e6, 1e-12 over [15,9,3], [15,6,5] (1 and 2 ancillas).\n"]
    out = {}
    gkeys = ["classes", "window", "herald", "falseflag", "falseflag_op"]
    for gi, (title, settings, kw) in enumerate(groups):
        g0 = len(lines)
        lines += [f"\n### {title}\n", "| flags on | window | f | false flags | alternative | " +
                  " | ".join(CODE_LABEL[c] for c in CODES_MAIN) + " | minimum overhead |",
                  "|---|---|---|---|---|" + "---|" * len(CODES_MAIN) + "---|"]
        for st in settings:
            cls, w, f = st[:3]
            rr = st[3] if len(st) > 3 else 0.0
            for alt in ([("erasure", None)] + ([(kw["mode"], kw["mode"])] if "mode" in kw else [])):
                mode = alt[0]
                cs = []
                for code in CODES_MAIN:
                    r = cell(code, 15, f, cls, w, rr, mode)
                    cs.append(f"{r['pL']:.2e} [{r['lo']:.1e}, {r['hi']:.1e}]" + (" (transferred)" if r.get("transferred") else "") if r else "-")
                b = best(f, cls, w, rr, mode)
                lines.append(f"| {cls} | {w or 'exact'} | {f} | {rr:g} | {mode} | " + " | ".join(cs) + f" | {b} |")
                out[f"{gkeys[gi]}|{cls}|w{w}|f{f}|r{rr:g}|{mode}"] = b
                r93 = cell(("15_9_3", 1), 15, f, cls, w, rr, mode)
                if r93:
                    out[f"{gkeys[gi]}|{cls}|w{w}|f{f}|r{rr:g}|{mode}|pXL_15_9_3"] = [r93["pL"], r93["lo"], r93["hi"]]
        NUMBERS.setdefault("md", {})[f"assump_{gkeys[gi]}"] = "\n".join(lines[g0 + 1:])
    # noise reading (bit flips only; d_Z = 17 where the literal-reading runs are)
    g0 = len(lines)
    lines += ["\n### idle-noise reading (bit flips at d_Z = 17; the literal reading also raises the phase flips, see REPORT)\n",
              "| flags on | window | f | " + " | ".join(f"{CODE_LABEL[c]} noop / literal" for c in CODES_MAIN) + " |",
              "|---|---|---|" + "---|" * len(CODES_MAIN)]
    for (cls, w, f) in [("none", 0, 0.0), ("idle", 0, 0.99), ("all", 0, 0.9), ("all", 0, 0.99), ("all", 64, 0.99), ("all", 1024, 0.99)]:
        cs = []
        for code in CODES_MAIN:
            a = cell(code, 17, f, cls, w)
            b = cell(code, 17, f, cls, w, idle="edge,cnot,op")
            cs.append((f"{a['pL']:.2e}" if a else "-") + " / " + (f"{b['pL']:.2e}" if b else "-"))
        lines.append(f"| {cls} | {w or 'exact'} | {f} | " + " | ".join(cs) + " |")
        a = cell(("15_9_3", 1), 17, f, cls, w)
        b = cell(("15_9_3", 1), 17, f, cls, w, idle="edge,cnot,op")
        if a and b and a["pL"] > 0:
            out[f"literal|{cls}|w{w}|f{f}|ratio_15_9_3"] = b["pL"] / a["pL"]
    NUMBERS["md"]["assump_literal"] = "\n".join(lines[g0 + 1:])
    NUMBERS["assumptions"] = out
    open(os.path.join(OUT, "assumptions.md"), "w").write("\n".join(lines) + "\n")


HEAD_SETTINGS = [("idle", 0, 0.9), ("idle", 0, 0.99), ("idle", 0, 1.0), ("idle+gate", 0, 0.99), ("all", 0, 0.5),
                 ("all", 0, 0.8), ("all", 0, 0.9), ("all", 0, 0.99), ("all", 0, 1.0), ("all", 1, 0.99), ("all", 64, 0.99),
                 ("all", 1024, 0.99), ("all", 4096, 0.99), ("all", 4096, 1.0), ("all", 4096, 0.9), ("idle", 64, 0.99),
                 ("idle", 4096, 0.99)]
ALT_CODES = [("ham15", 1), ("ham31", 1), ("xham16", 1), ("ham63", 1)]


def headline():
    """Key numbers quoted in FINDINGS / REPORT / COMPLETE (rendered from numbers.json)."""
    H = {}
    cs = OH.candidates(1e-3, 1e6)
    pub = OH.min_overhead(1e-12, cs, "elevator")
    H["published"] = dict(overhead=pub.overhead, code=pub.label, d=pub.d,
                          rot=OH.min_overhead(1e-12, OH.candidates(1e-3, 1e7), "rot").overhead,
                          xzzx=OH.min_overhead(1e-12, OH.candidates(1e-3, 1e7), "xzzx").overhead)
    rows = [r for r in flag_rows(("flag_main", "flag_supp", "flag_alt", "flag_ham63")) if r["idle"] == "edge,cnot"
            and r["p_x"] == 1e-9 and r["r"] == 0 and r.get("mode", "erasure") == "erasure"]

    def byc(cls, w, f, codes):
        out = {(r["code"], r["n_anc"], r["d"]): r for r in rows if (r["code"], r["n_anc"]) in codes and r["f"] == f
               and (f == 0 or (r["classes"] == cls and r["window"] == w))}
        if f > 0:          # flags may always be ignored: fall back to the flag-free rate
            for r in rows:
                if (r["code"], r["n_anc"]) in codes and r["f"] == 0:
                    out.setdefault((r["code"], r["n_anc"], r["d"]), r)
        return out

    for tag, fn in (("paper-pZL", pzl_paper), ("this-work-pZL", pzl_model)):
        h = {}
        for (cls, w, f) in [("none", 0, 0.0)] + HEAD_SETTINGS:
            key = f"{cls}|w{w}|f{f}"
            ent = {}
            for lab, codes in (("main", CODES_MAIN), ("all_codes", CODES_MAIN + ALT_CODES)):
                b = best_overhead(byc(cls, w, f, codes), 1e-3, 1e-12, fn, "pL", codes)
                bh = best_overhead(byc(cls, w, f, codes), 1e-3, 1e-12, fn, "hi", codes)
                ent[lab] = (dict(overhead=b[0], code=CODE_LABEL[(b[1], b[2])], d=b[3], pXL=b[4], pL=b[5]) if b else None)
                ent[lab + "_cons"] = (dict(overhead=bh[0], code=CODE_LABEL[(bh[1], bh[2])], d=bh[3]) if bh else None)
            for code in CODES_MAIN + ALT_CODES:
                b = best_overhead(byc(cls, w, f, [code]), 1e-3, 1e-12, fn, "pL", [code])
                ent[CODE_LABEL[code]] = (dict(overhead=b[0], d=b[3], pXL=b[4]) if b else None)
            h[key] = ent
        H[tag] = h
        ff = h["none|w0|f0.0"]["main"]
        H[tag + ":flagfree"] = ff
        best_flag = min((v["main"]["overhead"] for k, v in h.items() if v["main"] and k != "none|w0|f0.0"), default=None)
        H[tag + ":best_flagged_main"] = best_flag
        H[tag + ":best_flagged_all_codes"] = min((v["all_codes"]["overhead"] for k, v in h.items() if v["all_codes"]), default=None)
    # simulated d_Z = 15 bit-flip rates of [15,9,3] for the quoted settings (with 95% CI)
    sim = {}
    for (cls, w, f) in [("none", 0, 0.0)] + HEAD_SETTINGS:
        c = [r for r in rows if (r["code"], r["n_anc"]) == ("15_9_3", 1) and r["d"] == 15 and not r.get("transferred")
             and r["f"] == f and (f == 0 or (r["classes"] == cls and r["window"] == w))]
        if c:
            r = c[0]
            sim[f"{cls}|w{w}|f{f}"] = dict(pXL=r["pL"], lo=r["lo"], hi=r["hi"])
    H["sim_15_9_3_d15"] = sim
    NUMBERS["headline"] = H
    lines = ["\n## Headline numbers (p_Z = 1e-3, eta = 1e6, 1e-12 per round per logical qubit)\n",
             f"Published (paper's fits): {H['published']['overhead']:.1f} ({H['published']['code']}, d_Z = {H['published']['d']}).\n",
             "| flags | window | f | min overhead, main codes (paper pZL) | (this work pZL) | incl. Hamming codes (paper pZL) | (this work pZL) |",
             "|---|---|---|---|---|---|---|"]
    for (cls, w, f) in [("none", 0, 0.0)] + HEAD_SETTINGS:
        key = f"{cls}|w{w}|f{f}"
        cells = []
        for lab in ("main", "all_codes"):
            for tag in ("paper-pZL", "this-work-pZL"):
                e = H[tag][key][lab]
                cells.append(f"{e['overhead']:.1f} ({e['code']}, {e['d']})" if e else "not reached / not simulated")
        lines.append(f"| {cls} | {w or 'exact'} | {f} | " + " | ".join(cells) + " |")
    open(os.path.join(OUT, "headline.md"), "w").write("\n".join(lines) + "\n")


def aux_checks():
    """Known answers, decoder-optimality and decoder-variant checks, exact perfect-flag strata: summaries
    for the documents (from results/*.json written by the local check scripts)."""
    def load(name):
        fn = os.path.join(ROOT, "results", name)
        return json.load(open(fn)) if os.path.exists(fn) else None
    A = {}
    ka = load("known_answers.json")
    if ka:
        out = {}
        for k, v in ka.items():
            if not isinstance(v, dict):
                continue
            if k.startswith("KA1_code_capacity") or k.startswith("KA2_code_capacity"):
                sizes = {int(s): x for s, x in v.items()}
                dmax = max(sizes)
                out[k] = dict(max_size=dmax, patterns_below_d=sum(x["patterns"] for s, x in sizes.items() if s < dmax),
                              failures_below_d=sum(x["failures"] for s, x in sizes.items() if s < dmax),
                              patterns_at_d=sizes[dmax]["patterns"], failures_at_d=sizes[dmax]["failures"],
                              sets_with_failure_at_d=sizes[dmax].get("sets_with_failure"))
            elif k.startswith("KA2_circuit"):
                out[k] = dict(sets=sum(x["sets"] for x in v.values()), patterns=sum(x.get("patterns", 0) for x in v.values()),
                              failures=sum(x["failures"] for x in v.values()))
            elif k.startswith("KA1_circuit"):
                out[k] = {s: dict(samples=x.get("samples"), failures=x["failures"]) for s, x in v.items()}
        A["known_answers"] = out
    do = load("decoder_optimality.json")
    if do:
        A["decoder_optimality"] = dict(cases=len(do), n=sum(r["n"] for r in do), ml=sum(r["ml"] for r in do),
                                       mle=sum(r["mle"] for r in do), bposd=sum(r["bposd"] for r in do),
                                       disagree=sum(r["disagree_ml_mle"] for r in do), rows=do)
    dw = load("decoder_optimality_windows.json")
    if dw:
        A["decoder_optimality_windows"] = dict(cases=len(dw), n=sum(r["n"] for r in dw), ml=sum(r["ml"] for r in dw),
                                               mle=sum(r["mle"] for r in dw), disagree=sum(r["disagree"] for r in dw),
                                               windows=sorted({r["window"] for r in dw}), rows=dw)
    dv = load("decoder_variants_flagfree.json")
    if dv:
        A["decoder_variants_flagfree"] = dv
    pf = load("perfect_flags_exact.json")
    if pf:
        A["perfect_flags_exact"] = {f"{r['code']}|a{r['n_anc']}|d{r['d']}": {b: v["F"] for b, v in r["F"].items()} for r in pf}
    cs = class_sums_table()
    A["class_share"] = {}
    for key in ("15_9_3:a1:d15", "15_6_5:a1:d15", "15_6_5:a2:d15"):
        if key in cs:
            sm = cs[key]["sums"]
            tot = sum(v[0] for v in sm.values())
            A["class_share"][key] = {c: v[0] / tot for c, v in sm.items()}
    se = load("sensitivity_15_9_3.json")
    if se:
        A["sensitivity_15_9_3"] = se
        nat = next(r["ratio"] for r in se if r["label"] == "natural")
        orders = [r["ratio"] for r in se if r["label"] in ("reversed", "permutation 1", "permutation 2")]
        rounds = [r["ratio"] for r in se if "outer rounds" in r["label"]]
        mle = [r["ratio"] for r in se if r["decoder"] == "mle"]
        A["sensitivity_summary"] = dict(order_dev=max(abs(x - nat) / nat for x in orders),
                                        rounds_dev=max(abs(x - nat) / nat for x in rounds),
                                        mle_min=min(mle), mle_max=max(mle))
    zv = load(os.path.join("variants", "z_variants_v1.json"))
    if zv:
        def rng(code, var):
            xs = [r["ratio"] for r in zv if r["code"] == code and r["variant"] == var]
            return [min(xs), max(xs)] if xs else None
        A["z_variants"] = {f"{c}|{v}": rng(c, v) for c in ("15_9_3", "15_6_5")
                           for v in ("full/all-idle", "full/no-op-idle", "full/cnot-idle-only", "span/all-idle")}
    NUMBERS["checks"] = A


def strata_split(row, d_target=None, p_x=None):
    """Split p_XL of a row (optionally transferred) into the part from strata with only flagged events
    (a = 0: limited by the code distance) and the part with unflagged errors (a >= 1: limited by the
    flag efficiency).  Central values, per round per logical qubit."""
    from elevator.strata import pois
    if d_target is None or (d_target == row["d"] and (p_x is None or p_x == row["p_x"])):
        U, S, R, k = row["U"], row["S"], row["rounds"], row["k"]
    else:
        sums = class_sums_for(row["code"], row["n_anc"], d_target, row.get("n_outer", 5))
        p_x = row["p_x"] if p_x is None else p_x
        eff = {c: (row["f"] if c in CLASSES_OF[row["classes"]] else 0.0) for c in CLASS_LIST}
        U = p_x * sum((1 - eff[c]) * sums["sums"][c][0] for c in CLASS_LIST)
        S = p_x * sum(2 * eff[c] * sums["sums"][c][1] for c in CLASS_LIST)
        R, k = sums["rounds"], sums["k"]
    parts = {"flagged_only": 0.0, "with_unflagged": 0.0}
    keys = set(row["strata"]) | set(row["exact"])
    for key in keys:
        a, b = map(int, key.split(","))
        w = pois(a, U) * pois(b, S)
        if key in row["exact"]:
            v = row["exact"][key]
        else:
            f, n = row["strata"][key]
            v = f / n if n else 0.0
        parts["flagged_only" if a == 0 else "with_unflagged"] += w * v / (R * k)
    return parts


def limits_table():
    """What limits each result (evidence for 'every remaining limit belongs to the problem')."""
    L = {}
    lines = ["\n## Limits\n"]
    m = PHASE["rep"]
    # absolute floor of the construction: one repetition-code block per logical qubit (k/n -> 1, no
    # ancilla, ML decoding of the block): d_Z >= d_rep, overhead >= 2 d_rep - 1
    for pz, tgt in ((1e-3, 1e-12), (1e-2, 1e-9), (1e-2, 1e-12)):
        d_rep = next((d for d in range(3, 400, 2) if float(m.predict(d, pz)) <= tgt), None)
        L[f"absolute_floor|{pz:g}|{tgt:g}"] = dict(d_rep=d_rep, overhead=(2 * d_rep - 1) if d_rep else None)
    lines += ["### Absolute phase-flip floor of the construction\n",
              "Any Elevator-type memory spends at least one repetition-code block of distance d_Z per logical qubit; "
              "its phase flips alone reach the target only from d_rep (this work's repetition-code model), so the "
              "overhead is at least 2 d_rep - 1 even for k/n -> 1 and without ancilla noise.\n",
              "| p_Z | target | d_rep | overhead floor |", "|---|---|---|---|"]
    for k_, v in L.items():
        if k_.startswith("absolute_floor"):
            _, pz, tgt = k_.split("|")
            lines.append(f"| {pz} | {tgt} | {v['d_rep']} | {v['overhead']} |")
    # p_Z = 1e-3: per code, is the flagged overhead at its phase-flip floor?
    rows = [r for r in flag_rows(("flag_main", "flag_supp", "flag_alt", "flag_ham63")) if r["idle"] == "edge,cnot"
            and r["p_x"] == 1e-9 and r["r"] == 0 and r.get("mode", "erasure") == "erasure"]
    lines += ["\n### p_Z = 1e-3, eta = 1e6, 1e-12: is each code at its phase-flip floor?\n",
              "d_floor: smallest d_Z whose phase flips alone meet the target (flags cannot lower it).  At d_floor - 2 the "
              "phase flips alone exceed the target; at d_floor the lowest bit-flip rate over the flag settings is shown "
              "against the phase-flip rate.\n",
              "| code | phase model | d_floor | overhead | p_ZL(d_floor - 2) | p_ZL(d_floor) | lowest p_XL(d_floor) [95% upper] | setting |",
              "|---|---|---|---|---|---|---|---|"]
    for code in CODES_MAIN + ALT_CODES:
        for tag, fn in (("this-work-pZL", pzl_model), ("paper-pZL", pzl_paper)):
            try:
                dfl = next(d for d in range(3, 200, 2) if fn(code[0], code[1], d, 1e-3) <= 1e-12)
            except (StopIteration, KeyError):
                continue
            cand = [r for r in rows if (r["code"], r["n_anc"]) == code and r["d"] == dfl]
            if not cand:
                continue
            best = min(cand, key=lambda r: r["hi"])
            st = f"f={best['f']} {best['classes']} w={best['window'] or 'exact'}" + (" (transferred)" if best.get("transferred") else "")
            L[f"p1e-3|{CODE_LABEL[code]}|{tag}"] = dict(d_floor=dfl, overhead=overhead(code[0], code[1], dfl),
                                                       pZL_below=fn(code[0], code[1], dfl - 2, 1e-3), pZL=fn(code[0], code[1], dfl, 1e-3),
                                                       pXL=best["pL"], pXL_hi=best["hi"], setting=st)
            lines.append(f"| {CODE_LABEL[code]} | {tag} | {dfl} | {overhead(code[0], code[1], dfl):.1f} | "
                         f"{fn(code[0], code[1], dfl - 2, 1e-3):.2e} | {fn(code[0], code[1], dfl, 1e-3):.2e} | "
                         f"{best['pL']:.2e} [{best['hi']:.2e}] | {st} |")
    # p_Z = 1e-2 floors: what the remaining p_L is made of
    lines += ["\n### p_Z = 1e-2, eta = 1e6: composition of the lowest reachable p_L\n",
              "At each floor: phase flips (cannot be flagged), bit flips from sets of flagged events only (need >= d "
              "events forming a logical: the code's distance) and bit flips involving unflagged errors (fraction 1 - f).\n",
              "| code | flags | phase model | floor p_L | d_Z | p_ZL share | flagged-only share | unflagged share |",
              "|---|---|---|---|---|---|---|---|"]
    prow = [r for r in flag_rows(("flag_pz1e2",), transfers=False) if r["idle"] == "edge,cnot" and r["p_x"] == 1e-8]
    refs = defaultdict(dict)
    for r in prow:
        refs[(r["code"], r["n_anc"], r["f"], r["classes"], r["window"])][r["d"]] = r
    for tag, fn in (("this-work-pZL", pzl_model), ("paper-pZL", pzl_paper)):
        for key, byd in sorted(refs.items(), key=str):
            best = None
            for d in range(15, 302, 2):
                ref = byd[min(byd, key=lambda x: abs(x - d))]
                t = transfer_pxl(ref, d)
                if t is None:
                    continue
                tot = t[0] + fn(key[0], key[1], d, 1e-2)
                if best is None or tot < best[0]:
                    best = (tot, d, ref, t[0])
            if best is None:
                continue
            tot, d, ref, pxl = best
            sp = strata_split(ref, d_target=d)
            pzl = fn(key[0], key[1], d, 1e-2)
            fo, wu = sp["flagged_only"], sp["with_unflagged"]
            fl = "none" if key[2] == 0 else f"f={key[2]} {key[3]} w={key[4] or 'exact'}"
            L[f"p1e-2|{CODE_LABEL[key[:2]]}|{fl}|{tag}"] = dict(pL=tot, d=d, pZL=pzl, flagged_only=fo, with_unflagged=wu,
                                                               overhead=overhead(key[0], key[1], d),
                                                               reach=next((overhead(key[0], key[1], dd) for dd in range(15, 302, 2)
                                                                           if (transfer_pxl(byd[min(byd, key=lambda x: abs(x - dd))], dd) or [1])[0]
                                                                           + fn(key[0], key[1], dd, 1e-2) <= 1e-12), None))
            lines.append(f"| {CODE_LABEL[key[:2]]} | {fl} | {tag} | {tot:.2e} | {d} | {pzl / tot:.2f} | "
                         f"{fo / tot:.2f} | {wu / tot:.2f} |")
    NUMBERS["limits"] = L
    open(os.path.join(OUT, "limits.md"), "w").write("\n".join(lines) + "\n")
    # compact p_Z = 1e-2 table for the documents
    md = ["| code | flags | lowest p_L, paper pZL (d_Z, overhead) | this-work pZL (d_Z, overhead) | 1e-12 reached at overhead (paper / this work) | floor made of (this work: phase / flagged-only / unflagged) |",
          "|---|---|---|---|---|---|"]
    order = ["none", "f=0.9 idle w=exact", "f=0.99 idle w=exact", "f=0.9 all w=exact", "f=0.99 idle+gate w=exact",
             "f=0.99 all w=exact", "f=0.99 all w=64", "f=0.99 all w=1024", "f=1.0 all w=exact"]
    for code in ["[15,9,3]", "[15,6,5]", "[15,6,5] 2 anc", "Hamming [15,11,3]"]:
        for fl in order:
            a = L.get(f"p1e-2|{code}|{fl}|paper-pZL")
            b = L.get(f"p1e-2|{code}|{fl}|this-work-pZL")
            if not a or not b:
                continue
            ra = f"{a['reach']:.0f}" if a.get("reach") else "no"
            rb = f"{b['reach']:.0f}" if b.get("reach") else "no"
            ext = lambda x: " (extrap.)" if x["d"] > 69 else ""
            md.append(f"| {code} | {fl} | {a['pL']:.1e} ({a['d']}, {a['overhead']:.0f}){ext(a)} | {b['pL']:.1e} ({b['d']}, {b['overhead']:.0f}){ext(b)} | "
                      f"{ra} / {rb} | {b['pZL'] / b['pL']:.2f} / {b['flagged_only'] / b['pL']:.2f} / {b['with_unflagged'] / b['pL']:.2f} |")
    NUMBERS.setdefault("md", {})["pz1e2_table"] = "\n".join(md)


def literal_reading():
    """Sensitivity to the unstated idle-noise placement (literal reading: idle noise on every waiting block
    during logical-operation ticks).  Phase flips: the isolated repetition code with the extra idle ticks
    (results/phase_rep_literal) against the noop one; bit flips: flagged runs at d_Z = 17 (assumptions.md).
    The literal phase-flip floor uses the literal repetition-code model in the two-component model with
    the noop a, g, kappa (an approximation, labelled)."""
    from elevator.phasemodel import RepModel, load_rep, sweep_fraction
    d_lit = os.path.join(ROOT, "results", "phase_rep_literal")
    if not os.path.isdir(d_lit) or "two" not in PHASE:
        return
    rows = load_rep(d_lit)
    if len(rows) < 4:
        return
    ml = RepModel(rows)
    m = PHASE["rep"]
    out = {"ratio": {}}
    lines = ["\n## Literal idle-noise reading: phase flips\n",
             "Isolated repetition code with the extra idle ticks of the literal reading (2.73 per round on average) "
             "against the noop reading, per round:\n", "| p_Z | d_Z | literal | noop (model) | ratio |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["p"], r["d"])):
        pn = float(m.predict(r["d"], r["p"]))
        out["ratio"][f"{r['p']:g}|{r['d']}"] = r["y"] / pn
        lines.append(f"| {r['p']:.1e} | {r['d']} | {r['y']:.2e} | {pn:.2e} | {r['y'] / pn:.2f} |")
    th, _, _ = PHASE["two"]
    a, g, kap = np.exp(th)

    def pzl_lit(code, n_anc, d, pz):
        n, k = OH.ELEVATOR_NK[code]
        return float(n * a * ml.predict(d, pz) + n_anc * g * sweep_fraction(n, d) * ml.predict(d, kap * pz)) / k

    lines += ["\nPhase-flip floor at p_Z = 1e-3, 1e-12 under the literal reading (two-component model with the "
              "literal repetition code; approximation):\n", "| code | d_Z noop | d_Z literal | overhead literal |", "|---|---|---|---|"]
    for code in CODES_MAIN:
        dn = next((d for d in range(3, 99, 2) if pzl_model(code[0], code[1], d, 1e-3) <= 1e-12), None)
        try:
            dl = next((d for d in range(3, 99, 2) if pzl_lit(code[0], code[1], d, 1e-3) <= 1e-12), None)
        except Exception:
            dl = None
        out[f"floor|{CODE_LABEL[code]}"] = dict(d_noop=dn, d_literal=dl, overhead_literal=overhead(code[0], code[1], dl) if dl else None)
        lines.append(f"| {CODE_LABEL[code]} | {dn} | {dl} | {overhead(code[0], code[1], dl):.1f} |" if dl else f"| {CODE_LABEL[code]} | {dn} | - | - |")
    NUMBERS["literal"] = out
    open(os.path.join(OUT, "literal_reading.md"), "w").write("\n".join(lines) + "\n")


def schedule_comparison():
    """Flag-free Z memory under the full-sweep and the shortest-path ('local') ancilla paths, block-level
    model, BP+OSD, against the paper's fits at its sampled points (results/sched_local)."""
    import glob as _g
    from elevator.decode import wilson
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from summarize_repro import fit_z
    rows = []
    for fn in _g.glob(os.path.join(ROOT, "results", "sched_local", "*.json")):
        st = json.load(open(fn))
        sp = st["spec"]
        if not st.get("shots"):
            continue
        R, k = st["rounds"], st["k"]
        conv = lambda x: 1 - (1 - x) ** (1 / (R * k))
        lo, hi = wilson(st["fails"], st["shots"])
        pl = conv(st["fails"] / st["shots"])
        fit = fit_z(sp["code"], sp["n_anc"], sp["d"], sp["p_x"])
        rows.append(dict(code=sp["code"], n_anc=sp["n_anc"], d=sp["d"], p=sp["p_x"], mode=sp["mode"], fails=st["fails"],
                         shots=st["shots"], pL=pl, lo=conv(lo), hi=conv(hi), fit=fit, ratio=pl / fit,
                         rounds_per_outer=R / sp["n_outer"]))
    if not rows:
        return
    rows.sort(key=lambda r: (r["code"], r["n_anc"], r["d"], r["p"], r["mode"]))
    lines = ["\n## Ancilla path: full sweep vs shortest path (flag-free Z memory, BP+OSD, block level)\n",
             "| code | anc | d_Z | p_X | path | rounds per outer round | fails/shots | p_XL [95% CI] | fit | ratio |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    summ = defaultdict(list)
    for r in rows:
        lines.append(f"| {r['code']} | {r['n_anc']} | {r['d']} | {r['p']:.0e} | {r['mode']} | {r['rounds_per_outer']:.0f} | "
                     f"{r['fails']}/{r['shots']} | {r['pL']:.2e} [{r['lo']:.1e}, {r['hi']:.1e}] | {r['fit']:.2e} | {r['ratio']:.2f} |")
        summ[f"{r['code']}|a{r['n_anc']}|{r['mode']}"].append(r["ratio"])
    NUMBERS["schedule_comparison"] = {k: dict(min=min(v), max=max(v), n=len(v)) for k, v in summ.items()}
    open(os.path.join(OUT, "schedule_comparison.md"), "w").write("\n".join(lines) + "\n")


def counting_convention():
    """'Per logical qubit': P_any/(R k) (this work) vs the per-qubit marginal sum_i P_i/(R k).  Measured
    multiplicities (results/counting_convention.json), the X-memory reproduction in the marginal
    convention, and the headline overheads with every rate in the marginal convention."""
    fn = os.path.join(ROOT, "results", "counting_convention.json")
    if not os.path.exists(fn) or "two" not in PHASE:
        return
    cc = json.load(open(fn))
    mX = defaultdict(list)
    mZ = defaultdict(list)
    for r in cc:
        if r["memory"] == "X":
            mX[r["code"]].append(r["mult"])
        elif r.get("f", 0) == 0:
            mZ[(r["code"], r["n_anc"])].append(r["mult"])
    mX = {c: float(np.mean(v)) for c, v in mX.items()}
    mZ = {c: float(np.mean(v)) for c, v in mZ.items()}
    C = dict(rows=cc, mX=mX, mZ={f"{c[0]}|a{c[1]}": v for c, v in mZ.items()})
    xr = [r for r in cc if r["memory"] == "X"]
    C["x_ratio_sum"] = [min(r["ratio_sum"] for r in xr), max(r["ratio_sum"] for r in xr)] if xr else None
    # X-memory reproduction rows in the marginal convention (multiplicity of [15,9,3] applied)
    rep = NUMBERS.get("repro", {})
    k = "X:15_9_3:a1:full/noop bplsd-minsum"
    if k in rep and "15_9_3" in mX:
        C["x_repro_marginal"] = [rep[k]["ratio_min"] * mX["15_9_3"], rep[k]["ratio_max"] * mX["15_9_3"]]
    # headline overheads, every rate in the marginal convention (main codes with measured multiplicities)
    rows = [r for r in flag_rows(("flag_main", "flag_supp")) if r["idle"] == "edge,cnot" and r["p_x"] == 1e-9
            and r["r"] == 0 and r.get("mode", "erasure") == "erasure"]
    out = {}
    for (cls, w, f) in [("none", 0, 0.0), ("idle", 0, 0.99), ("idle", 0, 1.0), ("all", 0, 0.8), ("all", 0, 0.9),
                        ("all", 0, 0.99), ("all", 4096, 0.99)]:
        best = None
        for r in rows:
            code = (r["code"], r["n_anc"])
            if code not in mZ or r["code"] not in mX or r["f"] != f or (f > 0 and (r["classes"] != cls or r["window"] != w)):
                continue
            tot = r["pL"] * mZ[code] + pzl_model(r["code"], r["n_anc"], r["d"], 1e-3) * mX[r["code"]]
            if tot <= 1e-12:
                oh = overhead(r["code"], r["n_anc"], r["d"])
                if best is None or oh < best[0]:
                    best = (oh, CODE_LABEL[code], r["d"])
        out[f"{cls}|w{w}|f{f}"] = dict(overhead=best[0], code=best[1], d=best[2]) if best else None
    C["headline_marginal"] = out
    NUMBERS["convention"] = C


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


# ------------------------------------------------------------------ 6. p_Z = 1e-2: floors
def pz1e2(pzl_fn, tag, codes=CODES_MAIN + [("ham15", 1)]):
    rows = [r for r in flag_rows(("flag_pz1e2",), transfers=False) if r["idle"] == "edge,cnot" and r["p_x"] == 1e-8]
    if not rows:
        return
    refs = defaultdict(dict)
    for r in rows:
        refs[(r["code"], r["n_anc"], r["f"], r["classes"], r["window"])][r["d"]] = r
    lines = [f"\n## p_Z = 1e-2, eta = 1e6 (p_X = 1e-8): lowest reachable logical error rate (phase flips: {tag})\n",
             "Bit flips at d_Z other than the simulated 17/25/33 use the stratum failure fractions of the nearest "
             "simulated d_Z with exact fault intensities at the new d_Z (transfer; checked below).\n",
             "### Transfer check (prediction from d_Z = 17 vs direct stratified run)\n",
             "| code | flags | d_Z | direct p_XL [95% CI] | transferred from 17 [95% CI] |", "|---|---|---|---|---|"]
    checks = []
    for key, byd in sorted(refs.items()):
        if 17 in byd:
            for dd in (25, 33):
                if dd in byd:
                    t = transfer_pxl(byd[17], dd)
                    r = byd[dd]
                    if t is None:
                        continue
                    ok = not (t[2] < r["lo"] or t[1] > r["hi"])
                    checks.append(ok)
                    lines.append(f"| {CODE_LABEL[key[:2]]} | f={key[2]} {key[3]} w={key[4] or 'exact'} | {dd} | "
                                 f"{r['pL']:.2e} [{r['lo']:.2e}, {r['hi']:.2e}] | {t[0]:.2e} [{t[1]:.2e}, {t[2]:.2e}] {'' if ok else '(outside)'} |")
    NUMBERS[f"pz1e2_transfer_checks"] = dict(agree=int(sum(checks)), total=len(checks))
    lines += ["\n### Floor per code and flag setting (d_Z <= 301) and overhead to reach given rates\n",
              "Phase flips beyond d_Z ~ 70 (repetition code sampled to d_Z = 69 at p_Z >= 1.25e-2, elevator X memory "
              "to d_Z = 29 at p_Z = 1e-2) are extrapolations of the phase-flip model; floors there are marked '(extrap.)'.\n",
              "| code | flags | lowest p_L | at d_Z | overhead | p_XL there | p_ZL there | overhead for 1e-9 | 1e-10 | 1e-11 | 1e-12 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    out = {}
    for key, byd in sorted(refs.items()):
        if key[:2] not in codes:
            continue
        best = None
        reach = {}
        for d in range(15, 302, 2):
            ref_d = min(byd, key=lambda x: abs(x - d))
            t = transfer_pxl(byd[ref_d], d)
            if t is None:
                continue
            pzl = pzl_fn(key[0], key[1], d, 1e-2)
            tot = t[0] + pzl
            if best is None or tot < best[0]:
                best = (tot, d, overhead(key[0], key[1], d), t[0], pzl)
            for tg in (1e-9, 1e-10, 1e-11, 1e-12):
                if tot <= tg and tg not in reach:
                    reach[tg] = overhead(key[0], key[1], d)
        if best:
            out[key] = best + (reach,)
            rc = " | ".join(f"{reach[tg]:.1f}" if tg in reach else "-" for tg in (1e-9, 1e-10, 1e-11, 1e-12))
            lines.append(f"| {CODE_LABEL[key[:2]]} | f={key[2]} {key[3]} w={key[4] or 'exact'} | {best[0]:.2e}"
                         f"{' (extrap.)' if best[1] > 69 else ''} | {best[1]} | "
                         f"{best[2]:.1f} | {best[3]:.2e} | {best[4]:.2e} | {rc} |")
    NUMBERS.setdefault("pz1e2", {})[tag] = {f"{k[0]}|a{k[1]}|f{k[2]}|{k[3]}|w{k[4]}": dict(pL=v[0], d=v[1], overhead=v[2],
                                              reach={f"{tg:g}": oh for tg, oh in v[5].items()}) for k, v in out.items()}
    open(os.path.join(OUT, f"pz1e2_{tag}.md"), "w").write("\n".join(lines) + "\n")
    return out


# ------------------------------------------------------------------ 7. frontier
CLASS_RANK = {"none": 0, "idle": 1, "idle+gate": 2, "all": 3}


def frontier(pzl_fn, tag):
    """Frontier at p_Z = 1e-3, eta = 1e6 over every simulated code (main codes, Hamming alternatives),
    flag setting and noise alternative (exact MLE decoder, shown ML-optimal at the leading order).

    (a) requirements frontier: points with p_L <= 1e-12 non-dominated in (overhead, flag efficiency
        f, flag classes needed, timing window allowed, false-flag rate tolerated); p_L reported.
    (b) full frontier: non-dominated in (overhead, p_L, f, window) without a target."""
    rows = [r for r in flag_rows(("flag_main", "flag_alt", "flag_supp", "flag_falseflag", "flag_ham63"))
            if r["idle"] == "edge,cnot" and r["p_x"] == 1e-9 and r.get("mode", "erasure") == "erasure"]
    pts = []
    for r in rows:
        pl = r["pL"] + pzl_fn(r["code"], r["n_anc"], r["d"], 1e-3)
        pts.append(dict(code=r["code"], n_anc=r["n_anc"], d=r["d"], overhead=overhead(r["code"], r["n_anc"], r["d"]),
                        pL=pl, pXL_hi=r["hi"], f=r["f"], window=(10 ** 9 if r["f"] == 0 else r["window"]),
                        cls=CLASS_RANK[r["classes"]], classes=r["classes"], r=r["r"], transferred=bool(r.get("transferred"))))

    def dom_req(a, b):
        ge = (a["overhead"] <= b["overhead"] and a["f"] <= b["f"] and a["cls"] <= b["cls"]
              and a["window"] >= b["window"] and a["r"] >= b["r"])
        gt = (a["overhead"] < b["overhead"] or a["f"] < b["f"] or a["cls"] < b["cls"]
              or a["window"] > b["window"] or a["r"] > b["r"])
        return ge and gt

    for p in pts:
        p["pL_cons"] = p["pXL_hi"] + (p["pL"] - (p["pL"] - pzl_fn(p["code"], p["n_anc"], p["d"], 1e-3)))
    for p in pts:
        p["pL_cons"] = p["pXL_hi"] + pzl_fn(p["code"], p["n_anc"], p["d"], 1e-3)
    ok = [p for p in pts if p["pL_cons"] <= 1e-12]          # conservative: 95% upper bound of p_XL
    req = [p for p in ok if not any(dom_req(q, p) for q in ok)]
    # one line per distinct requirement vector (the lowest p_L among equals)
    uniq = {}
    for p in req:
        k = (round(p["overhead"], 3), p["f"], p["cls"], p["window"], p["r"])
        if k not in uniq or p["pL"] < uniq[k]["pL"]:
            uniq[k] = p
    req = sorted(uniq.values(), key=lambda p: (p["overhead"], p["f"], p["cls"], -p["window"]))

    # (b) per code and d_Z: the lowest p_L reached by any flag setting, and the least demanding settings
    #     that come within a factor 1.5 of it (smallest f; then the coarsest window and fewest classes)
    by = defaultdict(list)
    for p in pts:
        if p["r"] == 0:
            by[(p["code"], p["n_anc"], p["d"])].append(p)
    full = []
    for key, ps in by.items():
        best = min(ps, key=lambda p: p["pL"])
        near = [p for p in ps if p["pL"] <= 1.5 * best["pL"]]
        easy = min(near, key=lambda p: (p["f"], p["cls"], -p["window"]))
        coarse = max([p for p in near if p["f"] == easy["f"]], key=lambda p: (p["window"], -p["cls"]))
        noflag = [p for p in ps if p["f"] == 0]
        full.append(dict(code=key[0], n_anc=key[1], d=key[2], overhead=best["overhead"], pL_best=best["pL"],
                         pZL=pzl_fn(key[0], key[1], key[2], 1e-3), f=easy["f"], classes=easy["classes"],
                         window=coarse["window"], pL_noflags=(noflag[0]["pL"] if noflag else None)))
    full.sort(key=lambda p: (p["overhead"], p["pL_best"]))

    def wtxt(w):
        return "any (no flags)" if w == 10 ** 9 else ("exact" if w == 0 else str(w))

    lines = [f"\n## Frontier at p_Z = 1e-3, eta = 1e6 (phase flips: {tag})\n",
             "All simulated codes ([15,9,3], [15,6,5] with 1 and 2 ancillas, Hamming [15,11,3], [31,26,3], [63,57,3], "
             "extended Hamming [16,11,4]) and flag settings; decoder: exclusive-window MLE (ML at the leading order, "
             "results/decoder_optimality*.json; BP+OSD is worse on the same configurations).  p_L = p_XL + p_ZL.\n",
             "### (a) Requirements frontier for p_L <= 1e-12\n",
             "Non-dominated in overhead, flag efficiency f, flag classes needed, timing window allowed and false-flag "
             "rate tolerated, among the settings that reach 1e-12 with the 95% upper bound of p_XL (conservative).\n",
             "| overhead | code | d_Z | p_L | p_XL 95% upper | f | flags on | window (ticks) | false flags tolerated |",
             "|---|---|---|---|---|---|---|---|---|"]
    for p in req:
        lines.append(f"| {p['overhead']:.1f} | {CODE_LABEL[(p['code'], p['n_anc'])]} | {p['d']} | {p['pL']:.2e} | {p['pXL_hi']:.1e} | "
                     f"{p['f']} | {p['classes']} | {wtxt(p['window'])} | {p['r']:g} |" + (" (transferred)" if p["transferred"] else ""))
    lines += ["\n### (b) Lowest p_L per code and d_Z, and what it takes\n",
              "For every simulated (or transferred) code and d_Z: the lowest p_L of any flag setting, the phase-flip part "
              "of it (flags cannot lower it), the flag-free p_L, and the least demanding setting within a factor 1.5 of "
              "the lowest (smallest f, then fewest flag classes, then coarsest window).\n",
              "| overhead | code | d_Z | lowest p_L | of which p_ZL | p_L without flags | f needed | flags on | coarsest window |",
              "|---|---|---|---|---|---|---|---|---|"]
    for p in full:
        nf = f"{p['pL_noflags']:.2e}" if p["pL_noflags"] is not None else "-"
        lines.append(f"| {p['overhead']:.1f} | {CODE_LABEL[(p['code'], p['n_anc'])]} | {p['d']} | {p['pL_best']:.2e} | {p['pZL']:.2e} | "
                     f"{nf} | {p['f']} | {p['classes']} | {wtxt(p['window'])} |")
    open(os.path.join(OUT, f"frontier_{tag}.md"), "w").write("\n".join(lines) + "\n")
    NUMBERS.setdefault("frontier", {})[tag] = dict(requirements=req, per_code=full)
    md = ["| overhead | code | d_Z | p_L | f needed | flags on | coarsest window | false flags tolerated |",
          "|---|---|---|---|---|---|---|---|"]
    for p in req:
        md.append(f"| {p['overhead']:.1f} | {CODE_LABEL[(p['code'], p['n_anc'])]} | {p['d']} | {p['pL']:.1e} | {p['f']} | "
                  f"{p['classes']} | {wtxt(p['window'])} | {p['r']:g} |")
    NUMBERS.setdefault("md", {})[f"frontier_req_{tag}"] = "\n".join(md)
    md = ["| overhead | code | d_Z | lowest p_L | of which phase flips | without flags | least f within 1.5x | flags on | coarsest window |",
          "|---|---|---|---|---|---|---|---|---|"]
    seen = set()
    for p in full:
        if p["overhead"] > 90 or (p["code"], p["n_anc"]) in seen and p["overhead"] > 60:
            continue
        nf = f"{p['pL_noflags']:.1e}" if p["pL_noflags"] is not None else "-"
        md.append(f"| {p['overhead']:.1f} | {CODE_LABEL[(p['code'], p['n_anc'])]} | {p['d']} | {p['pL_best']:.1e} | "
                  f"{p['pZL']:.1e} | {nf} | {p['f']} | {p['classes']} | {wtxt(p['window'])} |")
        seen.add((p["code"], p["n_anc"]))
    NUMBERS["md"][f"frontier_rate_{tag}"] = "\n".join(md)
    return req


# ------------------------------------------------------------------ 8. figures
def plot_overheads(pzl_fn, tag):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in flag_rows(("flag_main", "flag_supp")) if r["idle"] == "edge,cnot" and r["p_x"] == 1e-9 and r["r"] == 0]
    f0 = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["f"] == 0}

    def oh_for(cls, w, f, codes=CODES_MAIN):
        if f == 0:
            byc = f0
        else:
            byc = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["f"] == f and r["classes"] == cls and r["window"] == w}
        b = best_overhead(byc, 1e-3, 1e-12, pzl_fn, "pL", codes)
        return b[0] if b else np.nan

    fs = [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 1.0]
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    ax = axs[0]
    for cls, lab in [("idle", "flags on idle locations"), ("idle+gate", "idle + gates"), ("all", "idle + gates + prep/meas")]:
        ys = [oh_for(cls, 0, f) for f in fs]
        ax.plot(fs, ys, "o-", label=lab)
    ax.axhline(88, color="gray", ls="--", label="published (no flags): 88")
    ax.set_xlabel("flag efficiency f"); ax.set_ylabel("qubit overhead per logical qubit")
    ax.set_title("p_Z=1e-3, eta=1e6, target 1e-12, exact timing"); ax.legend(fontsize=8); ax.set_ylim(40, 100)
    ax = axs[1]
    ws = [0, 1, 4, 16, 64, 256, 1024, 4096]
    for f in [0.8, 0.9, 0.95, 0.99, 1.0]:
        for cls, ls in [("all", "-"), ("idle", ":")]:
            ys = [oh_for(cls, w, f) for w in ws]
            if np.all(np.isnan(ys)):
                continue
            ax.plot([max(w, 0.5) for w in ws], ys, "o" + ls, label=f"f={f} ({cls})")
    ax.axhline(88, color="gray", ls="--")
    ax.set_xscale("log"); ax.set_xlabel("timing window (CNOT-layer ticks; 0.5 = exact)"); ax.set_ylim(40, 100)
    ax.set_title("overhead vs flag timing precision"); ax.legend(fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"overhead_vs_flags_{tag}.png"), dpi=130); plt.close(fig)


def plot_maps(pzl_fn, tag):
    """Heat maps over (flag efficiency, timing window): minimum overhead (best code) and the
    [15,9,3] bit-flip rate at d_Z = 15, for flags on all locations and on idle locations only."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in flag_rows(("flag_main", "flag_supp")) if r["idle"] == "edge,cnot" and r["p_x"] == 1e-9 and r["r"] == 0]
    fs = [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 1.0]
    ws = [0, 1, 4, 16, 64, 256, 1024, 4096]
    f0 = {(r["code"], r["n_anc"], r["d"]): r for r in rows if r["f"] == 0}
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for col, cls in enumerate(["all", "idle"]):
        OHm = np.full((len(fs), len(ws)), np.nan)
        PX = np.full((len(fs), len(ws)), np.nan)
        for i, f in enumerate(fs):
            for j, w in enumerate(ws):
                if f == 0:
                    byc = f0
                else:
                    byc = {(r["code"], r["n_anc"], r["d"]): r for r in rows
                           if r["f"] == f and r["classes"] == cls and r["window"] == w}
                    if not byc:
                        continue
                    for k_, v_ in f0.items():
                        byc.setdefault(k_, v_)
                b = best_overhead(byc, 1e-3, 1e-12, pzl_fn, "pL", CODES_MAIN)
                if b:
                    OHm[i, j] = b[0]
                r15 = byc.get(("15_9_3", 1, 15))
                if r15 is not None:
                    PX[i, j] = r15["pL"]
        for row, (M, lab, cmap) in enumerate([(OHm, "minimum overhead ([15,9,3], [15,6,5] 1/2 anc)", "viridis_r"),
                                              (np.log10(np.maximum(PX, 1e-18)), "log10 p_XL of [15,9,3], d_Z = 15", "magma_r")]):
            ax = axs[row, col]
            im = ax.imshow(M, origin="lower", aspect="auto", cmap=cmap)
            ax.set_xticks(range(len(ws))); ax.set_xticklabels(["exact"] + [str(w) for w in ws[1:]])
            ax.set_yticks(range(len(fs))); ax.set_yticklabels([str(f) for f in fs])
            ax.set_xlabel("timing window (CNOT-layer ticks)"); ax.set_ylabel("flag efficiency f")
            ax.set_title(f"{lab}\nflags on {cls} locations", fontsize=9)
            for i in range(len(fs)):
                for j in range(len(ws)):
                    if not np.isnan(M[i, j]):
                        ax.text(j, i, f"{M[i, j]:.1f}" if row == 0 else f"{M[i, j]:.1f}", ha="center", va="center", fontsize=6, color="w")
            fig.colorbar(im, ax=ax)
    fig.suptitle(f"p_Z = 1e-3, eta = 1e6, target 1e-12 (phase flips: {tag}; white = not reached / not simulated)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"map_f_window_{tag}.png"), dpi=130); plt.close(fig)


FIG_SETTINGS = [("none", 0, 0.0), ("idle", 0, 0.99), ("all", 0, 0.9), ("all", 0, 0.99), ("all", 1024, 0.99), ("all", 0, 1.0)]


def _source_rows(px_pref, codes, settings=FIG_SETTINGS, dirs=("flag_main", "flag_supp", "flag_alt", "flag_16_3_8", "flag_pz1e2")):
    """Directly simulated rows (no synthesized ones) per (code, setting): the one at d_Z = 15 (else
    the smallest d_Z) and p_X closest to px_pref (in log)."""
    rows = [r for r in flag_rows(dirs, transfers=False) if r["idle"] == "edge,cnot" and r["r"] == 0
            and r.get("mode", "erasure") == "erasure"]
    out = {}
    for code in codes:
        for (cls, w, f) in settings:
            cand = [r for r in rows if (r["code"], r["n_anc"]) == code and r["f"] == f
                    and (f == 0 or (r["classes"] == cls and r["window"] == w))]
            if not cand:
                continue
            out[(code, cls, w, f)] = min(cand, key=lambda r: (abs(math.log(r["p_x"] / px_pref)), abs(r["d"] - 15), r["d"]))
    return out


def fig1_this_work(pzl_fn, tag, codes=CODES_MAIN + [("16_3_8", 1)]):
    """Figure 1 of arXiv:2601.10786 (overhead vs bias at p_Z = 1e-3, 1e-12) from this work's bit-flip
    simulations: stratum failure fractions of one simulated (d_Z, p_X) per code and flag setting,
    re-weighted with the exact fault intensities at every (d_Z, p_X) (transfer)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    src = _source_rows(1e-9, codes)
    etas = np.logspace(np.log10(4e4), 7, 120)
    curves, steps = {}, {}
    for (cls, w, f) in FIG_SETTINGS:
        ys, prev, st = [], None, []
        for eta in etas:
            px = 1e-3 / eta
            best = None
            for code in codes:
                r = src.get((code, cls, w, f))
                if r is None:
                    continue
                for d in range(13, 42, 2):
                    t = transfer_pxl(r, d, p_x=px)
                    if t is None:
                        continue
                    if t[0] + pzl_fn(code[0], code[1], d, 1e-3) <= 1e-12:
                        oh = overhead(code[0], code[1], d)
                        if best is None or oh < best[0]:
                            best = (oh, code, d)
                        break
            ys.append(best[0] if best else np.nan)
            lab = (round(best[0], 1), CODE_LABEL[best[1]], best[2]) if best else None
            if lab != prev:
                st.append(dict(eta=float(eta), overhead=lab[0] if lab else None, code=lab[1] if lab else None,
                               d=lab[2] if lab else None))
                prev = lab
        curves[(cls, w, f)] = ys
        steps[f"{cls}|w{w}|f{f}"] = st
    NUMBERS.setdefault("fig1_this_work", {})[tag] = steps
    fig, ax = plt.subplots(figsize=(6, 4))
    pub = [(OH.min_overhead(1e-12, OH.candidates(1e-3, e), "elevator") or type("x", (), {"overhead": np.nan})).overhead
           for e in etas]
    ax.step(etas, pub, where="post", color="gray", ls="--", label="published (paper's fits)")
    for (cls, w, f), ys in curves.items():
        lab = "no flags (this work)" if f == 0 else f"f={f}, {cls}, {'exact' if w == 0 else str(w) + ' ticks'}"
        ax.step(etas, ys, where="post", label=lab)
    ax.set_xscale("log"); ax.set_ylim(0, 200); ax.set_xlabel("noise bias eta (p_Z = 1e-3)")
    ax.set_ylabel("qubits per logical qubit (1e-12)"); ax.legend(fontsize=7)
    ax.set_title(f"Fig. 1 from this work's simulations (phase flips: {tag})", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"fig1_this_work_{tag}.png"), dpi=130); plt.close(fig)
    lines = [f"\n## Figure 1 from this work's bit-flip simulations (phase flips: {tag})\n",
             "Steps of the minimum overhead (p_Z = 1e-3, target 1e-12) as the bias grows; bit flips from the "
             "simulated stratum failure fractions re-weighted to each p_X (transfer, validated in validation.md).\n",
             "| flags | from eta | overhead | code | d_Z |", "|---|---|---|---|---|"]
    for k, st in steps.items():
        for x in st:
            lines.append(f"| {k} | {x['eta']:.3g} | {x['overhead'] if x['overhead'] else 'not reached'} | {x['code'] or '-'} | {x['d'] or '-'} |")
    open(os.path.join(OUT, f"fig1_this_work_{tag}.md"), "w").write("\n".join(lines) + "\n")


def fig2_this_work(pzl_fn, tag, codes=CODES_MAIN):
    """Figure 2 (overhead vs target at eta = 1e6) and the reachable floors from this work's simulations."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    res = {}
    for ax, pz, px in [(axs[0], 1e-3, 1e-9), (axs[1], 1e-2, 1e-8)]:
        src = _source_rows(px, codes)
        dmax = 61 if pz == 1e-3 else 301
        targets = np.logspace(-18 if pz == 1e-3 else -14, -5 if pz == 1e-3 else -3, 300)
        cs = OH.candidates(pz, 1e6)
        ys = [(OH.min_overhead(t, cs, "elevator").overhead if OH.min_overhead(t, cs, "elevator") else np.nan) for t in targets]
        ax.step(targets, ys, where="post", color="gray", ls="--", label="published (paper's fits)")
        for (cls, w, f) in FIG_SETTINGS:
            tab = []
            floor = None
            floor_c = None
            for code in codes:
                r = src.get((code, cls, w, f))
                if r is None:
                    continue
                for d in range(13, dmax + 1, 2):
                    t = transfer_pxl(r, d, p_x=px)
                    if t is None:
                        continue
                    pzl = pzl_fn(code[0], code[1], d, pz)
                    tot = t[0] + pzl
                    tab.append((tot, overhead(code[0], code[1], d), code, d, t[0]))
                    if floor is None or tot < floor[0]:
                        floor = (tot, overhead(code[0], code[1], d), CODE_LABEL[code], d, t[0], t[2], r["d"], r["p_x"])
                    if floor_c is None or t[2] + pzl < floor_c[0]:
                        floor_c = (t[2] + pzl, overhead(code[0], code[1], d), CODE_LABEL[code], d)
            if not tab:
                continue
            ys = []
            for T in targets:
                ok = [x[1] for x in tab if x[0] <= T]
                ys.append(min(ok) if ok else np.nan)
            lab = "no flags" if f == 0 else f"f={f}, {cls}, {'exact' if w == 0 else str(w) + ' ticks'}"
            ax.step(targets, ys, where="post", label=lab)
            res[f"pz={pz:g}|{cls}|w{w}|f{f}"] = dict(floor_pL=floor[0], overhead=floor[1], code=floor[2], d=floor[3],
                                                      pXL=floor[4], pXL_hi=floor[5], src_d=floor[6], src_px=floor[7],
                                                      floor_conservative=floor_c[0], overhead_conservative=floor_c[1],
                                                      code_conservative=floor_c[2], d_conservative=floor_c[3],
                                                      at_dmax=floor[3] >= dmax - 1)
        ax.set_xscale("log"); ax.set_ylim(0, 400 if pz == 1e-2 else 200)
        ax.set_xlabel("target logical error rate per round"); ax.set_ylabel("qubits per logical qubit")
        ax.set_title(f"p_Z = {pz:g}, eta = 1e6 (phase flips: {tag})", fontsize=9)
    axs[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"fig2_this_work_{tag}.png"), dpi=130); plt.close(fig)
    NUMBERS.setdefault("fig2_this_work", {})[tag] = res
    lines = [f"\n## Figure 2 from this work's simulations: lowest reachable rate per flag setting (phase flips: {tag})\n",
             "Bit flips from the simulated failure fractions (source d_Z, p_X given) re-weighted to every d_Z (transfer); "
             "d_Z <= 61 at p_Z = 1e-3 and <= 301 at p_Z = 1e-2.  'Conservative' uses the 95% upper bound of p_XL.\n",
             "| p_Z | flags | lowest p_L | code | d_Z | overhead | p_XL there [95% upper] | conservative floor (overhead, code, d_Z) | source (d_Z, p_X) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for k, v in res.items():
        pz_, cls, w, f = k.split("|")
        lines.append(f"| {pz_[3:]} | {cls} {w} {f} | {v['floor_pL']:.2e}{' (at max d_Z)' if v['at_dmax'] else ''} | {v['code']} | {v['d']} | {v['overhead']:.1f} | "
                     f"{v['pXL']:.2e} [{v['pXL_hi']:.2e}] | {v['floor_conservative']:.2e} ({v['overhead_conservative']:.1f}, {v['code_conservative']}, {v['d_conservative']}) | "
                     f"{v['src_d']}, {v['src_px']:g} |")
    open(os.path.join(OUT, f"fig2_this_work_{tag}.md"), "w").write("\n".join(lines) + "\n")


def plot_bias(out, tag):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if not out:
        return
    etas = sorted({k[0] for k in out})
    fig, ax = plt.subplots(figsize=(6, 4))
    for (cls, w, f) in [("none", 0, 0.0), ("idle", 0, 0.99), ("all", 0, 0.9), ("all", 0, 0.99), ("all", 1024, 0.99), ("all", 0, 1.0)]:
        ys = [(out.get((e, cls, w, f)) or [np.nan])[0] for e in etas]
        ax.step(etas, ys, where="post", label=f"{'no flags' if f == 0 else f'f={f} {cls} w={w or chr(101)+chr(120)+chr(97)+chr(99)+chr(116)}'}")
    etas_f = np.logspace(np.log10(4e4), 7, 200)
    pub = []
    for e in etas_f:
        c = OH.min_overhead(1e-12, OH.candidates(1e-3, e), "elevator")
        pub.append(c.overhead if c else np.nan)
    ax.step(etas_f, pub, where="post", color="gray", ls="--", label="published (fits)")
    ax.set_xscale("log"); ax.set_xlabel("noise bias eta (p_Z = 1e-3)"); ax.set_ylabel("qubit overhead"); ax.set_ylim(40, 200)
    ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(os.path.join(OUT, f"overhead_vs_bias_{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    aux_checks()
    repro_tables()
    schedule_comparison()
    figures_from_fits()
    flag_tables(dirs=("flag_main", "flag_supp", "flag_falseflag"))
    flag_tables(dirs=("flag_literal",), idle="edge,cnot,op", label="literal")
    validation_table()
    transfer_check_main()
    plot_bias(bias_sweep(pzl_paper, "paper-pZL"), "paper-pZL")
    plot_overheads(pzl_paper, "paper-pZL")
    if phase_model() is not None:
        flag_tables(pzl_fn=pzl_model, tag="this-work-pZL", dirs=("flag_main", "flag_supp", "flag_falseflag"))
        if "two" in PHASE:
            phase_floor_table()
            required_f(pzl_model, "this-work-pZL")
        flag_tables(pzl_fn=pzl_model, tag="this-work-pZL", dirs=("flag_literal",), idle="edge,cnot,op", label="literal")
        flag_tables(pzl_fn=pzl_model, tag="this-work-pZL", dirs=("flag_alt", "flag_ham63"), label="alt",
                    codes=[("ham15", 1), ("ham31", 1), ("xham16", 1), ("ham63", 1)])
        plot_bias(bias_sweep(pzl_model, "this-work-pZL"), "this-work-pZL")
        plot_overheads(pzl_model, "this-work-pZL")
        plot_maps(pzl_model, "this-work-pZL")
        fig1_this_work(pzl_model, "this-work-pZL")
        assumptions_table()
        literal_reading()
        counting_convention()
        fig2_this_work(pzl_model, "this-work-pZL")
        pz1e2(pzl_model, "this-work-pZL")
        frontier(pzl_model, "this-work-pZL")
    pz1e2(pzl_paper, "paper-pZL")
    fig1_this_work(pzl_paper, "paper-pZL")
    fig2_this_work(pzl_paper, "paper-pZL")
    required_f(pzl_paper, "paper-pZL")
    frontier(pzl_paper, "paper-pZL")
    if "two" in PHASE:
        headline()
        limits_table()
    save_numbers()
    print("wrote", OUT)
