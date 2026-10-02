
## Limits

### Absolute phase-flip floor of the construction

Any Elevator-type memory spends at least one repetition-code block of distance d_Z per logical qubit; its phase flips alone reach the target only from d_rep (this work's repetition-code model), so the overhead is at least 2 d_rep - 1 even for k/n -> 1 and without ancilla noise.

| p_Z | target | d_rep | overhead floor |
|---|---|---|---|
| 0.001 | 1e-12 | 13 | 25 |
| 0.01 | 1e-09 | 29 | 57 |
| 0.01 | 1e-12 | 41 | 81 |

### p_Z = 1e-3, eta = 1e6, 1e-12: is each code at its phase-flip floor?

d_floor: smallest d_Z whose phase flips alone meet the target (flags cannot lower it).  At d_floor - 2 the phase flips alone exceed the target; at d_floor the lowest bit-flip rate over the flag settings is shown against the phase-flip rate.

| code | phase model | d_floor | overhead | p_ZL(d_floor - 2) | p_ZL(d_floor) | lowest p_XL(d_floor) [95% upper] | setting |
|---|---|---|---|---|---|---|---|
| [15,9,3] | this-work-pZL | 15 | 51.6 | 3.16e-12 | 1.10e-13 | 4.81e-18 [5.22e-18] | f=1.0 all w=exact |
| [15,9,3] | paper-pZL | 17 | 58.7 | 1.19e-12 | 4.99e-14 | 7.84e-18 [8.52e-18] | f=1.0 all w=exact (transferred) |
| [15,6,5] | this-work-pZL | 15 | 77.3 | 4.74e-12 | 1.65e-13 | 2.42e-30 [1.74e-26] | f=1.0 all w=exact |
| [15,6,5] | paper-pZL | 17 | 88.0 | 1.78e-12 | 7.49e-14 | 6.86e-30 [4.11e-26] | f=1.0 all w=exact (transferred) |
| [15,6,5] 2 anc | this-work-pZL | 15 | 82.2 | 6.64e-12 | 2.62e-13 | 5.70e-28 [3.23e-27] | f=1.0 all w=exact |
| [15,6,5] 2 anc | paper-pZL | 17 | 93.5 | 1.89e-12 | 7.96e-14 | 5.61e-31 [4.09e-27] | f=1.0 all w=exact |
| Hamming [15,11,3] | this-work-pZL | 15 | 42.2 | 2.59e-12 | 8.99e-14 | 3.67e-18 [3.88e-18] | f=1.0 all w=exact |
| Hamming [15,11,3] | paper-pZL | 15 | 42.2 | 2.30e-11 | 9.70e-13 | 3.67e-18 [3.88e-18] | f=1.0 all w=exact |
| Hamming [31,26,3] | this-work-pZL | 15 | 35.7 | 1.79e-12 | 5.47e-14 | 3.21e-17 [3.50e-17] | f=1.0 all w=exact |
| Hamming [31,26,3] | paper-pZL | 15 | 35.7 | 1.95e-11 | 8.21e-13 | 3.21e-17 [3.50e-17] | f=1.0 all w=exact |
| ext. Hamming [16,11,4] | this-work-pZL | 15 | 44.8 | 2.69e-12 | 9.24e-14 | 1.24e-22 [1.53e-22] | f=1.0 all w=exact |
| ext. Hamming [16,11,4] | paper-pZL | 17 | 51.0 | 1.03e-12 | 4.34e-14 | 2.04e-22 [2.52e-22] | f=1.0 all w=exact (transferred) |
| Hamming [63,57,3] | this-work-pZL | 15 | 32.6 | 1.46e-12 | 4.02e-14 | 2.38e-16 [2.59e-16] | f=1.0 all w=exact |
| Hamming [63,57,3] | paper-pZL | 15 | 32.6 | 1.78e-11 | 7.49e-13 | 2.38e-16 [2.59e-16] | f=1.0 all w=exact |

### p_Z = 1e-2, eta = 1e6: composition of the lowest reachable p_L

At each floor: phase flips (cannot be flagged), bit flips from sets of flagged events only (need >= d events forming a logical: the code's distance) and bit flips involving unflagged errors (fraction 1 - f).

| code | flags | phase model | floor p_L | d_Z | p_ZL share | flagged-only share | unflagged share |
|---|---|---|---|---|---|---|---|
| [15,6,5] | none | this-work-pZL | 4.39e-10 | 67 | 0.27 | 0.00 | 0.73 |
| [15,6,5] | f=0.5 all w=exact | this-work-pZL | 1.42e-10 | 73 | 0.23 | 0.00 | 0.77 |
| [15,6,5] | f=0.8 all w=exact | this-work-pZL | 3.02e-11 | 81 | 0.21 | 0.00 | 0.79 |
| [15,6,5] | f=0.9 all w=exact | this-work-pZL | 1.04e-11 | 85 | 0.26 | 0.00 | 0.74 |
| [15,6,5] | f=0.9 all w=4096 | this-work-pZL | 7.35e-11 | 75 | 0.30 | 0.00 | 0.70 |
| [15,6,5] | f=0.9 idle w=exact | this-work-pZL | 1.17e-10 | 73 | 0.28 | 0.00 | 0.72 |
| [15,6,5] | f=0.95 all w=exact | this-work-pZL | 3.49e-12 | 91 | 0.23 | 0.00 | 0.77 |
| [15,6,5] | f=0.99 all w=exact | this-work-pZL | 3.47e-13 | 103 | 0.19 | 0.02 | 0.79 |
| [15,6,5] | f=0.99 all w=1 | this-work-pZL | 2.22e-13 | 105 | 0.20 | 0.00 | 0.80 |
| [15,6,5] | f=0.99 all w=1024 | this-work-pZL | 2.18e-12 | 91 | 0.36 | 0.00 | 0.64 |
| [15,6,5] | f=0.99 all w=16 | this-work-pZL | 5.72e-13 | 99 | 0.27 | 0.00 | 0.73 |
| [15,6,5] | f=0.99 all w=256 | this-work-pZL | 1.95e-11 | 83 | 0.21 | 0.00 | 0.79 |
| [15,6,5] | f=0.99 all w=4 | this-work-pZL | 2.89e-13 | 105 | 0.15 | 0.00 | 0.85 |
| [15,6,5] | f=0.99 all w=4096 | this-work-pZL | 1.62e-11 | 83 | 0.25 | 0.59 | 0.15 |
| [15,6,5] | f=0.99 all w=64 | this-work-pZL | 6.00e-13 | 99 | 0.25 | 0.00 | 0.75 |
| [15,6,5] | f=0.99 idle w=exact | this-work-pZL | 9.67e-11 | 75 | 0.23 | 0.00 | 0.77 |
| [15,6,5] | f=0.99 idle w=4096 | this-work-pZL | 1.82e-10 | 71 | 0.28 | 0.00 | 0.72 |
| [15,6,5] | f=0.99 idle+gate w=exact | this-work-pZL | 3.36e-13 | 103 | 0.20 | 0.00 | 0.80 |
| [15,6,5] | f=0.999 all w=exact | this-work-pZL | 2.55e-14 | 115 | 0.22 | 0.69 | 0.09 |
| [15,6,5] | f=1.0 all w=exact | this-work-pZL | 2.34e-14 | 115 | 0.24 | 0.76 | 0.00 |
| [15,6,5] | f=1.0 idle w=exact | this-work-pZL | 8.99e-11 | 75 | 0.24 | 0.00 | 0.76 |
| [15,6,5] 2 anc | none | this-work-pZL | 1.90e-10 | 75 | 0.23 | 0.00 | 0.77 |
| [15,6,5] 2 anc | f=0.5 all w=exact | this-work-pZL | 5.80e-11 | 81 | 0.22 | 0.00 | 0.78 |
| [15,6,5] 2 anc | f=0.8 all w=exact | this-work-pZL | 8.98e-12 | 91 | 0.18 | 0.00 | 0.82 |
| [15,6,5] 2 anc | f=0.9 all w=exact | this-work-pZL | 2.68e-12 | 95 | 0.26 | 0.00 | 0.74 |
| [15,6,5] 2 anc | f=0.9 all w=4096 | this-work-pZL | 4.88e-11 | 81 | 0.26 | 0.62 | 0.13 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | this-work-pZL | 5.18e-11 | 81 | 0.24 | 0.00 | 0.76 |
| [15,6,5] 2 anc | f=0.95 all w=exact | this-work-pZL | 1.76e-12 | 99 | 0.17 | 0.00 | 0.83 |
| [15,6,5] 2 anc | f=0.99 all w=exact | this-work-pZL | 1.61e-13 | 111 | 0.16 | 0.02 | 0.82 |
| [15,6,5] 2 anc | f=0.99 all w=1 | this-work-pZL | 1.37e-13 | 111 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | this-work-pZL | 5.60e-12 | 91 | 0.28 | 0.37 | 0.35 |
| [15,6,5] 2 anc | f=0.99 all w=16 | this-work-pZL | 3.83e-14 | 117 | 0.20 | 0.00 | 0.80 |
| [15,6,5] 2 anc | f=0.99 all w=256 | this-work-pZL | 3.50e-13 | 105 | 0.25 | 0.00 | 0.75 |
| [15,6,5] 2 anc | f=0.99 all w=4 | this-work-pZL | 1.13e-13 | 111 | 0.23 | 0.00 | 0.77 |
| [15,6,5] 2 anc | f=0.99 all w=4096 | this-work-pZL | 2.40e-12 | 95 | 0.29 | 0.21 | 0.51 |
| [15,6,5] 2 anc | f=0.99 all w=64 | this-work-pZL | 1.35e-13 | 111 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | this-work-pZL | 4.17e-11 | 83 | 0.20 | 0.00 | 0.80 |
| [15,6,5] 2 anc | f=0.99 idle w=4096 | this-work-pZL | 8.56e-11 | 79 | 0.22 | 0.00 | 0.78 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | this-work-pZL | 1.39e-14 | 121 | 0.24 | 0.00 | 0.76 |
| [15,6,5] 2 anc | f=0.999 all w=exact | this-work-pZL | 4.70e-14 | 115 | 0.24 | 0.07 | 0.68 |
| [15,6,5] 2 anc | f=1.0 all w=exact | this-work-pZL | 8.37e-15 | 123 | 0.27 | 0.73 | 0.00 |
| [15,6,5] 2 anc | f=1.0 idle w=exact | this-work-pZL | 3.50e-11 | 83 | 0.24 | 0.00 | 0.76 |
| [15,9,3] | none | this-work-pZL | 1.29e-08 | 51 | 0.18 | 0.00 | 0.82 |
| [15,9,3] | f=0.5 all w=exact | this-work-pZL | 5.78e-09 | 55 | 0.17 | 0.00 | 0.83 |
| [15,9,3] | f=0.8 all w=exact | this-work-pZL | 2.21e-09 | 59 | 0.19 | 0.00 | 0.81 |
| [15,9,3] | f=0.9 all w=exact | this-work-pZL | 1.15e-09 | 63 | 0.16 | 0.00 | 0.84 |
| [15,9,3] | f=0.9 all w=4096 | this-work-pZL | 2.45e-09 | 59 | 0.17 | 0.28 | 0.55 |
| [15,9,3] | f=0.9 idle w=exact | this-work-pZL | 5.37e-09 | 55 | 0.18 | 0.00 | 0.82 |
| [15,9,3] | f=0.95 all w=exact | this-work-pZL | 6.66e-10 | 65 | 0.18 | 0.01 | 0.81 |
| [15,9,3] | f=0.99 all w=exact | this-work-pZL | 1.73e-10 | 71 | 0.19 | 0.05 | 0.76 |
| [15,9,3] | f=0.99 all w=1 | this-work-pZL | 2.06e-10 | 71 | 0.16 | 0.14 | 0.70 |
| [15,9,3] | f=0.99 all w=1024 | this-work-pZL | 9.57e-10 | 63 | 0.19 | 0.65 | 0.16 |
| [15,9,3] | f=0.99 all w=16 | this-work-pZL | 1.87e-10 | 71 | 0.18 | 0.15 | 0.67 |
| [15,9,3] | f=0.99 all w=256 | this-work-pZL | 8.23e-10 | 63 | 0.22 | 0.61 | 0.17 |
| [15,9,3] | f=0.99 all w=4 | this-work-pZL | 2.13e-10 | 71 | 0.16 | 0.15 | 0.70 |
| [15,9,3] | f=0.99 all w=4096 | this-work-pZL | 1.31e-09 | 61 | 0.21 | 0.66 | 0.13 |
| [15,9,3] | f=0.99 all w=64 | this-work-pZL | 3.82e-10 | 67 | 0.20 | 0.47 | 0.33 |
| [15,9,3] | f=0.99 idle w=exact | this-work-pZL | 4.79e-09 | 55 | 0.21 | 0.00 | 0.79 |
| [15,9,3] | f=0.99 idle w=4096 | this-work-pZL | 5.85e-09 | 55 | 0.17 | 0.04 | 0.79 |
| [15,9,3] | f=0.99 idle+gate w=exact | this-work-pZL | 1.83e-10 | 71 | 0.18 | 0.16 | 0.65 |
| [15,9,3] | f=0.999 all w=exact | this-work-pZL | 4.10e-11 | 77 | 0.23 | 0.32 | 0.45 |
| [15,9,3] | f=1.0 all w=exact | this-work-pZL | 2.10e-11 | 81 | 0.20 | 0.80 | 0.00 |
| [15,9,3] | f=1.0 idle w=exact | this-work-pZL | 4.50e-09 | 55 | 0.22 | 0.00 | 0.78 |
| Hamming [15,11,3] | none | this-work-pZL | 1.18e-08 | 49 | 0.25 | 0.00 | 0.75 |
| Hamming [15,11,3] | f=0.9 all w=exact | this-work-pZL | 1.55e-09 | 59 | 0.22 | 0.00 | 0.78 |
| Hamming [15,11,3] | f=0.9 idle w=exact | this-work-pZL | 5.89e-09 | 53 | 0.21 | 0.00 | 0.79 |
| Hamming [15,11,3] | f=0.99 all w=exact | this-work-pZL | 2.26e-10 | 69 | 0.18 | 0.03 | 0.79 |
| Hamming [15,11,3] | f=0.99 all w=1024 | this-work-pZL | 1.96e-09 | 59 | 0.18 | 0.74 | 0.09 |
| Hamming [15,11,3] | f=0.99 all w=64 | this-work-pZL | 4.43e-10 | 67 | 0.14 | 0.40 | 0.46 |
| Hamming [15,11,3] | f=0.99 idle w=exact | this-work-pZL | 4.98e-09 | 53 | 0.25 | 0.00 | 0.75 |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | this-work-pZL | 2.12e-10 | 69 | 0.20 | 0.01 | 0.80 |
| Hamming [15,11,3] | f=1.0 all w=exact | this-work-pZL | 1.67e-11 | 81 | 0.20 | 0.80 | 0.00 |
| [15,6,5] | none | paper-pZL | 6.27e-11 | 47 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.5 all w=exact | paper-pZL | 1.72e-11 | 49 | 0.13 | 0.00 | 0.87 |
| [15,6,5] | f=0.8 all w=exact | paper-pZL | 3.21e-12 | 53 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.9 all w=exact | paper-pZL | 9.93e-13 | 55 | 0.11 | 0.00 | 0.89 |
| [15,6,5] | f=0.9 all w=4096 | paper-pZL | 7.64e-12 | 51 | 0.11 | 0.00 | 0.89 |
| [15,6,5] | f=0.9 idle w=exact | paper-pZL | 1.41e-11 | 49 | 0.16 | 0.00 | 0.84 |
| [15,6,5] | f=0.95 all w=exact | paper-pZL | 2.88e-13 | 57 | 0.15 | 0.00 | 0.85 |
| [15,6,5] | f=0.99 all w=exact | paper-pZL | 2.11e-14 | 63 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.99 all w=1 | paper-pZL | 8.42e-15 | 63 | 0.25 | 0.00 | 0.75 |
| [15,6,5] | f=0.99 all w=1024 | paper-pZL | 5.26e-14 | 59 | 0.29 | 0.00 | 0.71 |
| [15,6,5] | f=0.99 all w=16 | paper-pZL | 3.75e-14 | 61 | 0.15 | 0.00 | 0.85 |
| [15,6,5] | f=0.99 all w=256 | paper-pZL | 2.15e-12 | 53 | 0.14 | 0.00 | 0.86 |
| [15,6,5] | f=0.99 all w=4 | paper-pZL | 2.18e-14 | 63 | 0.09 | 0.00 | 0.91 |
| [15,6,5] | f=0.99 all w=4096 | paper-pZL | 5.84e-13 | 55 | 0.20 | 0.51 | 0.30 |
| [15,6,5] | f=0.99 all w=64 | paper-pZL | 3.96e-14 | 61 | 0.14 | 0.00 | 0.86 |
| [15,6,5] | f=0.99 idle w=exact | paper-pZL | 1.15e-11 | 49 | 0.20 | 0.00 | 0.80 |
| [15,6,5] | f=0.99 idle w=4096 | paper-pZL | 2.43e-11 | 47 | 0.26 | 0.00 | 0.74 |
| [15,6,5] | f=0.99 idle+gate w=exact | paper-pZL | 2.13e-14 | 63 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.999 all w=exact | paper-pZL | 5.65e-16 | 69 | 0.18 | 0.40 | 0.41 |
| [15,6,5] | f=1.0 all w=exact | paper-pZL | 3.32e-16 | 71 | 0.11 | 0.89 | 0.00 |
| [15,6,5] | f=1.0 idle w=exact | paper-pZL | 1.07e-11 | 49 | 0.22 | 0.00 | 0.78 |
| [15,6,5] 2 anc | none | paper-pZL | 2.06e-11 | 49 | 0.12 | 0.00 | 0.88 |
| [15,6,5] 2 anc | f=0.5 all w=exact | paper-pZL | 6.03e-12 | 51 | 0.15 | 0.00 | 0.85 |
| [15,6,5] 2 anc | f=0.8 all w=exact | paper-pZL | 8.11e-13 | 55 | 0.15 | 0.00 | 0.85 |
| [15,6,5] 2 anc | f=0.9 all w=exact | paper-pZL | 1.27e-13 | 59 | 0.13 | 0.00 | 0.87 |
| [15,6,5] 2 anc | f=0.9 all w=4096 | paper-pZL | 4.62e-12 | 51 | 0.20 | 0.74 | 0.06 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | paper-pZL | 5.06e-12 | 51 | 0.18 | 0.00 | 0.82 |
| [15,6,5] 2 anc | f=0.95 all w=exact | paper-pZL | 1.26e-13 | 59 | 0.13 | 0.00 | 0.87 |
| [15,6,5] 2 anc | f=0.99 all w=exact | paper-pZL | 1.28e-14 | 63 | 0.17 | 0.00 | 0.83 |
| [15,6,5] 2 anc | f=0.99 all w=1 | paper-pZL | 8.33e-15 | 65 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | paper-pZL | 1.73e-13 | 57 | 0.26 | 0.22 | 0.52 |
| [15,6,5] 2 anc | f=0.99 all w=16 | paper-pZL | 9.49e-16 | 69 | 0.11 | 0.00 | 0.89 |
| [15,6,5] 2 anc | f=0.99 all w=256 | paper-pZL | 1.13e-14 | 63 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.99 all w=4 | paper-pZL | 7.04e-15 | 65 | 0.11 | 0.00 | 0.89 |
| [15,6,5] 2 anc | f=0.99 all w=4096 | paper-pZL | 7.01e-14 | 59 | 0.23 | 0.05 | 0.72 |
| [15,6,5] 2 anc | f=0.99 all w=64 | paper-pZL | 8.30e-15 | 65 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | paper-pZL | 3.99e-12 | 51 | 0.23 | 0.00 | 0.77 |
| [15,6,5] 2 anc | f=0.99 idle w=4096 | paper-pZL | 8.69e-12 | 51 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | paper-pZL | 2.09e-16 | 71 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.999 all w=exact | paper-pZL | 6.74e-16 | 69 | 0.16 | 0.06 | 0.77 |
| [15,6,5] 2 anc | f=1.0 all w=exact | paper-pZL | 8.62e-17 | 73 | 0.17 | 0.83 | 0.00 |
| [15,6,5] 2 anc | f=1.0 idle w=exact | paper-pZL | 3.24e-12 | 53 | 0.10 | 0.00 | 0.90 |
| [15,9,3] | none | paper-pZL | 4.73e-09 | 37 | 0.13 | 0.00 | 0.87 |
| [15,9,3] | f=0.5 all w=exact | paper-pZL | 1.97e-09 | 39 | 0.12 | 0.00 | 0.88 |
| [15,9,3] | f=0.8 all w=exact | paper-pZL | 6.92e-10 | 41 | 0.12 | 0.00 | 0.88 |
| [15,9,3] | f=0.9 all w=exact | paper-pZL | 3.43e-10 | 43 | 0.09 | 0.00 | 0.91 |
| [15,9,3] | f=0.9 all w=4096 | paper-pZL | 7.59e-10 | 41 | 0.11 | 0.30 | 0.59 |
| [15,9,3] | f=0.9 idle w=exact | paper-pZL | 1.82e-09 | 39 | 0.13 | 0.00 | 0.87 |
| [15,9,3] | f=0.95 all w=exact | paper-pZL | 1.92e-10 | 43 | 0.16 | 0.00 | 0.83 |
| [15,9,3] | f=0.99 all w=exact | paper-pZL | 4.38e-11 | 47 | 0.10 | 0.02 | 0.88 |
| [15,9,3] | f=0.99 all w=1 | paper-pZL | 5.14e-11 | 47 | 0.08 | 0.08 | 0.84 |
| [15,9,3] | f=0.99 all w=1024 | paper-pZL | 2.91e-10 | 43 | 0.11 | 0.72 | 0.17 |
| [15,9,3] | f=0.99 all w=16 | paper-pZL | 5.03e-11 | 47 | 0.08 | 0.18 | 0.73 |
| [15,9,3] | f=0.99 all w=256 | paper-pZL | 2.23e-10 | 43 | 0.14 | 0.66 | 0.20 |
| [15,9,3] | f=0.99 all w=4 | paper-pZL | 5.04e-11 | 47 | 0.08 | 0.08 | 0.84 |
| [15,9,3] | f=0.99 all w=4096 | paper-pZL | 3.81e-10 | 43 | 0.08 | 0.76 | 0.16 |
| [15,9,3] | f=0.99 all w=64 | paper-pZL | 1.06e-10 | 45 | 0.11 | 0.53 | 0.36 |
| [15,9,3] | f=0.99 idle w=exact | paper-pZL | 1.62e-09 | 39 | 0.14 | 0.00 | 0.86 |
| [15,9,3] | f=0.99 idle w=4096 | paper-pZL | 1.99e-09 | 39 | 0.12 | 0.04 | 0.84 |
| [15,9,3] | f=0.99 idle+gate w=exact | paper-pZL | 4.48e-11 | 47 | 0.09 | 0.08 | 0.82 |
| [15,9,3] | f=0.999 all w=exact | paper-pZL | 7.47e-12 | 51 | 0.08 | 0.23 | 0.70 |
| [15,9,3] | f=1.0 all w=exact | paper-pZL | 2.25e-12 | 53 | 0.09 | 0.91 | 0.00 |
| [15,9,3] | f=1.0 idle w=exact | paper-pZL | 1.51e-09 | 39 | 0.15 | 0.00 | 0.85 |
| Hamming [15,11,3] | none | paper-pZL | 4.39e-09 | 37 | 0.12 | 0.00 | 0.88 |
| Hamming [15,11,3] | f=0.9 all w=exact | paper-pZL | 4.77e-10 | 41 | 0.15 | 0.00 | 0.85 |
| Hamming [15,11,3] | f=0.9 idle w=exact | paper-pZL | 2.07e-09 | 39 | 0.09 | 0.00 | 0.91 |
| Hamming [15,11,3] | f=0.99 all w=exact | paper-pZL | 6.03e-11 | 45 | 0.16 | 0.01 | 0.83 |
| Hamming [15,11,3] | f=0.99 all w=1024 | paper-pZL | 6.20e-10 | 41 | 0.11 | 0.80 | 0.09 |
| Hamming [15,11,3] | f=0.99 all w=64 | paper-pZL | 1.29e-10 | 45 | 0.07 | 0.44 | 0.49 |
| Hamming [15,11,3] | f=0.99 idle w=exact | paper-pZL | 1.70e-09 | 39 | 0.11 | 0.00 | 0.89 |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | paper-pZL | 5.88e-11 | 45 | 0.16 | 0.00 | 0.84 |
| Hamming [15,11,3] | f=1.0 all w=exact | paper-pZL | 1.77e-12 | 53 | 0.10 | 0.90 | 0.00 |
