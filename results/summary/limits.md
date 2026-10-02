
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
| [15,9,3] | this-work-pZL | 15 | 51.6 | 3.20e-12 | 1.10e-13 | 4.81e-18 [5.22e-18] | f=1.0 all w=exact |
| [15,9,3] | paper-pZL | 17 | 58.7 | 1.19e-12 | 4.99e-14 | 7.84e-18 [8.52e-18] | f=1.0 all w=exact (transferred) |
| [15,6,5] | this-work-pZL | 15 | 77.3 | 4.80e-12 | 1.65e-13 | 2.42e-30 [1.74e-26] | f=1.0 all w=exact |
| [15,6,5] | paper-pZL | 17 | 88.0 | 1.78e-12 | 7.49e-14 | 6.86e-30 [4.11e-26] | f=1.0 all w=exact (transferred) |
| [15,6,5] 2 anc | this-work-pZL | 15 | 82.2 | 6.71e-12 | 2.62e-13 | 5.70e-28 [3.23e-27] | f=1.0 all w=exact |
| [15,6,5] 2 anc | paper-pZL | 17 | 93.5 | 1.89e-12 | 7.96e-14 | 5.61e-31 [4.09e-27] | f=1.0 all w=exact |
| Hamming [15,11,3] | this-work-pZL | 15 | 42.2 | 2.62e-12 | 9.02e-14 | 3.67e-18 [3.88e-18] | f=1.0 all w=exact |
| Hamming [15,11,3] | paper-pZL | 15 | 42.2 | 2.30e-11 | 9.70e-13 | 3.67e-18 [3.88e-18] | f=1.0 all w=exact |
| Hamming [31,26,3] | this-work-pZL | 15 | 35.7 | 1.82e-12 | 5.51e-14 | 3.21e-17 [3.50e-17] | f=1.0 all w=exact |
| Hamming [31,26,3] | paper-pZL | 15 | 35.7 | 1.95e-11 | 8.21e-13 | 3.21e-17 [3.50e-17] | f=1.0 all w=exact |
| ext. Hamming [16,11,4] | this-work-pZL | 15 | 44.8 | 2.72e-12 | 9.27e-14 | 1.24e-22 [1.53e-22] | f=1.0 all w=exact |
| ext. Hamming [16,11,4] | paper-pZL | 17 | 51.0 | 1.03e-12 | 4.34e-14 | 2.04e-22 [2.52e-22] | f=1.0 all w=exact (transferred) |
| Hamming [63,57,3] | this-work-pZL | 15 | 32.6 | 1.48e-12 | 4.06e-14 | 2.38e-16 [2.59e-16] | f=1.0 all w=exact |
| Hamming [63,57,3] | paper-pZL | 15 | 32.6 | 1.78e-11 | 7.49e-13 | 2.38e-16 [2.59e-16] | f=1.0 all w=exact |

### p_Z = 1e-2, eta = 1e6: composition of the lowest reachable p_L

