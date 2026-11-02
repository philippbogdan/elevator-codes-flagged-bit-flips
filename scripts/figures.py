"""Rebuild the three README figures from the included circuits and saved results.

Run analyze.py first to refresh results/summary/numbers.json:

  python scripts/analyze.py
  python scripts/figures.py

The first two figures use the headline selections. The third rebuilds candidate
rates for the paper codes using the analysis procedure and checks all 32 central
and upper-bound rate floors against numbers.json["fig2_this_work"], along with
the counts at the upper-bound floors. A mismatch stops the rebuild. Four bars
then compare the two phase models at p_Z = 1e-3 and 1e-2, with 99% exact
all-location flags, bias 1e6 and no false alarms. Each selects the smallest count
meeting 1e-12 errors per inner round per logical qubit using the upper bit-flip
bound; the higher-noise pair uses distance transfers.

Each figure overwrites a PNG and SVG in figures/. With the same inputs, fonts
and package versions, output is deterministic: SVG identifiers are fixed and
creator, software and date metadata are omitted. PNGs are opaque RGB images.
All rates come from saved samples and models, without fresh sampling.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FixedLocator  # noqa: E402

import analyze as A  # noqa: E402
from elevator.circuits import build_circuit  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.phasemodel import RepModel, load_rep  # noqa: E402

OUT = os.path.join(ROOT, "figures")
NUMBERS = json.load(open(os.path.join(ROOT, "results", "summary", "numbers.json")))

BG = "#fbfaf7"
INK = "#1d1c1a"
INK2 = "#55534e"
GRID = "#e4e2db"
GRAPHITE = "#77736b"
DEEP_BLUE = "#123b63"
AMBER = "#ae7400"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 12.5,
    "mathtext.fontset": "custom",
    "mathtext.rm": "sans",
    "mathtext.it": "sans:italic",
    "mathtext.bf": "sans:bold",
    "mathtext.cal": "sans",
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.labelsize": 13.5,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "xtick.labelsize": 12.5,
    "ytick.labelsize": 12.5,
    "legend.fontsize": 12.5,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "svg.fonttype": "path",
    "svg.hashsalt": "elevator-figures",
})


def save(fig, stem):
    """Write an opaque RGB PNG and SVG without variable metadata, then close."""
    os.makedirs(OUT, exist_ok=True)
    fig.canvas.draw()
    rgba = Image.fromarray(np.asarray(fig.canvas.buffer_rgba()))
    png = os.path.join(OUT, stem + ".png")
    Image.alpha_composite(Image.new("RGBA", rgba.size, BG), rgba).convert("RGB").save(png, optimize=True)
    with Image.open(png) as im:
        assert im.mode == "RGB" and im.size == rgba.size
    fig.savefig(os.path.join(OUT, stem + ".svg"), metadata={"Date": None, "Creator": None})
    plt.close(fig)
    print("wrote", os.path.join("figures", stem + ".png"), "and .svg")


def bare(ax):
    """Keep labels and horizontal guides while removing the plot frame."""
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, pad=6)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


# Figure 1: equal logical storage in the two selected circuit layouts.

def layout(name):
    """Return a d_Z = 17 circuit's qubit coordinates and unique CNOT connections."""
    code = load_code(name)
    circuit, _ = build_circuit(code, 17, "Z", n_anc=1, n_outer=1, mode="full",
                               p_x=0, p_z=0, idle_ctx=("edge", "cnot"))
    xy = circuit.get_final_qubit_coordinates()
    edges = set()
    for op in circuit.flattened():
        if op.name == "CX":
            q = [t.value for t in op.targets_copy()]
            edges.update(tuple(sorted(p)) for p in zip(q[::2], q[1::2]))
    assert circuit.num_qubits == len(xy) == 528
    pts = np.array([xy[i][:2] for i in sorted(xy)])
    segs = np.array([[xy[a][:2], xy[b][:2]] for a, b in sorted(edges)])
    return code, pts, segs


