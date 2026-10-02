"""Render FINDINGS.md, REPORT.md and COMPLETE.md from docs/templates/*.md and the regenerated numbers
(results/summary/numbers.json), so every number quoted in them is recomputed by ./reproduce.sh.

A placeholder {{ expr }} is a Python expression over N (numbers.json) and the formatting helpers
below; an expression that fails renders as [missing: expr] and is listed on stderr.

  python scripts/render_docs.py [--check]     (--check: exit 1 if anything is missing)
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = json.load(open(os.path.join(ROOT, "results", "summary", "numbers.json")))


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def e1(x):
    if x is None:
        return "-"
    if x == 0:
        return "0"
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def e2(x):
    if x is None:
        return "-"
    if x == 0:
        return "0"
    m, e = f"{x:.2e}".split("e")
    return f"{m}e{int(e)}"


def g(x):
    return f"{x:g}"


def pct(x):
    return f"{100 * x:.0f} %"


H = N.get("headline", {})


def ohv(tag, key, lab="main"):
    """minimum overhead (number) at p_Z = 1e-3, eta = 1e6, 1e-12 for a flag setting key 'cls|w..|f..'"""
    e = H[tag][key][lab]
    return e["overhead"] if e else None


def ohs(tag, key, lab="main"):
    """minimum overhead with its code and d_Z, as text"""
    e = H[tag][key][lab]
    return f"{e['overhead']:.1f} ({e['code']}, d_Z = {e['d']})" if e else "not reached"


def ohc(tag, key, lab="main"):
    """minimum overhead (central estimate), with the one from p_XL at its 95 % upper bound where it differs"""
    e, c = H[tag][key][lab], H[tag][key].get(lab + "_cons")
    s = ohs(tag, key, lab)
    if e and c and abs(e["overhead"] - c["overhead"]) < 1e-9:
        return s
    return s + "; 95 % bound: " + (f"{c['overhead']:.1f} ({c['code']}, d_Z = {c['d']})" if c else "not reached")


def reqf(tag, code, d, cls, w, which=0):
    """minimum flag efficiency (central = 0, conservative = 1) for code 'code|aN', d_Z, classes, window"""
    return N["required_f"][tag][f"{code}|d{d}|{cls}|w{w}"][which]


def first_eta(tag, key, code_label):
    """lowest bias from which the given code is the cheapest choice (Fig. 1 from this work's simulations)"""
    for st in N["fig1_this_work"][tag][key]:
        if st["code"] == code_label:
            return st["eta"]
    return None


def reach(key, hi=False):
    """overhead at which 1e-12 is reached at p_Z = 1e-2 (limits entry 'p1e-2|code|flags|tag', emulation
    closure over the settings it can emulate), from the central p_XL or from its 95 % upper bound"""
    e = N["limits"][key]
    v = e.get("c_reach_hi" if hi else "c_reach", e.get("reach_hi" if hi else "reach"))
    return f1(v) if v else "not reached"


def floor2(tag, key):
    """lowest reachable p_L at p_Z = 1e-2 (Fig. 2 from this work's simulations) for flag setting key"""
    return N["fig2_this_work"][tag][f"pz=0.01|{key}"]


def pfloor(code, pz, tgt, which="d_model"):
    return N["phase_floor"][f"{code}|{pz:g}|{tgt:g}"][which]


def asm(key, default="not simulated"):
    """an entry of the assumptions summary (numbers.json: assumptions)"""
    v = N.get("assumptions", {}).get(key)
    return default if v is None or v == "-" else v


def ci(e):
    """an entry with pXL, lo, hi as 'central [lo, hi]'"""
    return f"{e2(e['pXL'])} [{e1(e['lo'])}, {e1(e['hi'])}]"


def pxl3(key):
    """p_XL of [15,9,3] at d_Z = 15 for an assumptions entry, as 'central [lo, hi]'"""
    v = N.get("assumptions", {}).get(key + "|pXL_15_9_3")
    return "not simulated" if not v else f"{e1(v[0])} [{e1(v[1])}, {e1(v[2])}]"


ENV = dict(N=N, H=H, asm=asm, pxl3=pxl3, ci=ci, f1=f1, f2=f2, e1=e1, e2=e2, g=g, pct=pct, math=math, min=min, max=max, len=len, sum=sum,
           round=round, sorted=sorted, ohv=ohv, ohs=ohs, ohc=ohc, reqf=reqf, first_eta=first_eta, floor2=floor2, reach=reach, pfloor=pfloor,
           abs=abs, str=str, int=int, float=float, zip=zip, list=list, dict=dict, any=any, all=all)
PAT = re.compile(r"\{\{(.+?)\}\}", re.S)


def render(text, missing):
    def sub(m):
        expr = m.group(1).strip()
        try:
            return str(eval(expr, dict(ENV, __builtins__={})))
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{expr}  ({type(exc).__name__}: {exc})")
            return f"[missing: {expr}]"
    return PAT.sub(sub, text)


def main():
    missing = []
    tdir = os.path.join(ROOT, "docs", "templates")
    for name in sorted(os.listdir(tdir)):
        if not name.endswith(".md"):
            continue
        text = open(os.path.join(tdir, name)).read()
        out = render(text, missing)
        open(os.path.join(ROOT, name), "w").write(out)
    for m in missing:
        print("missing:", m, file=sys.stderr)
    print(f"rendered {len([n for n in os.listdir(tdir) if n.endswith('.md')])} documents, {len(missing)} missing values")
    if "--check" in sys.argv and missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
