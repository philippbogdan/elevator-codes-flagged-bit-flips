# Exact simulation specifications

Each `tasks/<folder>.jsonl` contains the specifications stored in `results/<folder>/`, one JSON object per line. These are the inputs needed to rerun the samples behind the qubit counts and sensitivity tables. [The results guide](../results/README.md) explains what each folder tests.

The `kind` selects physical Stim sampling (`phys`), isolated repetition sampling (`rep`), direct block-level sampling (`direct_block`) or fixed-event-count estimation (`strata`). Circuit fields set the outer code, repetition distance, noise, ancilla count and path. Flag fields set efficiency, covered locations, timing and false alarms. Sampling fields set the seed, sample limits, tolerances and stopping rules. Not every field applies to every kind.

[`task_id`](../elevator/tasks.py) hashes the specification, excluding `shots`, `max_fail` and `outdir`, to select the result filename. The runner also compares the complete specification before deciding whether a saved result can be reused. Changes to a specification therefore need care even when its filename stays the same.

[`run_tasks.py`](../scripts/run_tasks.py) executes a file using local CPU processes. [Reproduction instructions](../REPRODUCE.md) cover both resuming and fresh sampling. The separate decoder and analytic checks in the results root use dedicated scripts; they are not JSONL tasks.
