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

* **Flagging bit flips on every location cuts the overhead of the paper's codes by a third.**
  Without flags the minimum at the paper's operating point is 88.0 ([15,6,5], d_Z = 17)
  with the paper's phase-flip fit — the published 88, recomputed from this work's own bit-flip
  simulation — or 77.3 ([15,6,5], d_Z = 15) with this work's phase-flip model.  With
  flags on idle, gate, preparation and measurement locations at efficiency f = 0.9 it is
  58.7 ([15,9,3], d_Z = 17) and 51.6 ([15,9,3], d_Z = 15)
  (33 % and
  33 % fewer qubits):
  the higher-rate [15,9,3] becomes usable at η = 1e6.  §4.
* **With flags, higher-rate outer codes take over.**  Over the codes tried (Hamming [15,11,3],
  [31,26,3], [63,57,3], extended Hamming [16,11,4]), flags on all locations at f = 0.99 reach
  35.7 (Hamming [31,26,3], d_Z = 15) (paper pZL) and
  32.6 (Hamming [63,57,3], d_Z = 15) (this-work pZL) —
  59 % fewer qubits than the published 88.  §7.
* **Idle-only flags — the case arXiv:2607.01375 establishes — help only with a distance-4 code.**
  40 % of the bit flips that matter happen
  inside CNOTs (the rest while idle; preparation and measurement
  0.3 %)
  and stay unflagged.  [15,9,3] then saturates at p_XL =
  8.39e-13 per round (d_Z = 15, f = 1), at the target
  (88.0 ([15,6,5], d_Z = 17) with the paper's phase-flip fit,
  51.6 ([15,9,3], d_Z = 15) with this work's but only in the central
  estimate).  The extended Hamming [16,11,4] tolerates the unflagged gate flips: with idle-only flags
  at f = 0.9 it reaches 44.8 (ext. Hamming [16,11,4], d_Z = 15)
  (51.0 (ext. Hamming [16,11,4], d_Z = 17) paper pZL), needing f ≥
  0.761 with exact timing and
  0.899 with 4096-tick windows
  (paper pZL at d_Z = 17: 0.827 and
  0.989).  §4, §7.
* **Efficiency f ≈ 0.6–0.8 is enough, and timing hardly matters — if gates are flagged.**  The
  minimum efficiency for [15,9,3] at its phase-flip floor is
  0.582 (between 0.5 and 0.8) with exactly timed flags and
  0.712 (between 0.5 and 0.8) with windows of 4096 CNOT layers, longer
  than the whole simulated memory (five outer rounds), i.e. a flag that only says *which qubit*
  flipped (this-work pZL; paper pZL at d_Z = 17: 0.653 (between 0.5 and 0.8)
  and 0.779 (between 0.5 and 0.8)).  Counting each logical qubit's errors
  separately raises the requirement to between 0.8 and
  0.9 (item 13e).  Idle-only flags need exact or near-exact
  timing.  §4.
* **What remains is the phase-flip floor, which flags cannot lower.**  With flags each code reaches
  p_L = p_ZL at its phase-flip floor (for [15,9,3]: 51.6
  at d_Z = 15), set by errors flags cannot reveal; the floor is the
  same for an ideal phase-flip decoder, and no Elevator-type memory can go below
  25 qubits per logical qubit at this operating
  point.  §3, §8.
* **Bias.**  Flags move the bias at which [15,9,3] takes over from η ≈
  2.2e6 (no flags; published ≈ 1.8e6) down to
  4.9e5 (f = 0.9),
  1.8e5 (f = 0.99) and to the whole range
  η ≥ 4e4 with perfect flags (paper pZL).  §5.
* **p_Z = 1e-2.**  Flags push the memory past the bit-flip wall: [15,6,5] reaches 1e-12, which no
  code reaches without flags, at 269.3
  qubits per logical qubit (f = 0.99, paper pZL); [15,9,3] bottoms out at
  2.2e-12 even with perfect flags (its
  distance).  §6.

## 1. The published results are reproduced, up to two unstated circuit details

1. **Figures 1 and 2 follow exactly from the paper's own fitted models.**  Recomputed overheads:
   187.0 → 93.5 → 88.0 → 58.7 with steps at η =
   6.74e4, 1.21e5, 1.76e6 (Fig. 1), thin surface code
   125, XZZX 145; at p_Z = 1e-2 the floors are
   1.94e-9 ([15,9,3], d_Z =
   39) and
   2.08e-11 ([15,6,5] with two
   ancillas, d_Z = 49).  Evidence:
   `fig1_from_paper_fits.png`, `fig2_from_paper_fits.png`, `numbers.json:fig1_elevator_steps`.

2. **The same figures follow from this work's flag-free simulation.**  With the paper's phase-flip
   fit and this work's bit-flip rates (stratified, p_X ≤ 2.5e-8), the steps of Fig. 1 come out as
   187.0 ([16,3,8], d_Z = 17) from η = 4.00e4; 93.5 ([15,6,5] 2 anc, d_Z = 17) from η = 4.82e4; 88.0 ([15,6,5], d_Z = 17) from η = 8.80e4; 58.7 ([15,9,3], d_Z = 17) from η = 2.16e6
   (published: 187 below 6.7e4, 93.5 from 6.7e4, 88 from 1.21e5, 58.7 from 1.76e6): the same
   overheads, with the steps within a factor
   1.40
   in η.  Evidence: `fig1_this_work_paper-pZL.md/.png`.

