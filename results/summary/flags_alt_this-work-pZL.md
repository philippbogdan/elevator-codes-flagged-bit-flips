
## Flagged bit flips, p_X = 1e-09 (reading: idle=edge,cnot); phase flips from this-work-pZL

### Minimum qubit overhead at p_Z = 1e-3, eta = 1e6, target 1e-12 per round per logical qubit

Central estimate (conservative: bit-flip rate at its 95% upper bound) and the chosen code/d_Z.

Per code: minimum overhead ('n.r.' = simulated but not reaching the target, '-' = not simulated), then p_XL at d_Z = 15 per round per logical qubit [95% CI] (sampled logical failures behind it); these p_X = 1e-9 values lie below direct-sampling reach and come from the stratified estimator (model: Poisson strata, held-out check in validation.md).

| flags on | window (ticks) | f | false flags /qubit/tick | best overhead (central) | code, d_Z | p_XL | best (conservative) | Hamming [15,11,3] | Hamming [31,26,3] | ext. Hamming [16,11,4] | Hamming [63,57,3] | Hamming [15,11,3] p_XL(d=15) | Hamming [31,26,3] p_XL(d=15) | ext. Hamming [16,11,4] p_XL(d=15) | Hamming [63,57,3] p_XL(d=15) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | exact | 0.0 | 0 | not reached | - | - | not reached | - | n.r. | - | - | - | 1.27e-11 [1.2e-11, 1.3e-11] (1811) | - | - |
| all | exact | 0.8 | 0 | 42.2 | Hamming [15,11,3], 15 | 4.83e-13 | 42.2 | 42.2 (d=15) | - | - | - | 4.83e-13 [4.3e-13, 5.5e-13] (928) | - | - | - |
| all | exact | 0.9 | 0 | 42.2 | Hamming [15,11,3], 15 | 2.25e-13 | 42.2 | 42.2 (d=15) | - | - | - | 2.25e-13 [2.0e-13, 2.5e-13] (1208) | - | - | - |
| all | exact | 0.95 | 0 | 44.8 | ext. Hamming [16,11,4], 15 | 6.69e-15 | 44.8 | - | - | 44.8 (d=15) | - | - | - | 6.69e-15 [5.4e-15, 4.1e-14] (325) | - |
| all | exact | 0.99 | 0 | 44.8 | ext. Hamming [16,11,4], 15 | 2.70e-16 | 44.8 | - | - | 44.8 (d=15) | - | - | - | 2.70e-16 [2.2e-16, 7.2e-15] (361) | - |
| all | exact | 1.0 | 0 | 35.7 | Hamming [31,26,3], 15 | 3.21e-17 | 35.7 | - | 35.7 (d=15) | - | - | - | 3.21e-17 [3.0e-17, 3.5e-17] (19332) | - | - |
| all | 16 | 0.99 | 0 | 35.7 | Hamming [31,26,3], 15 | 8.67e-14 | 35.7 | - | 35.7 (d=15) | - | - | - | 8.67e-14 [7.2e-14, 1.9e-13] (680) | - | - |
| all | 64 | 1.0 | 0 | 42.2 | Hamming [15,11,3], 15 | 6.50e-14 | 42.2 | 42.2 (d=15) | - | - | - | 6.50e-14 [4.0e-14, 1.1e-13] (19) | - | - | - |
| all | 1024 | 0.99 | 0 | 42.2 | Hamming [15,11,3], 15 | 3.67e-13 | 42.2 | 42.2 (d=15) | - | - | - | 3.67e-13 [2.9e-13, 4.6e-13] (740) | - | - | - |
| all | 4096 | 0.99 | 0 | 42.2 | Hamming [15,11,3], 15 | 3.38e-13 | 42.2 | 42.2 (d=15) | - | - | - | 3.38e-13 [2.7e-13, 4.3e-13] (832) | - | - | - |
| idle | exact | 0.9 | 0 | not reached | - | - | not reached | n.r. | - | - | - | 1.23e-12 [1.1e-12, 1.4e-12] (1154) | - | - | - |
| idle | exact | 0.99 | 0 | not reached | - | - | not reached | n.r. | - | - | - | 9.73e-13 [8.7e-13, 1.1e-12] (1118) | - | - | - |
| idle | exact | 1.0 | 0 | not reached | - | - | not reached | n.r. | - | - | - | 9.13e-13 [8.2e-13, 1.0e-12] (1111) | - | - | - |