def memory_saving():
    """Draw three six-logical-qubit memories above two nine-logical-qubit memories."""
    head = NUMBERS["headline"]["paper-pZL"]
    rows = [("none|w0|f0.0", "15_6_5", 3, "No flags · [15,6,5]", GRAPHITE),
            ("all|w0|f0.9", "15_9_3", 2, "90% flagged · [15,9,3]", DEEP_BLUE)]
    W, H = 10.0, 5.6
    gap, margin, label_gap, row_gap = 4.2, 3.0, 2.2, 9.0
    built = []
    for key, name, copies, label, color in rows:
        code, pts, segs = layout(name)
        e, c = head[key]["main"], head[key]["main_cons"]
        assert e["code"] == c["code"] == A.CODE_LABEL[(name, 1)] and e["d"] == c["d"] == 17
        assert math.isclose(e["overhead"], c["overhead"]) and math.isclose(e["overhead"], len(pts) / code.k)
        # Both rows store 18 logical qubits; each memory includes its ancillas.
        assert copies * code.k == 18
        built.append((pts, segs, copies, label, f"{e['overhead']:.1f} qubits / logical qubit", color))
    lw_, lh_ = np.ptp(built[0][0], axis=0)
    width_u = 3 * lw_ + 2 * gap + 2 * margin
    height_u = width_u * H / W
    content = 2 * (1.6 + label_gap + lh_) + row_gap
    top = (height_u - content) / 2
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width_u)
    ax.set_ylim(height_u, 0)
    ax.set_axis_off()
    y = top
    for pts, segs, copies, label, count, color in built:
        base = y + 1.6
        y0 = base + label_gap
        for i in range(copies):
            off = np.array([margin + i * (lw_ + gap), y0]) - pts.min(axis=0)
            ax.add_collection(LineCollection(segs + off, colors=color, linewidths=1.25, zorder=1))
            ax.scatter(*(pts + off).T, s=13, c=color, edgecolors=BG, linewidths=0.5, zorder=2)
        right = margin + copies * lw_ + (copies - 1) * gap
        ax.text(margin, base, label, ha="left", va="baseline", fontsize=14.5, weight="bold")
        ax.text(right, base, count, ha="right", va="baseline", fontsize=14.5, color=INK2)
        y = y0 + lh_ + row_gap
    save(fig, "memory-saving")


# Figure 2: flag efficiency and timing at the headline noise and error target.

