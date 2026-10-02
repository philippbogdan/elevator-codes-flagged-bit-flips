
## Frontier at p_Z = 1e-3, eta = 1e6 (phase flips: paper-pZL)

All simulated codes ([15,9,3], [15,6,5] with 1 and 2 ancillas, Hamming [15,11,3], [31,26,3], [63,57,3], extended Hamming [16,11,4]) and flag settings; decoder: exclusive-window MLE (ML at the leading order, results/decoder_optimality*.json; BP+OSD is worse on the same configurations).  p_L = p_XL + p_ZL.

### (a) Requirements frontier for p_L <= 1e-12

Non-dominated in overhead, flag efficiency f, flag classes needed, timing window allowed and false-flag rate tolerated, among the settings that reach 1e-12 with the 95% upper bound of p_XL (conservative).

| overhead | code | d_Z | p_L | p_XL 95% upper | f | flags on | window (ticks) | false flags tolerated |
|---|---|---|---|---|---|---|---|---|
| 30.9 | Hamming [127,120,3] | 15 | 7.12e-13 | 2.4e-14 | 1.0 | all | exact | 0 |
| 32.6 | Hamming [63,57,3] | 15 | 9.09e-13 | 1.7e-13 | 0.995 | all | exact | 0 |
| 35.7 | Hamming [31,26,3] | 15 | 9.04e-13 | 9.1e-14 | 0.99 | all | exact | 0 |
| 40.6 | Hamming [31,26,3] | 17 (transferred) | 6.10e-13 | 6.3e-13 | 0.95 | all | exact | 0 |
| 40.6 | Hamming [31,26,3] | 17 (transferred) | 2.35e-13 | 3.9e-13 | 0.99 | all | 64 | 0 |
| 48.0 | Hamming [15,11,3] | 17 (transferred) | 6.96e-13 | 7.4e-13 | 0.8 | all | exact | 0 |
| 48.0 | Hamming [15,11,3] | 17 (transferred) | 4.99e-13 | 5.8e-13 | 0.99 | all | 4096 | 0 |
| 51.0 | ext. Hamming [16,11,4] | 17 (transferred) | 8.04e-13 | 8.5e-13 | 0.9 | idle | 4 | 0 |
| 51.0 | ext. Hamming [16,11,4] | 17 (transferred) | 7.14e-13 | 7.8e-13 | 0.99 | idle | 64 | 0 |
| 58.7 | [15,9,3] | 17 (transferred) | 5.19e-13 | 5.1e-13 | 0.8 | idle+gate | exact | 0 |
| 58.7 | [15,9,3] | 17 (transferred) | 5.71e-13 | 6.8e-13 | 0.8 | all | 64 | 0 |
| 58.7 | [15,9,3] | 17 (transferred) | 5.08e-13 | 5.8e-13 | 0.9 | all | 4096 | 0 |
| 88.0 | [15,6,5] | 17 | 7.52e-14 | 1.1e-14 | 0.0 | none | any (no flags) | 0 |

### (b) Lowest p_L per code and d_Z, and what it takes

For every simulated (or transferred) code and d_Z: the lowest p_L of any flag setting, the phase-flip part of it (flags cannot lower it), the flag-free p_L, and the least demanding setting within a factor 1.5 of the lowest (smallest f, then fewest flag classes, then coarsest window).

