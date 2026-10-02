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
  Variants tried: 'compress' (exactly d_Z rounds per check, several operations per gap) and
  'span' (stop after the last block of the check).  Two ancillas: both sweep in lockstep, one
  block apart, each measuring alternate checks.
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
  against an exact maximum-likelihood (coset) trellis decoder: identical failures on the
  leading strata (999 of 1000 shots agree).  BP+OSD with flag posteriors is kept as the
  paper-like decoder (20-30 % more failures).
* Isolated repetition code: PyMatching; equal to exact ML within statistics.

## 5. Rare-event estimation of bit flips, `elevator/strata.py`, `elevator/flagstudy.py`

Events are independent Poisson processes, so P_fail = sum_{a,b} Pois(a;U) Pois(b;S) F(a,b) with
a unflagged X errors, b flagged events, U and S exact intensities.  F(a,b) is estimated by
sampling exactly a and b events (plus false flags) and decoding; F(1,0) is computed exactly by
decoding every mechanism alone, F(0,1) = 0 is exact for a decoder with window exclusivity when
the DEM has no logical of weight <= 2 (checked).  Truncated or skipped strata enter the upper
confidence bound with weight one.  The estimator is validated against direct Monte Carlo at
p_X where both run (`results/summary/validation.md`).

## 6. Phase flips, `elevator/repcode.py`, `elevator/phasemodel.py`

p_ZL = (n_b / k) c(d, p) p_rep(d, p): p_rep from the isolated repetition code with the elevator's
inner round (sampled to ~1e-9 per round, fitted with a five-parameter model validated on held-out
points); c from the elevator X memory over (n_b/k) p_rep where both are sampled.
