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


if __name__ == "__main__":
    repro_tables()
    figures_from_fits()
    save_numbers()
    print("wrote", OUT)
