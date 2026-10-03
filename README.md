# Flagged bit flips in Elevator-code memories

How far flagging the bit flips of dissipative cat qubits (arXiv:2607.01375) cuts the qubit overhead
of Elevator-code quantum memories (arXiv:2601.10786), simulated in Stim.  Task: `PROBLEM.md`,
`GOAL.md`.

* `COMPLETE.md`: the goal, item by item, with the measurements that show it.
* `FINDINGS.md`: what the work establishes, each claim with its evidence.
* `REPORT.md`: each criterion against the published floor, what failed, what remains open.
* `docs/methods.md`: circuits, flag model, decoders, estimators, models.
* `./reproduce.sh analysis`: every table, figure and number (`results/summary/`) and the three
  documents above from the stored raw results (`results/`); `./reproduce.sh all` recomputes the
  raw results first from the task files in `tasks/`.

Code: `elevator/` (circuits, schedules, block-level bit-flip model, flags, decoders, estimators),
`scripts/` (task generation, runners, checks, analysis), `tests/test_core.py`.

The code is under the MIT licence (`LICENSE`); the papers it builds on are not included (see `data/README.md`).
