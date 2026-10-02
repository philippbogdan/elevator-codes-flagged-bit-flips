# REPORT — each criterion of GOAL.md against the published floor

Published floor (arXiv:2601.10786 fits, PROBLEM.md): 88 qubits per logical qubit at p_Z = 1e-3,
η = 1e6, 1e-12 per round ([15,6,5], d_Z = 17); [15,9,3] needs η ≥ 1.8e6 (58.7); thin surface 125,
thin XZZX 145; at p_Z = 1e-2, η = 1e6 the fits bottom out near 2e-9 ([15,9,3]) and 2e-11
([15,6,5], two ancillas).  Rendered from `results/summary/numbers.json` by `./reproduce.sh`.

## 1. Fidelity to the source (flags off)

| check | result | status |
|---|---|---|
| Figures 1 and 2 from the paper's fits | identical: steps 187.0 → 93.5 → 88.0 → 58.7 at η = 6.74e4, 1.21e5, 1.76e6; floors 1.94e-9, 2.08e-11 | met |
| Published operating point and Fig. 1 from this work's flag-free simulation (paper's phase-flip fit) | 88.0 ([15,6,5], d_Z = 17) at η = 1e6; Fig. 1: 187.0 → 93.5 → 88.0 → 58.7 with steps at η = 5.53e4, 6.98e4, 2.16e6 (published 187 → 93.5 → 88 → 58.7 at 6.7e4, 1.21e5, 1.76e6) | met |
| Z memory [15,6,5], one ancilla, 16 sampled points | 15/16 within 2× (0.43–1.33×) | met |
| Z memory [15,6,5], two ancillas | 14/16 within 2× (0.60–2.45×) | met at 14 of 16 points |
| Z memory [15,9,3] | full sweep: 6/16 within 2× (1.43–3.76×); shortest-path ancilla: 4/4 (1.42–1.89×) | met with the shortest-path ancilla; the main study keeps the (pessimistic) full sweep — explained below |
| X memory [15,9,3] (d_Z = 9, 11, 13; p_Z 5e-3 … 1e-2) | 0.38–0.47× counting any of the k logical qubits; 0.98–1.30× counting each logical qubit's errors (measured multiplicity 2.6) | met in the per-qubit count, which the paper's X fit evidently uses |
| Z memory [16,3,8] (needed only below η ≈ 7e4) | full sweep: 0/14 within 2× (2.6–17.8×); shortest-path ancilla: 1.47–1.93× (4 points) | met with the shortest-path ancilla (`schedule_comparison.md`); the main study keeps the full sweep — explained below |
| repetition code (paper's fit, App. B) | 0.7–1.4× for d_Z ≤ 13 over p_Z = 1e-3 … 1.3e-2 (the fit was sampled to d_Z = 11) | met |

Disagreements explained by evidence, not tuned away (FINDINGS §1):
* The placement of idle noise is unstated.  The literal reading (idle noise on every waiting
  block) is 1.2–7.9× above every published fit; without idle noise on blocks waiting during
  logical-operation ticks ("noop") [15,6,5] and the repetition code agree.  Every result is
  computed with the noop reading; the literal reading is kept as a sensitivity case.
* The X memory: a counting convention.  A failure flips 2.6 of the
  9 logical qubits on average; counting each logical qubit's errors separately puts the same shots
  at 0.82–1.30× the fit.  The
  paper's Z-memory fits instead match counting a failure once.  Every rate of this work counts a
  failure once (any of the k logical qubits) and divides by k; the per-qubit count changes no
  conclusion (FINDINGS 13e).  Decoders are ruled out (BP+OSD-CS7, BP+OSD-0, BP+LSD fail equally
  often on the same shots).
* [15,9,3] and [16,3,8] bit flips above their fits with the full-sweep ancilla: not the decoder
  (exact ML), not the check order or the number of outer rounds, but the unstated ancilla path —
  with the shortest path both agree within 2× at every point tested, while [15,6,5] (reproduced
  by the full sweep) then drops to 0.38–0.46×.  No single path matches all three fits; the paper's
  circuits are not public.  The flag study keeps the full sweep throughout: its [15,9,3] baseline
  is the pessimistic one, so flag gains measured against it are not inflated; [16,3,8] enters
  only Fig. 1 below η ≈ 7e4.

## 2. Known answers

Met exactly (FINDINGS item 6): repetition codes with every flip flagged correct every pattern of
up to d − 1 flips; [15,9,3] and [15,6,5] with perfect flags correct every pattern of up to d − 1
erased blocks, at code capacity and in the full circuit, by enumeration.

## 3. Statistics

Every rate has a 95 % interval from its sampled failures; the bit-flip rates at p_X ≤ 1e-8 are
labelled as below sampling reach and come with their model (Poisson strata, exact intensities,
sampled failure fractions) and its held-out checks: 30/30
direct-sampling points under flags agree with the stratified estimate at the same p_X and
30/30 with the p_X = 1e-9
failure fractions re-weighted; d_Z transfers 146/146
(p_Z = 1e-3) and 132/132
(p_Z = 1e-2); p_X transfers 24/24.  Strata in which sampling saw no failure enter the upper bound
at the smaller of their Wilson bound and an analytic bound from the code distance and the decoder's
costs (FINDINGS 7b; 1139 sampled strata checked against it,
0 violations) or the false-flag pair bounds; strata never sampled enter
at their bound or with failure probability one.  Overheads are stated from the central rate and,
where it differs, from the 95 % upper bound.  Phase flips below ~1e-9 are model extrapolations
(labelled; held-out checks in `phase_model.md`); the two phase-flip models (paper's fit, this
work's) are carried side by side.

## 4. Overhead against the published floor

Against the published 88 (paper's phase-flip fit) and against this work's own flag-free baseline
with its phase-flip model (77.3; the 88 → 77.3
difference is the phase-flip extrapolation alone, §3 of FINDINGS):

| setting (p_Z = 1e-3, η = 1e6, 1e-12) | paper pZL | fewer than 88 | this-work pZL | fewer than its flag-free |
|---|---|---|---|---|
| no flags | 88.0 ([15,6,5], d_Z = 17) | 0 % | 77.3 ([15,6,5], d_Z = 15) | – |
| idle-only flags, f = 0.99, exact timing | 88.0 ([15,6,5], d_Z = 17) | 0 % | 51.6 ([15,9,3], d_Z = 15) | 33 % (marginal: with the 95 % upper bound of p_XL 77.3) |
| idle-only flags, f = 0.99, 4096-tick windows | 88.0 ([15,6,5], d_Z = 17) | 0 % | 77.3 ([15,6,5], d_Z = 15) | 0 % |
| flags on all locations, f = 0.8, exact | 58.7 ([15,9,3], d_Z = 17) | 33 % | 51.6 ([15,9,3], d_Z = 15) | 33 % |
| flags on all locations, f = 0.9, 4096-tick windows | 58.7 ([15,9,3], d_Z = 17) | 33 % | 51.6 ([15,9,3], d_Z = 15) | 33 % |
| any flags, Hamming outer codes included | 32.6 | 63 % | 32.6 | 58 % |

p_Z = 1e-2, η = 1e6 (published: the fits bottom out near 2e-9 for [15,9,3] and 2e-11 for [15,6,5]
with two ancillas, neither reaches 1e-12).  Without flags this work finds
4.7e-9 and
2.1e-11 with the paper's phase-flip fit
(1.2e-8 and
1.8e-10 with this work's).  With flags
on all locations at f = 0.99 the floors fall to
4.4e-11 ([15,9,3]) and
5.3e-15 ([15,6,5], two
ancillas), and [15,6,5] reaches 1e-12 at 269.3
qubits per logical qubit (paper pZL; 472.0
this-work pZL; with p_XL at its 95 % upper bound 269.3 and
not reached).  Full table: FINDINGS §6.

## 5. The frontier

Non-dominated over codes (the paper's and four Hamming-family alternatives), decoders and every
flag setting, at p_Z = 1e-3, η = 1e6, 1e-12 with the conservative bit-flip bound (this-work pZL;
the paper-pZL version is in FINDINGS §7):

| overhead | code | d_Z | p_L | f needed | flags on | coarsest window | false flags tolerated |
|---|---|---|---|---|---|---|---|
| 32.6 | Hamming [63,57,3] | 15 | 4.6e-13 | 0.99 | all | 64 | 0 |
| 35.7 | Hamming [31,26,3] | 15 | 5.0e-13 | 0.95 | all | exact | 0 |
| 35.7 | Hamming [31,26,3] | 15 | 6.1e-13 | 0.99 | all | 256 | 0 |
| 42.2 | Hamming [15,11,3] | 15 | 5.7e-13 | 0.8 | all | exact | 0 |
| 42.2 | Hamming [15,11,3] | 15 | 4.3e-13 | 0.99 | all | 4096 | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 8.3e-13 | 0.5 | all | exact | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 8.5e-13 | 0.8 | idle | 4 | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 7.3e-13 | 0.9 | idle | 64 | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 8.2e-13 | 0.99 | idle | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 7.5e-13 | 0.8 | all | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 6.0e-13 | 0.8 | all | 16 | 1e-08 |
| 51.6 | [15,9,3] | 15 | 6.3e-13 | 0.8 | all | 4 | 1e-07 |
| 51.6 | [15,9,3] | 15 | 4.7e-13 | 0.9 | all | 16 | 1e-07 |
| 51.6 | [15,9,3] | 15 | 6.1e-13 | 0.99 | all | 64 | 1e-06 |
| 77.3 | [15,6,5] | 15 | 1.7e-13 | 0.0 | none | any (no flags) | 0 |

Pushed outward on the criterion furthest from its limit: overhead first (from 88 to the lowest
row above by admitting higher-rate outer codes), then the timing window (to 4096 ticks, longer
than the memory), then the flag efficiency.

## 6. Limits: which belong to the problem

| limit | why it belongs to the problem | evidence |
|---|---|---|
| overhead at p_Z = 1e-3 (each code at its phase-flip floor) | phase flips cannot be flagged; one step lower in d_Z they alone exceed the target; unchanged with an ideal decoder for the data blocks; any Elevator-type memory needs ≥ 25 qubits per logical qubit | `limits.md`, `phase_floor.md` |
| floors at p_Z = 1e-2 with perfect flags | the code's distance: ≥ d flagged events containing an undetectable logical, computed without a decoder | `limits.md`, `perfect_flags_exact.json` |
| flag efficiency required | set by unflagged bit flips under a decoder shown to be ML-optimal for the flag model (exact and coarse timing; [15,9,3] at p_Z = 1e-3, [15,6,5] in the p_Z = 1e-2 regime) | `decoder_optimality*.json`, `required_f_*.md` |
| timing precision | none within exact … 4096 ticks when gates are flagged | `flags_main_*.md` |
| false flags | with exact timing none up to 1e-06 per qubit per tick, the largest rate tested (95 % bound; the dominant strata bounded analytically, without decoding); with 64-tick windows up to 1e-06 (1e-06 central) | `assumptions.md`, `false_flag_bounds.json` |

## 7. What failed, what remains open

* No single circuit reproduces all three Z-memory fits: the full sweep matches [15,6,5], the
  shortest-path ancilla [15,9,3] and [16,3,8].  The paper's circuits are not public; the published
  overheads themselves are reproduced, and the X-memory gap is explained (counting convention).
* Whether flags exist during gates, preparation and measurement is a physics question this work
  cannot settle; it decides between the idle-only and all-location results above
  (arXiv:2607.01375 establishes idle flags only).
* The phase-flip floor at p_Z = 1e-3 rests on an extrapolation below sampling reach (model checked
  on held-out points); the paper's own extrapolation gives d_Z = 17 instead of 15.  Both are
  carried; every conclusion above holds under either.
* At p_Z = 1e-2 with timing windows the 95 % bounds are set by sampling: flagged-only strata with no failure in their samples (no analytic bound covers windows there), so 1e-12 is reached only in the central estimate for windows of 1, 4, 16, 64, 256, 1024, 4096 ticks ([15,6,5], f = 0.99, paper pZL).
* At p_Z = 1e-2 the floors with flags lie at d_Z = 39–121, beyond the largest elevator X memory sampled
  there (d_Z = 25, fitted within a factor 2); they are model extrapolations, marked as such.

