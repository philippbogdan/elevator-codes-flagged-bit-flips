
## Frontier at p_Z = 1e-3, eta = 1e6 (phase flips: this-work-pZL)

All simulated codes ([15,9,3], [15,6,5] with 1 and 2 ancillas, Hamming [15,11,3], [31,26,3], [63,57,3], extended Hamming [16,11,4]) and flag settings; decoder: exclusive-window MLE (ML at the leading order, results/decoder_optimality*.json; BP+OSD is worse on the same configurations).  p_L = p_XL + p_ZL.

### (a) Requirements frontier for p_L <= 1e-12

Non-dominated in overhead, flag efficiency f, flag classes needed, timing window allowed and false-flag rate tolerated, among the settings that reach 1e-12 with the 95% upper bound of p_XL (conservative).

| overhead | code | d_Z | p_L | p_XL 95% upper | f | flags on | window (ticks) | false flags tolerated |
|---|---|---|---|---|---|---|---|---|
| 51.6 | [15,9,3] | 15 | 4.49e-13 | 3.8e-13 | 0.8 | idle+gate | exact | 0 |
| 51.6 | [15,9,3] | 15 | 7.44e-13 | 8.2e-13 | 0.8 | all | 4096 | 0 |
| 51.6 | [15,9,3] | 15 | 9.29e-13 | 8.9e-13 | 0.999 | idle | exact | 0 |
| 77.3 | [15,6,5] | 15 | 1.54e-13 | 1.9e-14 | 0.0 | none | any (no flags) | 0 |

### (b) Lowest p_L per code and d_Z, and what it takes

For every simulated (or transferred) code and d_Z: the lowest p_L of any flag setting, the phase-flip part of it (flags cannot lower it), the flag-free p_L, and the least demanding setting within a factor 1.5 of the lowest (smallest f, then fewest flag classes, then coarsest window).

| overhead | code | d_Z | lowest p_L | of which p_ZL | p_L without flags | f needed | flags on | coarsest window |
|---|---|---|---|---|---|---|---|---|
| 44.4 | [15,9,3] | 13 | 3.03e-12 | 3.03e-12 | 5.34e-12 | 0.5 | idle | 4096 |
| 51.6 | [15,9,3] | 15 | 1.02e-13 | 1.02e-13 | 3.16e-12 | 0.98 | idle+gate | 4 |
| 58.7 | [15,9,3] | 17 | 3.76e-15 | 3.76e-15 | 4.10e-12 | 1.0 | idle+gate | 16 |
| 65.8 | [15,9,3] | 19 | 1.44e-16 | 1.44e-16 | 5.65e-12 | 1.0 | all | 16 |
| 66.7 | [15,6,5] | 13 | 4.54e-12 | 4.54e-12 | 4.54e-12 | 0.0 | none | any (no flags) |
| 70.8 | [15,6,5] 2 anc | 13 | 6.32e-12 | 6.32e-12 | - | 0.5 | idle | 4096 |
| 72.9 | [15,9,3] | 21 | 5.91e-18 | 5.91e-18 | 7.56e-12 | 1.0 | all | 16 |
| 77.3 | [15,6,5] | 15 | 1.54e-13 | 1.54e-13 | 1.54e-13 | 0.0 | none | any (no flags) |
| 80.0 | [15,9,3] | 23 | 2.53e-19 | 2.53e-19 | 9.86e-12 | 1.0 | all | 16 |
| 82.2 | [15,6,5] 2 anc | 15 | 2.41e-13 | 2.41e-13 | - | 0.5 | idle | 4096 |
| 87.1 | [15,9,3] | 25 | 1.11e-20 | 1.11e-20 | 1.26e-11 | 1.0 | all | 16 |
| 88.0 | [15,6,5] | 17 | 5.63e-15 | 5.63e-15 | 6.21e-15 | 0.0 | none | any (no flags) |
| 93.5 | [15,6,5] 2 anc | 17 | 9.70e-15 | 9.70e-15 | - | 0.5 | idle | 4096 |
| 98.7 | [15,6,5] | 19 | 2.16e-16 | 2.16e-16 | 1.20e-15 | 0.8 | idle | exact |
| 104.8 | [15,6,5] 2 anc | 19 | 3.95e-16 | 3.95e-16 | - | 0.5 | idle | 4096 |
| 109.3 | [15,6,5] | 21 | 8.86e-18 | 8.86e-18 | 1.61e-15 | 0.9 | all | 1024 |
| 116.2 | [15,6,5] 2 anc | 21 | 1.68e-17 | 1.68e-17 | - | 0.8 | idle+gate | exact |
| 120.0 | [15,6,5] | 23 | 3.79e-19 | 3.79e-19 | 2.49e-15 | 0.95 | idle+gate | exact |
| 127.5 | [15,6,5] 2 anc | 23 | 7.37e-19 | 7.37e-19 | - | 0.95 | idle+gate | exact |
| 130.7 | [15,6,5] | 25 | 1.67e-20 | 1.67e-20 | 3.74e-15 | 0.99 | all | 1024 |
| 138.8 | [15,6,5] 2 anc | 25 | 3.29e-20 | 3.29e-20 | - | 0.98 | idle+gate | exact |
