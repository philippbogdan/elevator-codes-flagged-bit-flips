
## Flagged bit flips, p_X = 1e-09 (reading: idle=edge,cnot); phase flips from paper-pZL

### Minimum qubit overhead at p_Z = 1e-3, eta = 1e6, target 1e-12 per round per logical qubit

Central estimate (conservative: bit-flip rate at its 95% upper bound) and the chosen code/d_Z.

| flags on | window (ticks) | f | false flags /qubit/tick | overhead (central) | code, d_Z | p_XL | overhead (conservative) |
|---|---|---|---|---|---|---|---|
| none | exact | 0.0 | 0 | not reached | - | - | not reached |
| all | 1 | 0.99 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 3.26e-22 | 104.8 |
| all | 1 | 1.0 | 0 | 58.7 | [15,9,3], 17 | 0.00e+00 | 58.7 |
| all | 4 | 0.9 | 0 | 65.8 | [15,9,3], 19 | 3.21e-13 | 65.8 |
| all | 4 | 0.99 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.79e-20 | 104.8 |
| all | 4 | 1.0 | 0 | 58.7 | [15,9,3], 17 | 0.00e+00 | 58.7 |
| all | 16 | 0.9 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.78e-19 | 104.8 |
| all | 16 | 0.99 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.78e-20 | 104.8 |
| all | 16 | 1.0 | 0 | 58.7 | [15,9,3], 17 | 0.00e+00 | 58.7 |
| all | 64 | 0.9 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.83e-18 | 104.8 |
| all | 64 | 0.99 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 7.07e-20 | 104.8 |
| all | 64 | 1.0 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 0.00e+00 | 104.8 |
| all | 256 | 0.9 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 3.48e-18 | 104.8 |
| all | 256 | 0.99 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.79e-20 | 104.8 |
| all | 256 | 1.0 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 0.00e+00 | 104.8 |
| all | 1024 | 0.9 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.78e-18 | 104.8 |
| all | 1024 | 0.99 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 3.90e-20 | 104.8 |
| all | 1024 | 1.0 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.83e-26 | 104.8 |
| all | 4096 | 0.9 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 1.90e-18 | 104.8 |
| all | 4096 | 0.99 | 0 | 58.7 | [15,9,3], 17 | 2.32e-13 | 58.7 |
| all | 4096 | 1.0 | 0 | 104.8 | [15,6,5] 2 anc, 19 | 2.79e-23 | 104.8 |
| idle | exact | 0.5 | 0 | not reached | - | - | not reached |
| idle | exact | 0.8 | 0 | not reached | - | - | not reached |
| idle | exact | 0.9 | 0 | not reached | - | - | not reached |
| idle | exact | 0.99 | 0 | not reached | - | - | not reached |
