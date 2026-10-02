
## Literal idle-noise reading: phase flips

Isolated repetition code with the extra idle ticks of the literal reading (2.73 per round on average) against the noop reading, per round:

| p_Z | d_Z | literal | noop (model) | ratio |
|---|---|---|---|---|
| 1.0e-03 | 5 | 1.03e-05 | 2.34e-06 | 4.42 |
| 1.0e-03 | 7 | 3.41e-07 | 5.57e-08 | 6.13 |
| 1.0e-03 | 9 | 1.38e-08 | 1.33e-09 | 10.40 |
| 1.0e-03 | 11 | 5.59e-10 | 3.17e-11 | 17.62 |
| 2.0e-03 | 5 | 7.95e-05 | 2.13e-05 | 3.74 |
| 2.0e-03 | 7 | 6.30e-06 | 9.61e-07 | 6.55 |
| 2.0e-03 | 9 | 3.65e-07 | 4.34e-08 | 8.41 |
| 2.0e-03 | 11 | 3.59e-08 | 1.96e-09 | 18.34 |
| 3.0e-03 | 17 | 8.59e-10 | 1.19e-11 | 71.92 |
| 5.0e-03 | 5 | 1.12e-03 | 2.30e-04 | 4.87 |
| 5.0e-03 | 7 | 2.18e-04 | 3.11e-05 | 7.02 |
| 5.0e-03 | 9 | 3.90e-05 | 4.19e-06 | 9.30 |
| 5.0e-03 | 11 | 8.97e-06 | 5.66e-07 | 15.87 |
| 5.0e-03 | 13 | 2.12e-06 | 7.63e-08 | 27.76 |
| 5.0e-03 | 15 | 3.99e-07 | 1.03e-08 | 38.74 |
| 5.0e-03 | 17 | 9.56e-08 | 1.39e-09 | 68.80 |

Phase-flip floor at p_Z = 1e-3, 1e-12 under the literal reading (two-component model with the literal repetition code; approximation):

| code | d_Z noop | d_Z literal | overhead literal |
|---|---|---|---|
| [15,9,3] | 15 | 17 | 58.7 |
| [15,6,5] | 15 | 17 | 88.0 |
| [15,6,5] 2 anc | 15 | 17 | 93.5 |
