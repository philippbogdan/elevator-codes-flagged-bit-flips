# Circuits, flags and error models

This package connects a physical Elevator-code memory to the qubit-count calculation. [`circuits.py`](circuits.py) and [`schedule.py`](schedule.py) define the physical operations; [`blocklevel.py`](blocklevel.py) reduces the bit-flip memory while preserving physical flag locations. [`codes.py`](codes.py) loads the published matrices and constructs the alternatives.

[`flags.py`](flags.py) models event detection, timing and false alarms. [`mle.py`](mle.py) solves the error-explanation integer programme; [`trellis.py`](trellis.py) and the logical-class decoder in `flags.py` support independent comparisons. [`strata.py`](strata.py) and [`flagstudy.py`](flagstudy.py) estimate rare failures by event count.

[`repcode.py`](repcode.py), [`phasemodel.py`](phasemodel.py) and [`overhead.py`](overhead.py) supply phase rates and physical qubit counts. [`decode.py`](decode.py), [`tasks.py`](tasks.py), [`known_answers.py`](known_answers.py) and [`analysis.py`](analysis.py) provide sampling, erasure checks and result loading.

For reuse, set the ancilla path, idle-noise locations and flag interpretation explicitly: some constructors default to the literal idle reading, while the headline uses `idle_ctx=["edge","cnot"]`. [Methods](../docs/methods.md) states the assumptions; [task specifications](../tasks/) record the exact settings behind each result.
