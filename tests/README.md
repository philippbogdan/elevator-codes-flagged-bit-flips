# Circuit and decoder invariants

[`test_core.py`](test_core.py) checks outer-code parameters, noiseless circuits, physical versus block-level detector models, circuit distances, erasure correction and the published-fit qubit baseline. It also checks the cost reconstruction used by the analytic bounds and samples cases bounded to have no failures.

These tests catch implementation inconsistencies. They do not establish gate-flag availability or validate extrapolated error rates. [Direct-sampling comparisons](../results/summary/validation.md) and [methods](../docs/methods.md) cover those separate questions. The full path in [REPRODUCE.md](../REPRODUCE.md) runs the tests before recomputing results.
