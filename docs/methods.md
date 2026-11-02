# Methods and assumptions

The calculation asks how much a signal locating a bit-flip event can reduce the physical qubits needed by an Elevator-code memory. The circuit model follows the [Elevator Codes paper, version 2](https://arxiv.org/abs/2601.10786v2), with the choices below where its description leaves room for interpretation. The flag model follows the [dissipative cat-qubit proposal, version 1](https://arxiv.org/abs/2607.01375v1) for idle qubits and extends it, as an assumption, to other locations. [References and input checksums](../data/README.md) identify the sources.

## Physical circuits

[`circuits.py`](../elevator/circuits.py) builds Stim circuits from [`schedule.py`](../elevator/schedule.py). An outer code $`[n,k,d_X]`$ has $`n`$ data blocks and $`n_{\rm anc}`$ logical ancillas in a column. Each row contains a phase-flip repetition block with $`d_Z`$ data qubits and $`d_Z-1`$ inner ancillas. Transversal CNOTs connect corresponding data qubits of adjacent rows.

An inner round has four ticks: prepare the inner ancillas in the X basis, apply CNOTs from ancilla $`j`$ to data qubit $`j`$, apply CNOTs to data qubit $`j+1`$, then measure the ancillas in the X basis. A logical ancilla's data qubits are prepared in the Z basis at the first tick of its first round and measured in Z at the last tick of its last round.

A CNOT followed by a SWAP compiles into two CNOT layers, ancilla to data then data to ancilla. A SWAP alone needs three layers. The main schedule places an inner round between successive logical operations and allows at least $`d_Z`$ rounds between a logical ancilla's preparation and readout.

Table I's noise channels are implemented as follows. Z-basis preparation and measurement have X errors with probability $`p_X`$; X-basis preparation and measurement have Z errors with probability $`p_Z`$. Idle qubits have both channels. A CNOT has IZ, ZI and ZZ errors with probability $`p_Z/3`$ each, and IX, XI and XX errors with probability $`p_X/3`$ each. Inner ancillas carry no noise between measurement and their next reset.

The Z memory starts the data in $`|0\rangle`$. Its observables are logical Z measurements on an information set of the outer code; its detectors compare successive outer checks. The X memory starts in $`|+\rangle`$, uses a basis of outer codewords for its logical X observables, and compares inner stabilisers with frames propagated through transversal CNOTs. Noiseless determinism and circuit distances are checked in [`test_core.py`](../tests/test_core.py), including distances 3 and 5 for the main outer codes.

## Circuit ambiguities

**Ancilla motion.** The main calculation measures each check during a sweep of the entire column, alternating direction. For $`n=15`$, this takes $`\max(d_Z,16)`$ inner rounds per check. With two logical ancillas, both sweep in lockstep, one block apart, measuring alternate checks. This is one reading of the paper, which does not specify the path completely.

Alternative schedules are retained: `compress` fits several operations between rounds to keep exactly $`d_Z`$ rounds per check; `span` stops at the final block in a check's support; `local` selects the nearest remaining check, approaches the nearer end of its support and resets in place after measuring it. The `ordered` variant keeps the matrix's check order while using local motion. See the [path comparison](../results/summary/schedule_comparison.md), [raw path samples](../results/sched_local/) and [circuit variants](../results/variants/).

The full sweep agrees better with the published [15,6,5] bit-flip fits. The shorter path improves agreement for [15,9,3] and [16,3,8]. Their full-sweep rates remain above the published fits, and that more pessimistic path is retained for the flag estimates. This discrepancy is unresolved; these circuits are not a uniquely reconstructed implementation of the paper.

**Idle-noise placement.** The main reading applies idle noise at inner-round boundaries and idle positions within inner CNOT layers, but omits it from blocks waiting during logical-operation layers: `idle_ctx=["edge","cnot"]`, labelled `noop`. The literal reading adds `"op"`, so every waiting block is noisy, and is labelled `all`. The main choice improves agreement without reproducing every published fit. The [comparison table](../results/summary/reproduction.md) gives 15 of 16 points within its factor-of-two/95% interval criterion for [15,6,5] with one ancilla, 6 of 16 for [15,9,3], and none of 14 for [16,3,8]. That criterion is an overlap test with a factor-of-two band, not equality with the fit.

The [literal-reading sensitivity](../results/summary/literal_reading.md) includes the extra phase noise as well as bit flips. It substitutes the repetition-code fit with extra idle ticks into the two-component phase model while retaining the main reading's fitted coefficients. That phase estimate is an approximation, not a separate fit of the complete memory. Literal-reading bit-flip comparisons at $`d_Z=17`$ use their own samples; the qubit selection also transfers those failure fractions to other distances with the literal reading's own fault sums.

## Block-level bit-flip model

The inner repetition code has bit-flip distance one. An X fault therefore changes the logical bit of a row during a slot, an interval between block-level operations. [`blocklevel.py`](../elevator/blocklevel.py) keeps the physical qubit, tick, before/after-CNOT location and fault class, then maps each fault to a slot. Locations with no logical effect are retained because they can still raise flags.

The reduced detector error model has the same mechanisms as the physical Stim circuit. Probability comparisons allow the small difference introduced by Stim's disjoint-error approximation. The executable comparison in [`test_blocklevel_equals_physical`](../tests/test_core.py) requires relative disagreement below $`10^{-4}`$ for its tested circuits; this is a tolerance, not an extra noise channel.

## Flags

An event randomises the cat qubit's bit, giving X with probability one half. A flag reports an event's possible location, not a certain X error. Each location's event probability is twice its Pauli-X probability, preserving the paper's X marginals when flags are ignored. At a CNOT, a control fault before the gate propagates as XX, a control fault after it gives XI, and a target fault gives IX.

Efficiency $`f`$ can differ between idle, gate, preparation and measurement locations. Only idle-qubit flags are supplied by the cat-qubit proposal; flags at the other classes are assumptions. The `herald` sensitivity instead treats a flagged event as a certain X error and must not be confused with the headline erasure model. See [`flags.py`](../elevator/flags.py) and the [assumption comparisons](../results/summary/assumptions.md).

A coarse flag identifies a qubit and an aligned window of $`w`$ ticks starting from tick zero. Exact timing, encoded as `window=0`, also distinguishes before and after a CNOT. A one-layer window does not. The schedule has four ticks per inner round and two or three per logical operation. For the main code, a check is roughly $`4d_Z+41`$ ticks and a typical outer round roughly 600 to 1,100 ticks; the exact duration follows the schedule and check support. All ticks are assumed to have equal duration because neither source fixes their relative physical durations.

Two effects are omitted: phase randomisation accompanying an event, whose rate is of order $`p_X`$ and hence a million times below $`p_Z`$ at the headline bias; and bit-flip events during inner-ancilla X-basis preparation or readout, where Table I specifies no X channel.

## Decoding

The unflagged Z memory uses ldpc BP+OSD, product-sum belief propagation with 100 iterations and OSD-CS order 7. The X memory uses BP+LSD, LSD-CS order 4. Low-noise X samples use min-sum with 30 iterations; the same-shot comparison in [`decoder_variants_flagfree.json`](../results/decoder_variants_flagfree.json) tests these settings against product-sum with 100 iterations. BP+OSD-CS7 is costly on that X-memory model. The paper specifies BP+OSD without fixing all these settings.

Flags are decoded with a most-likely-error integer programme, solved by HiGHS through SciPy. The decoder minimises the cost of an error explanation on the merged block-level detector model. Flagged windows allow at most one event explanation each. This exclusivity is an approximation for coarse windows, with corrections of order the window's event probability; exact timing resolves individual locations. BP+OSD with updated flag posteriors is also retained for comparison.

Choosing the most likely error explanation differs from summing probability over all explanations in a logical class. The exact-timing trellis checks give 237 versus 236 failures for the integer programme and logical maximum likelihood on [15,9,3], and 136 versus 132 on [15,6,5]. These are same-sample comparisons on the leading strata, not proof of equality. The raw counts are in [`decoder_optimality.json`](../results/decoder_optimality.json) and [`decoder_optimality_15_6_5.json`](../results/decoder_optimality_15_6_5.json).

For coarse timing, [`decoder_optimality_windows.json`](../results/decoder_optimality_windows.json) compares the integer programme with enumeration of every flagged-window assignment on flagged-only strata. Explanations containing unflagged flips are suppressed by their small prior and are omitted from that enumeration. The comparison is exact within that restriction. Isolated repetition codes use PyMatching; their comparison with logical maximum likelihood agrees within sampling statistics. [Known-answer checks](../results/known_answers.json) also enumerate correctable erasure patterns at code capacity and test them in circuits.

## Rare bit-flip rates

The headline target lies far below direct sampling. [`strata.py`](../elevator/strata.py) and [`flagstudy.py`](../elevator/flagstudy.py) use independent Poisson processes with intensities $`U`$ for unflagged X errors and $`S`$ for flagged events:

```math
P_{\rm fail}=\sum_{a,b\geq0}{\rm Pois}(a;U)\,{\rm Pois}(b;S)\,F(a,b).
```

The conditional failure probability $`F(a,b)`$ is estimated by sampling exactly $`a`$ unflagged X errors and $`b`$ flagged events, plus false flags if enabled. Positions follow their physical intensities. With no false flags, every single-error mechanism is decoded to obtain $`F(1,0)`$ exactly. Window exclusivity gives $`F(0,1)=0`$ when the model has no undetectable logical of weight at most two, which is checked. With exact timing, $`F(0,b)=0`$ below the code distance.

Sampling starts with `n1` samples in low-order strata, by default through $`a+b\leq(d_X+1)/2+1`$. Higher orders are sampled when their Poisson weight can affect the estimate, using a threshold of one thousandth of the running estimate. Further samples go to the largest product of weight and interval width. Sampling stops at the requested relative tolerance or when the upper rate is below the absolute tolerance, normally $`10^{-13}`$ per round per logical qubit. The task specification records overrides. Skipped strata enter the upper calculation at their available analytic bound, otherwise at failure probability one; the tail beyond `kmax` enters at its full Poisson weight.

Wilson intervals are calculated per sampled stratum, then weighted and summed. The resulting nominal 95% bounds are conditional on the model; they do not include phase-model uncertainty, missing physics or a general guarantee of simultaneous coverage across all strata. Counts chosen with the upper bit-flip bound are not confidence intervals for hardware cost.

The $`p_X=10^{-9}`$ and $`10^{-8}`$ rates are model estimates. [Held-out direct samples](../results/summary/validation.md) at $`p_X=3\times10^{-7}`$ and $`10^{-6}`$ test both stratification at the same noise and reweighting of the lower-noise failure fractions. Agreement there supports the model within the tested range, not direct observation of the headline rates.

### Perfectly located events

With exact timing, perfect efficiency and no false flags, the decoder knows all event positions and every event produces X with probability one half. Let $`K`$ be the subsets of an event set with trivial syndrome, and $`K_0`$ those also trivial logically. The conditional failure probability is $`1-|K_0|/|K|`$.

[`perfect_flags_exact.py`](../scripts/perfect_flags_exact.py) evaluates that expression without decoding, using four million sampled event sets per stored case in [`perfect_flags_exact.json`](../results/perfect_flags_exact.json). The expression is exact for a given set; the average over sets is still sampled, and tiny or zero observed rates retain sampling uncertainty. These samples replace the decoder-sampled flagged-only strata for all-location, exact-timing settings with equal efficiency across classes. Their location distribution is unchanged when efficiency falls below one. The analysis uses the nearest available distance and carries the sample counts into its bounds.

### Analytic stratum bounds

[`strata_caps.py`](../scripts/strata_caps.py) bounds failures using the merged model's distance and the decoder's own costs. For exact erasure flags without false alarms, all flagged choices have zero cost. Comparing a returned explanation $`\hat{x}`$ with the true unflagged explanation $`x'`$ gives:

```math
\sum_{c\in\hat{x}}w_c\leq\sum_{c\in x'}w_c+\epsilon.
```

Here $`\epsilon`$ accounts for the integer solver's gap. Failure requires the difference between the explanations to be an undetectable logical. A flagged location can contribute at most one column to that difference, so the decoded unflagged explanation needs at least $`q=d_{\rm DEM}-a-b`$ columns. If $`S_q`$ is the sum of the $`q`$ smallest background costs and $`W_b(u)`$ bounds a true column's cost after removing the largest $`b`$ other contributions, then for $`q\geq1`$:

```math
F(a,b)\leq\Pr\!\left[\sum_{i=1}^{a}W_b(u_i)\geq S_q-\epsilon\right].
```

The bound is zero when the maximum possible sum is smaller than the threshold. Otherwise it is evaluated by column and class for a single unflagged error, or by convolution with costs rounded upwards for several errors. Per-column, per-class counts are quadratic in $`d_Z`$: fitted at 17, 19 and 21, checked at 25 and 33, and built directly below 17. Bounds are recomputed at transfer targets. An exhaustive meet-in-the-middle search over up to four columns verifies $`d_{\rm DEM}\geq5`$ for [15,6,5] with either ancilla count.

The current [`numbers.json`](../results/summary/numbers.json) `strata_caps` entry checks 1,139 sampled strata with no violation. A violation means a sampled failure in a zero-bound stratum, or a Wilson lower endpoint above a positive bound; reconstruction of the decoder costs is tested in [`test_core.py`](../tests/test_core.py). Zero bounds remove otherwise unresolved zero-failure strata. They depend on the setting and distance: in particular, $`F(1,2)`$ is not uniformly bounded by zero across the full distance scan. Sampled upper endpoints are capped by these bounds; unsampled strata use the bound where available.

### False flags

False flags occur independently with probability $`r`$ per physical qubit per tick. For exact timing the implementation applies this per physical location; for a coarse window it uses the probability of at least one false flag during its covered ticks. The headline has $`r=0`$.

With false alarms, the usual zero-stratum shortcuts cannot be assumed. [`false_flag_bounds.py`](../scripts/false_flag_bounds.py) handles distance-three models, using unflagged costs $`w_c`$ and flagged-window costs $`v_{W,c}=\log(\pi_{W,0}/\pi_{W,c})`$, including the false-flag rate in the posteriors. Failure requires an alternative explanation that completes a logical and costs no more than the truth, allowing the solver gap.

The bound explicitly counts alternatives with numbers of unflagged and falsely flagged columns $`(1,1)`$, $`(0,2)`$, $`(1,2)`$ and $`(0,3)`$. Other allowed structures are bounded by the Poisson tail of the false-flag count. Two or more unflagged columns must be excluded by cost, otherwise the routine returns no bound. For $`F(1,0)`$, the truth's cost excludes its three largest window contributions and includes a tail for four or more false flags on that column. For $`F(0,1)`$, a coarse window may substitute another column; with exact timing a sufficient cost inequality can still prove a zero bound. The $`F(0,2)`$ bound is used only for exact timing. These decoding-free bounds replace Wilson upper endpoints only when smaller. [Raw bounds](../results/false_flag_bounds.json) and the [false-flag tables](../results/summary/assumptions.md) retain the tested settings.

### Transfers

Changing noise or distance changes the exact intensities and can also change the conditional failure fractions through the decoder priors and circuit layout. The transfer approximation reuses failure fractions from the nearest sampled distance, preferring the same $`p_X`$ and otherwise the reference low-noise samples. The target-curve selection resolves a distance tie towards the larger sampled distance.

[`class_sums.json`](../results/summary/class_sums.json) supplies the fault intensities. Its per-class sums are quadratic in $`d_Z`$ from 17 upwards, checked at further distances by [`class_sums.py`](../scripts/class_sums.py). The analysis uses these polynomials beyond the computed distances. Tests include the noise transfers above, distance 15 to 17 and 19 in [`transfer_check.md`](../results/summary/transfer_check.md), and 17 to 25 and 33 in the [higher-noise tables](../results/summary/README.md#noise-and-error-target). A transferred rate remains a prediction even when its intensities are calculated exactly.

## Phase-flip models

[`repcode.py`](../elevator/repcode.py) samples the isolated inner repetition code with PyMatching. [`phasemodel.py`](../elevator/phasemodel.py) fits $`\log p_{\rm rep}`$ as a straight line in $`(d_Z+1)/2`$ at each sampled noise level, weighted by failure counts. Fit covariances are inflated by reduced chi-squared when it exceeds one. Coefficients are interpolated linearly in log noise, or extrapolated from the nearest two noise levels outside the sampled range. Where enough distances are sampled, the largest distance at each noise is held out and predicted. The [phase-model table](../results/summary/phase_model.md) records those checks and the sampled range, which reaches distance 69 at the higher noise levels.

For the complete X memory, the principal model separates data blocks from the moving ancilla:

```math
k p_{ZL}=n a\,p_{\rm rep}(d_Z,p_Z)
 +n_{\rm anc}g\,s(d_Z)\,p_{\rm rep}(d_Z,\kappa p_Z),
\qquad s(d_Z)=\min\!\left(1,\frac{n+1}{d_Z}\right).
```

The data term has fitted multiplier $`a`$. The ancilla sees an effective noise multiplier $`\kappa`$, fitted near two, during its sweeping fraction $`s`$, with weight $`g`$. The held-out test fits at $`p_Z\geq3\times10^{-3}`$ and predicts lower-noise samples. Runs with ancilla noise suppressed constrain the data term. A fitted memory-to-repetition ratio is retained as a fallback if the two-component fit is unavailable.

The data-block penalty also has a decoder-independent component. Even a decoder told every other block's errors must decode a repetition block exposed to the logical-operation gates. [`op_noise_penalty.py`](../scripts/op_noise_penalty.py) measures the effect of three transversal CNOT layers per check, each adding Z with probability $`2p_Z/3`$, relative to a plain repetition code where both have many sampled failures. The phase-floor comparison replaces $`a`$ by the lower end of that penalty's interval and retains the ancilla term. It is a bound within this circuit and phase model, not a universal hardware limit.

Every main comparison also carries the paper's phase formula, labelled `paper-pZL`; the fitted model above is `this-work-pZL`. In [`overhead.py`](../elevator/overhead.py), the paper formula is rescaled by $`(n+n_{\rm anc})/16`$ and $`9/k`$. Applying it to Hamming codes is an extension assumption: the paper did not fit those codes. The two-component model likewise transfers its fitted coefficients to the other code layouts. Both models are extrapolated where the target falls below sampled rates. Flags do not remove the phase-flip floor.

## Counting logical errors

A shot fails when any of its $`k`$ logical observables is wrong. The conversion to errors per inner round per logical qubit, for $`R`$ rounds, is:

```math
p_L=1-(1-P_{\rm any})^{1/(Rk)}.
```

Counting each logical qubit's errors separately instead gives the mean marginal rate. At low failure probability their ratio is the mean number of logical qubits hit per failed shot. The same-shot measurements in [`counting_convention.json`](../results/counting_convention.json) give about 2.6 for the [15,9,3] X memory and 2.2 for its unflagged Z memory. The published X-memory fit agrees better with the marginal convention, while its Z-memory fits agree better with the any-observable convention. The paper-fit headline retains the published formula as supplied, so it is not a fully harmonised counting comparison.

The `convention` entry in [`numbers.json`](../results/summary/numbers.json) gives the measured multiplicities, both phase-rate conventions and a marginal-convention sensitivity using this work's phase model. Its main-code count still falls from 77.3 to 51.6 at 90% exact all-location efficiency. Applying measured multiplicities to unmeasured distances and flag settings is itself an approximation; this is not a fresh marginal-error simulation of every candidate.

## Choosing a qubit count

The physical qubits per logical qubit, including both types of ancilla, are:

```math
Q=\frac{(n+n_{\rm anc})(2d_Z-1)}{k}.
```

The analysis chooses the smallest count among evaluated code and distance candidates satisfying $`p_{XL}+p_{ZL}\leq p_{\rm target}`$. The upper-bound selection replaces only $`p_{XL}`$ with its nominal 95% upper endpoint. Missing candidates are not zero-error candidates.

A decoder may discard flags, ignore a location class or coarsen aligned timing windows. The main headline takes the best count among settings that can be emulated this way, using an unflagged rate when a code has no matching flagged sample. At $`p_Z=10^{-2}`$, only upper bounds are closed over these usable settings, and a central estimate is clipped if it exceeds such a bound, to avoid selecting minima of noisy central estimates. The target curves use their specified flag setting and the nearest-distance transfer procedure; they do not substitute another setting. See [`analyze.py`](../scripts/analyze.py) and the [table guide](../results/summary/README.md).

Independent-seed samples of the same setting are pooled stratum by stratum. If files share a seed, only the larger sample is retained. Required-efficiency estimates interpolate log bit-flip rate against $`\log(1-f)`$ between tested efficiencies; the reported bracket distinguishes interpolation from direct simulation. Pareto tables retain settings for which none of the evaluated alternatives improves the stated requirements without worsening another. They do not establish a global minimum over all possible codes, circuits or decoders.

## Software and reuse

[`requirements.txt`](../requirements.txt) pins Stim and sinter 1.16.0, ldpc 2.4.1, PyMatching 2.4.0, NumPy, SciPy and Matplotlib. Stim supplies circuits and detector models; ldpc supplies BP+OSD and BP+LSD; PyMatching decodes repetition codes; SciPy supplies HiGHS and fitting routines; NumPy handles arrays and sampling; Matplotlib renders figures. Sinter is installed alongside Stim; the sampling entry points here use the repository's own task runner.

[Reproduction instructions](../REPRODUCE.md) separate regeneration from saved evidence from fresh sampling. [Dependency licences and matrix provenance](../data/README.md) accompany the linked papers. The repository's original material is dedicated under [CC0 1.0](../LICENSE); dependencies and referenced material retain their own licences.