| overhead | code | d_Z | lowest p_L | of which p_ZL | p_L without flags | f needed | flags on | coarsest window |
|---|---|---|---|---|---|---|---|---|
| 28.1 | Hamming [63,57,3] | 13 | 1.78e-11 | 1.78e-11 | 5.63e-11 | 0.9 | all | exact |
| 30.8 | Hamming [31,26,3] | 13 | 1.95e-11 | 1.95e-11 | 2.91e-11 | 0.0 | none | any (no flags) |
| 30.9 | Hamming [127,120,3] | 15 | 7.12e-13 | 7.12e-13 | - | 1.0 | all | exact |
| 32.6 | Hamming [63,57,3] | 15 | 7.49e-13 | 7.49e-13 | 5.40e-11 | 0.99 | all | exact |
| 35.7 | Hamming [31,26,3] | 15 | 8.21e-13 | 8.21e-13 | 1.35e-11 | 0.98 | all | exact |
| 36.4 | Hamming [15,11,3] | 13 | 2.30e-11 | 2.30e-11 | 2.53e-11 | 0.0 | none | any (no flags) |
| 37.1 | Hamming [63,57,3] | 17 | 3.19e-14 | 3.15e-14 | 6.81e-11 | 1.0 | all | exact |
| 38.6 | ext. Hamming [16,11,4] | 13 | 2.45e-11 | 2.45e-11 | 2.67e-11 | 0.0 | none | any (no flags) |
| 40.6 | Hamming [31,26,3] | 17 | 3.46e-14 | 3.46e-14 | 1.63e-11 | 0.999 | all | exact |
| 41.5 | Hamming [63,57,3] | 19 | 1.81e-15 | 1.33e-15 | 8.49e-11 | 1.0 | all | exact |
| 42.2 | Hamming [15,11,3] | 15 | 9.70e-13 | 9.70e-13 | 3.93e-12 | 0.8 | all | exact |
| 44.4 | [15,9,3] | 13 | 2.82e-11 | 2.82e-11 | 3.05e-11 | 0.0 | none | any (no flags) |
| 44.8 | ext. Hamming [16,11,4] | 15 | 1.03e-12 | 1.03e-12 | 3.99e-12 | 0.8 | all | exact |
| 45.5 | Hamming [31,26,3] | 19 | 1.52e-15 | 1.46e-15 | 2.02e-11 | 1.0 | all | exact |
| 46.0 | Hamming [63,57,3] | 21 | 7.08e-16 | 5.59e-17 | 1.03e-10 | 1.0 | all | exact |
| 48.0 | Hamming [15,11,3] | 17 | 4.09e-14 | 4.09e-14 | 4.05e-12 | 0.995 | all | exact |
| 50.5 | Hamming [31,26,3] | 21 | 1.50e-16 | 6.13e-17 | 2.47e-11 | 1.0 | all | exact |
| 50.5 | Hamming [63,57,3] | 23 | 8.60e-16 | 2.35e-18 | 1.24e-10 | 1.0 | all | exact |
| 51.0 | ext. Hamming [16,11,4] | 17 | 4.34e-14 | 4.34e-14 | 3.83e-12 | 0.95 | all | exact |
| 51.6 | [15,9,3] | 15 | 1.19e-12 | 1.19e-12 | 4.25e-12 | 0.8 | idle+gate | 64 |
| 53.8 | Hamming [15,11,3] | 19 | 1.73e-15 | 1.72e-15 | 5.54e-12 | 1.0 | all | exact |
| 55.0 | Hamming [63,57,3] | 25 | 1.10e-15 | 9.92e-20 | 1.46e-10 | 1.0 | all | exact |
| 55.4 | Hamming [31,26,3] | 23 | 6.38e-17 | 2.58e-18 | 2.16e-11 | 1.0 | all | exact |
| 57.2 | ext. Hamming [16,11,4] | 19 | 1.83e-15 | 1.83e-15 | 5.23e-12 | 0.99 | all | 64 |
| 58.7 | [15,9,3] | 17 | 4.99e-14 | 4.99e-14 | 4.15e-12 | 0.98 | idle+gate | exact |
| 59.6 | Hamming [15,11,3] | 21 | 8.93e-17 | 7.25e-17 | 7.42e-12 | 1.0 | all | exact |
| 60.3 | Hamming [31,26,3] | 25 | 1.49e-16 | 1.09e-19 | 3.48e-11 | 1.0 | all | exact |
| 63.4 | ext. Hamming [16,11,4] | 21 | 7.70e-17 | 7.70e-17 | 7.00e-12 | 0.999 | all | exact |
| 65.5 | Hamming [15,11,3] | 23 | 2.95e-17 | 3.05e-18 | 9.67e-12 | 1.0 | all | exact |
| 65.8 | [15,9,3] | 19 | 2.10e-15 | 2.10e-15 | 5.55e-12 | 1.0 | all | 16 |
| 66.7 | [15,6,5] | 13 | 4.23e-11 | 4.23e-11 | 4.23e-11 | 0.0 | none | any (no flags) |
| 69.5 | ext. Hamming [16,11,4] | 23 | 3.24e-18 | 3.24e-18 | 9.13e-12 | 1.0 | all | exact |
| 70.8 | [15,6,5] 2 anc | 13 | 4.49e-11 | 4.49e-11 | 4.49e-11 | 0.0 | none | any (no flags) |
| 71.3 | Hamming [15,11,3] | 25 | 4.00e-17 | 1.28e-19 | 1.23e-11 | 1.0 | all | exact |
| 72.9 | [15,9,3] | 21 | 8.86e-17 | 8.86e-17 | 7.42e-12 | 1.0 | all | 16 |
| 75.7 | ext. Hamming [16,11,4] | 25 | 1.39e-19 | 1.36e-19 | 1.17e-11 | 1.0 | all | exact |
| 77.3 | [15,6,5] | 15 | 1.78e-12 | 1.78e-12 | 1.78e-12 | 0.0 | none | any (no flags) |
| 80.0 | [15,9,3] | 23 | 3.73e-18 | 3.73e-18 | 9.67e-12 | 1.0 | all | 16 |
| 82.2 | [15,6,5] 2 anc | 15 | 1.89e-12 | 1.89e-12 | 1.89e-12 | 0.0 | none | any (no flags) |
| 87.1 | [15,9,3] | 25 | 1.57e-19 | 1.57e-19 | 1.23e-11 | 1.0 | all | 16 |
| 88.0 | [15,6,5] | 17 | 7.49e-14 | 7.49e-14 | 7.52e-14 | 0.0 | none | any (no flags) |
| 93.5 | [15,6,5] 2 anc | 17 | 7.96e-14 | 7.96e-14 | 7.97e-14 | 0.0 | none | any (no flags) |
| 98.7 | [15,6,5] | 19 | 3.15e-15 | 3.15e-15 | 3.61e-15 | 0.0 | none | any (no flags) |
| 104.8 | [15,6,5] 2 anc | 19 | 3.35e-15 | 3.35e-15 | 3.65e-15 | 0.0 | none | any (no flags) |
| 109.3 | [15,6,5] | 21 | 1.33e-16 | 1.33e-16 | 8.75e-16 | 0.8 | idle+gate | 64 |
| 116.2 | [15,6,5] 2 anc | 21 | 1.41e-16 | 1.41e-16 | 6.29e-16 | 0.5 | idle+gate | 64 |
| 120.0 | [15,6,5] | 23 | 5.59e-18 | 5.59e-18 | 1.16e-15 | 0.9 | all | 1024 |
| 127.5 | [15,6,5] 2 anc | 23 | 5.94e-18 | 5.94e-18 | 7.61e-16 | 0.9 | all | 16 |
| 130.7 | [15,6,5] | 25 | 2.36e-19 | 2.36e-19 | 1.74e-15 | 0.95 | idle+gate | exact |
| 138.8 | [15,6,5] 2 anc | 25 | 2.50e-19 | 2.50e-19 | 1.13e-15 | 0.95 | idle+gate | 4 |
