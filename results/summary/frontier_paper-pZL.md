
## Frontier at p_Z = 1e-3, eta = 1e6 (phase flips: paper-pZL)

All simulated codes ([15,9,3], [15,6,5] with 1 and 2 ancillas, Hamming [15,11,3], [31,26,3], [63,57,3], extended Hamming [16,11,4]) and flag settings; decoder: exclusive-window MLE (ML at the leading order, results/decoder_optimality*.json; BP+OSD is worse on the same configurations).  p_L = p_XL + p_ZL.

### (a) Requirements frontier for p_L <= 1e-12

Non-dominated in overhead, flag efficiency f, flag classes needed, timing window allowed and false-flag rate tolerated, among the settings that reach 1e-12 with the 95% upper bound of p_XL (conservative).

| overhead | code | d_Z | p_L | p_XL 95% upper | f | flags on | window (ticks) | false flags tolerated |
|---|---|---|---|---|---|---|---|---|
| 35.7 | Hamming [31,26,3] | 15 | 8.21e-13 | 3.5e-17 | 1.0 | all | exact | 0 |
| 40.6 | Hamming [31,26,3] | 17 | 1.46e-13 | 2.5e-13 | 0.99 | all | 16 | 0 | (transferred)
| 48.0 | Hamming [15,11,3] | 17 | 6.96e-13 | 7.4e-13 | 0.8 | all | exact | 0 | (transferred)
| 48.0 | Hamming [15,11,3] | 17 | 4.99e-13 | 5.8e-13 | 0.99 | all | 4096 | 0 | (transferred)
| 58.7 | [15,9,3] | 17 | 5.19e-13 | 5.1e-13 | 0.8 | idle+gate | exact | 0 | (transferred)
| 58.7 | [15,9,3] | 17 | 5.71e-13 | 6.8e-13 | 0.8 | all | 64 | 0 | (transferred)
| 58.7 | [15,9,3] | 17 | 5.08e-13 | 5.8e-13 | 0.9 | all | 4096 | 0 | (transferred)
| 88.0 | [15,6,5] | 17 | 7.55e-14 | 2.6e-14 | 0.0 | none | any (no flags) | 0 | (transferred)

### (b) Lowest p_L per code and d_Z, and what it takes

For every simulated (or transferred) code and d_Z: the lowest p_L of any flag setting, the phase-flip part of it (flags cannot lower it), the flag-free p_L, and the least demanding setting within a factor 1.5 of the lowest (smallest f, then fewest flag classes, then coarsest window).

