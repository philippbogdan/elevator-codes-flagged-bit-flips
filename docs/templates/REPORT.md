# REPORT — each criterion of GOAL.md against the published floor

Published floor (arXiv:2601.10786 fits, PROBLEM.md): 88 qubits per logical qubit at p_Z = 1e-3,
η = 1e6, 1e-12 per round ([15,6,5], d_Z = 17); [15,9,3] needs η ≥ 1.8e6 (58.7); thin surface 125,
thin XZZX 145; at p_Z = 1e-2, η = 1e6 the fits bottom out near 2e-9 ([15,9,3]) and 2e-11
([15,6,5], two ancillas).  Rendered from `results/summary/numbers.json` by `./reproduce.sh`.

## 1. Fidelity to the source (flags off)

| check | result | status |
|---|---|---|
| Figures 1 and 2 from the paper's fits | identical: steps {{ " → ".join(f1(s["overhead"]) for s in N["fig1_elevator_steps"]) }} at η = {{ ", ".join(e2(s["eta"]) for s in N["fig1_elevator_steps"][1:]) }}; floors {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,9] 15_9_3 a1"]["pl"]) }}, {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,6] 15_6_5 a2"]["pl"]) }} | met |
| Published operating point from this work's flag-free simulation (paper's phase-flip fit) | {{ ohs("paper-pZL", "none|w0|f0.0") }} at η = 1e6; Fig. 1 steps at η = {{ ", ".join(e2(s["eta"]) for s in N["fig1_this_work"]["paper-pZL"]["none|w0|f0.0"]) }} (published 6.7e4, 1.21e5, 1.76e6) | met |
| Z memory [15,6,5], one ancilla, 16 sampled points | {{ int(N["repro"]["Z:15_6_5:a1:full/noop"]["within"]) }}/16 within 2× ({{ f2(N["repro"]["Z:15_6_5:a1:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_6_5:a1:full/noop"]["ratio_max"]) }}×) | met |
| Z memory [15,6,5], two ancillas | {{ int(N["repro"]["Z:15_6_5:a2:full/noop"]["within"]) }}/16 within 2× ({{ f2(N["repro"]["Z:15_6_5:a2:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_6_5:a2:full/noop"]["ratio_max"]) }}×) | met at 14 of 16 points |
| Z memory [15,9,3] | {{ int(N["repro"]["Z:15_9_3:a1:full/noop"]["within"]) }}/16 within 2× ({{ f2(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_max"]) }}×) | **not met at low p_X** — explained below |
| X memory [15,9,3] (d_Z = 9, 11, 13; p_Z 5e-3 … 1e-2) | {{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd-minsum"]["ratio_min"]) }}–{{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd"]["ratio_max"]) }}× | **just outside 2×** — explained below |
| repetition code (paper's fit, App. B) | 0.7–1.5× for d_Z ≤ 13 over p_Z = 1e-3 … 1.3e-2 (the fit was sampled to d_Z = 11) | met |

Disagreements explained by evidence, not tuned away (FINDINGS §1):
* The placement of idle noise is unstated.  The literal reading (idle noise on every waiting
  block) is 2–9× above every published fit; without idle noise on blocks waiting during
  logical-operation ticks ("noop") [15,6,5] and the repetition code agree.  Every result is
  computed with the noop reading; the literal reading is kept as a sensitivity case.
* [15,9,3] Z memory 1.4–3.8× above its fit, the X memory ≈ 0.4–0.5×: not the decoder (exact ML;
  BP+OSD-CS7, BP+OSD-0, BP+LSD equal on the same X-memory shots), not the check order, the number
  of outer rounds or the schedule variant.  The published fits lie between readings of the
  unstated idle-noise placement for both (cnot-only idle noise: [15,9,3] at 0.55–0.85×; literal:
  X memory at 2.3–2.5×).  The exact circuit is not recoverable from the text.  Impact: this work's
  [15,9,3] bit-flip baseline is pessimistic, so flag gains measured against it are not inflated.

## 2. Known answers

Met exactly (FINDINGS item 6): repetition codes with every flip flagged correct every pattern of
up to d − 1 flips; [15,9,3] and [15,6,5] with perfect flags correct every pattern of up to d − 1
erased blocks, at code capacity and in the full circuit, by enumeration.

## 3. Statistics

Every rate has a 95 % interval from its sampled failures; the bit-flip rates at p_X ≤ 1e-8 are
labelled as below sampling reach and come with their model (Poisson strata, exact intensities,
sampled failure fractions) and its held-out checks: {{ N["validation"]["agree"] }}/{{ N["validation"]["total"] }}
direct-sampling points under flags agree with the stratified estimate at the same p_X and
{{ N["validation_transfer"]["inside"] }}/{{ N["validation_transfer"]["total"] }} with the p_X = 1e-9
failure fractions re-weighted; d_Z transfers {{ N["transfer_check_main"]["agree"] }}/{{ N["transfer_check_main"]["total"] }}
(p_Z = 1e-3) and {{ N["pz1e2_transfer_checks"]["agree"] }}/{{ N["pz1e2_transfer_checks"]["total"] }}
(p_Z = 1e-2).  Phase flips below ~1e-9 are model extrapolations (labelled; held-out checks in
`phase_model.md`); the two phase-flip models (paper's fit, this work's) are carried side by side.

## 4. Overhead against the published floor

| setting (p_Z = 1e-3, η = 1e6, 1e-12) | paper pZL | this-work pZL | vs 88 |
|---|---|---|---|
| no flags | {{ ohs("paper-pZL", "none|w0|f0.0") }} | {{ ohs("this-work-pZL", "none|w0|f0.0") }} | {{ pct(1 - ohv("paper-pZL", "none|w0|f0.0") / 88) }} / {{ pct(1 - ohv("this-work-pZL", "none|w0|f0.0") / 88) }} fewer |
| idle-only flags, f = 1, exact timing | {{ ohs("paper-pZL", "idle|w0|f1.0") }} | {{ ohs("this-work-pZL", "idle|w0|f1.0") }} | {{ pct(1 - ohv("paper-pZL", "idle|w0|f1.0") / 88) }} / {{ pct(1 - ohv("this-work-pZL", "idle|w0|f1.0") / 88) }} fewer |
| flags on all locations, f = 0.8, exact | {{ ohs("paper-pZL", "all|w0|f0.8") }} | {{ ohs("this-work-pZL", "all|w0|f0.8") }} | {{ pct(1 - ohv("paper-pZL", "all|w0|f0.8") / 88) }} / {{ pct(1 - ohv("this-work-pZL", "all|w0|f0.8") / 88) }} fewer |
| flags on all locations, f = 0.9, 4096-tick windows | {{ ohs("paper-pZL", "all|w4096|f0.9") }} | {{ ohs("this-work-pZL", "all|w4096|f0.9") }} | {{ pct(1 - ohv("paper-pZL", "all|w4096|f0.9") / 88) }} / {{ pct(1 - ohv("this-work-pZL", "all|w4096|f0.9") / 88) }} fewer |
| any flags, Hamming outer codes included | {{ f1(N["headline"]["paper-pZL:best_flagged_all_codes"]) }} | {{ f1(N["headline"]["this-work-pZL:best_flagged_all_codes"]) }} | {{ pct(1 - N["headline"]["paper-pZL:best_flagged_all_codes"] / 88) }} / {{ pct(1 - N["headline"]["this-work-pZL:best_flagged_all_codes"] / 88) }} fewer |

p_Z = 1e-2, η = 1e6 (published: the fits bottom out near 2e-9 for [15,9,3] and 2e-11 for [15,6,5]
with two ancillas, neither reaches 1e-12).  Without flags this work finds
{{ e1(N["limits"]["p1e-2|[15,9,3]|none|paper-pZL"]["pL"]) }} and
{{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|none|paper-pZL"]["pL"]) }} with the paper's phase-flip fit
({{ e1(N["limits"]["p1e-2|[15,9,3]|none|this-work-pZL"]["pL"]) }} and
{{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|none|this-work-pZL"]["pL"]) }} with this work's).  With flags
on all locations at f = 0.99 the floors fall to
{{ e1(N["limits"]["p1e-2|[15,9,3]|f=0.99 all w=exact|paper-pZL"]["pL"]) }} ([15,9,3]) and
{{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|f=0.99 all w=exact|paper-pZL"]["pL"]) }} ([15,6,5], two
ancillas), and [15,6,5] reaches 1e-12 at {{ f1(N["limits"]["p1e-2|[15,6,5]|f=0.99 all w=exact|paper-pZL"]["reach"]) }}
qubits per logical qubit (paper pZL; {{ f1(N["limits"]["p1e-2|[15,6,5]|f=0.99 all w=exact|this-work-pZL"]["reach"]) }}
this-work pZL).  Full table: FINDINGS §6.

## 5. The frontier

Non-dominated over codes (the paper's and four Hamming-family alternatives), decoders and every
flag setting, at p_Z = 1e-3, η = 1e6, 1e-12 with the conservative bit-flip bound (this-work pZL;
the paper-pZL version is in FINDINGS §7):

{{ N["md"]["frontier_req_this-work-pZL"] }}

Pushed outward on the criterion furthest from its limit: overhead first (from 88 to the lowest
row above by admitting higher-rate outer codes), then the timing window (to 4096 ticks, longer
than the memory), then the flag efficiency.

## 6. Limits: which belong to the problem

| limit | why it belongs to the problem | evidence |
|---|---|---|
| overhead at p_Z = 1e-3 (each code at its phase-flip floor) | phase flips cannot be flagged; one step lower in d_Z they alone exceed the target; unchanged with an ideal decoder for the data blocks; any Elevator-type memory needs ≥ {{ N["limits"]["absolute_floor|0.001|1e-12"]["overhead"] }} qubits per logical qubit | `limits.md`, `phase_floor.md` |
| floors at p_Z = 1e-2 with perfect flags | the code's distance: ≥ d flagged events containing an undetectable logical, computed without a decoder | `limits.md`, `perfect_flags_exact.json` |
| flag efficiency required | set by unflagged bit flips under a decoder shown to be ML-optimal for the flag model (exact and coarse timing) | `decoder_optimality*.json`, `required_f_*.md` |
| timing precision | none within exact … 4096 ticks when gates are flagged | `flags_main_*.md` |
| false flags | tolerated up to 1e-6 per qubit per tick with exact timing (rigorous upper bounds); windows of 64 ticks: central estimates unchanged to 1e-6, upper bounds sample-limited | `assumptions.md`, `false_flag_bounds.json` |

## 7. What failed, what remains open

* The fit-level reproduction of [15,9,3] (Z memory at p_X ≤ 4.5e-6) and of the X memory (≈ 0.45×)
  — bracketed by readings of the text, not resolved; the paper's circuits are not public.  The
  published overheads themselves are reproduced.
* Whether flags exist during gates, preparation and measurement is a physics question this work
  cannot settle; it decides between the idle-only and all-location results above
  (arXiv:2607.01375 establishes idle flags only).
* The phase-flip floor at p_Z = 1e-3 rests on an extrapolation below sampling reach (model checked
  on held-out points); the paper's own extrapolation gives d_Z = 17 instead of 15.  Both are
  carried; every conclusion above holds under either.
* At p_Z = 1e-2 the floors with flags lie at d_Z ≈ 50–130, beyond the sampled phase-flip range
  (d_Z ≤ 69); they are marked as extrapolations.
* False flags with coarse windows: the upper bounds are limited by sampling, not by a property of
  the problem; the central estimates show no effect up to 1e-6 per qubit per tick.