3. **The paper's circuits evidently carry no idle noise on blocks that wait during a
   logical-operation tick.**  With idle noise on every waiting block (the literal reading of Table
   I) the simulated rates are 1.2–7.9× above the published fits for both memories (Z memory:
   0/16,
   3/16 and
   1/16 points within 2×; X memory
   2.3–2.5×);
   without it ("noop") [15,6,5] agrees at 15/16
   points (ratios 0.43–1.33)
   and [15,6,5] with two ancillas at 14/16
   (0.60–2.45).
   The same inner round makes the isolated repetition code agree with the paper's repetition-code
   fit within 0.7–1.4× for d_Z ≤ 13 (`phase_model.md`).  Evidence: `reproduction.md`,
   `results/variants/z_variants_v1.json`.

4. **The X-memory gap is a counting convention; the [15,9,3] and [16,3,8] bit-flip excesses are
   the unstated ancilla path.**
   * *X memory.*  Counting a failure when any of the k logical observables is wrong and dividing by
     k (this work's convention throughout) puts the X memory at
     0.38–0.47×
     the published fit, at every d_Z and p_Z alike.  A phase flip of a block flips every logical X̄
     that contains it: a failure hits 2.6 logical qubits on average
     ([15,6,5]: 2.3).  Counting each logical qubit's errors
     separately (the per-qubit marginal) the same shots give
     0.82–1.30× the fit, and all
     X-memory points 0.98–1.30×
     (`counting_convention.json`).  The paper's Z-memory fits, by contrast, match the
     any-of-k convention ([15,6,5]: 0.87×
     any-of-k, 1.74× per-qubit).
     Decoders are ruled out on the same shots: BP+OSD-CS7, BP+OSD-0 and BP+LSD fail equally often
     (bplsd_cs4: 163, bposd_cs7: 151, bposd0_ps: 159, bposd0_ms: 170
     of 600 shots, `decoder_variants_flagfree.json`).
     Every rate below uses the any-of-k convention; in the per-qubit convention all rates rise by
     these multiplicities and the conclusions of §4 hold (item 13e).
   * *[15,9,3] bit flips* are 1.4–3.8×
     above the published fit (6/16 points within
     2×, the excess growing towards p_X = 1e-6).  Not the decoder: exact maximum likelihood leaves
     2.0–2.4×
     (`sensitivity_15_9_3.json`); not the check order (≤ 16 %)
     or the number of outer rounds (≤ 10 %).  It
     is the ancilla path, which the paper does not state: with the shortest path an ancilla moving
     by SWAPs can take, instead of a full sweep per check, [15,9,3] agrees within 2× at
     4/4
     points tested (1.42–1.89×)
     and so does [16,3,8] (4/4,
     1.47–1.93×, against
     2.6–17.8× with the full
     sweep), while [15,6,5], which the full sweep reproduces, drops to
     0.38–0.46×
     (`schedule_comparison.md`; the shortest path also gives m·d_Z rounds per outer round, as the
     paper states).  The paper's circuits thus differ in their ancilla paths in a way the text does
     not fix; no single path matches all three Z-memory fits (the idle-noise placement brackets
     them too: idle noise only during CNOT layers puts [15,9,3] at
     0.55–0.85×,
     the literal reading at 4.5–5.8×).
     The flag study keeps the full sweep, whose [15,9,3] bit flips are the higher ones.  Consequence: this work's [15,9,3] baseline is pessimistic, by up to
     3.8× at p_X ~ 1e-6 (within
     1.44× of the
     fit at p_X = 1e-9), so flag gains measured against it are not inflated, and every flagged
     result is compared with this work's own flag-free baseline as well as the published one.

## 2. The decoder is optimal for its flag model; the estimator predicts held-out samples

5. **Exact most-likely-error decoding (integer program with window exclusivity) equals maximum
   likelihood where it matters.**  Exactly timed flags: on 3000
   sampled leading-order configurations of [15,9,3] (d_Z = 17) ML fails
   236 times and the MLE
   237 (BP+OSD-CS7: 303).
   Coarse timing (windows of 64, 1024, 4096
   ticks), where ML is computed by enumerating every assignment of flagged events to the locations
   of their windows: ML 91 versus MLE
   92 failures on
   70000 configurations.  Evidence:
   `results/decoder_optimality.json`, `results/decoder_optimality_windows.json`.

6. **Known answers are met exactly.**  Repetition codes of distance 3, 5, 7, 9 with every flip
   flagged correct every pattern of up to d − 1 flips (all
   19171 patterns for d = 9)
   and fail on exactly half the patterns when all d bits are erased; the same holds at circuit
   level.  [15,9,3] and [15,6,5] with perfect flags and no other noise correct every pattern of up
   to d − 1 erased blocks — at code capacity
   (451 and
   25931 flip patterns)
   and in the full circuit (1353 and
   77793 patterns at three times) —
   and fail only on erasure sets that contain a codeword
   (9 and
   12 sets, the
   numbers of minimum-weight codewords).  Evidence: `results/known_answers.json`.

7. **The stratified estimator and its transfers predict held-out direct samples under flags.**
   Direct Monte Carlo against the stratified estimate at the same p_X:
   30/30 configurations agree within 95 %
   intervals; the failure fractions measured at p_X = 1e-9 (the ones behind every overhead),
   re-weighted to the held-out p_X, contain 30/30
   direct results (`validation.md`).  Transfer in d_Z: 146/146
   direct runs at d_Z = 17, 19 agree with the prediction from d_Z = 15 and
   24/24 direct runs at p_X = 1e-10 and
   2.5e-8 with the p_X transfer used for the bias sweep (`transfer_check.md`), and
   48/48 at p_Z = 1e-2
   (d_Z = 17 → 25, 33).  Exactly timed perfect flags need no decoding at all: their failure
   probability is the probability that the flagged events contain an undetectable logical, computed
   from 4e6 event sets per point (`perfect_flags_exact.json`; [15,9,3]: F(0,3) =
   1.41e-4).

## 3. Phase flips: the floor that flags cannot lower

8. **The elevator's phase flips are those of its data blocks — isolated repetition codes — plus its
   moving logical ancilla, which behaves like a repetition code at ≈ 2.2×
   the noise.**  Switching off the noise of the logical ancilla and of the logical-operation CNOTs
   brings the elevator to 1.0–2.6× (n_b/k) × the isolated repetition code for d_Z ≤ 17 (up to
   6.0× at d_Z = 25, p_Z = 1e-2); with it on, the ratio grows with d_Z
   much faster (×13 at d_Z = 21, ×42 at 25, p_Z = 1e-2).  The two-component model below fits every
   sampled elevator point (d_Z ≤ 25) within a factor 2 (`phase_model.md`).  Model: p_ZL k = n a p_rep(d, p) + n_anc g s(d)
   p_rep(d, κp), a = 1.49, g = 0.06,
   κ = 2.22.  This is the paper's lower elevator threshold
   (1/34.4 versus 1/25) made explicit.  Evidence: `phase_model.md`.

9. **The repetition-code model predicts held-out points.**  p_rep is fitted at each sampled p_Z as
   a straight line in (d_Z + 1)/2 through its large-d points (sampled down to 1.3e-9 per round at
   p_Z = 1e-3 and out to d_Z = 69 at p_Z ≥ 1.25e-2) and interpolated in log p.  Leaving out the
   largest-d point at each p_Z predicts it within
   0.94–1.48×
   for p_Z ≤ 1e-2, all inside their 95 % intervals.  The two-component elevator model fitted on
   p_Z ≥ 3e-3 predicts the held-out low-p elevator points within
   1.57–2.00×
   (below the measured values; the final model includes them).

10. **Phase-flip floor at p_Z = 1e-3: d_Z = 15 for both codes**
    (overhead 51.6 for [15,9,3],
    77.3 for [15,6,5],
    82.2 with two ancillas), the same with an
    ideal decoder for the data blocks; the paper's fit puts it at d_Z = 17.  At d_Z = 15 the paper's
    fit gives 1.2e-12 for [15,9,3] and this
    work's model 1.1e-13.  Part of the
    gap is the counting convention (item 4: the paper's X fit counts per logical qubit; in this work's
    any-of-k count the fit would be 4.6e-13,
    below 1e-12 as well), the rest is the extrapolation below sampling reach: the paper's elevator fit
    decays by 0.042 per step of d_Z at p_Z = 1e-3, while the repetition code sampled at p_Z = 1e-3
    decays by 0.024 per step
    (the paper's own repetition-code fit: 0.026).  Counting per logical qubit, this work's model gives
    2.9e-13 at d_Z = 15: the floor
    stays at 15 in either count.  Evidence: `phase_floor.md`, `phase_model.md`, `counting_convention.json`.

## 4. Flagged bit flips at p_Z = 1e-3, η = 1e6

11. **Gate flags decide the gain.**  At d_Z = 15 the [15,9,3] bit-flip rate (stratified estimate,
    95 % interval) is 3.06e-12 without flags,
    8.69e-13 with idle-only flags at f = 0.99 and
    8.39e-13 at f = 1, but
    1.23e-14 with idle and gate flags at f = 0.99
    and 2.03e-14 with preparation and measurement flags
    added; with every location flagged at f = 1 and exact timing the rate is
    4.81e-18 (only sets of ≥ 3 flagged events that
    contain an undetectable logical fail).  Evidence: `flags_main_*.md`, `assumptions.md`.

12. **Minimum overhead across f ∈ [0, 1] and timing from exact to 4096 CNOT layers.**  Full grid:
    `flags_main_paper-pZL.md`, `flags_main_this-work-pZL.md`, `map_f_window_this-work-pZL.png`,
    `overhead_vs_flags_*.png`; summary (`headline.md`; central estimates of p_XL, and the overhead
    with p_XL at its 95 % upper bound where that differs):

    | flags on | window | f | paper pZL | this-work pZL |
    |---|---|---|---|---|
    | none | – | 0 | 88.0 ([15,6,5], d_Z = 17) | 77.3 ([15,6,5], d_Z = 15) |
    | idle | exact | 0.99 | 88.0 ([15,6,5], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15); 95 % bound: 77.3 ([15,6,5], d_Z = 15) |
    | idle | exact | 1 | 88.0 ([15,6,5], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | idle | 4096 | 0.99 | 88.0 ([15,6,5], d_Z = 17) | 77.3 ([15,6,5], d_Z = 15) |
    | idle + gate | exact | 0.99 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | exact | 0.5 | 88.0 ([15,6,5], d_Z = 17) | 77.3 ([15,6,5], d_Z = 15) |
    | all | exact | 0.8 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | exact | 0.9 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | 1 | 0.99 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | 64 | 0.99 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | 1024 | 0.99 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | 4096 | 0.9 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |
    | all | 4096 | 1 | 58.7 ([15,9,3], d_Z = 17) | 51.6 ([15,9,3], d_Z = 15) |

    A window of 1 tick is one CNOT layer; an inner round is 4 ticks, an outer round of [15,9,3] at
    d_Z = 15 about 600 ticks, the whole simulated memory (5 outer rounds) about 3000.

13. **[15,6,5] needs no flags at η = 1e6 and gains nothing from them**: its bit flips are already
    far below the target at d_Z = 15 (p_XL ≈ 3.5e-16),
    so its overhead is its phase-flip floor with or without flags; flags pay through the switch to
    the higher-rate [15,9,3].

13b. **False flags cost nothing up to 1e-6 per qubit per tick when timing is exact.**  [15,9,3]
    at f = 0.99 on all locations: p_XL = 2.0e-14 [1.1e-14, 3.8e-14] without false
    flags, 2.0e-14 [1.1e-14, 3.9e-14] at r = 1e-8 and
    2.6e-14 [2.1e-14, 1.9e-13] at r = 1e-6 (95 % intervals; the single- and
    two-event strata are bounded analytically, `false_flag_bounds.json`: a failure needs falsely
    flagged locations that complete the real events to a logical, and with exact timing the decoder
    never prefers two flags over one).  With 64-tick windows the 95 % upper bound stays below the
    target up to r = 1e-08 and the
    central estimate up to r = 1e-06
    (2.9e-13 [6.0e-14, 3.4e-11] at 1e-6); beyond, the bound is set by the
    analytic pair bound, which is loose for windows (the two-flags-cost-more argument is proved only
    for exact timing).
    Full sweep, including f = 0.8–0.9 with 4–16-tick windows (the regime a photon-counting
    threshold would select): `assumptions.md`.

13c. **Heralded flags (a flag certifies the X) versus erasures (the event's X occurs with
    probability ½).**  [15,9,3]: idle-only flags at f = 1 4.9e-13 [4.6e-13, 5.5e-13]
    (heralded) vs 8.4e-13 [7.8e-13, 9.0e-13] (erasure); all locations at f = 0.9
    3.8e-14 [3.1e-14, 8.5e-14] vs 1.6e-13 [1.5e-13, 1.8e-13]
    (`assumptions.md`): a flag that certifies the X carries more information, and halves the
    number of flagged events.  The minimum overhead with idle-only flags at f = 1 becomes
    51.6 ([15,9,3], d=15) (erasure: 51.6 ([15,9,3], d=15); this-work
    pZL), and with p_XL at its 95 % upper bound 51.6 ([15,9,3], d=15) (erasure:
    77.3 ([15,6,5], d=15)).  The erasure model is the one arXiv:2607.01375 supports (a flip leaves the cat's bit
    random) and is used everywhere else.

13d. **The idle-noise reading moves both error types but not the conclusion.**  Under the literal
    reading the [15,9,3] bit flips are ×2.7 higher
    without flags (d_Z = 17), the repetition code's phase flips ×4–93 (extra idle ticks,
    `literal_reading.md`) and the phase-flip floor moves to d_Z =
    17 ([15,9,3]) and 17
    ([15,6,5]).  The minimum overhead is then
    88.0 ([15,6,5], d_Z = 17) without flags and
    58.7 ([15,9,3], d_Z = 17) with flags on all
    locations at f = 0.99 (idle-only, f = 0.99:
    88.0 ([15,6,5], d_Z = 17)).

13e. **The counting convention does not change the conclusion.**  Counting each logical qubit's
    errors separately multiplies the phase-flip rates by 2.6
    ([15,9,3]) and 2.3 ([15,6,5]) and the bit-flip rates by
    2.2 and 2.1
    (measured, item 4); with every rate counted that way the minimum overhead (this-work pZL) is
    77.3 without flags,
    77.3 with idle-only flags at f = 1,
    77.3 at f = 0.8 and
    51.6 at f = 0.9 on all locations
    (51.6 with 4096-tick windows at
    f = 0.99): the efficiency needed rises to between 0.8 and
    0.9, the saving is the same.

## 5. Bias from 4e4 to 1e7

14. **Flags let [15,9,3] serve at lower bias** (Fig. 1 recomputed with flags,
    `fig1_this_work_*.md/.png`): with the paper's phase-flip fit it is the cheapest code from
    η = 2.16e6 without flags,
    1.13e6 with idle-only flags (f = 0.99),
    4.90e5 (all locations, f = 0.9),
    1.77e5 (f = 0.99),
    4.68e5 (f = 0.99, 1024-tick windows) and
    over the whole range with perfect flags; with this work's phase-flip model the same thresholds
    are 1.88e6,
    1.03e6,
    4.26e5,
    1.54e5 and
    4.07e5.  The bit-flip rates at other
    p_X re-weight the p_X = 1e-9 failure fractions with exact intensities (validated in §2, item 7).

## 6. p_Z = 1e-2, η = 1e6: the lowest reachable rate and its overhead

15. **Without flags this work reproduces the published floors where its bit-flip rates agree with
    the fits.**  With the paper's phase-flip fit the flag-free floors are
    2.1e-11 ([15,6,5], two ancillas, d_Z =
    49; published 2.08e-11 at 49) and
    4.7e-9 ([15,9,3], d_Z =
    37; published 1.94e-9 at 39, the gap being the
    [15,9,3] bit-flip excess of item 4).  This work's phase-flip model, which decays more slowly at
    large d_Z (the moving ancilla, §3), puts them higher:
    2.1e-10 and
    1.3e-8.

16. **Flags push the memory past the bit-flip wall.**  Lowest p_L per flag setting (phase flips
    beyond d_Z = 25, the largest elevator X memory sampled at p_Z = 1e-2, are extrapolations of the
    phase-flip model, marked), the overhead at which 1e-12
    is reached, and what the floor is made of (`pz1e2_*.md`, `limits.md`, `fig2_this_work_*.md`):

| code | flags | lowest p_L [with p_XL at its 95% upper bound], paper pZL (d_Z, overhead) | this-work pZL | 1e-12 reached at overhead (paper / this work) | floor made of (this work: phase / flagged-only / unflagged) |
|---|---|---|---|---|---|
| [15,9,3] | none | 4.7e-09 [≤ 4.9e-09] (37, 130) (extrap.) | 1.3e-08 [≤ 1.4e-08] (51, 180) (extrap.) | no / no | 0.22 / 0.00 / 0.78 |
| [15,9,3] | f=0.9 idle w=exact | 1.8e-09 [≤ 2.0e-09] (39, 137) (extrap.) | 5.7e-09 [≤ 6.1e-09] (55, 194) (extrap.) | no / no | 0.22 / 0.00 / 0.77 |
| [15,9,3] | f=0.99 idle w=exact | 1.6e-09 [≤ 1.7e-09] (39, 137) (extrap.) | 5.1e-09 [≤ 5.6e-09] (57, 201) (extrap.) | no / no | 0.17 / 0.00 / 0.83 |
| [15,9,3] | f=0.9 all w=exact | 3.4e-10 [≤ 3.8e-10] (43, 151) (extrap.) | 1.2e-09 [≤ 1.4e-09] (63, 222) (extrap.) | no / no | 0.20 / 0.00 / 0.79 |
| [15,9,3] | f=0.99 idle+gate w=exact | 4.5e-11 [≤ 6.1e-11] (47, 165) (extrap.) | 2.0e-10 [≤ 4.4e-10] (73, 258) (extrap.) | no / no | 0.17 / 0.17 / 0.66 |
| [15,9,3] | f=0.99 all w=exact | 4.4e-11 [≤ 4.9e-11] (47, 165) (extrap.) | 1.8e-10 [≤ 2.1e-10] (73, 258) (extrap.) | no / no | 0.18 / 0.05 / 0.77 |
| [15,9,3] | f=0.99 all w=64 | 1.1e-10 [≤ 2.1e-10] (45, 158) (extrap.) | 4.0e-10 [≤ 9.0e-10] (69, 244) (extrap.) | no / no | 0.18 / 0.48 / 0.34 |
| [15,9,3] | f=0.99 all w=1024 | 2.9e-10 [≤ 4.3e-10] (43, 151) (extrap.) | 1.0e-09 [≤ 1.6e-09] (65, 229) (extrap.) | no / no | 0.16 / 0.67 / 0.17 |
| [15,9,3] | f=1.0 all w=exact | 2.2e-12 [≤ 2.4e-12] (53, 187) (extrap.) | 2.3e-11 [≤ 2.5e-11] (81, 286) (extrap.) | no / no | 0.28 / 0.72 / 0.00 |
| [15,6,5] | none | 5.6e-11 [≤ 8.7e-11] (47, 248) (extrap.) | 4.4e-10 [≤ 5.7e-10] (69, 365) (extrap.) | no / no | 0.25 / 0.00 / 0.75 |
| [15,6,5] | f=0.9 idle w=exact | 1.4e-11 [≤ 4.4e-11] (49, 259) (extrap.) | 1.3e-10 [≤ 3.2e-10] (75, 397) (extrap.) | no / no | 0.26 / 0.00 / 0.74 |
| [15,6,5] | f=0.99 idle w=exact | 1.3e-11 [≤ 4.1e-11] (49, 259) (extrap.) | 1.2e-10 [≤ 3.0e-10] (75, 397) (extrap.) | no / no | 0.27 / 0.00 / 0.73 |
| [15,6,5] | f=0.9 all w=exact | 2.3e-13 [≤ 1.1e-11] (57, 301) (extrap.) | 4.6e-12 [≤ 1.5e-10] (91, 483) (extrap.) | 269 / no | 0.28 / 0.00 / 0.72 |
| [15,6,5] | f=0.99 idle+gate w=exact | 7.2e-15 [≤ 7.2e-12] (65, 344) (extrap.) | 2.1e-13 [≤ 6.8e-10] (107, 568) (extrap.) | 269 / 493 | 0.27 / 0.00 / 0.73 |
| [15,6,5] | f=0.99 all w=exact | 8.5e-15 [≤ 1.3e-12] (63, 333) (extrap.) | 2.4e-13 [≤ 3.8e-11] (107, 568) (extrap.) | 269 / 493 | 0.23 / 0.04 / 0.74 |
| [15,6,5] | f=0.99 all w=64 | 4.0e-14 [≤ 4.8e-10] (61, 323) (extrap.) | 6.8e-13 [≤ 3.7e-09] (101, 536) (extrap.) | 269 / 504 | 0.26 / 0.00 / 0.74 |
| [15,6,5] | f=0.99 all w=1024 | 5.3e-14 [≤ 4.4e-10] (59, 312) (extrap.) | 2.5e-12 [≤ 2.6e-09] (93, 493) (extrap.) | 269 / no | 0.35 / 0.00 / 0.65 |
| [15,6,5] | f=1.0 all w=exact | 3.3e-16 [≤ 5.6e-15] (71, 376) (extrap.) | 2.8e-14 [≤ 1.2e-11] (117, 621) (extrap.) | 269 / 493 | 0.27 / 0.73 / 0.00 |
| [15,6,5] 2 anc | none | 2.1e-11 [≤ 3.8e-11] (49, 275) (extrap.) | 2.1e-10 [≤ 3.0e-10] (77, 434) (extrap.) | no / no | 0.20 / 0.00 / 0.80 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | 4.4e-12 [≤ 1.9e-11] (51, 286) (extrap.) | 5.1e-11 [≤ 1.7e-10] (83, 468) (extrap.) | no / no | 0.25 / 0.00 / 0.75 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | 5.1e-12 [≤ 1.8e-11] (51, 286) (extrap.) | 5.8e-11 [≤ 1.6e-10] (83, 468) (extrap.) | no / no | 0.22 / 0.00 / 0.78 |
| [15,6,5] 2 anc | f=0.9 all w=exact | 1.3e-13 [≤ 2.8e-12] (59, 332) (extrap.) | 3.0e-12 [≤ 5.6e-11] (97, 547) (extrap.) | 286 / no | 0.26 / 0.00 / 0.74 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | 2.1e-16 [≤ 1.7e-12] (71, 400) (extrap.) | 1.7e-14 [≤ 1.9e-10] (123, 694) (extrap.) | 286 / 547 | 0.28 / 0.00 / 0.72 |
| [15,6,5] 2 anc | f=0.99 all w=exact | 1.3e-14 [≤ 2.6e-13] (63, 354) (extrap.) | 1.8e-13 [≤ 1.1e-11] (113, 638) (extrap.) | 286 / 547 | 0.19 / 0.02 / 0.80 |
| [15,6,5] 2 anc | f=0.99 all w=64 | 8.3e-15 [≤ 3.1e-10] (65, 366) (extrap.) | 1.5e-13 [≤ 2.7e-09] (115, 649) (extrap.) | 286 / 547 | 0.15 / 0.00 / 0.85 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | 1.7e-13 [≤ 1.9e-10] (57, 320) (extrap.) | 6.5e-12 [≤ 1.2e-09] (93, 524) (extrap.) | 286 / no | 0.27 / 0.38 / 0.35 |
| [15,6,5] 2 anc | f=1.0 all w=exact | 8.6e-17 [≤ 3.2e-16] (73, 411) (extrap.) | 1.0e-14 [≤ 4.6e-13] (127, 717) (extrap.) | 286 / 547 | 0.21 / 0.79 / 0.00 |
| Hamming [15,11,3] | none | 4.4e-09 [≤ 4.5e-09] (37, 106) (extrap.) | 1.2e-08 [≤ 1.3e-08] (51, 147) (extrap.) | no / no | 0.19 / 0.00 / 0.81 |
| Hamming [15,11,3] | f=0.9 idle w=exact | 2.1e-09 [≤ 2.2e-09] (39, 112) (extrap.) | 6.2e-09 [≤ 6.5e-09] (53, 153) (extrap.) | no / no | 0.25 / 0.00 / 0.75 |
| Hamming [15,11,3] | f=0.99 idle w=exact | 1.7e-09 [≤ 1.8e-09] (39, 112) (extrap.) | 5.2e-09 [≤ 5.5e-09] (55, 159) (extrap.) | no / no | 0.20 / 0.00 / 0.80 |
| Hamming [15,11,3] | f=0.9 all w=exact | 4.8e-10 [≤ 5.1e-10] (41, 118) (extrap.) | 1.6e-09 [≤ 1.8e-09] (61, 176) (extrap.) | no / no | 0.19 / 0.00 / 0.81 |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | 5.9e-11 [≤ 6.6e-11] (45, 129) (extrap.) | 2.2e-10 [≤ 2.9e-10] (71, 205) (extrap.) | no / no | 0.18 / 0.01 / 0.82 |
| Hamming [15,11,3] | f=0.99 all w=exact | 6.0e-11 [≤ 6.4e-11] (45, 129) (extrap.) | 2.4e-10 [≤ 2.6e-10] (71, 205) (extrap.) | no / no | 0.16 / 0.03 / 0.81 |
| Hamming [15,11,3] | f=0.99 all w=64 | 1.3e-10 [≤ 2.0e-10] (45, 129) (extrap.) | 4.7e-10 [≤ 7.4e-10] (67, 193) (extrap.) | no / no | 0.19 / 0.38 / 0.43 |
| Hamming [15,11,3] | f=0.99 all w=1024 | 6.2e-10 [≤ 7.4e-10] (41, 118) (extrap.) | 2.1e-09 [≤ 2.5e-09] (59, 170) (extrap.) | no / no | 0.22 / 0.70 / 0.08 |
| Hamming [15,11,3] | f=1.0 all w=exact | 1.8e-12 [≤ 1.9e-12] (53, 153) (extrap.) | 1.9e-11 [≤ 1.9e-11] (83, 240) (extrap.) | no / no | 0.19 / 0.81 / 0.00 |

    With flags on all locations [15,6,5] reaches 1e-12 — which neither code reaches without flags —
    at 269.3 qubits per logical
    qubit (paper pZL; 493.3
    with this work's phase-flip model), and its floor drops by 3–4 orders of magnitude.  [15,9,3]
    stays above 1e-12 even with perfect flags: there its floor is made of sets of ≥ 3 flagged events
    that contain an undetectable logical — its distance.

## 7. Alternatives and the frontier

17. **Higher-rate outer codes become usable with flags, and push the overhead towards the bare
    repetition-code floor.**  The frontier at p_Z = 1e-3, η = 1e6 over every code, decoder and flag
    setting simulated — Hamming [15,11,3], [31,26,3], [63,57,3] and extended Hamming [16,11,4]
    besides the paper's codes — requiring p_L ≤ 1e-12 with the 95 % upper bound of p_XL
    (`frontier_*.md`; this-work pZL):

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
| 51.6 | [15,9,3] | 15 | 1.9e-13 | 0.99 | all | 64 | 1e-08 |
| 51.6 | [15,9,3] | 15 | 1.4e-13 | 0.99 | all | exact | 1e-06 |
| 77.3 | [15,6,5] | 15 | 1.7e-13 | 0.0 | none | any (no flags) | 0 |

    and with the paper's phase-flip fit:

| overhead | code | d_Z | p_L | f needed | flags on | coarsest window | false flags tolerated |
|---|---|---|---|---|---|---|---|
| 32.6 | Hamming [63,57,3] | 15 | 9.1e-13 | 0.995 | all | exact | 0 |
| 35.7 | Hamming [31,26,3] | 15 | 9.0e-13 | 0.99 | all | exact | 0 |
| 40.6 | Hamming [31,26,3] | 17 (transferred) | 6.1e-13 | 0.95 | all | exact | 0 |
| 40.6 | Hamming [31,26,3] | 17 (transferred) | 2.4e-13 | 0.99 | all | 64 | 0 |
| 48.0 | Hamming [15,11,3] | 17 (transferred) | 7.0e-13 | 0.8 | all | exact | 0 |
| 48.0 | Hamming [15,11,3] | 17 (transferred) | 5.0e-13 | 0.99 | all | 4096 | 0 |
| 51.0 | ext. Hamming [16,11,4] | 17 (transferred) | 8.0e-13 | 0.9 | idle | 4 | 0 |
| 51.0 | ext. Hamming [16,11,4] | 17 (transferred) | 7.1e-13 | 0.99 | idle | 64 | 0 |
| 58.7 | [15,9,3] | 17 (transferred) | 5.2e-13 | 0.8 | idle+gate | exact | 0 |
| 58.7 | [15,9,3] | 17 (transferred) | 5.7e-13 | 0.8 | all | 64 | 0 |
| 58.7 | [15,9,3] | 17 (transferred) | 5.1e-13 | 0.9 | all | 4096 | 0 |
| 88.0 | [15,6,5] | 17 | 7.5e-14 | 0.0 | none | any (no flags) | 0 |

    Each step outward came from relaxing the criterion furthest from its limit: the overhead (codes
    of higher rate, which flags make admissible), then the timing window (to 4096 ticks), then the
    efficiency.  The decoder axis is closed: the MLE is ML at the leading order (item 5) and
    BP+OSD is worse on the same configurations.  Lowest p_L per code and d_Z and what it takes:

| overhead | code | d_Z | lowest p_L | of which phase flips | without flags | least f within 1.5x | flags on | coarsest window |
|---|---|---|---|---|---|---|---|---|
| 28.1 | Hamming [63,57,3] | 13 | 1.4e-12 | 1.4e-12 | 4.0e-11 | 0.99 | all | 64 |
| 30.8 | Hamming [31,26,3] | 13 | 1.8e-12 | 1.8e-12 | 1.1e-11 | 0.9 | all | exact |
| 32.6 | Hamming [63,57,3] | 15 | 4.0e-14 | 4.0e-14 | 5.3e-11 | 1.0 | all | exact |
| 35.7 | Hamming [31,26,3] | 15 | 5.5e-14 | 5.5e-14 | 1.3e-11 | 0.999 | all | exact |
| 36.4 | Hamming [15,11,3] | 13 | 2.6e-12 | 2.6e-12 | 4.8e-12 | 0.5 | all | exact |
| 37.1 | Hamming [63,57,3] | 17 | 1.6e-15 | 1.2e-15 | 6.8e-11 | 1.0 | all | exact |
| 38.6 | ext. Hamming [16,11,4] | 13 | 2.7e-12 | 2.7e-12 | 4.9e-12 | 0.5 | all | exact |
| 40.6 | Hamming [31,26,3] | 17 | 2.0e-15 | 1.9e-15 | 1.6e-11 | 1.0 | all | exact |
| 41.5 | Hamming [63,57,3] | 19 | 5.3e-16 | 4.5e-17 | 8.5e-11 | 1.0 | all | exact |
| 42.2 | Hamming [15,11,3] | 15 | 9.0e-14 | 9.0e-14 | 3.1e-12 | 0.99 | all | 16 |
| 44.4 | [15,9,3] | 13 | 3.1e-12 | 3.1e-12 | 5.4e-12 | 0.5 | idle | 4096 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 9.2e-14 | 9.2e-14 | 3.0e-12 | 0.9 | all | exact |
| 45.5 | Hamming [31,26,3] | 19 | 1.4e-16 | 7.9e-17 | 2.0e-11 | 1.0 | all | exact |
| 46.0 | Hamming [63,57,3] | 21 | 6.5e-16 | 1.9e-18 | 1.0e-10 | 1.0 | all | exact |
| 48.0 | Hamming [15,11,3] | 17 | 3.5e-15 | 3.5e-15 | 4.0e-12 | 1.0 | all | exact |
| 50.5 | Hamming [31,26,3] | 21 | 9.2e-17 | 3.6e-18 | 2.5e-11 | 1.0 | all | exact |
| 50.5 | Hamming [63,57,3] | 23 | 8.6e-16 | 8.5e-20 | 1.2e-10 | 1.0 | all | exact |
| 51.0 | ext. Hamming [16,11,4] | 17 | 3.7e-15 | 3.7e-15 | 3.8e-12 | 0.98 | all | exact |
| 51.6 | [15,9,3] | 15 | 1.1e-13 | 1.1e-13 | 3.2e-12 | 0.98 | idle+gate | 4 |
| 53.8 | Hamming [15,11,3] | 19 | 1.5e-16 | 1.4e-16 | 5.5e-12 | 1.0 | all | exact |
| 55.0 | Hamming [63,57,3] | 25 | 1.1e-15 | 4.2e-21 | 1.5e-10 | 1.0 | all | exact |
| 55.4 | Hamming [31,26,3] | 23 | 6.1e-17 | 1.8e-19 | 2.2e-11 | 1.0 | all | exact |
| 57.2 | ext. Hamming [16,11,4] | 19 | 1.5e-16 | 1.5e-16 | 5.2e-12 | 0.999 | all | exact |
| 58.7 | [15,9,3] | 17 | 4.3e-15 | 4.3e-15 | 4.1e-12 | 1.0 | idle+gate | 16 |
| 59.6 | Hamming [15,11,3] | 21 | 2.3e-17 | 6.2e-18 | 7.4e-12 | 1.0 | all | exact |
| 66.7 | [15,6,5] | 13 | 4.7e-12 | 4.7e-12 | 4.7e-12 | 0.0 | none | any (no flags) |
| 70.8 | [15,6,5] 2 anc | 13 | 6.6e-12 | 6.6e-12 | 6.6e-12 | 0.0 | none | any (no flags) |

## 8. Limits

18. **Every remaining limit is one of three properties of the problem** (`limits.md`):
    * *Phase flips, which flags cannot reveal.*  At p_Z = 1e-3 every code on the frontier sits at
      its phase-flip floor: one step lower in d_Z its phase flips alone exceed 1e-12, at the floor its
      bit flips are orders of magnitude below them (e.g. [15,9,3]: p_ZL(13) =
      3.13e-12, p_ZL(15) =
      1.10e-13, lowest p_XL(15) =
      4.81e-18).  The floor does not move with an
      ideal decoder for the data blocks (§3), and no Elevator-type memory can go below
      25 qubits per logical qubit at this
      operating point (one repetition-code block of distance
      13 per logical qubit, k/n → 1, no ancilla).
    * *The code distance.*  With perfect, exactly timed flags failures need ≥ d flagged events that
      contain an undetectable logical (computed without a decoder, item 7); at p_Z = 1e-2 this
      sets the [15,9,3] and Hamming floors (flagged-only share
      0.72
      of the [15,9,3] floor).
    * *Unflagged bit flips, i.e. the flag efficiency (and which locations can raise flags).*  With
      f < 1 the remaining bit flips involve unflagged errors (shares in `limits.md`); the efficiency
      needed is that of an ML-optimal decoder (item 5), so it is a property of the code and the flag
      model, not of this decoder.
    Timing precision is not a limit anywhere in the range tested when gates are flagged.  The
    remaining open problems — the two fit-level reproduction residuals, and whether flags exist
    during gates — are listed in `REPORT.md`.
