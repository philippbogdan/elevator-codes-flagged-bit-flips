
## Frontier at p_Z = 1e-3, eta = 1e6 (phase flips: this-work-pZL)

All simulated codes ([15,9,3], [15,6,5] with 1 and 2 ancillas, Hamming [15,11,3], [31,26,3], [63,57,3], extended Hamming [16,11,4]) and flag settings; decoder: exclusive-window MLE (ML at the leading order, results/decoder_optimality*.json; BP+OSD is worse on the same configurations).  p_L = p_XL + p_ZL.

### (a) Requirements frontier for p_L <= 1e-12

Non-dominated in overhead, flag efficiency f, flag classes needed, timing window allowed and false-flag rate tolerated, among the settings that reach 1e-12 with the 95% upper bound of p_XL (conservative).

| overhead | code | d_Z | p_L | p_XL 95% upper | f | flags on | window (ticks) | false flags tolerated |
|---|---|---|---|---|---|---|---|---|
| 32.6 | Hamming [63,57,3] | 15 | 4.64e-13 | 8.0e-13 | 0.99 | all | 64 | 0 |
| 35.7 | Hamming [31,26,3] | 15 | 5.03e-13 | 5.0e-13 | 0.95 | all | exact | 0 |
| 35.7 | Hamming [31,26,3] | 15 | 6.13e-13 | 8.1e-13 | 0.99 | all | 256 | 0 |
| 42.2 | Hamming [15,11,3] | 15 | 5.74e-13 | 5.5e-13 | 0.8 | all | exact | 0 |
| 42.2 | Hamming [15,11,3] | 15 | 4.28e-13 | 4.3e-13 | 0.99 | all | 4096 | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 8.33e-13 | 8.2e-13 | 0.5 | all | exact | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 8.51e-13 | 8.7e-13 | 0.8 | idle | 4 | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 7.33e-13 | 7.4e-13 | 0.9 | idle | 64 | 0 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 8.23e-13 | 8.6e-13 | 0.99 | idle | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 7.52e-13 | 8.2e-13 | 0.8 | all | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 6.03e-13 | 5.8e-13 | 0.8 | all | 16 | 1e-08 |
| 51.6 | [15,9,3] | 15 | 1.91e-13 | 1.6e-13 | 0.99 | all | 64 | 1e-08 |
| 51.6 | [15,9,3] | 15 | 1.37e-13 | 1.9e-13 | 0.99 | all | exact | 1e-06 |
| 77.3 | [15,6,5] | 15 | 1.66e-13 | 1.9e-14 | 0.0 | none | any (no flags) | 0 |

### (b) Lowest p_L per code and d_Z, and what it takes

For every simulated (or transferred) code and d_Z: the lowest p_L of any flag setting, the phase-flip part of it (flags cannot lower it), the flag-free p_L, and the least demanding setting within a factor 1.5 of the lowest (smallest f, then fewest flag classes, then coarsest window).

