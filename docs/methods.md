# Methods

Everything here is rebuilt from the text of arXiv:2601.10786v2 (no code or data were released)
and arXiv:2607.01375v1.  Code: `elevator/`; task specifications: `tasks/`; raw results:
`results/`; analysis: `scripts/analyze.py`; one command: `./reproduce.sh`.

## 1. Physical circuits (Stim 1.16.0), `elevator/circuits.py`, `elevator/schedule.py`

* Layout: a column of P = n + n_anc rows; a row is one phase-flip repetition-code block of d_Z
  data qubits and d_Z - 1 inner ancillas (the paper's Fig. 3).  Transversal CNOTs act between
  data qubit j of adjacent rows.
* Inner round (4 ticks, every row): R_X inner ancillas; CNOT ancilla_j -> data_j; CNOT
  ancilla_j -> data_{j+1}; M_X.  A logical ancilla is prepared (R_Z on its data qubits) at the
  first tick of its first round and read out (M_Z) at the last tick of its last round.
* Logical operations (the paper's text): CNOT+SWAP compiled into 2 CNOT layers
  CNOT(anc->data), CNOT(data->anc); SWAP into 3 layers.  One inner round between consecutive
  logical operations; at least d_Z rounds between the ancilla's preparation and readout.
* Ancilla path ("elevator", chosen here, the paper does not specify it): every check is
  measured during one sweep of the whole column (n logical operations), alternating down and
  up.  With n = 15 this gives d_Z rounds per check for d_Z >= 16 - the paper's "m d_Z rounds
  per outer round ... n_L < d_Z in the operating regime" - and 16 rounds per check below.
  Variants tried: 'compress' (exactly d_Z rounds per check, several operations per gap),
  'span' (stop after the last block of the check) and 'local' (the shortest path: the ancilla
  takes the nearest remaining check of the outer round, heads for the nearer end of its support
  and is reset in place; m·d_Z rounds per outer round as the paper states).  The full sweep
  reproduces the [15,6,5] fits, the shortest path the [15,9,3] and [16,3,8] fits
  (`results/summary/schedule_comparison.md`); the flag study uses the full sweep throughout.
  Two ancillas: both sweep in lockstep, one block apart, each measuring alternate checks.
* Noise (Table I): prep/measure in Z: X at p_X; prep/measure in X: Z at p_Z; idle: X at p_X,
  Z at p_Z; CNOT: IZ, ZI, ZZ at p_Z/3, IX, XI, XX at p_X/3.  Which locations count as idle is
  not stated: the reading that reproduces the published fits (below) has no idle noise on
  blocks that are not taking part in a logical-operation tick ("noop"); the literal reading
  ("all": idle noise on every waiting block) is kept as a sensitivity case.
* Memories: Z-type (data in |0>, observables Z_L of an information set of the outer code,
  detectors = consecutive outer-check comparisons) and X-type (data in |+>, observables X-bar
  of a basis of outer codewords, detectors = inner X-stabiliser comparisons with frames
  propagated through the transversal CNOTs).  Every circuit is checked deterministic without
  noise; circuit-level distances (Stim's undetectable-error search) are 3 and 5.

## 2. Exact block-level reduction of the bit-flip memory, `elevator/blocklevel.py`

Bit flips matter only to the Z-type memory, and the inner code has bit-flip distance 1, so every
physical X fault flips the logical bit of one row in one *slot* (an interval between that row's
block-level operations).  The reduction keeps every physical location (qubit, tick, sub-location
before/after a CNOT, class idle/gate/prep/meas) and maps it to its slot.  Its detector error model
equals Stim's for the physical circuit (same mechanisms; probabilities equal to 1e-5 relative,
the size of Stim's disjoint-error approximation).

## 3. Flag model, `elevator/flags.py`

* Event model (arXiv:2607.01375): a bit-flip event leaves the cat's bit random, so it produces
  X with probability 1/2.  Each location's event probability is twice its Table-I X
  probability, so the Pauli marginals - and every flag-free number - are those of the paper.
  For a CNOT the control's X faults split into 'before' (propagates: XX) and 'after' (XI)
  sub-locations; the target's (IX) is a third.
* Flag efficiency f per location class: idle (established by arXiv:2607.01375), gate,
  prep, meas (not established; switched on separately and measured).
* False flags: probability r per physical qubit per tick, independent.
* Timing precision: a flag reports (qubit, window) with windows of w ticks (CNOT layers)
  aligned to tick 0; 'exact' also resolves before/after within a CNOT.  An inner round is 4
  ticks, a logical operation 2-3, a check ~ 4 d_Z + 41 ticks, an outer round ~600-1100 ticks.
  All ticks are taken to last the same time (neither paper fixes durations).
* Not modelled: the phase randomisation that accompanies an event (its rate, ~p_X, is 10^6
  below p_Z), events on inner ancillas during their X-basis preparation and readout (no X
  error there in Table I).

## 4. Decoders

* Flag-free reproduction: BP+OSD (ldpc 2.4.1, product-sum, 100 iterations, OSD-CS order 7)
  for the Z memory; BP+LSD (LSD-CS order 4; min-sum 30 iterations for the low-p runs, which
  matched product-sum 100 iterations on the same 4500 shots) for the X memory - BP+OSD-CS7
  takes > 2 s per shot there.
* Flags: exact most-likely-error decoding as an integer program (HiGHS) on the block-level
  detector error model, with a flagged window's events made mutually exclusive.  Checked
  against exact maximum likelihood (a coset trellis for exact timing, enumeration of the windows'
  assignments for coarse timing) on the strata that dominate failure, for [15,9,3] and for
  [15,6,5] in the p_Z = 1e-2 regime (§8; numbers in FINDINGS item 5).  BP+OSD with flag
  posteriors is kept as the paper-like decoder (more failures on the same configurations).
* Isolated repetition code: PyMatching; equal to exact ML within statistics.

## 5. Rare-event estimation of bit flips, `elevator/strata.py`, `elevator/flagstudy.py`

Events are independent Poisson processes, so P_fail = sum_{a,b} Pois(a;U) Pois(b;S) F(a,b) with
a unflagged X errors, b flagged events, U and S exact intensities.  F(a,b) is estimated by
sampling exactly a and b events (plus false flags) and decoding; F(1,0) is computed exactly by
decoding every mechanism alone, F(0,1) = 0 is exact for a decoder with window exclusivity when
the DEM has no logical of weight <= 2 (checked), and F(0,b) = 0 for b < d with exact timing.
Allocation: every stratum up to a + b <= (d+1)/2 + 1 gets n1 samples, higher strata only if
their Poisson weight can matter (>= 1e-3 of the running estimate; skipped weight enters the
upper bound with failure probability one), then samples go where weight x interval width is
largest until the 95 % interval is within the relative tolerance or its upper end is below
1e-13 per round per logical qubit.  Strata beyond a + b = kmax enter the upper bound with
weight one.  Intervals: Wilson per stratum, combined with the Poisson weights.

Every p_X = 1e-9 or 1e-8 number is below direct-sampling reach and is labelled as such.  The
model behind it (the Poisson decomposition with sampled F) is checked against direct Monte
Carlo at p_X = 3e-7 and 1e-6 with flags on (`results/summary/validation.md`): the stratified
estimate at the same p_X and the p_X = 1e-9 failure fractions re-weighted to that p_X must both
contain the direct result.

**Exactly timed perfect flags** (f = 1 on every class, no false flags, U = 0): the decoder knows
every event's location, each event is an X with probability 1/2, so maximum likelihood fails
with probability 1 - |K0|/|K| where K are the subsets of the event set with trivial syndrome and
K0 those that are also logically trivial.  F(0,b) then needs no decoding and is computed to
~2 % from 4e6 sampled event sets (`scripts/perfect_flags_exact.py`); these values replace the
sampled ones for that flag setting, and for every exactly timed setting that flags all four classes
at the same f < 1 (its flagged events then have the same location distribution, and with no
unflagged error the decoder picks among the zero-cost flag explanations exactly as with perfect
flags).

**Analytic bounds on F(a,b)** (`scripts/strata_caps.py`; exactly timed erasure flags, no false
flags).  The decoder minimises sum_c w_c x_c over the unflagged merged columns plus the flagged
windows' costs, which are all 0 here (X or no X at a known location, probability 1/2 each).
Against the true explanation — at most a unflagged columns, each flagged window's true choice —
optimality gives sum_{x^} w <= sum_{x'} w + eps (eps covers the MIP gap).  A failure makes
x^ + x' + (y^ + y') an undetectable logical of the merged block-level DEM, and a window
contributes at most one column, so |x^| >= d_DEM - a - b =: k.  The left side is at least S_k,
the sum of the k smallest background column costs (removing the flagged locations only raises
costs); the right side is at most sum_i W_b(u_i), the costs of the true columns with the b largest
other contributions removed.  Hence F(a,b) <= P(sum_i W_b(u_i) >= S_k - eps) over the unflagged-error
distribution: exactly 0 when a max W_b < S_k - eps, else computed per (column, class) bucket
(a = 1) or by convolution with costs rounded up (a >= 2).  The per-column, per-class location
counts are exact quadratics in d_Z (fitted at 17, 19, 21, checked at 25 and 33; built directly
below 17), so the bound is evaluated at every transfer target; d_DEM >= 5 for [15,6,5] (one and
two ancillas) is verified by an exhaustive meet-in-the-middle search over all sets of up to four
columns.  The bounds are checked against every sampled stratum (882 strata, no sampled failure
fraction above its bound) and against the decoder's own column costs (agreement to 1e-7).  For
[15,6,5] they give F(1,1) = F(1,2) = 0 and F(2,0) <= 1e-5 ... 1e-2 at every d_Z of interest, which
removes the zero-failure strata that dominated the 95 % upper bounds; sampled strata use
min(Wilson upper end, bound), and strata never sampled their bound (1 if none).

**Analytic bounds with false flags** (`scripts/false_flag_bounds.py`; distance-3 codes, any timing).
With false flags no stratum is exactly 0, and F(1,0), F(0,1), F(0,2) carry most of the Poisson weight.
The decoder fails only if its explanation differs from the truth by a nontrivial logical of >= 3
columns, made of true columns it drops or swaps and an alternative set E' of n_x unflagged columns and
n_f columns of falsely flagged windows whose decoder cost is at most that of the truth (+ eps).  With
the decoder's own costs (w for unflagged columns, v = log(pi_0/pi_c) for flagged-window columns, the
false-flag rate inside pi), every (n_x, n_f) that the costs allow is bounded explicitly — (1,1), (0,2),
(1,2), (0,3), summing P(c) <= r_W N_W(c) (some window holding column c falsely flagged) over the
completions to a logical — and the rest by the Poisson tail of the number of false flags; n_x >= 2
must be cost-impossible.  For F(1,0) the true column's cost is taken with its three largest window
contributions removed, plus the probability of four or more false flags on it; for F(0,1) the true
flagged event's own window may be switched to another of its columns; with exact timing
2 min(v_min, w_min) > max v gives F(0,1) = 0.  No decoding is involved; the bounds replace the upper
end of the Wilson interval where smaller.

**Transfers.**  F(a,b) depends on p_X and d_Z only through the decoder's priors and the
circuit's layout, while U and S are exact linear functions of p_X and of per-class fault sums
(`results/summary/class_sums.json`, exact quadratics in d_Z for d_Z >= 17).  Rates at a (d_Z,
p_X) that was not simulated re-weight the failure fractions of the nearest simulated d_Z (same
p_X if available, else p_X = 1e-9).  Checked: p_X transfer against the held-out direct samples
(validation.md); d_Z transfer at p_Z = 1e-2 (d_Z = 17 -> 25, 33, `pz1e2_*.md`) and at p_X = 1e-9
(d_Z = 15 -> 17, 19, `transfer_check.md`).  Every transferred number is marked as such.

## 6. Phase flips, `elevator/repcode.py`, `elevator/phasemodel.py`

* p_rep(d, p): the isolated repetition code with the elevator's inner round (PyMatching, equal
  to ML for this code within statistics), sampled down to ~1e-9 per round (p_Z = 1e-3) and out to
  d_Z = 69 at p_Z >= 1.25e-2.  At each sampled p, log p_rep is a straight line in h = (d+1)/2
  through the large-d points (weighted least squares, covariance inflated by chi^2), interpolated
  linearly in log p between sampled p (`RepModel`); the largest-d point of every p is held out and
  predicted.
* Elevator X memory (BP+LSD): p_ZL k = n a p_rep(d, p) + n_anc g s(d) p_rep(d, kappa p),
  s(d) = min(1, (n+1)/d): the data blocks behave like isolated repetition codes up to the factor a,
  the moving ancilla like a repetition code at kappa ~ 2 times the noise, active for the sweep
  fraction of its lifetime.  Held-out test: fit on p_Z >= 3e-3, predict p_Z < 3e-3.
* Decoder-independent part of a (`scripts/op_noise_penalty.py`): a decoder told every other block's
  and the ancilla's errors still faces an isolated repetition code with the gate noise of the
  logical operations the block takes part in (three transversal CNOT layers per check, Z with
  2p/3 each), measured relative to the plain repetition code (Stim + PyMatching) at p_Z where both
  have many failures.
* The phase-flip floor of a code is the smallest d_Z whose phase-flip rate alone is below the
  target; the 'ideal decoder' bound (data blocks at that decoder-independent factor instead of a,
  the ancilla term kept) is reported next to it.  Flags cannot lower it.

## 6b. Counting logical errors

A shot fails if any of the k logical observables is wrong; rates per round per logical qubit are
1 - (1 - P_fail)^(1/(R k)).  The alternative — each logical qubit's errors counted separately — is
larger by the mean number of logical qubits a failure hits, measured on the same shots
(`scripts/counting_convention.py`): ~2.6 (X memory, [15,9,3]), ~2.2 (Z memory).  The paper's
X-memory fit matches the per-qubit count, its Z-memory fits the any-of-k count; the overhead
conclusions are given in both (FINDINGS 13e).

## 7. Overheads

n_b (2 d_Z - 1) / k per logical qubit, n_b counting the logical ancillas; the minimum over the
codes and d_Z whose p_XL + p_ZL meets the target (central estimate; the conservative column uses
the 95 % upper bound of p_XL).  Two phase-flip models are carried everywhere: the paper's fit
('paper-pZL') and this work's model ('this-work-pZL').  A decoder can always ignore the flags, so
for a code without a run at some flag setting its flag-free rate is used there; more generally a
setting can always be degraded to one it can emulate (coarser aligned windows, flags dropped at
random, a class ignored).  At p_Z = 1e-3 the minimum overhead of a setting is the best over the
settings it can emulate; at p_Z = 1e-2, where the estimates are noisier, the 95 % bounds are closed
that way and a central value above such a bound is replaced by it.  Runs of the same setting with
independent seeds are pooled stratum by stratum (runs sharing a seed: the larger one is kept).

## 8. Checks of optimality

* Exact timing: exclusive-window MLE vs the exact coset ML (trellis) on the leading strata,
  `results/decoder_optimality.json` ([15,9,3], p_X = 1e-9) and `results/decoder_optimality_15_6_5.json`
  ([15,6,5], p_X = 1e-8, the strata of the p_Z = 1e-2 floors).
* Coarse timing: for strata of flagged events only, ML by enumerating every assignment 'window W
  flipped column c or nothing' (unflagged explanations are suppressed by p_X), against the MLE on
  the same samples: `results/decoder_optimality_windows.json`.
* Flag-free decoders at the paper's sampled points (BP+LSD-CS4, BP+OSD-CS7, ldpc's default
  BP+OSD-0): `results/decoder_variants_flagfree.json`.
