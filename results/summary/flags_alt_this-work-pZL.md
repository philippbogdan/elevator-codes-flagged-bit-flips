
## Flagged bit flips, p_X = 1e-09 (reading: idle=edge,cnot); phase flips from this-work-pZL

### Minimum qubit overhead at p_Z = 1e-3, eta = 1e6, target 1e-12 per round per logical qubit

Central estimate (conservative: bit-flip rate at its 95% upper bound) and the chosen code/d_Z.

Per code: minimum overhead ('n.r.' = simulated but not reaching the target, '-' = not simulated), then p_XL at d_Z = 15 per round per logical qubit [95% CI] (sampled logical failures behind it); these p_X = 1e-9 values lie below direct-sampling reach and come from the stratified estimator (model: Poisson strata, held-out check in validation.md).

| flags on | window (ticks) | f | false flags /qubit/tick | best overhead (central) | code, d_Z | p_XL | best (conservative) | Hamming [15,11,3] | Hamming [31,26,3] | ext. Hamming [16,11,4] | Hamming [63,57,3] | Hamming [15,11,3] p_XL(d=15) | Hamming [31,26,3] p_XL(d=15) | ext. Hamming [16,11,4] p_XL(d=15) | Hamming [63,57,3] p_XL(d=15) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | exact | 0.0 | 0 | not reached | - | - | not reached | - | n.r. | - | - | - | 1.27e-11 [1.2e-11, 1.3e-11] (1811) | - | - |
| all | exact | 0.5 | 0 | not reached | - | - | not reached | n.r. | n.r. | - | - | 1.28e-12 [1.2e-12, 1.4e-12] (1124) | 5.11e-12 [4.6e-12, 5.7e-12] (1231) | - | - |
| all | exact | 0.8 | 0 | 42.2 | Hamming [15,11,3], 15 | 4.83e-13 | 42.2 | 42.2 (d=15) | - | - | - | 4.83e-13 [4.3e-13, 5.5e-13] (928) | - | - | - |
| all | exact | 0.9 | 0 | 42.2 | Hamming [15,11,3], 15 | 2.25e-13 | 42.2 | 42.2 (d=15) | - | - | - | 2.25e-13 [2.0e-13, 2.5e-13] (1208) | - | - | - |
| all | exact | 0.95 | 0 | 42.2 | Hamming [15,11,3], 15 | 1.07e-13 | 42.2 | 42.2 (d=15) | - | 44.8 (d=15) | - | 1.07e-13 [9.7e-14, 1.2e-13] (1063) | - | 6.69e-15 [5.4e-15, 4.1e-14] (325) | - |
| all | exact | 0.98 | 0 | 42.2 | Hamming [15,11,3], 15 | 6.35e-14 | 42.2 | 42.2 (d=15) | - | 44.8 (d=15) | - | 6.35e-14 [4.4e-14, 9.1e-14] (559) | - | 1.12e-15 [9.0e-16, 1.5e-14] (349) | - |
| all | exact | 0.99 | 0 | 42.2 | Hamming [15,11,3], 15 | 2.69e-14 | 42.2 | 42.2 (d=15) | - | 44.8 (d=15) | - | 2.69e-14 [1.8e-14, 4.0e-14] (557) | - | 2.70e-16 [2.2e-16, 7.2e-15] (361) | - |
| all | exact | 0.995 | 0 | 44.8 | ext. Hamming [16,11,4], 15 | 7.40e-17 | 44.8 | - | - | 44.8 (d=15) | - | - | - | 7.40e-17 [6.0e-17, 3.5e-15] (347) | - |
| all | exact | 0.999 | 0 | 44.8 | ext. Hamming [16,11,4], 15 | 3.18e-18 | 44.8 | - | - | 44.8 (d=15) | - | - | - | 3.18e-18 [2.6e-18, 7.0e-16] (348) | - |
| all | exact | 1.0 | 0 | 35.7 | Hamming [31,26,3], 15 | 3.21e-17 | 35.7 | - | 35.7 (d=15) | 44.8 (d=15) | - | - | 3.21e-17 [3.0e-17, 3.5e-17] (19332) | 1.24e-22 [1.0e-22, 1.5e-22] (5624) | - |
| all | 1 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 9.44e-14 | 35.7 | - | 35.7 (d=15) | 44.8 (d=15) | - | - | 9.44e-14 [7.9e-14, 2.0e-13] (698) | 2.69e-16 [2.2e-16, 7.0e-14] (333) | - |
| all | 16 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 8.67e-14 | 35.7 | - | 35.7 (d=15) | 44.8 (d=15) | - | - | 8.67e-14 [7.2e-14, 1.9e-13] (680) | 2.54e-16 [2.0e-16, 7.0e-14] (330) | - |
| all | 64 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 1.57e-13 | 35.7 | - | 35.7 (d=15) | 44.8 (d=15) | - | - | 1.57e-13 [9.7e-14, 3.0e-13] (670) | 2.85e-16 [2.3e-16, 7.0e-14] (352) | - |
| all | 64 | 1.0 | 0 | 35.7 | Hamming [31,26,3], 15 | 8.33e-14 | 35.7 | 42.2 (d=15) | 35.7 (d=15) | - | - | 6.50e-14 [4.0e-14, 1.1e-13] (19) | 8.33e-14 [3.5e-14, 2.0e-13] (6) | - | - |
| all | 256 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 5.58e-13 | 35.7 | - | 35.7 (d=15) | - | - | - | 5.58e-13 [3.9e-13, 8.1e-13] (700) | - | - |
| all | 1024 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 8.38e-13 | 42.2 | 42.2 (d=15) | 35.7 (d=15) | - | - | 3.67e-13 [2.9e-13, 4.6e-13] (740) | 8.38e-13 [6.2e-13, 1.1e-12] (735) | - | - |
| all | 4096 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 7.17e-13 | 42.2 | 42.2 (d=15) | 35.7 (d=15) | - | - | 3.38e-13 [2.7e-13, 4.3e-13] (832) | 7.17e-13 [5.1e-13, 1.0e-12] (764) | - | - |
| all | 4096 | 1.0 | 0 | 42.2 | Hamming [15,11,3], 15 | 2.80e-13 | 42.2 | 42.2 (d=15) | n.r. | - | - | 2.80e-13 [2.2e-13, 3.5e-13] (79) | 9.81e-13 [7.6e-13, 1.3e-12] (62) | - | - |
| idle | exact | 0.9 | 0 | not reached | - | - | not reached | n.r. | n.r. | - | - | 1.23e-12 [1.1e-12, 1.4e-12] (1154) | 4.79e-12 [4.3e-12, 5.3e-12] (1185) | - | - |
| idle | exact | 0.99 | 0 | not reached | - | - | not reached | n.r. | n.r. | - | - | 9.73e-13 [8.7e-13, 1.1e-12] (1118) | 4.04e-12 [3.6e-12, 4.5e-12] (1193) | - | - |
| idle | exact | 1.0 | 0 | not reached | - | - | not reached | n.r. | n.r. | - | - | 9.13e-13 [8.2e-13, 1.0e-12] (1111) | 4.19e-12 [3.8e-12, 4.6e-12] (1177) | - | - |
