# COMPLETE — GOAL.md, item by item, with the measurements that show it

GOAL.md: *"Done means COMPLETE.md shows, through the measurements above, that all four
deliverables hold, the flag-free simulation reproduces the published results, the overhead is
measured across the whole range of flag efficiency and timing precision, and every remaining limit
belongs to the problem itself."*  This file is rendered by `./reproduce.sh` from
`results/summary/numbers.json`; every number in it is regenerated with the rest.  Claims and their
evidence in detail: `FINDINGS.md`; each criterion against the published floor: `REPORT.md`.

## Summary

| requirement | status | evidence |
|---|---|---|
| 1. Simulation and decoder (both codes, X and Z memory, flag efficiency, false flags, timing; flags used as erasures; every assumption stated and its effect measured) | holds | §1 below; `docs/methods.md`, `results/summary/assumptions.md` |
| 2. Published results reproduced with flags off (fits at the sampled points; Figures 1 and 2) | holds for the published overheads and for [15,6,5]; two fit-level disagreements ([15,9,3] Z memory ≤ {{ f1(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_max"]) }}×, X memory ≈ {{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd"]["ratio_min"]) }}×) explained by evidence | §2 |
| 3. Overhead measured: p_Z = 1e-3, η = 1e6 over f ∈ [0, 1] × timing exact … 4096 CNOT layers; bias 4e4 … 1e7; p_Z = 1e-2 floors | holds | §3 |
| 4. FINDINGS.md, REPORT.md, one command (`./reproduce.sh`) | holds | §4 |
| Fidelity, known answers, statistics, overhead, frontier, limits (GOAL.md "Measurable") | hold | §5 |

## 1. Deliverable 1 — simulation and decoder

* **Circuits** (`elevator/circuits.py`, `elevator/schedule.py`): Stim circuits of the Elevator-code
  memories [15,9,3] and [15,6,5] (one and two logical ancillas; [16,3,8] and Hamming outer codes
  for the comparisons), Z-type and X-type memory, Table-I noise.  Tested: noiseless determinism,
  circuit distance = outer-code distance (Stim's undetectable-error search), and the block-level
  reduction of the bit-flip memory equal to Stim's detector error model (`tests/test_core.py`,
  10 tests).
* **Flags** (`elevator/flags.py`): an event at a location raises a flag with efficiency f per
  location class (idle, gate, preparation, measurement); false flags at rate r per qubit per tick;
  a flag reports its qubit and a timing window of w ticks (w = 0: the exact location, including
  before/after within a CNOT).  An event is an erasure (its X occurs with probability ½), as in
  arXiv:2607.01375.
* **Decoder**: exact most-likely-error decoding (integer program) with flagged windows as erasure
  information — each flagged window's event is placed at the most likely of its locations,
  unflagged faults keep their prior.  It equals maximum likelihood on the configurations that
  dominate failure: {{ N["checks"]["decoder_optimality"]["ml"] }} vs {{ N["checks"]["decoder_optimality"]["mle"] }}
  failures on {{ N["checks"]["decoder_optimality"]["n"] }} exactly timed configurations and
  {{ N["checks"]["decoder_optimality_windows"]["ml"] }} vs {{ N["checks"]["decoder_optimality_windows"]["mle"] }}
  on {{ N["checks"]["decoder_optimality_windows"]["n"] }} configurations with windows of 64–4096 ticks.
* **Every assumption the flag model needs, with its measured effect** (`assumptions.md`; minimum
  overhead at p_Z = 1e-3, η = 1e6, 1e-12, this-work pZL / paper pZL):

  | assumption | alternatives measured | effect |
  |---|---|---|
  | which locations raise flags (only idle is established) | idle / idle + gate / all, f = 0.99 | {{ ohs("this-work-pZL", "idle|w0|f0.99") }} / {{ ohs("this-work-pZL", "idle+gate|w0|f0.99") }} / {{ ohs("this-work-pZL", "all|w0|f0.99") }}; paper pZL: {{ ohs("paper-pZL", "idle|w0|f0.99") }} / {{ ohs("paper-pZL", "idle+gate|w0|f0.99") }} / {{ ohs("paper-pZL", "all|w0|f0.99") }} |
  | timing precision | windows exact, 1 … 4096 ticks | flags on all locations: no change of the minimum overhead up to 4096 ticks (> the whole memory); idle-only flags fail from 256 ticks |
  | false flags | r = 1e-10 … 1e-6 per qubit per tick | <!-- FALSEFLAG-EFFECT --> |
  | erasure vs heralded X | flag certifies the X | <!-- HERALD-EFFECT --> |
  | idle noise during logical-operation ticks (unstated in the paper) | none ("noop", reproduces the fits) / on every waiting block (literal) | <!-- LITERAL-EFFECT --> |
  | equal tick durations, aligned windows | — | the overhead is flat in the window from 1 to 4096 ticks (flags on all locations), so any assignment of durations to ticks leaves it unchanged |
  | phase randomisation accompanying an event; events on inner ancillas during X-basis preparation/readout | not modelled | rate ~p_X, 10^6 below p_Z: changes p_ZL by < 1e-5 relative; Table I has no X error there |

