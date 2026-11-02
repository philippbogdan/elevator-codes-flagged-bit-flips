# Circuit variants

[z_variants_v1.json](z_variants_v1.json) compares unflagged Z-memory rates under different ancilla paths and idle-noise placements. These cases support the [circuit-ambiguity discussion](../../docs/methods.md#circuit-ambiguities), not a separate headline saving.

[`variants_z.py`](../../scripts/variants_z.py) regenerates this list directly; it is an auxiliary comparison rather than a JSONL task file. The full [reproduction path](../../REPRODUCE.md) supplies its output path and sample count.
