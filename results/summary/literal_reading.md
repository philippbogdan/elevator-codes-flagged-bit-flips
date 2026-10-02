
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
| 2.0e-03 | 13 | 3.64e-09 | 8.85e-11 | 41.16 |
| 2.0e-03 | 15 | 1.60e-10 | 3.99e-12 | 40.12 |
| 3.0e-03 | 5 | 2.50e-04 | 4.72e-05 | 5.29 |
| 3.0e-03 | 7 | 2.95e-05 | 3.75e-06 | 7.86 |
| 3.0e-03 | 17 | 8.31e-10 | 1.19e-11 | 69.58 |
| 5.0e-03 | 5 | 1.12e-03 | 2.30e-04 | 4.87 |
| 5.0e-03 | 7 | 2.18e-04 | 3.11e-05 | 7.02 |
| 5.0e-03 | 9 | 3.90e-05 | 4.19e-06 | 9.30 |
| 5.0e-03 | 11 | 8.97e-06 | 5.66e-07 | 15.87 |
| 5.0e-03 | 13 | 2.12e-06 | 7.63e-08 | 27.76 |
| 5.0e-03 | 15 | 3.99e-07 | 1.03e-08 | 38.74 |
| 5.0e-03 | 17 | 9.56e-08 | 1.39e-09 | 68.80 |
| 5.0e-03 | 19 | 1.74e-08 | 1.87e-10 | 92.80 |

Phase-flip floor at p_Z = 1e-3, 1e-12 under the literal reading (two-component model with the literal repetition code; approximation):

| code | d_Z noop | d_Z literal | overhead literal |
|---|---|---|---|
| [15,9,3] | 15 | 17 | 58.7 |
| [15,6,5] | 15 | 17 | 88.0 |
| [15,6,5] 2 anc | 15 | 19 | 104.8 |

Overhead at p_Z = 1e-3, eta = 1e6, 1e-12 under the literal reading (runs at d_Z = 17, transferred to other d_Z with the literal reading's fault sums; p_XL shown at d_Z = 17):

| flags | [15,9,3] p_XL | [15,6,5] p_XL | minimum overhead |
|---|---|---|---|
| none|w0|f0.0 | 1.12e-11 | 1.67e-15 | 88.0 ([15,6,5], d_Z = 17) |
| idle|w0|f0.99 | 1.62e-12 | 9.58e-17 | 88.0 ([15,6,5], d_Z = 17) |
| all|w0|f0.9 | 2.29e-12 | 2.56e-17 | 88.0 ([15,6,5], d_Z = 17) |
| all|w0|f0.99 | 5.97e-14 | 2.94e-21 | 58.7 ([15,9,3], d_Z = 17) |
| all|w1024|f0.99 | 3.92e-13 | 1.67e-15 | 58.7 ([15,9,3], d_Z = 17) |
