
## Frontier at p_Z = 1e-3, eta = 1e6 (phase flips: this-work-pZL)

All simulated codes ([15,9,3], [15,6,5] with 1 and 2 ancillas, Hamming [15,11,3], [31,26,3], [63,57,3], extended Hamming [16,11,4]) and flag settings; decoder: exclusive-window MLE (ML at the leading order, results/decoder_optimality*.json; BP+OSD is worse on the same configurations).  p_L = p_XL + p_ZL.

### (a) Requirements frontier for p_L <= 1e-12

Non-dominated in overhead, flag efficiency f, flag classes needed, timing window allowed and false-flag rate tolerated, among the settings that reach 1e-12 with the 95% upper bound of p_XL (conservative).

| overhead | code | d_Z | p_L | p_XL 95% upper | f | flags on | window (ticks) | false flags tolerated |
|---|---|---|---|---|---|---|---|---|
| 35.7 | Hamming [31,26,3] | 15 | 1.42e-13 | 1.9e-13 | 0.99 | all | 16 | 0 |
| 42.2 | Hamming [15,11,3] | 15 | 5.76e-13 | 5.5e-13 | 0.8 | all | exact | 0 |
| 42.2 | Hamming [15,11,3] | 15 | 4.30e-13 | 4.3e-13 | 0.99 | all | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 4.60e-13 | 3.8e-13 | 0.8 | idle+gate | exact | 0 |
| 51.6 | [15,9,3] | 15 | 7.55e-13 | 8.2e-13 | 0.8 | all | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 1.39e-13 | 2.1e-13 | 0.99 | all | exact | 1e-06 |
| 77.3 | [15,6,5] | 15 | 1.71e-13 | 1.9e-14 | 0.0 | none | any (no flags) | 0 |

### (b) Lowest p_L per code and d_Z, and what it takes

For every simulated (or transferred) code and d_Z: the lowest p_L of any flag setting, the phase-flip part of it (flags cannot lower it), the flag-free p_L, and the least demanding setting within a factor 1.5 of the lowest (smallest f, then fewest flag classes, then coarsest window).

