# FINDINGS — flagged bit flips in Elevator-code memories

What this work establishes, each claim with its evidence.  Every number below is rendered from
`results/summary/numbers.json` by `scripts/render_docs.py`, and every table and figure cited is in
`results/summary/`; `./reproduce.sh analysis` regenerates both from the raw results in `results/`
(`./reproduce.sh all` recomputes those too).  Methods: `docs/methods.md`.

Conventions.  Logical error rates are per inner repetition-code round and per logical qubit: a
shot fails if any of the k logical observables is wrong, and the rate is 1 − (1 − P_fail)^(1/(R k))
over its R rounds (the convention of the paper's Z-memory fits; item 4 and 13e for counting each
logical qubit separately).
Overhead = physical qubits (ancillas included) per logical qubit = n_b (2 d_Z − 1) / k.  The main
operating point is the paper's: p_Z = 1e-3, bias η = 1e6 (p_X = 1e-9), target 1e-12 per round.
Bit-flip rates at p_X ≤ 1e-8 lie far below direct sampling; they come from the stratified
estimator (exact Poisson weights × sampled conditional failure probabilities, §2) and are
marked as such in every table.  Phase flips cannot be flagged; two phase-flip models are carried
through every overhead: the paper's own fit (**paper pZL**) and this work's model (**this-work
pZL**, §3), so that each flag result is stated both against the published baseline and against
this work's own.

## The answer in brief

* **Flagging bit flips on every location cuts the overhead by a third at the paper's operating
  point.**  Without flags the minimum is {{ ohs("paper-pZL", "none|w0|f0.0") }} with the paper's
  phase-flip fit — the published 88, now recomputed from this work's own bit-flip simulation — or
  {{ ohs("this-work-pZL", "none|w0|f0.0") }} with this work's phase-flip model.  With flags on idle,
  gate, preparation and measurement locations at efficiency f = 0.9 it is
  {{ ohs("paper-pZL", "all|w0|f0.9") }} and {{ ohs("this-work-pZL", "all|w0|f0.9") }} respectively
  ({{ pct(1 - ohv("paper-pZL", "all|w0|f0.9") / ohv("paper-pZL", "none|w0|f0.0")) }} and
  {{ pct(1 - ohv("this-work-pZL", "all|w0|f0.9") / ohv("this-work-pZL", "none|w0|f0.0")) }} fewer
  qubits): the higher-rate [15,9,3] code becomes usable at η = 1e6.  §4.
* **Efficiency f ≈ 0.6–0.8 is enough, and timing hardly matters — if gates are flagged.**  The
  minimum efficiency for [15,9,3] at its phase-flip floor is
  {{ reqf("this-work-pZL", "15_9_3|a1", 15, "all", 0) }} with exactly timed flags and
  {{ reqf("this-work-pZL", "15_9_3|a1", 15, "all", 4096) }} with windows of 4096 CNOT layers, longer
  than the whole simulated memory (five outer rounds), i.e. a flag that only says *which qubit*
  flipped (this-work pZL; paper pZL at d_Z = 17: {{ reqf("paper-pZL", "15_9_3|a1", 17, "all", 0) }}
  and {{ reqf("paper-pZL", "15_9_3|a1", 17, "all", 4096) }}).  §4.
* **Idle-only flags — the case arXiv:2607.01375 establishes — are not enough.**
  {{ pct(N["checks"]["class_share"]["15_9_3:a1:d15"]["gate"]) }} of the bit flips that matter happen
  inside CNOTs (the rest while idle; preparation and measurement
  {{ f"{100 * (N['checks']['class_share']['15_9_3:a1:d15']['prep'] + N['checks']['class_share']['15_9_3:a1:d15']['meas']):.1f} %" }})
  and stay unflagged; [15,9,3] then saturates at
  p_XL = {{ e2(H["sim_15_9_3_d15"]["idle|w0|f1.0"]["pXL"]) }} per round (d_Z = 15, f = 1), barely
  below the target: with the paper's phase-flip fit no idle-only setting beats the flag-free 88
  ({{ ohs("paper-pZL", "idle|w0|f1.0") }} at f = 1); with this work's it needs f ≥
  {{ reqf("this-work-pZL", "15_9_3|a1", 15, "idle", 0) }} (central estimate; with the 95 % upper bound
  of p_XL: {{ reqf("this-work-pZL", "15_9_3|a1", 15, "idle", 0, 1) }}) and fails for windows of
  256 ticks or more.  Flags during gates are the open experimental question that decides the gain.  §4.
* **What remains is the phase-flip floor, which flags cannot lower.**  With flags the [15,9,3]
  memory at d_Z = 15 reaches p_L = p_ZL: its bit-flip part is gone and the overhead equals the
  code's phase-flip floor ({{ f1(pfloor("15_9_3|a1", 1e-3, 1e-12, "oh_model")) }} at d_Z =
  {{ pfloor("15_9_3|a1", 1e-3, 1e-12) }}), set by errors flags cannot reveal; the floor is the same for
  an ideal phase-flip decoder.  §3, §7, §8.
