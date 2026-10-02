#!/bin/bash
# One command that regenerates every number in FINDINGS.md / REPORT.md / COMPLETE.md.
#
#   ./reproduce.sh analysis    # from the stored raw results in results/ (minutes)
#   ./reproduce.sh all         # recompute every raw result, then the analysis
#                              # (~2000 core-hours; runs locally with RUNNER=local or on
#                              #  the clusters with RUNNER=gpurun, which is the default)
#
# Raw results are idempotent: a task whose result file exists with the same spec is skipped,
# so an interrupted run resumes where it stopped.
set -euo pipefail
cd "$(dirname "$0")"
MODE="${1:-analysis}"
RUNNER="${RUNNER:-gpurun}"
PY=".venv/bin/python"

if [ ! -x "$PY" ]; then
  uv venv .venv --python 3.12
  uv pip install --python .venv/bin/python "stim==1.16.0" "sinter==1.16.0" "ldpc==2.4.1" "pymatching==2.4.0" numpy scipy matplotlib
fi

run_tasks () {   # $1 = task file, $2 = output dir, $3 = number of cluster tasks, $4 = cpus, $5 = mem (GB)
  if [ "$RUNNER" = "local" ]; then
    "$PY" scripts/run_tasks.py "$1" "$2"
  else
    gpurun --on condor --tasks "$3" --cpus "$4" --mem "$5" --time 2d \
      scripts/remote_python.sh scripts/run_tasks.py "$1" "$2"
  fi
}

if [ "$MODE" = "all" ]; then
  # task files (deterministic)
  "$PY" scripts/make_repro_tasks.py
  for t in main literal bias alt pz1e2 validation; do "$PY" scripts/make_flag_tasks.py "$t"; done
  for t in rep xlow; do "$PY" scripts/make_phase_tasks.py "$t"; done
  # flag-free reproduction of arXiv:2601.10786 (physical Stim circuits, BP+OSD / BP+LSD)
  run_tasks tasks/repro_z.jsonl results/repro_z 20 16 16
  run_tasks tasks/repro_x.jsonl results/repro_x 36 16 16
  # phase flips: isolated repetition code and the elevator X memory at lower p
  run_tasks tasks/phase_rep.jsonl results/phase_rep 22 16 8
  run_tasks tasks/phase_xlow.jsonl results/phase_xlow 19 16 24
  # flagged bit flips (block-level reduction, exact MLE decoder, stratified estimator)
  run_tasks tasks/flag_main.jsonl results/flag_main 66 8 8
  run_tasks tasks/flag_literal.jsonl results/flag_literal 13 8 8
  run_tasks tasks/flag_bias.jsonl results/flag_bias 60 8 8
  run_tasks tasks/flag_alt.jsonl results/flag_alt 50 8 8
  run_tasks tasks/flag_pz1e2.jsonl results/flag_pz1e2 36 8 16
  run_tasks tasks/flag_validation.jsonl results/flag_validation 30 8 8
  # known answers (local, ~25 min)
  "$PY" scripts/known_answers.py --out results/known_answers.json
  # per-class fault sums used to transfer bit-flip rates across d_Z
  "$PY" scripts/class_sums.py
fi

# analysis: every table, figure and number
"$PY" scripts/analyze.py
echo "numbers: results/summary/numbers.json; tables: results/summary/*.md"