| overhead | code | d_Z | lowest p_L | of which p_ZL | p_L without flags | f needed | flags on | coarsest window |
|---|---|---|---|---|---|---|---|---|
| 30.8 | Hamming [31,26,3] | 13 | 1.78e-12 | 1.78e-12 | 1.13e-11 | 0.99 | all | 16 |
| 35.7 | Hamming [31,26,3] | 15 | 5.56e-14 | 5.55e-14 | 1.27e-11 | 1.0 | all | exact |
| 36.4 | Hamming [15,11,3] | 13 | 2.65e-12 | 2.61e-12 | - | 0.8 | all | exact |
| 38.6 | ext. Hamming [16,11,4] | 13 | 2.71e-12 | 2.71e-12 | - | 0.95 | all | exact |
| 40.6 | Hamming [31,26,3] | 17 | 2.05e-15 | 2.00e-15 | 1.62e-11 | 1.0 | all | exact |
| 42.2 | Hamming [15,11,3] | 15 | 1.58e-13 | 9.29e-14 | - | 1.0 | all | 64 |
| 44.4 | [15,9,3] | 13 | 3.19e-12 | 3.19e-12 | 5.49e-12 | 0.5 | idle | 4096 |
| 44.8 | ext. Hamming [16,11,4] | 15 | 9.56e-14 | 9.53e-14 | - | 0.95 | all | exact |
| 45.5 | Hamming [31,26,3] | 19 | 1.48e-16 | 8.26e-17 | 2.02e-11 | 1.0 | all | exact |
| 48.0 | Hamming [15,11,3] | 17 | 9.19e-14 | 3.64e-15 | - | 1.0 | all | 64 |
| 50.5 | Hamming [31,26,3] | 21 | 9.20e-17 | 3.78e-18 | 2.47e-11 | 1.0 | all | exact |
| 51.0 | ext. Hamming [16,11,4] | 17 | 4.21e-15 | 3.87e-15 | - | 0.99 | all | exact |
| 51.6 | [15,9,3] | 15 | 1.14e-13 | 1.14e-13 | 3.18e-12 | 0.98 | idle+gate | 4 |
| 53.8 | Hamming [15,11,3] | 19 | 1.23e-13 | 1.49e-16 | - | 1.0 | all | 64 |
| 55.4 | Hamming [31,26,3] | 23 | 6.14e-17 | 1.84e-19 | 2.16e-11 | 1.0 | all | exact |
| 57.2 | ext. Hamming [16,11,4] | 19 | 6.38e-16 | 1.59e-16 | - | 0.99 | all | exact |
| 58.7 | [15,9,3] | 17 | 4.44e-15 | 4.44e-15 | 4.10e-12 | 0.999 | all | exact |
| 59.6 | Hamming [15,11,3] | 21 | 1.64e-13 | 6.52e-18 | - | 1.0 | all | 64 |
| 60.3 | Hamming [31,26,3] | 25 | 1.49e-16 | 9.23e-21 | 3.48e-11 | 1.0 | all | exact |
| 63.4 | ext. Hamming [16,11,4] | 21 | 6.50e-16 | 6.93e-18 | - | 0.99 | all | exact |
| 65.5 | Hamming [15,11,3] | 23 | 2.15e-13 | 2.97e-19 | - | 1.0 | all | 64 |
| 65.8 | [15,9,3] | 19 | 1.82e-16 | 1.82e-16 | 5.65e-12 | 1.0 | all | 16 |
| 66.7 | [15,6,5] | 13 | 4.78e-12 | 4.78e-12 | 4.78e-12 | 0.0 | none | any (no flags) |
| 69.5 | ext. Hamming [16,11,4] | 23 | 8.42e-16 | 3.15e-19 | - | 0.99 | all | exact |
| 70.8 | [15,6,5] 2 anc | 13 | 6.79e-12 | 6.79e-12 | - | 0.5 | idle | 4096 |
| 71.3 | Hamming [15,11,3] | 25 | 2.75e-13 | 1.39e-20 | - | 1.0 | all | 64 |
| 72.9 | [15,9,3] | 21 | 7.97e-18 | 7.97e-18 | 7.56e-12 | 1.0 | all | 16 |
| 75.7 | ext. Hamming [16,11,4] | 25 | 1.08e-15 | 1.47e-20 | - | 0.99 | all | exact |
| 77.3 | [15,6,5] | 15 | 1.70e-13 | 1.70e-13 | 1.71e-13 | 0.0 | none | any (no flags) |
| 80.0 | [15,9,3] | 23 | 3.63e-19 | 3.63e-19 | 9.86e-12 | 1.0 | all | 16 |
| 82.2 | [15,6,5] 2 anc | 15 | 2.75e-13 | 2.75e-13 | - | 0.5 | idle | 4096 |
| 87.1 | [15,9,3] | 25 | 1.69e-20 | 1.69e-20 | 1.26e-11 | 1.0 | all | 16 |
| 88.0 | [15,6,5] | 17 | 6.66e-15 | 6.66e-15 | 7.24e-15 | 0.0 | none | any (no flags) |
| 93.5 | [15,6,5] 2 anc | 17 | 1.18e-14 | 1.18e-14 | - | 0.5 | idle | 4096 |
| 98.7 | [15,6,5] | 19 | 2.73e-16 | 2.73e-16 | 1.26e-15 | 0.5 | idle+gate | exact |
| 104.8 | [15,6,5] 2 anc | 19 | 5.09e-16 | 5.09e-16 | - | 0.5 | idle | 4096 |
| 109.3 | [15,6,5] | 21 | 1.20e-17 | 1.20e-17 | 1.61e-15 | 0.9 | all | 1024 |
| 116.2 | [15,6,5] 2 anc | 21 | 2.30e-17 | 2.30e-17 | - | 0.8 | idle+gate | exact |
| 120.0 | [15,6,5] | 23 | 5.44e-19 | 5.44e-19 | 2.49e-15 | 0.95 | idle+gate | exact |
| 127.5 | [15,6,5] 2 anc | 23 | 1.07e-18 | 1.07e-18 | - | 0.9 | all | 16 |
| 130.7 | [15,6,5] | 25 | 2.54e-20 | 2.54e-20 | 3.74e-15 | 0.99 | all | 1024 |
| 138.8 | [15,6,5] 2 anc | 25 | 5.03e-20 | 5.03e-20 | - | 0.98 | idle+gate | 64 |
