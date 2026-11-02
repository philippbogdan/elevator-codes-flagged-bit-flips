# Reproduce the results

From the repository root, run:

```sh
./reproduce.sh
```

This rebuilds the analysis from the included samples in minutes, then renders the README figures and checks the headline. It creates `.venv` and installs [`requirements.txt`](requirements.txt) if that environment is absent. With `uv` available it selects Python 3.12; otherwise it uses `python3`, which must support the pinned packages. An existing environment is reused without reinstalling dependencies. Only the initial dependency installation needs network access; the papers need not be downloaded.

## What the command writes

| Step | Output |
|---|---|
| [`scripts/analyze.py`](scripts/analyze.py) | Tables and `numbers.json` in [results/summary/](results/summary/), including both phase-flip models, transfers, sensitivity comparisons and code selections. |
| [`scripts/figures.py`](scripts/figures.py) | `memory-saving`, `flag-requirements` and `noise-and-target`, as RGB PNG and SVG in [figures/](figures/). The last figure compares four selections at a fixed error target. |
| [`scripts/check_headline.py`](scripts/check_headline.py) | Console checks of the qubit count, selected code and distance for each of its 18 entries; a non-zero exit on mismatch. |

The analysis prints its output directory. The checker then prints an `ok` line for each expected entry, ending with:

```text
18 of 18 headline numbers match
```

Among those entries are 88.0 without flags, 58.7 for the paper codes at 90% exact all-location efficiency, and 35.7 including Hamming at 99%, all with the paper phase model. The matching comparison with this work's phase model is 77.3 to 51.6. Conditions and upper-bound selections are in [headline.md](results/summary/headline.md). Matching these entries verifies regeneration from the saved evidence; it does not validate the physical assumptions independently.

The third figure has its own selection checks in the renderer. It rebuilds candidate rates, checks all 32 central and upper-bound rate floors and the counts at the upper-bound floors against `numbers.json["fig2_this_work"]`, then selects the smallest count meeting 10^-12 errors per inner round per logical qubit for each phase model and noise level. These four bars use the paper codes, 99% exact all-location flags, bias 10^6, no false alarms and the upper bit-flip bound. The [figure guide](figures/README.md#fixed-target-selections) lists their counts and distance transfers. The 18-entry headline checker does not separately check all four bar selections.

## Compare with the stored output

Before rebuilding, preserve the generated tables and figures in a new directory:

```sh
mkdir comparison-before
cp -R results/summary comparison-before/summary
cp -R figures comparison-before/figures
./reproduce.sh
diff -ru comparison-before/summary results/summary
diff -ru comparison-before/figures figures
```

No output from either `diff` means the tables, numerical JSON and figures are byte-for-byte identical. Use a new comparison directory on another attempt. The rebuild overwrites generated output but leaves the raw samples and task files intact. To compare one table or number directly, inspect [headline.md](results/summary/headline.md), the `headline` object in [numbers.json](results/summary/numbers.json), and the explicit expectations in [check_headline.py](scripts/check_headline.py).

The renderer fixes SVG identifiers, omits creator and date metadata, and writes opaque RGB PNGs without text metadata, giving deterministic files with the same inputs, fonts and package versions. Different fonts or package versions can still change their appearance and bytes. Compare the PNGs visually and check the first two figures against `headline`; for the third, inspect `target_candidates` and `fixed_target` in the renderer, since `fig2_this_work` stores rate floors rather than the four fixed-target selections. A file difference by itself does not establish a numerical difference.

## Full computation

```sh
./reproduce.sh all
```

The full path runs the core tests, rebuilds the analytic stratum bounds, runs every file in [tasks/](tasks/), then runs the decoder, erasure, circuit-sensitivity, perfect-flag, fault-intensity, counting-convention and false-flag checks listed in [`reproduce.sh`](reproduce.sh). It ends with the same table rebuild, figures and headline check. The included matrices and implemented reference formulas supply all scientific inputs.

Each `tasks/<folder>.jsonl` corresponds to `results/<folder>/`. The runner uses local CPU processes, defaulting to the detected CPU count. Existing direct-sampling results resume or are skipped when their stopping rule has been met; an existing stratified result with a matching specification is skipped. The standalone checks are rerun and overwrite their own outputs. Thus `all` on the supplied repository is a resume-and-check path, not a fresh sample of every task.

For a fresh computation while preserving the stored evidence, start in a separate copy of the repository. In that copy, use a new backup name and move the results aside before running:

```sh
mv results results-stored
mkdir -p results/variants
./reproduce.sh all
```

For planning, allow about 1,500 CPU core-hours for a full recomputation. This estimate comes only from a comment in the original run's reproduction script; it has no measurement behind it. The saved `seconds` fields mix summed direct-sampling time with elapsed time for parallel stratum sampling, so their sum is not a reliable CPU budget. Sampling outcomes and runtimes can vary with process count, library versions and stopping rules even with the stored seeds. Compare fresh failure counts and intervals using the [validation tables](results/summary/validation.md) and [methods](docs/methods.md), rather than requiring raw JSON to match byte for byte.

For one results folder, or to limit CPU processes, use the same runner directly:

```sh
.venv/bin/python scripts/run_tasks.py tasks/flag_main.jsonl results/flag_main --procs 2
```

In a fresh calculation, build `results/strata_caps.json` first with `scripts/strata_caps.py`; the full command already does this. Keep the chosen result directory empty for a fresh sample, or retain it to use the runner's resume rules. `scripts/run_tasks.py --help` describes the available controls. A read-only coverage check is:

```sh
.venv/bin/python scripts/orphans.py
```

It should end with `0 unmatched specifications`: every saved task result has a specification in `tasks/`. Auxiliary checks have dedicated scripts rather than task specifications. The [scripts guide](scripts/README.md) maps them to their evidence files.
