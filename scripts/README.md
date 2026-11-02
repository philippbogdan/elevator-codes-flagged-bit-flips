# Rebuild and inspect the evidence

[`analyze.py`](analyze.py) turns the saved samples into the tables and numerical selections behind the qubit saving. [`figures.py`](figures.py) draws the three README figures as RGB PNGs and SVGs. [`check_headline.py`](check_headline.py) checks the counts, codes and distances of 18 headline entries. [Reproduction instructions](../REPRODUCE.md) give the common command and a stored-output comparison.

```text
saved samples -> analyze.py -> summary tables and numbers.json
circuits + saved samples + summary -> figures.py -> three PNG/SVG pairs
numbers.json -> check_headline.py -> 18 expected entries
```

The first two figures use the headline selections. For `noise-and-target`, the renderer rebuilds candidate rates and checks all 32 central and upper-bound rate floors, plus the counts at the upper-bound floors, against `numbers.json["fig2_this_work"]`. It then selects four minimum counts at 10^-12 errors per inner round per logical qubit, using paper codes, 99% exact all-location flags, bias 10^6, no false alarms and the upper bit-flip bound. The [figure guide](../figures/README.md#fixed-target-selections) records the two phase models, two noise levels and distance transfers. The 18-entry checker does not separately verify all four bars.

| Script | Purpose and output |
|---|---|
| [run_tasks.py](run_tasks.py) | Run a JSONL specification file into a chosen results folder; resume or skip matching results according to their stopping rules. |
| [orphans.py](orphans.py) | Check whether every saved task result has a specification in `tasks/`. The default only reads files. |
| [summarize_repro.py](summarize_repro.py) | Print unflagged rates against the published fits for chosen result directories. |
| [class_sums.py](class_sums.py) | Physical fault intensities by location class, stored in `results/summary/class_sums.json`. |
| [strata_caps.py](strata_caps.py) | Merged-model distances and count polynomials in `results/strata_caps.json`; supplies analytic stratum bounds. |
| [false_flag_bounds.py](false_flag_bounds.py) | Cost-based failure bounds with false alarms in `results/false_flag_bounds.json`. |
| [perfect_flags_exact.py](perfect_flags_exact.py) | Sample event positions and evaluate their conditional failure probability without decoding, writing `results/perfect_flags_exact.json`. |
| [known_answers.py](known_answers.py) | Erasure-pattern checks at code capacity and in circuits, writing `results/known_answers.json`. |
| [decoder_optimality.py](decoder_optimality.py), [decoder_optimality_15_6_5.py](decoder_optimality_15_6_5.py) | Exact-timing comparison of error-explanation decoding with logical maximum likelihood; outputs share the script stems. |
| [decoder_optimality_windows.py](decoder_optimality_windows.py) | Coarse-window comparison on flagged-only strata, writing `results/decoder_optimality_windows.json`. |
| [decoder_variants_flagfree.py](decoder_variants_flagfree.py), [decoder_check_16_3_8.py](decoder_check_16_3_8.py) | Same-shot comparisons between unflagged decoders; outputs share the script stems. |
| [sensitivity_15_9_3.py](sensitivity_15_9_3.py), [variants_z.py](variants_z.py) | Circuit and decoder choices behind the fit discrepancy; write `results/sensitivity_15_9_3.json` and the chosen variant file. |
| [counting_convention.py](counting_convention.py) | Any-observable versus marginal error counts in `results/counting_convention.json`. |
| [op_noise_penalty.py](op_noise_penalty.py) | Phase-flip cost of the logical-operation gates in `results/op_noise_penalty.json`. |

The calculation scripts write their outputs. Use the commands in [REPRODUCE.md](../REPRODUCE.md) to preserve the stored evidence before fresh sampling. [`methods.md`](../docs/methods.md) explains which checks support each approximation and which circuit questions remain unresolved.