At each floor: phase flips (cannot be flagged), bit flips from sets of flagged events only (need >= d events forming a logical: the code's distance) and bit flips involving unflagged errors (fraction 1 - f).

| code | flags | phase model | floor p_L | d_Z | p_ZL share | flagged-only share | unflagged share |
|---|---|---|---|---|---|---|---|
| [15,6,5] | none | this-work-pZL | 4.15e-10 | 67 | 0.22 | 0.00 | 0.78 |
| [15,6,5] | f=0.5 all w=exact | this-work-pZL | 1.34e-10 | 71 | 0.29 | 0.00 | 0.71 |
| [15,6,5] | f=0.8 all w=exact | this-work-pZL | 2.82e-11 | 79 | 0.25 | 0.00 | 0.75 |
| [15,6,5] | f=0.9 all w=exact | this-work-pZL | 9.64e-12 | 85 | 0.21 | 0.00 | 0.79 |
| [15,6,5] | f=0.9 all w=4096 | this-work-pZL | 6.84e-11 | 75 | 0.24 | 0.00 | 0.75 |
| [15,6,5] | f=0.9 idle w=exact | this-work-pZL | 1.10e-10 | 73 | 0.23 | 0.00 | 0.77 |
| [15,6,5] | f=0.95 all w=exact | this-work-pZL | 3.26e-12 | 91 | 0.17 | 0.00 | 0.83 |
| [15,6,5] | f=0.99 all w=exact | this-work-pZL | 3.19e-13 | 101 | 0.21 | 0.02 | 0.77 |
| [15,6,5] | f=0.99 all w=1 | this-work-pZL | 1.89e-13 | 103 | 0.24 | 0.00 | 0.76 |
| [15,6,5] | f=0.99 all w=1024 | this-work-pZL | 7.44e-12 | 85 | 0.27 | 0.34 | 0.39 |
| [15,6,5] | f=0.99 all w=16 | this-work-pZL | 1.54e-12 | 95 | 0.16 | 0.00 | 0.84 |
| [15,6,5] | f=0.99 all w=256 | this-work-pZL | 6.83e-12 | 85 | 0.29 | 0.18 | 0.53 |
| [15,6,5] | f=0.99 all w=4 | this-work-pZL | 2.67e-13 | 103 | 0.17 | 0.00 | 0.83 |
| [15,6,5] | f=0.99 all w=4096 | this-work-pZL | 1.33e-11 | 83 | 0.23 | 0.56 | 0.21 |
| [15,6,5] | f=0.99 all w=64 | this-work-pZL | 1.52e-12 | 95 | 0.16 | 0.01 | 0.83 |
| [15,6,5] | f=0.99 idle w=exact | this-work-pZL | 9.11e-11 | 73 | 0.28 | 0.00 | 0.72 |
| [15,6,5] | f=0.99 idle w=4096 | this-work-pZL | 1.71e-10 | 71 | 0.23 | 0.00 | 0.77 |
| [15,6,5] | f=0.99 idle+gate w=exact | this-work-pZL | 3.09e-13 | 101 | 0.22 | 0.00 | 0.78 |
| [15,6,5] | f=0.999 all w=exact | this-work-pZL | 2.27e-14 | 113 | 0.24 | 0.67 | 0.09 |
| [15,6,5] | f=1.0 all w=exact | this-work-pZL | 2.08e-14 | 113 | 0.27 | 0.73 | 0.00 |
| [15,6,5] | f=1.0 idle w=exact | this-work-pZL | 8.48e-11 | 75 | 0.20 | 0.00 | 0.80 |
| [15,6,5] 2 anc | none | this-work-pZL | 1.79e-10 | 73 | 0.28 | 0.00 | 0.72 |
| [15,6,5] 2 anc | f=0.5 all w=exact | this-work-pZL | 5.45e-11 | 79 | 0.26 | 0.00 | 0.74 |
| [15,6,5] 2 anc | f=0.8 all w=exact | this-work-pZL | 8.38e-12 | 89 | 0.20 | 0.00 | 0.80 |
| [15,6,5] 2 anc | f=0.9 all w=exact | this-work-pZL | 3.84e-12 | 93 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.9 all w=4096 | this-work-pZL | 4.55e-11 | 81 | 0.20 | 0.66 | 0.14 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | this-work-pZL | 4.86e-11 | 81 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.95 all w=exact | this-work-pZL | 1.63e-12 | 97 | 0.19 | 0.00 | 0.81 |
| [15,6,5] 2 anc | f=0.99 all w=exact | this-work-pZL | 8.60e-14 | 111 | 0.19 | 0.03 | 0.78 |
| [15,6,5] 2 anc | f=0.99 all w=1 | this-work-pZL | 7.71e-14 | 111 | 0.22 | 0.00 | 0.78 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | this-work-pZL | 9.34e-12 | 89 | 0.18 | 0.72 | 0.10 |
| [15,6,5] 2 anc | f=0.99 all w=16 | this-work-pZL | 9.94e-14 | 111 | 0.17 | 0.00 | 0.83 |
| [15,6,5] 2 anc | f=0.99 all w=256 | this-work-pZL | 8.51e-12 | 89 | 0.20 | 0.70 | 0.10 |
| [15,6,5] 2 anc | f=0.99 all w=4 | this-work-pZL | 1.04e-13 | 111 | 0.16 | 0.00 | 0.84 |
| [15,6,5] 2 anc | f=0.99 all w=4096 | this-work-pZL | 2.28e-11 | 83 | 0.27 | 0.68 | 0.05 |
| [15,6,5] 2 anc | f=0.99 all w=64 | this-work-pZL | 2.42e-13 | 105 | 0.24 | 0.09 | 0.67 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | this-work-pZL | 3.90e-11 | 81 | 0.24 | 0.00 | 0.76 |
| [15,6,5] 2 anc | f=0.99 idle w=4096 | this-work-pZL | 8.05e-11 | 77 | 0.27 | 0.00 | 0.73 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | this-work-pZL | 1.07e-13 | 109 | 0.24 | 0.00 | 0.76 |
| [15,6,5] 2 anc | f=0.999 all w=exact | this-work-pZL | 4.19e-14 | 113 | 0.26 | 0.07 | 0.67 |
| [15,6,5] 2 anc | f=1.0 all w=exact | this-work-pZL | 7.42e-15 | 121 | 0.28 | 0.72 | 0.00 |
| [15,6,5] 2 anc | f=1.0 idle w=exact | this-work-pZL | 3.28e-11 | 83 | 0.19 | 0.00 | 0.81 |
| [15,9,3] | none | this-work-pZL | 1.25e-08 | 49 | 0.25 | 0.00 | 0.75 |
| [15,9,3] | f=0.5 all w=exact | this-work-pZL | 5.58e-09 | 53 | 0.23 | 0.00 | 0.77 |
| [15,9,3] | f=0.8 all w=exact | this-work-pZL | 2.14e-09 | 59 | 0.16 | 0.00 | 0.84 |
| [15,9,3] | f=0.9 all w=exact | this-work-pZL | 1.11e-09 | 61 | 0.20 | 0.00 | 0.79 |
| [15,9,3] | f=0.9 all w=4096 | this-work-pZL | 2.37e-09 | 57 | 0.23 | 0.26 | 0.51 |
| [15,9,3] | f=0.9 idle w=exact | this-work-pZL | 5.22e-09 | 55 | 0.16 | 0.00 | 0.84 |
| [15,9,3] | f=0.95 all w=exact | this-work-pZL | 6.42e-10 | 65 | 0.15 | 0.01 | 0.84 |
| [15,9,3] | f=0.99 all w=exact | this-work-pZL | 1.65e-10 | 71 | 0.16 | 0.05 | 0.79 |
| [15,9,3] | f=0.99 all w=1 | this-work-pZL | 1.98e-10 | 69 | 0.20 | 0.12 | 0.67 |
| [15,9,3] | f=0.99 all w=1024 | this-work-pZL | 9.23e-10 | 63 | 0.16 | 0.68 | 0.17 |
| [15,9,3] | f=0.99 all w=16 | this-work-pZL | 1.80e-10 | 71 | 0.15 | 0.16 | 0.70 |
| [15,9,3] | f=0.99 all w=256 | this-work-pZL | 7.88e-10 | 63 | 0.19 | 0.64 | 0.18 |
| [15,9,3] | f=0.99 all w=4 | this-work-pZL | 2.03e-10 | 69 | 0.20 | 0.13 | 0.67 |
| [15,9,3] | f=0.99 all w=4096 | this-work-pZL | 1.26e-09 | 61 | 0.18 | 0.68 | 0.14 |
| [15,9,3] | f=0.99 all w=64 | this-work-pZL | 3.66e-10 | 67 | 0.17 | 0.49 | 0.34 |
| [15,9,3] | f=0.99 idle w=exact | this-work-pZL | 4.63e-09 | 55 | 0.18 | 0.00 | 0.82 |
| [15,9,3] | f=0.99 idle w=4096 | this-work-pZL | 5.64e-09 | 53 | 0.23 | 0.04 | 0.74 |
| [15,9,3] | f=0.99 idle+gate w=exact | this-work-pZL | 1.75e-10 | 71 | 0.15 | 0.17 | 0.68 |
| [15,9,3] | f=0.999 all w=exact | this-work-pZL | 3.86e-11 | 77 | 0.19 | 0.34 | 0.47 |
| [15,9,3] | f=1.0 all w=exact | this-work-pZL | 1.96e-11 | 79 | 0.24 | 0.76 | 0.00 |
| [15,9,3] | f=1.0 idle w=exact | this-work-pZL | 4.34e-09 | 55 | 0.19 | 0.00 | 0.81 |
| Hamming [15,11,3] | none | this-work-pZL | 1.14e-08 | 49 | 0.22 | 0.00 | 0.78 |
| Hamming [15,11,3] | f=0.9 all w=exact | this-work-pZL | 1.49e-09 | 59 | 0.19 | 0.00 | 0.81 |
| Hamming [15,11,3] | f=0.9 idle w=exact | this-work-pZL | 5.70e-09 | 53 | 0.18 | 0.00 | 0.82 |
| Hamming [15,11,3] | f=0.99 all w=exact | this-work-pZL | 2.17e-10 | 69 | 0.15 | 0.03 | 0.82 |
| Hamming [15,11,3] | f=0.99 all w=1024 | this-work-pZL | 1.90e-09 | 57 | 0.23 | 0.69 | 0.08 |
| Hamming [15,11,3] | f=0.99 all w=64 | this-work-pZL | 4.26e-10 | 65 | 0.18 | 0.38 | 0.44 |
| Hamming [15,11,3] | f=0.99 idle w=exact | this-work-pZL | 4.80e-09 | 53 | 0.22 | 0.00 | 0.78 |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | this-work-pZL | 2.03e-10 | 69 | 0.16 | 0.01 | 0.83 |
| Hamming [15,11,3] | f=1.0 all w=exact | this-work-pZL | 1.56e-11 | 79 | 0.25 | 0.75 | 0.00 |
| [15,6,5] | none | paper-pZL | 6.27e-11 | 47 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.5 all w=exact | paper-pZL | 1.72e-11 | 49 | 0.13 | 0.00 | 0.87 |
| [15,6,5] | f=0.8 all w=exact | paper-pZL | 3.21e-12 | 53 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.9 all w=exact | paper-pZL | 9.93e-13 | 55 | 0.11 | 0.00 | 0.89 |
| [15,6,5] | f=0.9 all w=4096 | paper-pZL | 7.64e-12 | 51 | 0.11 | 0.00 | 0.89 |
| [15,6,5] | f=0.9 idle w=exact | paper-pZL | 1.41e-11 | 49 | 0.16 | 0.00 | 0.84 |
| [15,6,5] | f=0.95 all w=exact | paper-pZL | 2.88e-13 | 57 | 0.15 | 0.00 | 0.85 |
| [15,6,5] | f=0.99 all w=exact | paper-pZL | 2.11e-14 | 63 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.99 all w=1 | paper-pZL | 1.32e-14 | 63 | 0.16 | 0.00 | 0.84 |
| [15,6,5] | f=0.99 all w=1024 | paper-pZL | 4.60e-13 | 55 | 0.25 | 0.13 | 0.62 |
| [15,6,5] | f=0.99 all w=16 | paper-pZL | 1.66e-13 | 59 | 0.09 | 0.00 | 0.91 |
| [15,6,5] | f=0.99 all w=256 | paper-pZL | 5.82e-13 | 55 | 0.20 | 0.05 | 0.75 |
| [15,6,5] | f=0.99 all w=4 | paper-pZL | 2.18e-14 | 63 | 0.09 | 0.00 | 0.91 |
| [15,6,5] | f=0.99 all w=4096 | paper-pZL | 8.29e-13 | 55 | 0.14 | 0.51 | 0.35 |
| [15,6,5] | f=0.99 all w=64 | paper-pZL | 1.62e-13 | 59 | 0.09 | 0.00 | 0.90 |
| [15,6,5] | f=0.99 idle w=exact | paper-pZL | 1.15e-11 | 49 | 0.20 | 0.00 | 0.80 |
| [15,6,5] | f=0.99 idle w=4096 | paper-pZL | 2.43e-11 | 47 | 0.26 | 0.00 | 0.74 |
| [15,6,5] | f=0.99 idle+gate w=exact | paper-pZL | 2.13e-14 | 63 | 0.10 | 0.00 | 0.90 |
| [15,6,5] | f=0.999 all w=exact | paper-pZL | 5.65e-16 | 69 | 0.18 | 0.40 | 0.41 |
| [15,6,5] | f=1.0 all w=exact | paper-pZL | 3.32e-16 | 71 | 0.11 | 0.89 | 0.00 |
| [15,6,5] | f=1.0 idle w=exact | paper-pZL | 1.07e-11 | 49 | 0.22 | 0.00 | 0.78 |
| [15,6,5] 2 anc | none | paper-pZL | 2.06e-11 | 49 | 0.12 | 0.00 | 0.88 |
| [15,6,5] 2 anc | f=0.5 all w=exact | paper-pZL | 6.03e-12 | 51 | 0.15 | 0.00 | 0.85 |
| [15,6,5] 2 anc | f=0.8 all w=exact | paper-pZL | 8.11e-13 | 55 | 0.15 | 0.00 | 0.85 |
| [15,6,5] 2 anc | f=0.9 all w=exact | paper-pZL | 3.23e-13 | 57 | 0.14 | 0.00 | 0.86 |
| [15,6,5] 2 anc | f=0.9 all w=4096 | paper-pZL | 4.62e-12 | 51 | 0.20 | 0.74 | 0.06 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | paper-pZL | 5.06e-12 | 51 | 0.18 | 0.00 | 0.82 |
| [15,6,5] 2 anc | f=0.95 all w=exact | paper-pZL | 1.26e-13 | 59 | 0.13 | 0.00 | 0.87 |
| [15,6,5] 2 anc | f=0.99 all w=exact | paper-pZL | 5.27e-15 | 65 | 0.15 | 0.00 | 0.84 |
| [15,6,5] 2 anc | f=0.99 all w=1 | paper-pZL | 4.64e-15 | 65 | 0.17 | 0.00 | 0.83 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | paper-pZL | 9.07e-13 | 55 | 0.13 | 0.78 | 0.09 |
| [15,6,5] 2 anc | f=0.99 all w=16 | paper-pZL | 5.58e-15 | 65 | 0.14 | 0.00 | 0.86 |
| [15,6,5] 2 anc | f=0.99 all w=256 | paper-pZL | 8.30e-13 | 55 | 0.15 | 0.76 | 0.09 |
| [15,6,5] 2 anc | f=0.99 all w=4 | paper-pZL | 7.04e-15 | 65 | 0.11 | 0.00 | 0.89 |
| [15,6,5] 2 anc | f=0.99 all w=4096 | paper-pZL | 2.13e-12 | 53 | 0.16 | 0.80 | 0.04 |
| [15,6,5] 2 anc | f=0.99 all w=64 | paper-pZL | 1.00e-14 | 63 | 0.22 | 0.01 | 0.77 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | paper-pZL | 3.99e-12 | 51 | 0.23 | 0.00 | 0.77 |
| [15,6,5] 2 anc | f=0.99 idle w=4096 | paper-pZL | 8.69e-12 | 51 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | paper-pZL | 5.91e-15 | 65 | 0.14 | 0.00 | 0.86 |
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
