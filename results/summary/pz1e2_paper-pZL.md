
## p_Z = 1e-2, eta = 1e6 (p_X = 1e-8): lowest reachable logical error rate (phase flips: paper-pZL)

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
| [15,6,5] | f=0.0 none w=exact | 5.65e-11 | 47 | 248.0 | 5.02e-11 | 6.31e-12 | 194.7 | 226.7 | - | - |
| [15,6,5] | f=1.0 all w=exact | 3.47e-16 | 69 | 365.3 | 2.45e-16 | 1.02e-16 | 194.7 | 226.7 | 248.0 | 269.3 |
| [15,6,5] 2 anc | f=0.0 none w=exact | 2.19e-11 | 49 | 274.8 | 1.95e-11 | 2.46e-12 | 218.2 | 240.8 | - | - |
| [15,6,5] 2 anc | f=0.9 all w=exact | 4.39e-13 | 57 | 320.2 | 3.95e-13 | 4.45e-14 | 218.2 | 240.8 | 263.5 | 297.5 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | 3.17e-12 | 53 | 297.5 | 2.84e-12 | 3.31e-13 | 218.2 | 240.8 | 263.5 | - |
| [15,6,5] 2 anc | f=0.99 all w=exact | 6.97e-15 | 65 | 365.5 | 6.17e-15 | 8.05e-16 | 218.2 | 240.8 | 263.5 | 286.2 |
| [15,6,5] 2 anc | f=0.99 all w=64 | 8.30e-15 | 65 | 365.5 | 7.49e-15 | 8.05e-16 | 218.2 | 240.8 | 263.5 | 286.2 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | 1.73e-13 | 57 | 320.2 | 1.29e-13 | 4.45e-14 | 218.2 | 240.8 | 263.5 | 286.2 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | 5.44e-12 | 51 | 286.2 | 4.53e-12 | 9.02e-13 | 218.2 | 240.8 | 263.5 | - |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | 2.49e-16 (extrap.) | 71 | 399.5 | 2.10e-16 | 3.97e-17 | 218.2 | 240.8 | 263.5 | 286.2 |
| [15,6,5] 2 anc | f=1.0 all w=exact | 8.06e-18 (extrap.) | 77 | 433.5 | 6.11e-18 | 1.96e-18 | 218.2 | 240.8 | 263.5 | 286.2 |
| [15,9,3] | f=0.0 none w=exact | 4.73e-09 | 37 | 129.8 | 4.10e-09 | 6.34e-10 | - | - | - | - |
| [15,9,3] | f=0.9 idle w=exact | 1.82e-09 | 39 | 136.9 | 1.59e-09 | 2.33e-10 | - | - | - | - |
| [15,9,3] | f=0.99 all w=exact | 4.30e-11 | 47 | 165.3 | 3.88e-11 | 4.21e-12 | 129.8 | 151.1 | - | - |
| [15,9,3] | f=0.99 all w=64 | 1.06e-10 | 45 | 158.2 | 9.42e-11 | 1.15e-11 | 129.8 | - | - | - |
| [15,9,3] | f=0.99 idle+gate w=exact | 4.48e-11 | 47 | 165.3 | 4.06e-11 | 4.21e-12 | 129.8 | 151.1 | - | - |
| [15,9,3] | f=1.0 all w=exact | 2.25e-12 | 53 | 186.7 | 2.04e-12 | 2.08e-13 | 129.8 | 144.0 | 165.3 | - |
| Hamming [15,11,3] | f=0.0 none w=exact | 4.46e-09 | 37 | 106.2 | 3.94e-09 | 5.19e-10 | - | - | - | - |
| Hamming [15,11,3] | f=0.9 all w=exact | 4.82e-10 | 41 | 117.8 | 4.12e-10 | 6.98e-11 | 106.2 | - | - | - |
| Hamming [15,11,3] | f=0.9 idle w=exact | 1.97e-09 | 39 | 112.0 | 1.78e-09 | 1.90e-10 | - | - | - | - |
| Hamming [15,11,3] | f=0.99 all w=exact | 6.03e-11 | 45 | 129.5 | 5.09e-11 | 9.38e-12 | 106.2 | 123.6 | - | - |
| Hamming [15,11,3] | f=0.99 all w=64 | 1.29e-10 | 45 | 129.5 | 1.20e-10 | 9.38e-12 | 106.2 | - | - | - |
| Hamming [15,11,3] | f=0.99 all w=1024 | 6.20e-10 | 41 | 117.8 | 5.50e-10 | 6.98e-11 | 106.2 | - | - | - |
| Hamming [15,11,3] | f=0.99 idle w=exact | 1.70e-09 | 39 | 112.0 | 1.51e-09 | 1.90e-10 | - | - | - | - |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | 5.88e-11 | 45 | 129.5 | 4.95e-11 | 9.38e-12 | 106.2 | 123.6 | - | - |
| Hamming [15,11,3] | f=1.0 all w=exact | 1.77e-12 | 53 | 152.7 | 1.60e-12 | 1.70e-13 | 106.2 | 117.8 | 135.3 | - |