* **Bias.**  Flags move the bias at which [15,9,3] takes over from η ≈
  {{ e1(first_eta("paper-pZL", "none|w0|f0.0", "[15,9,3]")) }} (no flags; published ≈ 1.8e6) down to
  {{ e1(first_eta("paper-pZL", "all|w0|f0.9", "[15,9,3]")) }} (f = 0.9),
  {{ e1(first_eta("paper-pZL", "all|w0|f0.99", "[15,9,3]")) }} (f = 0.99) and to the whole range
  η ≥ 4e4 with perfect flags (paper pZL).  §5.
* **p_Z = 1e-2.**  See §6 for the lowest reachable rate and its overhead per flag setting.

## 1. The published results are reproduced, up to two unstated circuit details

1. **Figures 1 and 2 follow exactly from the paper's own fitted models.**  Recomputed overheads:
   {{ " → ".join(f1(s["overhead"]) for s in N["fig1_elevator_steps"]) }} with steps at η =
   {{ ", ".join(e2(s["eta"]) for s in N["fig1_elevator_steps"][1:]) }} (Fig. 1), thin surface code
   125, XZZX 145; at p_Z = 1e-2 the floors are
   {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,9] 15_9_3 a1"]["pl"]) }} ([15,9,3], d_Z =
   {{ N["fig2_from_fits_floors"]["pz=0.01"]["[15,9] 15_9_3 a1"]["d"] }}) and
   {{ e2(N["fig2_from_fits_floors"]["pz=0.01"]["[15,6] 15_6_5 a2"]["pl"]) }} ([15,6,5] with two
   ancillas, d_Z = {{ N["fig2_from_fits_floors"]["pz=0.01"]["[15,6] 15_6_5 a2"]["d"] }}).  Evidence:
   `fig1_from_paper_fits.png`, `fig2_from_paper_fits.png`, `numbers.json:fig1_elevator_steps`.

2. **The same figures follow from this work's flag-free simulation.**  With the paper's phase-flip
   fit and this work's bit-flip rates (stratified, p_X ≤ 2.5e-8), the steps of Fig. 1 come out as
   {{ "; ".join(f"{s['overhead']} ({s['code']}, d_Z = {s['d']}) from η = {e2(s['eta'])}" for s in N["fig1_this_work"]["paper-pZL"]["none|w0|f0.0"]) }}
   (published: 88 from 1.21e5, 58.7 from 1.76e6).  Evidence: `fig1_this_work_paper-pZL.md/.png`.

3. **The paper's circuits evidently carry no idle noise on blocks that wait during a
   logical-operation tick.**  With idle noise on every waiting block (the literal reading of Table
   I) the simulated rates are 2–9× above the published fits for both memories (Z memory:
   {{ int(N["repro"]["Z:15_9_3:a1:full/all"]["within"]) }}/16,
   {{ int(N["repro"]["Z:15_6_5:a1:full/all"]["within"]) }}/16 and
   {{ int(N["repro"]["Z:15_6_5:a2:full/all"]["within"]) }}/16 points within 2×; X memory
   {{ f1(N["repro"]["X:15_9_3:a1:full/all bplsd"]["ratio_min"]) }}–{{ f1(N["repro"]["X:15_9_3:a1:full/all bplsd"]["ratio_max"]) }}×);
   without it ("noop") [15,6,5] agrees at {{ int(N["repro"]["Z:15_6_5:a1:full/noop"]["within"]) }}/16
   points (ratios {{ f2(N["repro"]["Z:15_6_5:a1:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_6_5:a1:full/noop"]["ratio_max"]) }})
   and [15,6,5] with two ancillas at {{ int(N["repro"]["Z:15_6_5:a2:full/noop"]["within"]) }}/16
   ({{ f2(N["repro"]["Z:15_6_5:a2:full/noop"]["ratio_min"]) }}–{{ f2(N["repro"]["Z:15_6_5:a2:full/noop"]["ratio_max"]) }}).
   The same inner round makes the isolated repetition code agree with the paper's repetition-code
   fit within 0.7–1.5× for d_Z ≤ 13 (`phase_model.md`).  Evidence: `reproduction.md`,
   `results/variants/z_variants_v1.json`.

