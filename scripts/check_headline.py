"""Check the headline numbers in results/summary/numbers.json.

  python scripts/check_headline.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (phase-flip model, flag setting, code set, expected qubits per logical qubit, expected code, expected d_Z)
EXPECTED = [
    ("published", None, None, 88.0, "[15,6] 15_6_5 a1", 17),
    ("paper-pZL", "none|w0|f0.0", "main", 88.0, "[15,6,5]", 17),
    ("paper-pZL", "all|w0|f0.8", "main", 58.7, "[15,9,3]", 17),
    ("paper-pZL", "all|w0|f0.9", "main", 58.7, "[15,9,3]", 17),
    ("paper-pZL", "all|w0|f0.99", "main", 58.7, "[15,9,3]", 17),
    ("paper-pZL", "all|w0|f1.0", "main", 58.7, "[15,9,3]", 17),
    ("paper-pZL", "idle|w0|f0.9", "main", 88.0, "[15,6,5]", 17),
    ("paper-pZL", "idle|w0|f0.99", "main", 88.0, "[15,6,5]", 17),
    ("paper-pZL", "idle|w0|f0.9", "all_codes", 51.0, "ext. Hamming [16,11,4]", 17),
    ("paper-pZL", "all|w0|f0.8", "all_codes", 48.0, "Hamming [15,11,3]", 17),
    ("paper-pZL", "all|w0|f0.9", "all_codes", 48.0, "Hamming [15,11,3]", 17),
    ("paper-pZL", "all|w0|f0.99", "all_codes", 35.7, "Hamming [31,26,3]", 15),
    ("paper-pZL", "all|w0|f1.0", "all_codes", 30.9, "Hamming [127,120,3]", 15),
    ("paper-pZL", "all|w1|f0.99", "main", 58.7, "[15,9,3]", 17),
    ("paper-pZL", "all|w4096|f0.99", "main", 58.7, "[15,9,3]", 17),
    ("paper-pZL", "all|w1024|f0.99", "all_codes", 40.6, "Hamming [31,26,3]", 17),
    ("this-work-pZL", "none|w0|f0.0", "main", 77.3, "[15,6,5]", 15),
    ("this-work-pZL", "all|w0|f0.9", "main", 51.6, "[15,9,3]", 15),
]


def main():
    h = json.load(open(os.path.join(ROOT, "results", "summary", "numbers.json")))["headline"]
    bad = 0
    for model, setting, codes, want, code, d in EXPECTED:
        e = h["published"] if model == "published" else h[model][setting][codes]
        ok = round(e["overhead"], 1) == want and e["code"] == code and e["d"] == d
        bad += not ok
        label = "published" if model == "published" else f"{model:14s} {setting:16s} {codes:9s}"
        print(f"{'ok  ' if ok else 'FAIL'} {label}  {e['overhead']:6.1f}  {e['code']} d_Z={e['d']}"
              + ("" if ok else f"   expected {want} {code} d_Z={d}"))
    print(f"{len(EXPECTED) - bad} of {len(EXPECTED)} headline numbers match")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