def flag_requirements():
    """Compare code sets at exact timing, then timing windows at 99% efficiency.

    Circles show all-location estimates, with small offsets for visibility.
    Both idle-only diamonds sit on the 90% category centre. Upward stems end at
    counts selected using the upper bit-flip bound with the phase model fixed.
    """
    head = NUMBERS["headline"]["paper-pZL"]
    panels = [
        (["none|w0|f0.0", "all|w0|f0.5", "all|w0|f0.8", "all|w0|f0.9", "all|w0|f0.99", "all|w0|f1.0"],
         ["0", "50", "80", "90", "99", "100"], "Flagged events (%, tested settings)", {3: "idle|w0|f0.9"}),
        (["all|w0|f0.99", "all|w1|f0.99", "all|w64|f0.99", "all|w1024|f0.99", "all|w4096|f0.99"],
         ["Exact", "1", "64", "1,024", "4,096"], "Timing window (gate layers)", {}),
    ]
    sets = [("main", DEEP_BLUE, -0.1), ("all_codes", AMBER, 0.1)]
    fig = plt.figure(figsize=(10, 4.7), dpi=200)
    left, right, mid, bottom, height = 0.088, 0.015, 0.035, 0.205, 0.645
    unit = (1 - left - right - mid) / 11
    x0 = left
    for i, (keys, ticks, xlabel, idle) in enumerate(panels):
        n = len(keys)
        ax = fig.add_axes([x0, bottom, n * unit, height])
        x0 += n * unit + mid
        bare(ax)
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(25, 95)
        ax.yaxis.set_major_locator(FixedLocator(range(30, 91, 10)))
        ax.set_xticks(range(n), ticks)
        ax.set_xlabel(xlabel, labelpad=8)
        if i == 0:
            ax.set_ylabel("Physical qubits / logical qubit", labelpad=10)
        else:
            ax.tick_params(labelleft=False)
        for lab, color, dx in sets:
            pts = [(j + dx, head[k][lab], head[k][lab + "_cons"], "o") for j, k in enumerate(keys)]
            pts += [(j, head[k][lab], head[k][lab + "_cons"], "D") for j, k in idle.items()]
            ax.plot([p[0] for p in pts if p[3] == "o"], [p[1]["overhead"] for p in pts if p[3] == "o"],
                    color=color, lw=1.5, zorder=2)
            for x, c, u, m in pts:
                assert c is not None and u is not None and u["overhead"] >= c["overhead"] - 1e-9
                # A stem ends at the count selected with the upper bit-flip bound.
                if u["overhead"] > c["overhead"] + 1e-9:
                    ax.vlines(x, c["overhead"], u["overhead"], color=color, lw=1.3, zorder=3)
                    ax.hlines(u["overhead"], x - 0.055, x + 0.055, color=color, lw=1.3, zorder=3)
                ax.plot(x, c["overhead"], m, ms=9.5 if m == "o" else 8, mfc=color, mec=BG, mew=1.4 if m == "o" else 1.8, zorder=4)
    handles = [Line2D([], [], ls="none", marker="o", ms=9.5, mfc=DEEP_BLUE, mec=BG, label="Paper codes"),
               Line2D([], [], ls="none", marker="o", ms=9.5, mfc=AMBER, mec=BG, label="Including Hamming"),
               Line2D([], [], ls="none", marker="o", ms=9.5, mfc=GRAPHITE, mec=BG, label="All locations"),
               Line2D([], [], ls="none", marker="D", ms=8, mfc=GRAPHITE, mec=BG, label="Idle only")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(left - 0.008, 0.995), ncol=4, frameon=False,
               handletextpad=0.3, columnspacing=1.8, borderaxespad=0.2)
    save(fig, "flag-requirements")


# Figure 3: four fixed-target selections at 99% exact all-location flags.

# Retain all four settings to check the broader rate floors before selecting bars.
TARGET_SETTINGS = [("none", 0, 0.0), ("all", 0, 0.9), ("all", 0, 0.99), ("all", 1024, 0.99)]


def target_candidates():
    """Rebuild paper-code candidates and check the saved rate floors.

    Use the same source-row choice, distance transfers and phase models as
    analyze.fig2_this_work. Across two noise levels, four flag settings and two
    phase models, check 32 central and upper-bound minima and the 16 counts at
    the upper-bound minima. Return all candidate rates for fixed_target to
    select the four bars; counts at the rate floors do not define these bars.
    """
    # Refit the repetition model and restore the saved two-component phase fit.
    A.PHASE["rep"] = RepModel(load_rep(os.path.join(ROOT, "results", "phase_rep")))
    assert np.allclose(A.PHASE["rep"].coef, NUMBERS["phase_rep_fit"]["coef"], rtol=1e-10, atol=1e-10)
    t = NUMBERS["phase_two_component"]
    A.PHASE["two"] = (np.log([t["a"], t["g"], t["kappa"]]), np.array(t["cov"]), None)
    pzl = {"paper-pZL": A.pzl_paper, "this-work-pZL": A.pzl_model}
    out = {}
    # Match the analysis distance limits at fixed noise bias p_Z / p_X = 10^6.
    for pz, px, dmax in ((1e-3, 1e-9, 61), (1e-2, 1e-8, 301)):
        src = A._source_rows(px, A.CODES_MAIN, settings=TARGET_SETTINGS)
        for cls, w, f in TARGET_SETTINGS:
            key = f"{cls}|w{w}|f{f}"
            cand = {m: [] for m in pzl}
            for code in A.CODES_MAIN:
                byd = src.get((code, cls, w, f))
                if byd is None:
                    continue
                for d in range(13, dmax + 1, 2):
                    r = A._nearest(byd, d)
                    tx = A.transfer_pxl(r, d, p_x=px)
                    if tx is None:
                        continue
                    for m, fn in pzl.items():
                        p = fn(*code, d, pz)
                        cand[m].append(dict(p_l=tx[0] + p, p_l_upper_x=tx[2] + p, overhead=A.overhead(*code, d),
                                            code=code, d=d, source_d=r["d"], source_p_x=r["p_x"]))
            for m, rows in cand.items():
                stored = NUMBERS["fig2_this_work"][m][f"pz={pz:g}|{key}"]
                lo = min(rows, key=lambda r: r["p_l_upper_x"])
                assert math.isclose(min(r["p_l"] for r in rows), stored["floor_pL"], rel_tol=1e-9)
                assert math.isclose(lo["p_l_upper_x"], stored["floor_conservative"], rel_tol=1e-9)
                assert math.isclose(lo["overhead"], stored["overhead_conservative"], rel_tol=1e-12)
                out[(m, pz, key)] = rows
    return out


