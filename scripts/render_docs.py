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


ENV = dict(N=N, f1=f1, f2=f2, e1=e1, e2=e2, g=g, pct=pct, math=math, min=min, max=max, len=len, sum=sum,
           round=round, sorted=sorted)
PAT = re.compile(r"\{\{(.+?)\}\}", re.S)


def render(text, missing):
    def sub(m):
        expr = m.group(1).strip()
        try:
            return str(eval(expr, {"__builtins__": {}}, ENV))
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
