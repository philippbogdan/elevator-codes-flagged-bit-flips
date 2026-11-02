# Tables behind the qubit saving

[headline.md](headline.md) gives the matched code selections: 88.0 to 58.7 with the paper phase model and 77.3 to 51.6 with this work's model. [numbers.json](numbers.json) stores the unrounded values and their component evidence. Both comparisons assume 90% exact all-location flags and no false alarms at the main noise and target setting.

Counts include ancillas. Rates are per inner round per logical qubit. `paper-pZL` uses the published phase formula, extended by rescaling for Hamming codes; `this-work-pZL` uses the fitted repetition-plus-ancilla model. A bracketed upper-bound count uses the nominal 95% upper bit-flip rate, with the phase model fixed. It is not a confidence interval for total hardware cost. A transferred rate reuses sampled failure fractions at another noise or distance; it is not directly sampled at the stated target.

## Flag requirements

- [Headline](headline.md): central and upper-bound selections, including idle-only flags and coarse timing.
- [Required efficiency, paper phase model](required_f_paper-pZL.md) and [fitted phase model](required_f_this-work-pZL.md): interpolated efficiencies with their tested brackets.
- [Main flags, paper phase model](flags_main_paper-pZL.md) and [fitted phase model](flags_main_this-work-pZL.md): per-code error rates and overheads. [Alternative codes](flags_alt_this-work-pZL.md) gives the Hamming comparison with the fitted phase model.
- [Assumptions](assumptions.md): flag classes, false alarms, certain-X flags and noise placement.

## Code selection

[Pareto settings with the paper phase model](pareto_paper-pZL.md) and [with the fitted phase model](pareto_this-work-pZL.md) identify non-dominated combinations among the evaluated candidates. They expose the trade between qubit count, flag efficiency, covered locations, timing and false alarms. They do not prove a minimum over every possible code or decoder. [Phase floors](phase_floor.md) and [limits](limits.md) separate phase noise from flagged and unflagged bit flips.

## Noise and error target

- [Bias with the paper phase model](bias_paper-pZL.md) and [with the fitted phase model](bias_this-work-pZL.md) give the sampled bias comparisons. The [paper-model bias reconstruction](fig1_this_work_paper-pZL.md) and [fitted-model reconstruction](fig1_this_work_this-work-pZL.md) add distance transfers.
- [Target-rate floors with the paper phase model](fig2_this_work_paper-pZL.md) and [with the fitted phase model](fig2_this_work_this-work-pZL.md) give the lowest reachable rate within each scan, not the smallest cost at an arbitrary target. The [README figure](../../figures/noise-and-target.png) instead selects four minimum counts at 10^-12 errors per inner round per logical qubit, using the upper bit-flip bound with 99% exact all-location flags, bias 10^6 and no false alarms. For the paper codes, the paper fits and this work's phase model select 58.7 and 51.6 at p_Z = 10^-3, then 269.3 and 524.2 at p_Z = 10^-2. The [figure guide](../../figures/README.md#fixed-target-selections) records the selected codes, ancillas, distances, scan limits and higher-noise distance transfers; these are model estimates below direct sampling.
- [Higher-noise floors](pz1e2_floors.md), [paper-model selections](pz1e2_paper-pZL.md) and [fitted-model selections](pz1e2_this-work-pZL.md) cover the higher physical phase-flip rate and its distance-transfer checks.

## Assumptions and checks

[Reproduction against the published fits](reproduction.md), [ancilla paths](schedule_comparison.md) and [literal idle noise](literal_reading.md) expose the unresolved circuit choices. The literal-reading flag tables use the [paper phase model](flags_literal_paper-pZL.md) and [fitted phase model](flags_literal_this-work-pZL.md).

[Direct-sampling validation](validation.md), [distance and noise transfers](transfer_check.md), [phase fits](phase_model.md) and [fault intensities](class_sums.json) support the rare-rate estimates. `numbers.json` also contains `checks`, `strata_caps` and `convention`, linking decoder comparisons, analytic bounds and logical-error counting to the [raw evidence](../README.md).

[`analyze.py`](../../scripts/analyze.py) regenerates these tables and `numbers.json`; [`class_sums.py`](../../scripts/class_sums.py) regenerates the fault-intensity input. [Reproduction instructions](../../REPRODUCE.md) explain how to compare the output with the saved files.
