#!/bin/bash
# ./reproduce.sh       Rebuild tables and figures from saved samples, then check the headline.
# ./reproduce.sh all   Run tests, resume samples and rerun separate checks before the rebuild.
# See REPRODUCE.md for a fresh computation that preserves the supplied results.
set -euo pipefail
cd "$(dirname "$0")"
MODE="${1:-analysis}"
PY=".venv/bin/python"

if [ ! -x "$PY" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv --python 3.12
    uv pip install --python "$PY" -r requirements.txt
  else
    python3 -m venv .venv
    "$PY" -m pip install -r requirements.txt
  fi
fi

if [ "$MODE" = "all" ]; then
  "$PY" -m pytest -q tests/test_core.py
  "$PY" scripts/strata_caps.py
  for t in tasks/*.jsonl; do
    name="$(basename "$t" .jsonl)"
    "$PY" scripts/run_tasks.py "$t" "results/$name"
  done
  "$PY" scripts/known_answers.py --out results/known_answers.json
  "$PY" scripts/decoder_optimality.py 500
  "$PY" scripts/decoder_optimality_windows.py 2000
  "$PY" scripts/decoder_optimality_15_6_5.py 1600
  "$PY" scripts/decoder_variants_flagfree.py 600
  "$PY" scripts/sensitivity_15_9_3.py
  "$PY" scripts/variants_z.py results/variants/z_variants_v1.json 20000
  "$PY" scripts/perfect_flags_exact.py 4000000
  "$PY" scripts/class_sums.py
  "$PY" scripts/counting_convention.py
  "$PY" scripts/op_noise_penalty.py
  "$PY" scripts/decoder_check_16_3_8.py 20000
  "$PY" scripts/false_flag_bounds.py
fi

"$PY" scripts/analyze.py
"$PY" scripts/figures.py
"$PY" scripts/check_headline.py
