
## Literal idle-noise reading: phase flips

Isolated repetition code with the extra idle ticks of the literal reading (2.73 per round on average) against the noop reading, per round:

| p_Z | d_Z | literal | noop (model) | ratio |
|---|---|---|---|---|
| 1.0e-03 | 5 | 1.03e-05 | 2.34e-06 | 4.42 |
| 1.0e-03 | 7 | 3.41e-07 | 5.57e-08 | 6.13 |
| 1.0e-03 | 9 | 1.38e-08 | 1.33e-09 | 10.40 |
| 2.0e-03 | 7 | 6.30e-06 | 9.61e-07 | 6.55 |
| 5.0e-03 | 5 | 1.12e-03 | 2.22e-04 | 5.05 |
| 5.0e-03 | 7 | 2.18e-04 | 3.03e-05 | 7.19 |
| 5.0e-03 | 13 | 2.12e-06 | 7.72e-08 | 27.42 |

Phase-flip floor at p_Z = 1e-3, 1e-12 under the literal reading (two-component model with the literal repetition code; approximation):

| code | d_Z noop | d_Z literal | overhead literal |
|---|---|---|---|
| [15,9,3] | 15 | 17 | 58.7 |
| [15,6,5] | 15 | 17 | 88.0 |
| [15,6,5] 2 anc | 15 | 19 | 104.8 |