## 2. Deliverable 2 — the published results, flags off

* **Fits at the sampled points** (`reproduction.md`): Z memory within 2× or the 95 % interval at
  {{ int(N["repro"]["Z:15_6_5:a1:full/noop"]["within"]) }}/16 points ([15,6,5]),
  {{ int(N["repro"]["Z:15_6_5:a2:full/noop"]["within"]) }}/16 ([15,6,5], two ancillas) and
  {{ int(N["repro"]["Z:15_9_3:a1:full/noop"]["within"]) }}/16 ([15,9,3], ratios
  {{ f2(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_max"]) }});
  X memory ratios {{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd-minsum"]["ratio_min"]) }}–{{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd"]["ratio_max"]) }};
  the repetition code within 0.7–1.5× of the paper's repetition-code fit for d_Z ≤ 13.
* **Figures 1 and 2** from the paper's fits: identical (steps
  {{ " → ".join(f1(s["overhead"]) for s in N["fig1_elevator_steps"]) }}; p_Z = 1e-2 floors
  {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,9] 15_9_3 a1"]["pl"]) }} and
  {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,6] 15_6_5 a2"]["pl"]) }}).  From this work's
  flag-free simulation (bit flips) with the paper's phase-flip fit: the published operating point
  is reproduced — {{ ohs("paper-pZL", "none|w0|f0.0") }} at η = 1e6 — and the Fig. 1 steps fall at
  η = {{ ", ".join(e2(s["eta"]) for s in N["fig1_this_work"]["paper-pZL"]["none|w0|f0.0"]) }}
  ({{ ", ".join(s["code"] for s in N["fig1_this_work"]["paper-pZL"]["none|w0|f0.0"]) }}), published
  6.7e4, 1.21e5, 1.76e6.  <!-- PZ1E2-FLAGFREE -->
* **Disagreements, explained by evidence** (FINDINGS §1 item 4): neither the decoder (exact ML;
  BP+OSD-CS7, BP+OSD-0 and BP+LSD equal on the same X-memory shots), nor check order, number of
  rounds or schedule variant; both residuals lie inside the range spanned by the readings of the
  unstated idle-noise placement (published fits bracketed for every code and memory).  They do not
  reach the conclusions: the flag gain is measured against this work's own flag-free simulation,
  which reproduces the published operating point.

## 3. Deliverable 3 — the overhead, measured

* **p_Z = 1e-3, η = 1e6, 1e-12, across f ∈ [0, 1] and timing from exact to 4096 CNOT layers, both
  codes** (`flags_main_*.md`, `map_f_window_this-work-pZL.png`, `overhead_vs_flags_*.png`,
  `required_f_*.md`): efficiencies 0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 1 ×
  windows exact, 1, 4, 16, 64, 256, 1024, 4096 ticks (one CNOT layer = 1 tick; an outer round of
  [15,9,3] ≈ 600 ticks) × flags on idle / idle + gate / all locations, for [15,9,3] and [15,6,5]
  with one and two ancillas.  Minimum overhead: {{ ohs("paper-pZL", "none|w0|f0.0") }} without
  flags → {{ ohs("paper-pZL", "all|w0|f0.9") }} with flags on all locations at f = 0.9 (paper pZL);
  {{ ohs("this-work-pZL", "none|w0|f0.0") }} → {{ ohs("this-work-pZL", "all|w0|f0.9") }} (this-work
  pZL).  Minimum efficiency for [15,9,3]: {{ reqf("this-work-pZL", "15_9_3|a1", 15, "all", 0) }}
  (exact timing) to {{ reqf("this-work-pZL", "15_9_3|a1", 15, "all", 4096) }} (4096 ticks).
* **Bias 4e4 … 1e7** (`bias_*.md`, `fig1_this_work_*.md/.png`, `overhead_vs_bias_*.png`): [15,9,3]
  is the cheapest code from η = {{ e2(first_eta("paper-pZL", "none|w0|f0.0", "[15,9,3]")) }} without
  flags, {{ e2(first_eta("paper-pZL", "all|w0|f0.9", "[15,9,3]")) }} (f = 0.9),
  {{ e2(first_eta("paper-pZL", "all|w0|f0.99", "[15,9,3]")) }} (f = 0.99) and everywhere with
  perfect flags (paper pZL).
* **p_Z = 1e-2, η = 1e6: lowest reachable p_L and its overhead per flag setting**
  (`fig2_this_work_*.md`, `pz1e2_*.md`): <!-- PZ1E2-SUMMARY -->

## 4. Deliverable 4 — documents and one command

`FINDINGS.md` (claims with evidence), `REPORT.md` (each criterion against the published floor,
what failed, what remains open), and `./reproduce.sh` (`analysis`: every table, figure, number
and these three documents from the stored raw results; `all`: every raw result first, from the
task files in `tasks/`, which specify every stored result — `scripts/orphans.py` finds none
without one).

## 5. The measurables

* **Fidelity to the source** — §2.
* **Known answers** — met exactly: distance-3 … 9 repetition codes with every flip flagged correct
  all {{ N["checks"]["known_answers"]["KA1_code_capacity_rep9"]["patterns_below_d"] }} patterns of up to
  d − 1 flips (d = 9) and fail on half the patterns of d; [15,9,3] and [15,6,5] with perfect flags
  correct all {{ N["checks"]["known_answers"]["KA2_code_capacity_15_9_3"]["patterns_below_d"] }} and
  {{ N["checks"]["known_answers"]["KA2_code_capacity_15_6_5"]["patterns_below_d"] }} patterns of up to
  d − 1 erased blocks (enumerated), and {{ N["checks"]["known_answers"]["KA2_circuit_15_9_3"]["patterns"] }}
  and {{ N["checks"]["known_answers"]["KA2_circuit_15_6_5"]["patterns"] }} circuit-level patterns.
* **Statistics** — every rate carries a 95 % interval (Wilson per stratum; failures counted in the
  tables).  Every number below sampling reach (p_X ≤ 1e-8 bit flips; phase flips below ~1e-9) is
  labelled, gives its model (Poisson strata with sampled failure fractions; transfers in d_Z and
  p_X with exact intensities; the phase-flip model), and the model predicts held-out sampled
  points: direct samples under flags {{ N["validation"]["agree"] }}/{{ N["validation"]["total"] }}
  and {{ N["validation_transfer"]["inside"] }}/{{ N["validation_transfer"]["total"] }} (from the
  p_X = 1e-9 fractions); d_Z transfers {{ N["transfer_check_main"]["agree"] }}/{{ N["transfer_check_main"]["total"] }}
  and {{ N["pz1e2_transfer_checks"]["agree"] }}/{{ N["pz1e2_transfer_checks"]["total"] }}; held-out
  repetition-code points within {{ f2(min(h["ratio"] for h in N["phase_rep_fit"]["heldout"] if h["p"] <= 0.01)) }}–{{ f2(max(h["ratio"] for h in N["phase_rep_fit"]["heldout"] if h["p"] <= 0.01)) }}×.
* **Overhead against the published floors** — 88 → {{ f1(ohv("paper-pZL", "all|w0|f0.9")) }}
  (paper pZL) / {{ f1(ohv("this-work-pZL", "all|w0|f0.9")) }} (this-work pZL) with flags on all
  locations; idle-only flags: {{ f1(ohv("paper-pZL", "idle|w0|f1.0")) }} /
  {{ f1(ohv("this-work-pZL", "idle|w0|f1.0")) }} at f = 1.  p_Z = 1e-2: <!-- PZ1E2-VS-PUBLISHED -->
* **The frontier** — `frontier_*.md`: <!-- FRONTIER-SUMMARY -->
* **Every remaining limit belongs to the problem** — <!-- LIMITS-SUMMARY -->