| overhead | code | d_Z | lowest p_L | of which p_ZL | p_L without flags | f needed | flags on | coarsest window |
|---|---|---|---|---|---|---|---|---|
| 30.8 | Hamming [31,26,3] | 13 | 1.95e-11 | 1.95e-11 | 2.91e-11 | 0.0 | none | any (no flags) |
| 35.7 | Hamming [31,26,3] | 15 | 8.21e-13 | 8.21e-13 | 1.35e-11 | 0.99 | all | 16 |
| 36.4 | Hamming [15,11,3] | 13 | 2.31e-11 | 2.30e-11 | - | 0.8 | all | exact |
| 38.6 | ext. Hamming [16,11,4] | 13 | 2.45e-11 | 2.45e-11 | - | 0.95 | all | exact |
| 40.6 | Hamming [31,26,3] | 17 | 3.46e-14 | 3.46e-14 | 1.63e-11 | 1.0 | all | exact |
| 42.2 | Hamming [15,11,3] | 15 | 1.04e-12 | 9.70e-13 | - | 0.8 | all | exact |
| 44.4 | [15,9,3] | 13 | 2.82e-11 | 2.82e-11 | 3.05e-11 | 0.0 | none | any (no flags) |
| 44.8 | ext. Hamming [16,11,4] | 15 | 1.03e-12 | 1.03e-12 | - | 0.95 | all | exact |
| 45.5 | Hamming [31,26,3] | 19 | 1.52e-15 | 1.46e-15 | 2.02e-11 | 1.0 | all | exact |
| 48.0 | Hamming [15,11,3] | 17 | 1.29e-13 | 4.09e-14 | - | 1.0 | all | 64 |
| 50.5 | Hamming [31,26,3] | 21 | 1.50e-16 | 6.13e-17 | 2.47e-11 | 1.0 | all | exact |
| 51.0 | ext. Hamming [16,11,4] | 17 | 4.38e-14 | 4.34e-14 | - | 0.95 | all | exact |
| 51.6 | [15,9,3] | 15 | 1.19e-12 | 1.19e-12 | 4.25e-12 | 0.8 | idle+gate | 64 |
| 53.8 | Hamming [15,11,3] | 19 | 1.24e-13 | 1.72e-15 | - | 1.0 | all | 64 |
| 55.4 | Hamming [31,26,3] | 23 | 6.38e-17 | 2.58e-18 | 2.16e-11 | 1.0 | all | exact |
| 57.2 | ext. Hamming [16,11,4] | 19 | 2.31e-15 | 1.83e-15 | - | 0.99 | all | exact |
| 58.7 | [15,9,3] | 17 | 4.99e-14 | 4.99e-14 | 4.15e-12 | 0.98 | idle+gate | exact |
| 59.6 | Hamming [15,11,3] | 21 | 1.64e-13 | 7.25e-17 | - | 1.0 | all | 64 |
| 60.3 | Hamming [31,26,3] | 25 | 1.49e-16 | 1.09e-19 | 3.48e-11 | 1.0 | all | exact |
| 63.4 | ext. Hamming [16,11,4] | 21 | 7.20e-16 | 7.70e-17 | - | 0.99 | all | exact |
| 65.5 | Hamming [15,11,3] | 23 | 2.15e-13 | 3.05e-18 | - | 1.0 | all | 64 |
| 65.8 | [15,9,3] | 19 | 2.10e-15 | 2.10e-15 | 5.66e-12 | 1.0 | all | 16 |
| 66.7 | [15,6,5] | 13 | 4.23e-11 | 4.23e-11 | 4.23e-11 | 0.0 | none | any (no flags) |
| 69.5 | ext. Hamming [16,11,4] | 23 | 8.45e-16 | 3.24e-18 | - | 0.99 | all | exact |
| 70.8 | [15,6,5] 2 anc | 13 | 4.49e-11 | 4.49e-11 | - | 0.5 | idle | 4096 |
| 71.3 | Hamming [15,11,3] | 25 | 2.75e-13 | 1.28e-19 | - | 1.0 | all | 64 |
| 72.9 | [15,9,3] | 21 | 8.86e-17 | 8.86e-17 | 7.56e-12 | 1.0 | all | 16 |
| 75.7 | ext. Hamming [16,11,4] | 25 | 1.08e-15 | 1.36e-19 | - | 0.99 | all | exact |
| 77.3 | [15,6,5] | 15 | 1.78e-12 | 1.78e-12 | 1.78e-12 | 0.0 | none | any (no flags) |
| 80.0 | [15,9,3] | 23 | 3.73e-18 | 3.73e-18 | 9.86e-12 | 1.0 | all | 16 |
| 82.2 | [15,6,5] 2 anc | 15 | 1.89e-12 | 1.89e-12 | - | 0.5 | idle | 4096 |
| 87.1 | [15,9,3] | 25 | 1.57e-19 | 1.57e-19 | 1.26e-11 | 1.0 | all | 16 |
| 88.0 | [15,6,5] | 17 | 7.49e-14 | 7.49e-14 | 7.55e-14 | 0.0 | none | any (no flags) |
| 93.5 | [15,6,5] 2 anc | 17 | 7.96e-14 | 7.96e-14 | - | 0.5 | idle | 4096 |
| 98.7 | [15,6,5] | 19 | 3.15e-15 | 3.15e-15 | 4.14e-15 | 0.0 | none | any (no flags) |
| 104.8 | [15,6,5] 2 anc | 19 | 3.35e-15 | 3.35e-15 | - | 0.5 | idle | 4096 |
| 109.3 | [15,6,5] | 21 | 1.33e-16 | 1.33e-16 | 1.73e-15 | 0.8 | idle+gate | exact |
| 116.2 | [15,6,5] 2 anc | 21 | 1.41e-16 | 1.41e-16 | - | 0.5 | idle+gate | exact |
| 120.0 | [15,6,5] | 23 | 5.59e-18 | 5.59e-18 | 2.49e-15 | 0.9 | all | 1024 |
| 127.5 | [15,6,5] 2 anc | 23 | 5.94e-18 | 5.94e-18 | - | 0.9 | all | 16 |
| 130.7 | [15,6,5] | 25 | 2.36e-19 | 2.36e-19 | 3.74e-15 | 0.95 | idle+gate | exact |
| 138.8 | [15,6,5] 2 anc | 25 | 2.50e-19 | 2.50e-19 | - | 0.95 | idle+gate | exact |