| overhead | code | d_Z | lowest p_L | of which p_ZL | p_L without flags | f needed | flags on | coarsest window |
|---|---|---|---|---|---|---|---|---|
| 28.1 | Hamming [63,57,3] | 13 | 1.45e-12 | 1.45e-12 | 3.99e-11 | 0.99 | all | 64 |
| 30.8 | Hamming [31,26,3] | 13 | 1.78e-12 | 1.78e-12 | 1.13e-11 | 0.9 | all | exact |
| 32.6 | Hamming [63,57,3] | 15 | 4.04e-14 | 4.01e-14 | 5.32e-11 | 1.0 | all | exact |
| 35.7 | Hamming [31,26,3] | 15 | 5.49e-14 | 5.48e-14 | 1.27e-11 | 0.999 | all | exact |
| 36.4 | Hamming [15,11,3] | 13 | 2.57e-12 | 2.57e-12 | 4.80e-12 | 0.5 | all | exact |
| 37.1 | Hamming [63,57,3] | 17 | 1.60e-15 | 1.25e-15 | 6.81e-11 | 1.0 | all | exact |
| 38.6 | ext. Hamming [16,11,4] | 13 | 2.67e-12 | 2.67e-12 | 4.90e-12 | 0.5 | all | exact |
| 40.6 | Hamming [31,26,3] | 17 | 2.00e-15 | 1.95e-15 | 1.62e-11 | 1.0 | all | exact |
| 41.5 | Hamming [63,57,3] | 19 | 5.28e-16 | 4.53e-17 | 8.49e-11 | 1.0 | all | exact |
| 42.2 | Hamming [15,11,3] | 15 | 9.04e-14 | 9.04e-14 | 3.05e-12 | 0.99 | all | 16 |
| 44.4 | [15,9,3] | 13 | 3.14e-12 | 3.14e-12 | 5.45e-12 | 0.5 | idle | 4096 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 9.29e-14 | 9.29e-14 | 3.05e-12 | 0.9 | all | exact |
| 45.5 | Hamming [31,26,3] | 19 | 1.46e-16 | 8.04e-17 | 2.02e-11 | 1.0 | all | exact |
| 46.0 | Hamming [63,57,3] | 21 | 6.54e-16 | 1.89e-18 | 1.03e-10 | 1.0 | all | exact |
| 48.0 | Hamming [15,11,3] | 17 | 3.53e-15 | 3.52e-15 | 4.02e-12 | 1.0 | all | exact |
| 50.5 | Hamming [31,26,3] | 21 | 9.19e-17 | 3.69e-18 | 2.47e-11 | 1.0 | all | exact |
| 50.5 | Hamming [63,57,3] | 23 | 8.57e-16 | 8.72e-20 | 1.24e-10 | 1.0 | all | exact |
| 51.0 | ext. Hamming [16,11,4] | 17 | 3.74e-15 | 3.74e-15 | 3.79e-12 | 0.98 | all | exact |
| 51.6 | [15,9,3] | 15 | 1.11e-13 | 1.11e-13 | 3.17e-12 | 0.98 | idle+gate | 4 |
| 53.8 | Hamming [15,11,3] | 19 | 1.55e-16 | 1.45e-16 | 5.54e-12 | 1.0 | all | exact |
| 55.0 | Hamming [63,57,3] | 25 | 1.10e-15 | 4.29e-21 | 1.46e-10 | 1.0 | all | exact |
| 55.4 | Hamming [31,26,3] | 23 | 6.14e-17 | 1.80e-19 | 2.16e-11 | 1.0 | all | exact |
| 57.2 | ext. Hamming [16,11,4] | 19 | 1.54e-16 | 1.54e-16 | 5.23e-12 | 0.999 | all | exact |
| 58.7 | [15,9,3] | 17 | 4.30e-15 | 4.30e-15 | 4.10e-12 | 0.999 | all | exact |
| 59.6 | Hamming [15,11,3] | 21 | 2.32e-17 | 6.35e-18 | 7.42e-12 | 1.0 | all | exact |
| 60.3 | Hamming [31,26,3] | 25 | 1.49e-16 | 9.14e-21 | 3.48e-11 | 1.0 | all | exact |
| 63.4 | ext. Hamming [16,11,4] | 21 | 6.75e-18 | 6.75e-18 | 7.00e-12 | 1.0 | all | exact |
| 65.5 | Hamming [15,11,3] | 23 | 2.67e-17 | 2.91e-19 | 9.67e-12 | 1.0 | all | exact |
| 65.8 | [15,9,3] | 19 | 1.77e-16 | 1.77e-16 | 5.55e-12 | 1.0 | all | 16 |
| 66.7 | [15,6,5] | 13 | 4.70e-12 | 4.70e-12 | 4.70e-12 | 0.0 | none | any (no flags) |
| 69.5 | ext. Hamming [16,11,4] | 23 | 3.11e-19 | 3.10e-19 | 9.13e-12 | 1.0 | all | exact |
| 70.8 | [15,6,5] 2 anc | 13 | 6.59e-12 | 6.59e-12 | 6.59e-12 | 0.0 | none | any (no flags) |
| 71.3 | Hamming [15,11,3] | 25 | 3.99e-17 | 1.37e-20 | 1.23e-11 | 1.0 | all | exact |
| 72.9 | [15,9,3] | 21 | 7.76e-18 | 7.76e-18 | 7.42e-12 | 1.0 | all | 16 |
| 75.7 | ext. Hamming [16,11,4] | 25 | 1.75e-20 | 1.46e-20 | 1.17e-11 | 1.0 | all | exact |
| 77.3 | [15,6,5] | 15 | 1.66e-13 | 1.66e-13 | 1.66e-13 | 0.0 | none | any (no flags) |
| 80.0 | [15,9,3] | 23 | 3.56e-19 | 3.56e-19 | 9.67e-12 | 1.0 | all | 16 |
| 82.2 | [15,6,5] 2 anc | 15 | 2.64e-13 | 2.64e-13 | 2.64e-13 | 0.0 | none | any (no flags) |
| 87.1 | [15,9,3] | 25 | 1.68e-20 | 1.68e-20 | 1.23e-11 | 1.0 | all | 16 |
| 88.0 | [15,6,5] | 17 | 6.45e-15 | 6.45e-15 | 6.76e-15 | 0.0 | none | any (no flags) |
| 93.5 | [15,6,5] 2 anc | 17 | 1.13e-14 | 1.13e-14 | 1.14e-14 | 0.0 | none | any (no flags) |
| 98.7 | [15,6,5] | 19 | 2.65e-16 | 2.65e-16 | 7.21e-16 | 0.5 | idle+gate | exact |
| 104.8 | [15,6,5] 2 anc | 19 | 4.92e-16 | 4.92e-16 | 7.95e-16 | 0.5 | idle | 4096 |
| 109.3 | [15,6,5] | 21 | 1.16e-17 | 1.16e-17 | 7.53e-16 | 0.9 | all | 1024 |
| 116.2 | [15,6,5] 2 anc | 21 | 2.24e-17 | 2.24e-17 | 5.11e-16 | 0.8 | idle+gate | 4096 |
| 120.0 | [15,6,5] | 23 | 5.34e-19 | 5.34e-19 | 1.16e-15 | 0.95 | idle+gate | exact |
| 127.5 | [15,6,5] 2 anc | 23 | 1.05e-18 | 1.05e-18 | 7.56e-16 | 0.9 | all | 16 |
| 130.7 | [15,6,5] | 25 | 2.52e-20 | 2.52e-20 | 1.74e-15 | 0.99 | all | 1024 |
| 138.8 | [15,6,5] 2 anc | 25 | 4.98e-20 | 4.98e-20 | 1.13e-15 | 0.98 | idle+gate | 64 |