4. **The X-memory gap is a counting convention; the [15,9,3] bit-flip excess is bracketed by the
   unstated circuit details.**
   * *X memory.*  Counting a failure when any of the k logical observables is wrong and dividing by
     k (this work's convention throughout) puts the X memory at
     {{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd-minsum"]["ratio_min"]) }}–{{ f2(N["repro"]["X:15_9_3:a1:full/noop bplsd"]["ratio_max"]) }}×
     the published fit, at every d_Z and p_Z alike.  A phase flip of a block flips every logical X̄
     that contains it: a failure hits {{ f1(N["convention"]["mX"]["15_9_3"]) }} logical qubits on average
     ([15,6,5]: {{ f1(N["convention"]["mX"]["15_6_5"]) }}).  Counting each logical qubit's errors
     separately (the per-qubit marginal) the same shots give
     {{ f2(N["convention"]["x_ratio_sum"][0]) }}–{{ f2(N["convention"]["x_ratio_sum"][1]) }}× the fit, and all
     X-memory points {{ f2(N["convention"]["x_repro_marginal"][0]) }}–{{ f2(N["convention"]["x_repro_marginal"][1]) }}×
     (`counting_convention.json`).  The paper's Z-memory fits, by contrast, match the
     any-of-k convention ([15,6,5]: {{ f2([r["ratio_any"] for r in N["convention"]["rows"] if r["memory"] == "Z" and r["code"] == "15_6_5" and r["n_anc"] == 1][0]) }}×
     any-of-k, {{ f2([r["ratio_sum"] for r in N["convention"]["rows"] if r["memory"] == "Z" and r["code"] == "15_6_5" and r["n_anc"] == 1][0]) }}× per-qubit).
     Decoders are ruled out on the same shots: BP+OSD-CS7, BP+OSD-0 and BP+LSD fail equally often
     ({{ ", ".join(f"{k}: {v['fails']}" for k, v in N["checks"]["decoder_variants_flagfree"][0]["decoders"].items()) }}
     of {{ N["checks"]["decoder_variants_flagfree"][0]["shots"] }} shots, `decoder_variants_flagfree.json`).
     Every rate below uses the any-of-k convention; in the per-qubit convention all rates rise by
     these multiplicities and the conclusions of §4 hold (item 13e).
   * *[15,9,3] bit flips* are {{ f1(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_min"]) }}–{{ f1(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_max"]) }}×
     above the published fit ({{ int(N["repro"]["Z:15_9_3:a1:full/noop"]["within"]) }}/16 points within
     2×, the excess growing towards p_X = 1e-6).  Not the decoder: exact maximum likelihood leaves
     {{ f1(N["checks"]["sensitivity_summary"]["mle_min"]) }}–{{ f1(N["checks"]["sensitivity_summary"]["mle_max"]) }}×
     (`sensitivity_15_9_3.json`); not the check order (≤ {{ pct(N["checks"]["sensitivity_summary"]["order_dev"]) }})
     or the number of outer rounds (≤ {{ pct(N["checks"]["sensitivity_summary"]["rounds_dev"]) }}).  The
     ancilla path matters at d_Z < n + 1: a shortest-path ancilla instead of a full sweep brings
     [15,9,3] to {{ f2(N["schedule_comparison"]["15_9_3|a1|local"]["min"]) }}–{{ f2(N["schedule_comparison"]["15_9_3|a1|local"]["max"]) }}×
     but [15,6,5] to {{ f2(N["schedule_comparison"]["15_6_5|a1|local"]["min"]) }}–{{ f2(N["schedule_comparison"]["15_6_5|a1|local"]["max"]) }}×
     (`schedule_comparison.md`), and the idle-noise placement brackets it (idle noise only during
     CNOT layers: {{ f2(N["checks"]["z_variants"]["15_9_3|full/cnot-idle-only"][0]) }}–{{ f2(N["checks"]["z_variants"]["15_9_3|full/cnot-idle-only"][1]) }}×;
     literal: {{ f1(N["checks"]["z_variants"]["15_9_3|full/all-idle"][0]) }}–{{ f1(N["checks"]["z_variants"]["15_9_3|full/all-idle"][1]) }}×).
     No single reading of the text matches all three published Z-memory fits (the paper's
     [16,3,8] fit, needed only below η ≈ 7e4, is
     {{ f1(N["repro"]["Z:16_3_8:a1:full/noop"]["ratio_min"]) }}–{{ f1(N["repro"]["Z:16_3_8:a1:full/noop"]["ratio_max"]) }}× below
     this work's full-sweep rates, {{ f1(N["schedule_comparison"]["16_3_8|a1|local"]["min"]) }}–{{ f1(N["schedule_comparison"]["16_3_8|a1|local"]["max"]) }}×
     with the shortest path).  Consequence: this work's [15,9,3] baseline is pessimistic, by up to
     {{ f1(N["repro"]["Z:15_9_3:a1:full/noop"]["ratio_max"]) }}× at p_X ~ 1e-6 (within
     {{ f2(N["headline"]["sim_15_9_3_d15"]["none|w0|f0.0"]["pXL"] / (15 ** 2.33 * (37.18e-9) ** 1.94)) }}× of the
     fit at p_X = 1e-9), so flag gains measured against it are not inflated, and every flagged
     result is compared with this work's own flag-free baseline as well as the published one.

## 2. The decoder is optimal for its flag model; the estimator predicts held-out samples

5. **Exact most-likely-error decoding (integer program with window exclusivity) equals maximum
   likelihood where it matters.**  Exactly timed flags: on {{ N["checks"]["decoder_optimality"]["n"] }}
   sampled leading-order configurations of [15,9,3] (d_Z = 17) ML fails
   {{ N["checks"]["decoder_optimality"]["ml"] }} times and the MLE
   {{ N["checks"]["decoder_optimality"]["mle"] }} (BP+OSD-CS7: {{ N["checks"]["decoder_optimality"]["bposd"] }}).
   Coarse timing (windows of {{ ", ".join(str(w) for w in N["checks"]["decoder_optimality_windows"]["windows"]) }}
   ticks), where ML is computed by enumerating every assignment of flagged events to the locations
   of their windows: ML {{ N["checks"]["decoder_optimality_windows"]["ml"] }} versus MLE
   {{ N["checks"]["decoder_optimality_windows"]["mle"] }} failures on
   {{ N["checks"]["decoder_optimality_windows"]["n"] }} configurations.  Evidence:
   `results/decoder_optimality.json`, `results/decoder_optimality_windows.json`.

6. **Known answers are met exactly.**  Repetition codes of distance 3, 5, 7, 9 with every flip
   flagged correct every pattern of up to d − 1 flips (all
   {{ N["checks"]["known_answers"]["KA1_code_capacity_rep9"]["patterns_below_d"] }} patterns for d = 9)
   and fail on exactly half the patterns when all d bits are erased; the same holds at circuit
   level.  [15,9,3] and [15,6,5] with perfect flags and no other noise correct every pattern of up
   to d − 1 erased blocks — at code capacity
   ({{ N["checks"]["known_answers"]["KA2_code_capacity_15_9_3"]["patterns_below_d"] }} and
   {{ N["checks"]["known_answers"]["KA2_code_capacity_15_6_5"]["patterns_below_d"] }} flip patterns)
   and in the full circuit ({{ N["checks"]["known_answers"]["KA2_circuit_15_9_3"]["patterns"] }} and
   {{ N["checks"]["known_answers"]["KA2_circuit_15_6_5"]["patterns"] }} patterns at three times) —
   and fail only on erasure sets that contain a codeword
   ({{ N["checks"]["known_answers"]["KA2_code_capacity_15_9_3"]["sets_with_failure_at_d"] }} and
   {{ N["checks"]["known_answers"]["KA2_code_capacity_15_6_5"]["sets_with_failure_at_d"] }} sets, the
   numbers of minimum-weight codewords).  Evidence: `results/known_answers.json`.

7. **The stratified estimator and its transfers predict held-out direct samples under flags.**
   Direct Monte Carlo against the stratified estimate at the same p_X:
   {{ N["validation"]["agree"] }}/{{ N["validation"]["total"] }} configurations agree within 95 %
   intervals; the failure fractions measured at p_X = 1e-9 (the ones behind every overhead),
   re-weighted to the held-out p_X, contain {{ N["validation_transfer"]["inside"] }}/{{ N["validation_transfer"]["total"] }}
   direct results (`validation.md`).  Transfer in d_Z: {{ N["transfer_check_main"]["agree"] }}/{{ N["transfer_check_main"]["total"] }}
   direct runs at d_Z = 17, 19 agree with the prediction from d_Z = 15 (`transfer_check.md`) and
   {{ N["pz1e2_transfer_checks"]["agree"] }}/{{ N["pz1e2_transfer_checks"]["total"] }} at p_Z = 1e-2
   (d_Z = 17 → 25, 33).  Exactly timed perfect flags need no decoding at all: their failure
   probability is the probability that the flagged events contain an undetectable logical, computed
   from 4e6 event sets per point (`perfect_flags_exact.json`; [15,9,3]: F(0,3) =
   {{ e2(N["checks"]["perfect_flags_exact"]["15_9_3|a1|d15"]["3"]) }}).

## 3. Phase flips: the floor that flags cannot lower

8. **The elevator's phase flips are those of its data blocks — isolated repetition codes — plus its
   moving logical ancilla, which behaves like a repetition code at ≈ {{ f1(N["phase_two_component"]["kappa"]) }}×
   the noise.**  Switching off the noise of the logical ancilla and of the logical-operation CNOTs
   brings the elevator to 1.0–1.8× (n_b/k) × the isolated repetition code; with it on the ratio grows
   with d_Z (to ~10 at d_Z = 21, p_Z = 1e-2).  Model: p_ZL k = n a p_rep(d, p) + n_anc g s(d)
   p_rep(d, κp), a = {{ f2(N["phase_two_component"]["a"]) }}, g = {{ f2(N["phase_two_component"]["g"]) }},
   κ = {{ f2(N["phase_two_component"]["kappa"]) }}.  This is the paper's lower elevator threshold
   (1/34.4 versus 1/25) made explicit.  Evidence: `phase_model.md`.

9. **The repetition-code model predicts held-out points.**  p_rep is fitted at each sampled p_Z as
   a straight line in (d_Z + 1)/2 through its large-d points (sampled down to 1.3e-9 per round at
   p_Z = 1e-3 and out to d_Z = 69 at p_Z ≥ 1.25e-2) and interpolated in log p.  Leaving out the
   largest-d point at each p_Z predicts it within
   {{ f2(min(h["ratio"] for h in N["phase_rep_fit"]["heldout"] if h["p"] <= 0.01)) }}–{{ f2(max(h["ratio"] for h in N["phase_rep_fit"]["heldout"] if h["p"] <= 0.01)) }}×
   for p_Z ≤ 1e-2, all inside their 95 % intervals.  The two-component elevator model fitted on
   p_Z ≥ 3e-3 predicts the held-out low-p elevator points within
   {{ f2(min(h["ratio"] for h in N["phase_two_component_heldout"])) }}–{{ f2(max(h["ratio"] for h in N["phase_two_component_heldout"])) }}×
   (below the measured values; the final model includes them).

10. **Phase-flip floor at p_Z = 1e-3: d_Z = {{ pfloor("15_9_3|a1", 1e-3, 1e-12) }} for both codes**
    (overhead {{ f1(pfloor("15_9_3|a1", 1e-3, 1e-12, "oh_model")) }} for [15,9,3],
    {{ f1(pfloor("15_6_5|a1", 1e-3, 1e-12, "oh_model")) }} for [15,6,5],
    {{ f1(pfloor("15_6_5|a2", 1e-3, 1e-12, "oh_model")) }} with two ancillas), the same with an
    ideal decoder for the data blocks; the paper's fit puts it at d_Z = 17.  At d_Z = 15 the paper's
    fit gives {{ e1(N["convention"]["phase_compare"]["[15,9,3]|d15"]["paper"]) }} for [15,9,3] and this
    work's model {{ e1(N["convention"]["phase_compare"]["[15,9,3]|d15"]["this_work"]) }}.  Part of the
    gap is the counting convention (item 4: the paper's X fit counts per logical qubit; in this work's
    any-of-k count the fit would be {{ e1(N["convention"]["phase_compare"]["[15,9,3]|d15"]["paper_anyofk"]) }},
    below 1e-12 as well), the rest is the extrapolation below sampling reach: the paper's elevator fit
    decays by 0.042 per step of d_Z at p_Z = 1e-3, while the repetition code sampled at p_Z = 1e-3
    decays by {{ "%.3f" % [t["step_ratio"] for t in N["phase_rep_fit"]["table"] if t["p"] == 0.001][0] }} per step
    (the paper's own repetition-code fit: 0.026).  Counting per logical qubit, this work's model gives
    {{ e1(N["convention"]["phase_compare"]["[15,9,3]|d15"]["this_work_perqubit"]) }} at d_Z = 15: the floor
    stays at 15 in either count.  Evidence: `phase_floor.md`, `phase_model.md`, `counting_convention.json`.

## 4. Flagged bit flips at p_Z = 1e-3, η = 1e6

11. **Gate flags decide the gain.**  At d_Z = 15 the [15,9,3] bit-flip rate (stratified estimate,
    95 % interval) is {{ e2(H["sim_15_9_3_d15"]["none|w0|f0.0"]["pXL"]) }} without flags,
    {{ e2(H["sim_15_9_3_d15"]["idle|w0|f0.99"]["pXL"]) }} with idle-only flags at f = 0.99 and
    {{ e2(H["sim_15_9_3_d15"]["idle|w0|f1.0"]["pXL"]) }} at f = 1, but
    {{ e2(H["sim_15_9_3_d15"]["idle+gate|w0|f0.99"]["pXL"]) }} with idle and gate flags at f = 0.99
    and {{ e2(H["sim_15_9_3_d15"]["all|w0|f0.99"]["pXL"]) }} with preparation and measurement flags
    added; with every location flagged at f = 1 and exact timing the rate is
    {{ e2(H["sim_15_9_3_d15"]["all|w0|f1.0"]["pXL"]) }} (only sets of ≥ 3 flagged events that
    contain an undetectable logical fail).  Evidence: `flags_main_*.md`, `assumptions.md`.

12. **Minimum overhead across f ∈ [0, 1] and timing from exact to 4096 CNOT layers.**  Full grid:
    `flags_main_paper-pZL.md`, `flags_main_this-work-pZL.md`, `map_f_window_this-work-pZL.png`,
    `overhead_vs_flags_*.png`; summary (`headline.md`):

    | flags on | window | f | paper pZL | this-work pZL |
    |---|---|---|---|---|
    | none | – | 0 | {{ ohs("paper-pZL", "none|w0|f0.0") }} | {{ ohs("this-work-pZL", "none|w0|f0.0") }} |
    | idle | exact | 0.99 | {{ ohs("paper-pZL", "idle|w0|f0.99") }} | {{ ohs("this-work-pZL", "idle|w0|f0.99") }} |
    | idle | exact | 1 | {{ ohs("paper-pZL", "idle|w0|f1.0") }} | {{ ohs("this-work-pZL", "idle|w0|f1.0") }} |
    | idle | 4096 | 0.99 | {{ ohs("paper-pZL", "idle|w4096|f0.99") }} | {{ ohs("this-work-pZL", "idle|w4096|f0.99") }} |
    | idle + gate | exact | 0.99 | {{ ohs("paper-pZL", "idle+gate|w0|f0.99") }} | {{ ohs("this-work-pZL", "idle+gate|w0|f0.99") }} |
    | all | exact | 0.5 | {{ ohs("paper-pZL", "all|w0|f0.5") }} | {{ ohs("this-work-pZL", "all|w0|f0.5") }} |
    | all | exact | 0.8 | {{ ohs("paper-pZL", "all|w0|f0.8") }} | {{ ohs("this-work-pZL", "all|w0|f0.8") }} |
    | all | exact | 0.9 | {{ ohs("paper-pZL", "all|w0|f0.9") }} | {{ ohs("this-work-pZL", "all|w0|f0.9") }} |
    | all | 1 | 0.99 | {{ ohs("paper-pZL", "all|w1|f0.99") }} | {{ ohs("this-work-pZL", "all|w1|f0.99") }} |
    | all | 64 | 0.99 | {{ ohs("paper-pZL", "all|w64|f0.99") }} | {{ ohs("this-work-pZL", "all|w64|f0.99") }} |
    | all | 1024 | 0.99 | {{ ohs("paper-pZL", "all|w1024|f0.99") }} | {{ ohs("this-work-pZL", "all|w1024|f0.99") }} |
    | all | 4096 | 0.9 | {{ ohs("paper-pZL", "all|w4096|f0.9") }} | {{ ohs("this-work-pZL", "all|w4096|f0.9") }} |
    | all | 4096 | 1 | {{ ohs("paper-pZL", "all|w4096|f1.0") }} | {{ ohs("this-work-pZL", "all|w4096|f1.0") }} |

    A window of 1 tick is one CNOT layer; an inner round is 4 ticks, an outer round of [15,9,3] at
    d_Z = 15 about 600 ticks, the whole simulated memory (5 outer rounds) about 3000.

13. **[15,6,5] needs no flags at η = 1e6 and gains nothing from them**: its bit flips are already
    far below the target at d_Z = 15 (p_XL ≈ {{ e1(H["this-work-pZL"]["none|w0|f0.0"]["[15,6,5]"]["pXL"]) }}),
    so its overhead is its phase-flip floor with or without flags; flags pay through the switch to
    the higher-rate [15,9,3].

13b. **False flags cost nothing up to 1e-6 per qubit per tick when timing is exact.**  [15,9,3]
    at f = 0.99 on all locations: p_XL = {{ pxl3("falseflag|all|w0|f0.99|r0|erasure") }} without false
    flags, {{ pxl3("falseflag|all|w0|f0.99|r1e-08|erasure") }} at r = 1e-8 and
    {{ pxl3("falseflag|all|w0|f0.99|r1e-06|erasure") }} at r = 1e-6 (95 % intervals; the single- and
    two-event strata are bounded analytically, `false_flag_bounds.json`: a failure needs falsely
    flagged locations that complete the real events to a logical, and with exact timing the decoder
    never prefers two flags over one).  With 64-tick windows the central estimates are unchanged up
    to 1e-6 ({{ pxl3("falseflag|all|w64|f0.99|r1e-06|erasure") }}) but the upper bounds are limited by
    sampling.  Full sweep, including f = 0.8–0.9 with 4–16-tick windows (the regime a photon-counting
    threshold would select): `assumptions.md`.

13c. **Heralded flags (a flag certifies the X) versus erasures (the event's X occurs with
    probability ½).**  [15,9,3] at f = 0.99: idle-only {{ pxl3("herald|idle|w0|f0.99|r0|herald") }}
    (heralded) vs {{ pxl3("herald|idle|w0|f0.99|r0|erasure") }} (erasure); all locations
    {{ pxl3("herald|all|w0|f0.99|r0|herald") }} vs {{ pxl3("herald|all|w0|f0.99|r0|erasure") }}
    (`assumptions.md`).

13d. **The idle-noise reading moves both error types but not the conclusion.**  Under the literal
    reading the [15,9,3] bit flips are ×{{ f1(asm("literal|none|w0|f0.0|ratio_15_9_3")) }} higher
    without flags (d_Z = 17), the repetition code's phase flips ×4–30 (extra idle ticks,
    `literal_reading.md`) and the phase-flip floor moves to d_Z =
    {{ N["literal"]["floor|[15,9,3]"]["d_literal"] }}: flag-free {{ f1(N["literal"]["floor|[15,6,5]"]["overhead_literal"]) }},
    flagged {{ f1(N["literal"]["floor|[15,9,3]"]["overhead_literal"]) }} — the same one-third saving.

13e. **The counting convention does not change the conclusion.**  Counting each logical qubit's
    errors separately multiplies the phase-flip rates by {{ f1(N["convention"]["mX"]["15_9_3"]) }}
    ([15,9,3]) and {{ f1(N["convention"]["mX"]["15_6_5"]) }} ([15,6,5]) and the bit-flip rates by
    {{ f1(N["convention"]["mZ"]["15_9_3|a1"]) }} and {{ f1(N["convention"]["mZ"]["15_6_5|a1"]) }}
    (measured, item 4); with every rate counted that way the minimum overhead (this-work pZL) is
    {{ f1(N["convention"]["headline_marginal"]["none|w0|f0.0"]["overhead"]) }} without flags,
    {{ f1(N["convention"]["headline_marginal"]["idle|w0|f1.0"]["overhead"]) }} with idle-only flags at f = 1,
    {{ f1(N["convention"]["headline_marginal"]["all|w0|f0.8"]["overhead"]) }} at f = 0.8 and
    {{ f1(N["convention"]["headline_marginal"]["all|w0|f0.9"]["overhead"]) }} at f = 0.9 on all locations
    ({{ f1(N["convention"]["headline_marginal"]["all|w4096|f0.99"]["overhead"]) }} with 4096-tick windows at
    f = 0.99): the efficiency needed rises from ≈ 0.6 to ≈ 0.85, the saving is the same.

## 5. Bias from 4e4 to 1e7

14. **Flags let [15,9,3] serve at lower bias** (Fig. 1 recomputed with flags,
    `fig1_this_work_*.md/.png`): with the paper's phase-flip fit it is the cheapest code from
    η = {{ e2(first_eta("paper-pZL", "none|w0|f0.0", "[15,9,3]")) }} without flags,
    {{ e2(first_eta("paper-pZL", "idle|w0|f0.99", "[15,9,3]")) }} with idle-only flags (f = 0.99),
    {{ e2(first_eta("paper-pZL", "all|w0|f0.9", "[15,9,3]")) }} (all locations, f = 0.9),
    {{ e2(first_eta("paper-pZL", "all|w0|f0.99", "[15,9,3]")) }} (f = 0.99),
    {{ e2(first_eta("paper-pZL", "all|w1024|f0.99", "[15,9,3]")) }} (f = 0.99, 1024-tick windows) and
    over the whole range with perfect flags; with this work's phase-flip model the same thresholds
    are {{ e2(first_eta("this-work-pZL", "none|w0|f0.0", "[15,9,3]")) }},
    {{ e2(first_eta("this-work-pZL", "idle|w0|f0.99", "[15,9,3]")) }},
    {{ e2(first_eta("this-work-pZL", "all|w0|f0.9", "[15,9,3]")) }},
    {{ e2(first_eta("this-work-pZL", "all|w0|f0.99", "[15,9,3]")) }} and
    {{ e2(first_eta("this-work-pZL", "all|w1024|f0.99", "[15,9,3]")) }}.  The bit-flip rates at other
    p_X re-weight the p_X = 1e-9 failure fractions with exact intensities (validated in §2, item 7).

## 6. p_Z = 1e-2, η = 1e6: the lowest reachable rate and its overhead

15. **Without flags this work reproduces the published floors where its bit-flip rates agree with
    the fits.**  With the paper's phase-flip fit the flag-free floors are
    {{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|none|paper-pZL"]["pL"]) }} ([15,6,5], two ancillas, d_Z =
    {{ N["limits"]["p1e-2|[15,6,5] 2 anc|none|paper-pZL"]["d"] }}; published 2.08e-11 at 49) and
    {{ e1(N["limits"]["p1e-2|[15,9,3]|none|paper-pZL"]["pL"]) }} ([15,9,3], d_Z =
    {{ N["limits"]["p1e-2|[15,9,3]|none|paper-pZL"]["d"] }}; published 1.94e-9 at 39, the gap being the
    [15,9,3] bit-flip excess of item 4).  This work's phase-flip model, which decays more slowly at
    large d_Z (the moving ancilla, §3), puts them higher:
    {{ e1(N["limits"]["p1e-2|[15,6,5] 2 anc|none|this-work-pZL"]["pL"]) }} and
    {{ e1(N["limits"]["p1e-2|[15,9,3]|none|this-work-pZL"]["pL"]) }}.

16. **Flags push the memory past the bit-flip wall.**  Lowest p_L per flag setting (phase flips
    beyond d_Z ≈ 70 are extrapolations of the phase-flip model, marked), the overhead at which 1e-12
    is reached, and what the floor is made of (`pz1e2_*.md`, `limits.md`, `fig2_this_work_*.md`):

{{ N["md"]["pz1e2_table"] }}

    With flags on all locations [15,6,5] reaches 1e-12 — which neither code reaches without flags —
    at {{ f1(N["limits"]["p1e-2|[15,6,5]|f=0.99 all w=exact|paper-pZL"]["reach"]) }} qubits per logical
    qubit (paper pZL; {{ f1(N["limits"]["p1e-2|[15,6,5]|f=0.99 all w=exact|this-work-pZL"]["reach"]) }}
    with this work's phase-flip model), and its floor drops by 3–4 orders of magnitude.  [15,9,3]
    stays above 1e-12 even with perfect flags: there its floor is made of sets of ≥ 3 flagged events
    that contain an undetectable logical — its distance.

## 7. Alternatives and the frontier

17. **Higher-rate outer codes become usable with flags, and push the overhead towards the bare
    repetition-code floor.**  The frontier at p_Z = 1e-3, η = 1e6 over every code, decoder and flag
    setting simulated — Hamming [15,11,3], [31,26,3], [63,57,3] and extended Hamming [16,11,4]
    besides the paper's codes — requiring p_L ≤ 1e-12 with the 95 % upper bound of p_XL
    (`frontier_*.md`; this-work pZL):

{{ N["md"]["frontier_req_this-work-pZL"] }}

    and with the paper's phase-flip fit:

{{ N["md"]["frontier_req_paper-pZL"] }}

    Each step outward came from relaxing the criterion furthest from its limit: the overhead (codes
    of higher rate, which flags make admissible), then the timing window (to 4096 ticks), then the
    efficiency.  The decoder axis is closed: the MLE is ML at the leading order (item 5) and
    BP+OSD is worse on the same configurations.  Lowest p_L per code and d_Z and what it takes:

{{ N["md"]["frontier_rate_this-work-pZL"] }}

## 8. Limits

18. **Every remaining limit is one of three properties of the problem** (`limits.md`):
    * *Phase flips, which flags cannot reveal.*  At p_Z = 1e-3 every code on the frontier sits at
      its phase-flip floor: one step lower in d_Z its phase flips alone exceed 1e-12, at the floor its
      bit flips are orders of magnitude below them (e.g. [15,9,3]: p_ZL(13) =
      {{ e2(N["limits"]["p1e-3|[15,9,3]|this-work-pZL"]["pZL_below"]) }}, p_ZL(15) =
      {{ e2(N["limits"]["p1e-3|[15,9,3]|this-work-pZL"]["pZL"]) }}, lowest p_XL(15) =
      {{ e2(N["limits"]["p1e-3|[15,9,3]|this-work-pZL"]["pXL"]) }}).  The floor does not move with an
      ideal decoder for the data blocks (§3), and no Elevator-type memory can go below
      {{ N["limits"]["absolute_floor|0.001|1e-12"]["overhead"] }} qubits per logical qubit at this
      operating point (one repetition-code block of distance
      {{ N["limits"]["absolute_floor|0.001|1e-12"]["d_rep"] }} per logical qubit, k/n → 1, no ancilla).
    * *The code distance.*  With perfect, exactly timed flags failures need ≥ d flagged events that
      contain an undetectable logical (computed without a decoder, item 7); at p_Z = 1e-2 this
      sets the [15,9,3] and Hamming floors (flagged-only share
      {{ f2(N["limits"]["p1e-2|[15,9,3]|f=1.0 all w=exact|this-work-pZL"]["flagged_only"] / N["limits"]["p1e-2|[15,9,3]|f=1.0 all w=exact|this-work-pZL"]["pL"]) }}
      of the [15,9,3] floor).
    * *Unflagged bit flips, i.e. the flag efficiency (and which locations can raise flags).*  With
      f < 1 the remaining bit flips involve unflagged errors (shares in `limits.md`); the efficiency
      needed is that of an ML-optimal decoder (item 5), so it is a property of the code and the flag
      model, not of this decoder.
    Timing precision is not a limit anywhere in the range tested when gates are flagged.  The
    remaining open problems — the two fit-level reproduction residuals, and whether flags exist
    during gates — are listed in `REPORT.md`.
