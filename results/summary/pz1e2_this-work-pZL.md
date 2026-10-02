
## p_Z = 1e-2, eta = 1e6 (p_X = 1e-8): lowest reachable logical error rate (phase flips: this-work-pZL)

Bit flips at d_Z other than the simulated 17/25/33 use the stratum failure fractions of the nearest simulated d_Z with exact fault intensities at the new d_Z (transfer; checked below).

### Transfer check (prediction from d_Z = 17 vs direct stratified run)

| code | flags | d_Z | direct p_XL [95% CI] | transferred from 17 [95% CI] |
|---|---|---|---|---|
| [15,6,5] 2 anc | f=0.99 all w=64 | 25 | 6.73e-17 [1.25e-17, 1.39e-11] | 6.68e-17 [1.23e-17, 1.40e-11]  |
| [15,6,5] 2 anc | f=0.99 all w=1024 | 25 | 4.27e-16 [1.30e-16, 1.39e-11] | 2.93e-16 [7.55e-17, 1.38e-11]  |
| [15,9,3] | f=0.9 idle w=exact | 25 | 4.31e-10 [4.02e-10, 4.64e-10] | 4.32e-10 [4.02e-10, 4.65e-10]  |
| [15,9,3] | f=0.99 all w=64 | 25 | 1.66e-11 [9.45e-12, 3.25e-11] | 1.73e-11 [1.04e-11, 3.35e-11]  |
| [15,9,3] | f=0.99 idle+gate w=exact | 25 | 6.42e-12 [5.57e-12, 7.60e-12] | 6.07e-12 [5.31e-12, 7.29e-12]  |
| [15,9,3] | f=1.0 all w=exact | 25 | 5.09e-14 [4.69e-14, 5.53e-14] | 5.05e-14 [4.65e-14, 5.48e-14]  |
| [15,9,3] | f=1.0 all w=exact | 33 | 1.95e-13 [1.80e-13, 2.12e-13] | 1.99e-13 [1.83e-13, 2.16e-13]  |
| Hamming [15,11,3] | f=0.99 idle w=exact | 25 | 4.10e-10 [3.85e-10, 4.37e-10] | 4.33e-10 [4.06e-10, 4.61e-10]  |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | 25 | 9.52e-12 [8.88e-12, 1.04e-11] | 8.52e-12 [7.89e-12, 9.38e-12]  |

### Floor per code and flag setting (d_Z <= 301) and overhead to reach given rates

Phase flips beyond d_Z ~ 70 (repetition code sampled to d_Z = 69 at p_Z >= 1.25e-2, elevator X memory to d_Z = 29 at p_Z = 1e-2) are extrapolations of the phase-flip model; floors there are marked '(extrap.)'.