def fixed_target(cands, key="all|w0|f0.99", target=1e-12):
    """Select the least costly qualifying candidate for each noise/model pair.

    Qualification uses the upper bit-flip rate plus the modelled phase rate.
    Defaults give four selections at 99% exact all-location flags and a target
    of 1e-12 per inner round per logical qubit. Code, distance and ancilla count
    may differ between selections.
    """
    sel = {}
    for (m, pz, k), rows in cands.items():
        if k == key:
            ok = [r for r in rows if r["p_l_upper_x"] <= target]
            assert ok, (m, pz, k)
            sel[(m, pz)] = min(ok, key=lambda r: r["overhead"])
    assert len(sel) == 4
    return sel


def noise_and_target():
    """Draw four directly labelled bars on one zero-based physical-qubit scale.

    Pair the paper phase fits and this work's phase model at each noise level.
    Bar lengths retain full precision; only the displayed counts are rounded.
    The README caption supplies the fixed target and flag conditions.
    """
    sel = fixed_target(target_candidates())
    groups = [(1e-3, r"$p_Z\,=\,10^{-3}$"), (1e-2, r"$p_Z\,=\,10^{-2}$")]
    models = [("paper-pZL", "Paper phase fits"), ("this-work-pZL", "This work's phase model")]
    step, bar = 3.45, 0.56
    fig = plt.figure(figsize=(10, 4.2), dpi=200)
    ax = fig.add_axes([0.25, 0.215, 0.725, 0.765])
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.set_xlim(0, 600)
    ax.set_ylim(step + 2 + 0.45, -0.5)
    ax.set_xticks(range(0, 601, 100))
    ax.set_yticks([])
    ax.tick_params(axis="x", length=0, pad=6)
    ax.set_xlabel("Physical qubits / logical qubit", labelpad=8)
    for g, (pz, facet) in enumerate(groups):
        y0 = g * step
        ax.vlines(range(0, 601, 100), y0 + 0.55, y0 + 2.45, color=GRID, lw=0.8, zorder=0)
        ax.text(0, y0, facet, ha="left", va="center", fontsize=16.5)
        for i, (m, label) in enumerate(models):
            y, v = y0 + 1 + i, sel[(m, pz)]["overhead"]
            ax.barh(y, v, height=bar, color=GRAPHITE, zorder=2)
            ax.text(v + 7, y, f"{v:.1f}", ha="left", va="center", fontsize=14)
            ax.text(-0.025, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=14)
    save(fig, "noise-and-target")


if __name__ == "__main__":
    memory_saving()
    flag_requirements()
    noise_and_target()
