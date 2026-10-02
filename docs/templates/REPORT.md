# REPORT — each criterion of GOAL.md against the published floor

Published floor (arXiv:2601.10786 fits, PROBLEM.md): 88 qubits per logical qubit at p_Z = 1e-3,
η = 1e6, 1e-12 per round ([15,6,5], d_Z = 17); [15,9,3] needs η ≥ 1.8e6 (58.7); thin surface 125,
thin XZZX 145; at p_Z = 1e-2, η = 1e6 the fits bottom out near 2e-9 ([15,9,3]) and 2e-11
([15,6,5], two ancillas).  Rendered from `results/summary/numbers.json` by `./reproduce.sh`.

## 1. Fidelity to the source (flags off)

| check | result | status |
|---|---|---|
| Figures 1 and 2 from the paper's fits | identical: steps {{ " → ".join(f1(s["overhead"]) for s in N["fig1_elevator_steps"]) }} at η = {{ ", ".join(e2(s["eta"]) for s in N["fig1_elevator_steps"][1:]) }}; floors {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,9] 15_9_3 a1"]["pl"]) }}, {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,6] 15_6_5 a2"]["pl"]) }} | met |
| Published operating point and Fig. 1 from this work's flag-free simulation (paper's phase-flip fit) | {{ ohs("paper-pZL", "none|w0|f0.0") }} at η = 1e6; Fig. 1: {{ " → ".join(str(st["overhead"]) for st in N["fig1_this_work"]["paper-pZL"]["none|w0|f0.0"]) }} with steps at η = {{ ", ".join(e2(st["eta"]) for st in N["fig1_this_work"]["paper-pZL"]["none|w0|f0.0"][1:]) }} (published 187 → 93.5 → 88 → 58.7 at 6.7e4, 1.21e5, 1.76e6) | met |
| Z memory [15,6,5], one ancilla, 16 sampled points | {{ int(N["repro"]["Z:15_6_5:a1:full/noop"]["within"]) }}/16 within 2× ({{ f2(N["repro"]["Z:15_6_5:a1:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_6_5:a1:full/noop"]["ratio_max"]) }}×) | met |
| Z memory [15,6,5], two ancillas | {{ int(N["repro"]["Z:15_6_5:a2:full/noop"]["within"]) }}/16 within 2× ({{ f2(N["repro"]["Z:15_6_5:a2:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_6_5:a2:full/noop"]["ratio_max"]) }}×) | met at 14 of 16 points |
| Z memory [15,9,3] | full sweep: {{ int(N["repro"]["Z:15_9_3:a1:full/noop"]["within"]) }}/16 within 2× ({{ f2(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_max"]) }}×); shortest-path ancilla: {{ N["schedule_comparison"]["15_9_3|a1|local"]["within2"] }}/{{ N["schedule_comparison"]["15_9_3|a1|local"]["n"] }} ({{ f2(N["schedule_comparison"]["15_9_3|a1|local"]["min"]) }}–{{ f2(N["schedule_comparison"]["15_9_3|a1|local"]["max"]) }}×) | met with the shortest-path ancilla; the main study keeps the (pessimistic) full sweep — explained below |
| X memory [15,9,3] (d_Z = 9, 11, 13; p_Z 5e-3 … 1e-2) | {{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd-minsum"]["ratio_min"]) }}–{{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd"]["ratio_max"]) }}× counting any of the k logical qubits; {{ f2(N["convention"]["x_repro_marginal"][0]) }}–{{ f2(N["convention"]["x_repro_marginal"][1]) }}× counting each logical qubit's errors (measured multiplicity {{ f1(N["convention"]["mX"]["15_9_3"]) }}) | met in the per-qubit count, which the paper's X fit evidently uses |
| Z memory [16,3,8] (needed only below η ≈ 7e4) | full sweep: {{ int(N["repro"]["Z:16_3_8:a1:full/noop"]["within"]) }}/{{ int(N["repro"]["Z:16_3_8:a1:full/noop"]["n"]) }} within 2× ({{ f1(N["repro"]["Z:16_3_8:a1:full/noop"]["ratio_min"]) }}–{{ f1(N["repro"]["Z:16_3_8:a1:full/noop"]["ratio_max"]) }}×); shortest-path ancilla: {{ f2(N["schedule_comparison"]["16_3_8|a1|local"]["min"]) }}–{{ f2(N["schedule_comparison"]["16_3_8|a1|local"]["max"]) }}× ({{ N["schedule_comparison"]["16_3_8|a1|local"]["n"] }} points) | met with the shortest-path ancilla (`schedule_comparison.md`); the main study keeps the full sweep — explained below |
| repetition code (paper's fit, App. B) | {{ f1(N["phase_rep_vs_paper"]["min"]) }}–{{ f1(N["phase_rep_vs_paper"]["max"]) }}× for d_Z ≤ 13 over p_Z = 1e-3 … 1.3e-2 (the fit was sampled to d_Z = 11) | met |

Disagreements explained by evidence, not tuned away (FINDINGS §1):
* The placement of idle noise is unstated.  The literal reading (idle noise on every waiting
  block) is {{ f1(N["repro_literal_range"][0]) }}–{{ f1(N["repro_literal_range"][1]) }}× above every published fit; without idle noise on blocks waiting during
  logical-operation ticks ("noop") [15,6,5] and the repetition code agree.  Every result is
  computed with the noop reading; the literal reading is kept as a sensitivity case.
* The X memory: a counting convention.  A failure flips {{ f1(N["convention"]["mX"]["15_9_3"]) }} of the
  9 logical qubits on average; counting each logical qubit's errors separately puts the same shots
  at {{ f2(N["convention"]["x_ratio_sum"][0]) }}–{{ f2(N["convention"]["x_ratio_sum"][1]) }}× the fit.  The
  paper's Z-memory fits instead match counting a failure once.  Every rate of this work counts a
  failure once (any of the k logical qubits) and divides by k; the per-qubit count changes no
  conclusion (FINDINGS 13e).  Decoders are ruled out (BP+OSD-CS7, BP+OSD-0, BP+LSD fail equally
  often on the same shots).
* [15,9,3] and [16,3,8] bit flips above their fits with the full-sweep ancilla: not the decoder
  (exact ML), not the check order or the number of outer rounds, but the unstated ancilla path —
  with the shortest path both agree within 2× at every point tested, while [15,6,5] (reproduced
  by the full sweep) then drops to {{ f2(N["schedule_comparison"]["15_6_5|a1|local"]["min"]) }}–{{ f2(N["schedule_comparison"]["15_6_5|a1|local"]["max"]) }}×.  No single path matches all three fits; the paper's
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
sampled failure fractions) and its held-out checks: {{ N["validation"]["agree"] }}/{{ N["validation"]["total"] }}
direct-sampling points under flags agree with the stratified estimate at the same p_X and
{{ N["validation_transfer"]["inside"] }}/{{ N["validation_transfer"]["total"] }} with the p_X = 1e-9
failure fractions re-weighted; d_Z transfers {{ N["transfer_check_main"]["agree"] }}/{{ N["transfer_check_main"]["total"] }}
(p_Z = 1e-3) and {{ N["pz1e2_transfer_checks"]["agree"] }}/{{ N["pz1e2_transfer_checks"]["total"] }}
(p_Z = 1e-2); p_X transfers {{ N["transfer_check_px"]["agree"] }}/{{ N["transfer_check_px"]["total"] }}.  Strata in which sampling saw no failure enter the upper bound
at the smaller of their Wilson bound and an analytic bound from the code distance and the decoder's
costs (FINDINGS 7b; {{ N["strata_caps"]["strata_checked"] }} sampled strata checked against it,
{{ N["strata_caps"]["violations"] }} violations) or the false-flag pair bounds; strata never sampled enter
at their bound or with failure probability one.  Overheads are stated from the central rate and,
where it differs, from the 95 % upper bound.  Phase flips below ~1e-9 are model extrapolations
(labelled; held-out checks in `phase_model.md`); the two phase-flip models (paper's fit, this
work's) are carried side by side.

## 4. Overhead against the published floor

Against the published 88 (paper's phase-flip fit) and against this work's own flag-free baseline
with its phase-flip model ({{ f1(ohv("this-work-pZL", "none|w0|f0.0")) }}; the 88 → {{ f1(ohv("this-work-pZL", "none|w0|f0.0")) }}
difference is the phase-flip extrapolation alone, §3 of FINDINGS):

| setting (p_Z = 1e-3, η = 1e6, 1e-12) | paper pZL | fewer than 88 | this-work pZL | fewer than its flag-free |
|---|---|---|---|---|
| no flags | {{ ohs("paper-pZL", "none|w0|f0.0") }} | {{ pct(1 - ohv("paper-pZL", "none|w0|f0.0") / 88) }} | {{ ohs("this-work-pZL", "none|w0|f0.0") }} | – |
| idle-only flags, f = 0.99, exact timing | {{ ohs("paper-pZL", "idle|w0|f0.99") }} | {{ pct(1 - ohv("paper-pZL", "idle|w0|f0.99") / 88) }} | {{ ohs("this-work-pZL", "idle|w0|f0.99") }} | {{ pct(1 - ohv("this-work-pZL", "idle|w0|f0.99") / ohv("this-work-pZL", "none|w0|f0.0")) }}{{ "" if (H["this-work-pZL"]["idle|w0|f0.99"]["main_cons"] or {}).get("overhead") == ohv("this-work-pZL", "idle|w0|f0.99") else " (marginal: with the 95 % upper bound of p_XL " + str(round((H["this-work-pZL"]["idle|w0|f0.99"]["main_cons"] or {}).get("overhead", 0), 1)) + ")" }} |
| idle-only flags, f = 0.99, 4096-tick windows | {{ ohs("paper-pZL", "idle|w4096|f0.99") }} | {{ pct(1 - ohv("paper-pZL", "idle|w4096|f0.99") / 88) }} | {{ ohs("this-work-pZL", "idle|w4096|f0.99") }} | {{ pct(1 - ohv("this-work-pZL", "idle|w4096|f0.99") / ohv("this-work-pZL", "none|w0|f0.0")) }} |
| flags on all locations, f = 0.8, exact | {{ ohs("paper-pZL", "all|w0|f0.8") }} | {{ pct(1 - ohv("paper-pZL", "all|w0|f0.8") / 88) }} | {{ ohs("this-work-pZL", "all|w0|f0.8") }} | {{ pct(1 - ohv("this-work-pZL", "all|w0|f0.8") / ohv("this-work-pZL", "none|w0|f0.0")) }} |
| flags on all locations, f = 0.9, 4096-tick windows | {{ ohs("paper-pZL", "all|w4096|f0.9") }} | {{ pct(1 - ohv("paper-pZL", "all|w4096|f0.9") / 88) }} | {{ ohs("this-work-pZL", "all|w4096|f0.9") }} | {{ pct(1 - ohv("this-work-pZL", "all|w4096|f0.9") / ohv("this-work-pZL", "none|w0|f0.0")) }} |
| any flags, Hamming outer codes included | {{ f1(N["headline"]["paper-pZL:best_flagged_all_codes"]) }} | {{ pct(1 - N["headline"]["paper-pZL:best_flagged_all_codes"] / 88) }} | {{ f1(N["headline"]["this-work-pZL:best_flagged_all_codes"]) }} | {{ pct(1 - N["headline"]["this-work-pZL:best_flagged_all_codes"] / ohv("this-work-pZL", "none|w0|f0.0")) }} |

p_Z = 1e-2, η = 1e6 (published: the fits bottom out near 2e-9 for [15,9,3] and 2e-11 for [15,6,5]
with two ancillas, neither reaches 1e-12).  Without flags this work finds
{{ e1(N["limits"]["p1e-2|[15,9,3]|none|paper-pZL"]["pL"]) }} and
{{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|none|paper-pZL"]["pL"]) }} with the paper's phase-flip fit
({{ e1(N["limits"]["p1e-2|[15,9,3]|none|this-work-pZL"]["pL"]) }} and
{{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|none|this-work-pZL"]["pL"]) }} with this work's).  With flags
on all locations at f = 0.99 the floors fall to
{{ e1(N["limits"]["p1e-2|[15,9,3]|f=0.99 all w=exact|paper-pZL"]["pL"]) }} ([15,9,3]) and
{{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|f=0.99 all w=exact|paper-pZL"]["pL"]) }} ([15,6,5], two
ancillas), and [15,6,5] reaches 1e-12 at {{ reach("p1e-2|[15,6,5]|f=0.99 all w=exact|paper-pZL") }}
qubits per logical qubit (paper pZL; {{ reach("p1e-2|[15,6,5]|f=0.99 all w=exact|this-work-pZL") }}
this-work pZL; with p_XL at its 95 % upper bound {{ reach("p1e-2|[15,6,5]|f=0.99 all w=exact|paper-pZL", True) }} and
{{ reach("p1e-2|[15,6,5]|f=0.99 all w=exact|this-work-pZL", True) }}).  Full table: FINDINGS §6.

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
| false flags | with exact timing none up to {{ g(N["assumptions"]["tolerance"]["all|w0|f0.99"]["max_r_conservative"]) }} per qubit per tick, the largest rate tested (95 % bound; the dominant strata bounded analytically, without decoding); with 64-tick windows up to {{ g(N["assumptions"]["tolerance"]["all|w64|f0.99"]["max_r_conservative"]) }} ({{ g(N["assumptions"]["tolerance"]["all|w64|f0.99"]["max_r_central"]) }} central) | `assumptions.md`, `false_flag_bounds.json` |

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
* At p_Z = 1e-2 the floors with flags lie at d_Z = {{ min(v["d"] for k, v in N["limits"].items() if k.startswith("p1e-2|") and "none" not in k) }}–{{ max(v["d"] for k, v in N["limits"].items() if k.startswith("p1e-2|") and "none" not in k) }}, beyond the largest elevator X memory sampled
  there (d_Z = 25, fitted within a factor 2); they are model extrapolations, marked as such.
{{ ("* False flags with 64-tick windows: between " + g(N["assumptions"]["tolerance"]["all|w64|f0.99"]["max_r_conservative"]) + " and " + g(N["assumptions"]["tolerance"]["all|w64|f0.99"]["max_r_central"]) + " per qubit per tick the 95 % upper bound, not the central estimate, exceeds the target: a sampling limit, not a property of the problem.") if N["assumptions"]["tolerance"]["all|w64|f0.99"]["max_r_conservative"] != N["assumptions"]["tolerance"]["all|w64|f0.99"]["max_r_central"] else "* False flags: with exact timing and with 64-tick windows the 95 % bounds meet the target up to the largest rate tested (1e-6 per qubit per tick); no open item." }}