| code | flags | lowest p_L | at d_Z | overhead | p_XL there | p_ZL there | overhead for 1e-9 | 1e-10 | 1e-11 | 1e-12 |
|---|---|---|---|---|---|---|---|---|---|---|
| [15,6,5] | f=0.0 none w=exact | 4.20e-10 | 69 | 365.3 | 3.32e-10 | 8.74e-11 | 312.0 | - | - | - |
| [15,6,5] | f=1.0 all w=exact | 2.83e-14 (extrap.) | 115 | 610.7 | 2.13e-14 | 7.05e-15 | 312.0 | 365.3 | 429.3 | 482.7 |
| [15,6,5] 2 anc | f=0.0 none w=exact | 2.07e-10 (extrap.) | 75 | 422.2 | 1.56e-10 | 5.03e-11 | 342.8 | - | - | - |
| [15,6,5] 2 anc | f=0.9 all w=exact | 5.60e-12 (extrap.) | 93 | 524.2 | 4.36e-12 | 1.24e-12 | 342.8 | 410.8 | 478.8 | - |
| [15,6,5] 2 anc | f=0.9 idle w=exact | 3.74e-11 (extrap.) | 83 | 467.5 | 2.78e-11 | 9.64e-12 | 342.8 | 410.8 | - | - |
| [15,6,5] 2 anc | f=0.99 all w=exact | 9.31e-14 (extrap.) | 115 | 648.8 | 7.90e-14 | 1.41e-14 | 342.8 | 410.8 | 467.5 | 535.5 |
| [15,6,5] 2 anc | f=0.99 all w=64 | 1.40e-13 (extrap.) | 113 | 637.5 | 1.19e-13 | 2.11e-14 | 342.8 | 410.8 | 467.5 | 535.5 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | 5.88e-12 (extrap.) | 91 | 512.8 | 4.02e-12 | 1.87e-12 | 342.8 | 410.8 | 478.8 | - |
| [15,6,5] 2 anc | f=0.99 idle w=exact | 5.58e-11 (extrap.) | 81 | 456.2 | 4.12e-11 | 1.46e-11 | 342.8 | 422.2 | - | - |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | 1.57e-14 (extrap.) | 121 | 682.8 | 1.15e-14 | 4.19e-15 | 342.8 | 410.8 | 467.5 | 535.5 |
| [15,6,5] 2 anc | f=1.0 all w=exact | 2.28e-15 (extrap.) | 131 | 739.5 | 1.72e-15 | 5.57e-16 | 342.8 | 410.8 | 467.5 | 535.5 |
| [15,9,3] | f=0.0 none w=exact | 1.31e-08 | 51 | 179.6 | 1.05e-08 | 2.58e-09 | - | - | - | - |
| [15,9,3] | f=0.9 idle w=exact | 5.49e-09 | 55 | 193.8 | 4.39e-09 | 1.10e-09 | - | - | - | - |
| [15,9,3] | f=0.99 all w=exact | 1.72e-10 (extrap.) | 73 | 257.8 | 1.47e-10 | 2.54e-11 | 200.9 | - | - | - |
| [15,9,3] | f=0.99 all w=64 | 3.90e-10 | 69 | 243.6 | 3.31e-10 | 5.83e-11 | 200.9 | - | - | - |
| [15,9,3] | f=0.99 idle+gate w=exact | 1.88e-10 (extrap.) | 71 | 250.7 | 1.49e-10 | 3.84e-11 | 200.9 | - | - | - |
| [15,9,3] | f=1.0 all w=exact | 2.17e-11 (extrap.) | 81 | 286.2 | 1.68e-11 | 4.85e-12 | 200.9 | 236.4 | - | - |
| Hamming [15,11,3] | f=0.0 none w=exact | 1.23e-08 | 49 | 141.1 | 9.03e-09 | 3.24e-09 | - | - | - | - |
| Hamming [15,11,3] | f=0.9 all w=exact | 1.58e-09 | 61 | 176.0 | 1.33e-09 | 2.54e-10 | - | - | - | - |
| Hamming [15,11,3] | f=0.9 idle w=exact | 5.78e-09 | 53 | 152.7 | 4.40e-09 | 1.38e-09 | - | - | - | - |
| Hamming [15,11,3] | f=0.99 all w=exact | 2.30e-10 (extrap.) | 71 | 205.1 | 1.98e-10 | 3.14e-11 | 158.5 | - | - | - |
| Hamming [15,11,3] | f=0.99 all w=64 | 4.52e-10 | 67 | 193.5 | 3.79e-10 | 7.23e-11 | 164.4 | - | - | - |
| Hamming [15,11,3] | f=0.99 all w=1024 | 2.01e-09 | 59 | 170.2 | 1.62e-09 | 3.87e-10 | - | - | - | - |
| Hamming [15,11,3] | f=0.99 idle w=exact | 5.08e-09 | 55 | 158.5 | 4.18e-09 | 9.02e-10 | - | - | - | - |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | 2.16e-10 (extrap.) | 71 | 205.1 | 1.85e-10 | 3.14e-11 | 158.5 | - | - | - |
| Hamming [15,11,3] | f=1.0 all w=exact | 1.72e-11 (extrap.) | 81 | 234.2 | 1.33e-11 | 3.97e-12 | 158.5 | 193.5 | - | - |
