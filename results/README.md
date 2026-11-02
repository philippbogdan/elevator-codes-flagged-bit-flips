# Evidence for the memory estimates

The [summary tables](summary/) connect each qubit count to its noise model, flag setting and error estimate. The JSON files here retain the samples, task specifications and separate checks needed to inspect that calculation. A small reported rate may be a stratified estimate or a transfer, not a directly observed frequency; [methods](../docs/methods.md) explains the distinction.

## Samples

| Folder | What it tests |
|---|---|
| [flag_main/](flag_main/), [flag_supp/](flag_supp/) | Main outer codes across flag efficiencies, location classes and timing windows. |
| [flag_alt/](flag_alt/), [flag_ham63/](flag_ham63/) | Hamming and extended Hamming alternatives behind the larger conditional saving. |
| [flag_16_3_8/](flag_16_3_8/) | The additional paper code in the lower-bias comparison. |
| [flag_bias/](flag_bias/) | Transfer in physical bit-flip rate and noise bias. |
| [flag_pz1e2/](flag_pz1e2/) | Bit-flip samples for the higher-noise comparison and distance-transfer checks. |
| [flag_validation/](flag_validation/) | Direct Monte Carlo against stratification where failures can be sampled. |
| [flag_falseflag/](flag_falseflag/), [flag_herald/](flag_herald/) | False alarms and the more optimistic certain-X interpretation of a flag. |
| [flag_literal/](flag_literal/) | Bit flips with idle noise on every waiting block. |
| [phase_rep/](phase_rep/), [phase_rep_literal/](phase_rep_literal/) | Isolated repetition-code phase noise, with and without extra idle ticks. |
| [phase_xlow/](phase_xlow/), [phase_xlarge/](phase_xlarge/), [phase_ancdiag/](phase_ancdiag/) | Full-memory phase samples, longer repetition blocks and ancilla-noise sensitivity. |
| [repro_z/](repro_z/), [repro_x/](repro_x/), [repro_16_3_8/](repro_16_3_8/) | Unflagged memories compared with published fits. |
| [sched_local/](sched_local/), [variants/](variants/) | Ancilla motion and circuit interpretations behind the unresolved fit discrepancies. |

Each sampled JSON has a `spec`. Its matching line in `tasks/<folder>.jsonl` supplies the inputs to rerun that result. Direct samples store `shots` and `fails`; stratified samples store event intensities, per-stratum counts, exact cases and combined estimates. Inspect the specification before comparing two files. Independent seeds can be pooled, while repeated seeds cannot be counted twice.

## Separate checks

| Evidence | Claim it checks |
|---|---|
| [known_answers.json](known_answers.json) | Erasure correction on repetition and outer codes, including circuit tests. |
| [decoder_optimality.json](decoder_optimality.json), [decoder_optimality_15_6_5.json](decoder_optimality_15_6_5.json), [decoder_optimality_windows.json](decoder_optimality_windows.json) | Most-likely-error decisions against logical maximum likelihood on matched samples. The counts differ. |
| [decoder_variants_flagfree.json](decoder_variants_flagfree.json), [decoder_check_16_3_8.json](decoder_check_16_3_8.json) | Sensitivity to decoder settings without flags. |
| [sensitivity_15_9_3.json](sensitivity_15_9_3.json) | Check order, memory duration and decoding in the circuit with a fit discrepancy. |
| [strata_caps.json](strata_caps.json), [false_flag_bounds.json](false_flag_bounds.json) | Distance and cost bounds used to control rare unsampled failures. |
| [perfect_flags_exact.json](perfect_flags_exact.json) | Sampled event sets whose conditional failure probability can be evaluated without decoding. |
| [counting_convention.json](counting_convention.json) | Any-observable failure versus errors counted separately per logical qubit. |
| [op_noise_penalty.json](op_noise_penalty.json) | The data-block phase penalty from logical-operation gates. |

The [script guide](../scripts/README.md) maps these files to their calculations. [Reproduction](../REPRODUCE.md) separates rebuilding tables from rerunning the samples.
