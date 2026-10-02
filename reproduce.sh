#!/bin/bash
# One command that regenerates every number in FINDINGS.md, REPORT.md and COMPLETE.md.
#
#   ./reproduce.sh analysis    # from the stored raw results in results/ (minutes): every table,
#                              # figure and number (results/summary/), then the three documents
#   ./reproduce.sh all         # recompute every raw result first (~1500 core-hours on the clusters
#                              # with RUNNER=gpurun, the default; RUNNER=local runs it here)
#
# Raw results are idempotent: a task whose result file exists with the same spec is skipped, so an
# interrupted run resumes where it stopped.  The task files in tasks/ are the exact specifications
# of every stored result (scripts/orphans.py lists results without one: none).
set -euo pipefail
cd "$(dirname "$0")"
MODE="${1:-analysis}"
RUNNER="${RUNNER:-gpurun}"
PY=".venv/bin/python"

if [ ! -x "$PY" ]; then
  uv venv .venv --python 3.12
  uv pip install --python .venv/bin/python "stim==1.16.0" "sinter==1.16.0" "ldpc==2.4.1" "pymatching==2.4.0" \
    numpy scipy matplotlib pytest
fi

run_tasks () {   # $1 = task file, $2 = default output dir, $3 = cluster tasks, $4 = processes per task
  if [ "$RUNNER" = "local" ]; then
    "$PY" scripts/run_tasks.py "$1" "$2"
  else
    gpurun --on condor --tasks "$3" --cpus 16 --mem 16 --time 2d \
      scripts/remote_python.sh scripts/run_tasks.py "$1" "$2" --procs "$4"
  fi
}

if [ "$MODE" = "all" ]; then
  "$PY" -m pytest -q tests/test_core.py
  # flag-free reproduction of arXiv:2601.10786 (physical Stim circuits, BP+OSD / BP+LSD)
  run_tasks tasks/repro_z.jsonl results/repro_z 20 16
  run_tasks tasks/repro_x.jsonl results/repro_x 36 16
  # phase flips: isolated repetition code, elevator X memory at lower p, ancilla diagnostic, large d
  run_tasks tasks/phase_rep.jsonl results/phase_rep 22 16
  run_tasks tasks/phase_rep_high.jsonl results/phase_rep 34 16
  run_tasks tasks/phase_xlow.jsonl results/phase_xlow 19 16
  run_tasks tasks/phase_ancdiag.jsonl results/phase_ancdiag 10 16
  run_tasks tasks/phase_ancdiag_low.jsonl results/phase_ancdiag 2 16
  # flagged bit flips (block-level reduction, exact MLE decoder, stratified estimator):
  # core list (d_Z = 15 grid, p_Z = 1e-2 core, validation), second-priority list (alternatives,
  # bias checks, false flags, heralded flags, literal reading, p_Z = 1e-2, [16,3,8], phase extras),
  # the d_Z = 17 main grid, [63,57,3] and the older literal-reading runs
  run_tasks tasks/core_local.jsonl results/flag_main 30 16
  run_tasks tasks/tier_b.jsonl results/flag_main 30 12
  run_tasks tasks/flag_main_rem_local.jsonl results/flag_main 22 16
  run_tasks tasks/ham63_sel.jsonl results/flag_ham63 4 8
  run_tasks tasks/ffcap.jsonl results/flag_supp 6 16              # false flags with analytic caps
  run_tasks tasks/sched_local.jsonl results/sched_local 8 16      # ancilla-path sensitivity (flags off)
  run_tasks tasks/xham16_idle.jsonl results/flag_alt 4 16         # [16,11,4] with idle-only flags
  [ -s tasks/legacy.jsonl ] && run_tasks tasks/legacy.jsonl results/flag_literal 4 16
  # local checks (minutes to an hour each)
  "$PY" scripts/known_answers.py --out results/known_answers.json
  "$PY" scripts/decoder_optimality.py 500
  "$PY" scripts/decoder_optimality_windows.py 2000
  "$PY" scripts/decoder_variants_flagfree.py 600
  "$PY" scripts/sensitivity_15_9_3.py
  "$PY" scripts/variants_z.py results/variants/z_variants_v1.json 20000
  "$PY" scripts/perfect_flags_exact.py 4000000
  "$PY" scripts/class_sums.py
  "$PY" scripts/counting_convention.py
  "$PY" scripts/decoder_check_16_3_8.py 20000
  "$PY" scripts/false_flag_bounds.py
fi

# analysis: every table, figure and number, then the documents rendered from them
"$PY" scripts/analyze.py
"$PY" scripts/render_docs.py
echo "numbers: results/summary/numbers.json; tables: results/summary/*.md; documents: FINDINGS.md REPORT.md COMPLETE.md"
