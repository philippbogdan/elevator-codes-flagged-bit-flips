
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
| [15,9,3] | this-work-pZL | 15 | 51.6 | 3.17e-12 | 1.12e-13 | 4.81e-18 [5.22e-18] | f=1.0 all w=exact |
| [15,9,3] | paper-pZL | 17 | 58.7 | 1.19e-12 | 4.99e-14 | 7.84e-18 [8.52e-18] | f=1.0 all w=exact (transferred) |
| [15,6,5] | this-work-pZL | 15 | 77.3 | 4.76e-12 | 1.68e-13 | 2.42e-30 [1.74e-26] | f=1.0 all w=exact |
| [15,6,5] | paper-pZL | 17 | 88.0 | 1.78e-12 | 7.49e-14 | 6.86e-30 [4.11e-26] | f=1.0 all w=exact (transferred) |
| [15,6,5] 2 anc | this-work-pZL | 15 | 82.2 | 6.75e-12 | 2.71e-13 | 2.65e-31 [2.19e-27] | f=1.0 all w=exact (transferred) |
| [15,6,5] 2 anc | paper-pZL | 17 | 93.5 | 1.89e-12 | 7.96e-14 | 5.61e-31 [4.09e-27] | f=1.0 all w=exact |
| Hamming [15,11,3] | this-work-pZL | 15 | 42.2 | 2.60e-12 | 9.19e-14 | 2.69e-14 [4.01e-14] | f=0.99 all w=exact |
| Hamming [15,11,3] | paper-pZL | 15 | 42.2 | 2.30e-11 | 9.70e-13 | 2.69e-14 [4.01e-14] | f=0.99 all w=exact |
| Hamming [31,26,3] | this-work-pZL | 15 | 35.7 | 1.78e-12 | 5.51e-14 | 3.21e-17 [3.50e-17] | f=1.0 all w=exact |
| Hamming [31,26,3] | paper-pZL | 15 | 35.7 | 1.95e-11 | 8.21e-13 | 3.21e-17 [3.50e-17] | f=1.0 all w=exact |
| ext. Hamming [16,11,4] | this-work-pZL | 15 | 44.8 | 2.70e-12 | 9.43e-14 | 1.24e-22 [1.53e-22] | f=1.0 all w=exact |
| ext. Hamming [16,11,4] | paper-pZL | 17 | 51.0 | 1.03e-12 | 4.34e-14 | 2.04e-22 [2.52e-22] | f=1.0 all w=exact (transferred) |

### p_Z = 1e-2, eta = 1e6: composition of the lowest reachable p_L

At each floor: phase flips (cannot be flagged), bit flips from sets of flagged events only (need >= d events forming a logical: the code's distance) and bit flips involving unflagged errors (fraction 1 - f).

| code | flags | phase model | floor p_L | d_Z | p_ZL share | flagged-only share | unflagged share |
|---|---|---|---|---|---|---|---|
| [15,6,5] | none | this-work-pZL | 4.18e-10 | 67 | 0.31 | 0.00 | 0.69 |
| [15,6,5] | f=0.99 all w=exact | this-work-pZL | 2.12e-13 | 105 | 0.25 | 0.00 | 0.75 |
| [15,6,5] | f=1.0 all w=exact | this-work-pZL | 2.81e-14 | 115 | 0.24 | 0.76 | 0.00 |
| [15,6,5] 2 anc | none | this-work-pZL | 2.06e-10 | 75 | 0.24 | 0.00 | 0.76 |
| [15,6,5] 2 anc | f=0.9 all w=exact | this-work-pZL | 5.56e-12 | 93 | 0.22 | 0.00 | 0.78 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | this-work-pZL | 3.72e-11 | 83 | 0.25 | 0.00 | 0.75 |
| [15,6,5] 2 anc | f=0.99 all w=exact | this-work-pZL | 9.26e-14 | 115 | 0.15 | 0.00 | 0.85 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | this-work-pZL | 5.84e-12 | 91 | 0.31 | 0.35 | 0.33 |
| [15,6,5] 2 anc | f=0.99 all w=64 | this-work-pZL | 1.40e-13 | 113 | 0.15 | 0.00 | 0.85 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | this-work-pZL | 5.54e-11 | 81 | 0.26 | 0.00 | 0.74 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | this-work-pZL | 1.56e-14 | 121 | 0.26 | 0.00 | 0.74 |
| [15,6,5] 2 anc | f=1.0 all w=exact | this-work-pZL | 2.25e-15 | 131 | 0.24 | 0.76 | 0.00 |
| [15,9,3] | none | this-work-pZL | 1.31e-08 | 51 | 0.19 | 0.00 | 0.81 |
| [15,9,3] | f=0.9 idle w=exact | this-work-pZL | 5.47e-09 | 55 | 0.20 | 0.00 | 0.80 |
| [15,9,3] | f=0.99 all w=exact | this-work-pZL | 1.72e-10 | 73 | 0.14 | 0.03 | 0.83 |
| [15,9,3] | f=0.99 all w=64 | this-work-pZL | 3.89e-10 | 69 | 0.15 | 0.50 | 0.35 |
| [15,9,3] | f=0.99 idle+gate w=exact | this-work-pZL | 1.87e-10 | 71 | 0.20 | 0.16 | 0.64 |
| [15,9,3] | f=1.0 all w=exact | this-work-pZL | 2.16e-11 | 81 | 0.22 | 0.78 | 0.00 |
| Hamming [15,11,3] | none | this-work-pZL | 1.22e-08 | 49 | 0.26 | 0.00 | 0.74 |
| Hamming [15,11,3] | f=0.9 all w=exact | this-work-pZL | 1.58e-09 | 61 | 0.16 | 0.00 | 0.84 |
| Hamming [15,11,3] | f=0.9 idle w=exact | this-work-pZL | 5.76e-09 | 53 | 0.24 | 0.00 | 0.76 |
| Hamming [15,11,3] | f=0.99 all w=exact | this-work-pZL | 2.29e-10 | 69 | 0.20 | 0.00 | 0.80 |
| Hamming [15,11,3] | f=0.99 all w=1024 | this-work-pZL | 2.00e-09 | 59 | 0.19 | 0.72 | 0.09 |
| Hamming [15,11,3] | f=0.99 all w=64 | this-work-pZL | 4.51e-10 | 67 | 0.16 | 0.39 | 0.45 |
| Hamming [15,11,3] | f=0.99 idle w=exact | this-work-pZL | 5.07e-09 | 55 | 0.18 | 0.00 | 0.82 |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | this-work-pZL | 2.16e-10 | 71 | 0.14 | 0.01 | 0.85 |
| Hamming [15,11,3] | f=1.0 all w=exact | this-work-pZL | 1.72e-11 | 81 | 0.23 | 0.77 | 0.00 |
| [15,6,5] | none | paper-pZL | 5.65e-11 | 47 | 0.11 | 0.00 | 0.89 |
| [15,6,5] | f=0.99 all w=exact | paper-pZL | 8.37e-15 | 63 | 0.25 | 0.00 | 0.75 |
| [15,6,5] | f=1.0 all w=exact | paper-pZL | 3.47e-16 | 69 | 0.29 | 0.71 | 0.00 |
| [15,6,5] 2 anc | none | paper-pZL | 2.19e-11 | 49 | 0.11 | 0.00 | 0.89 |
| [15,6,5] 2 anc | f=0.9 all w=exact | paper-pZL | 4.39e-13 | 57 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.9 idle w=exact | paper-pZL | 3.17e-12 | 53 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.99 all w=exact | paper-pZL | 6.97e-15 | 65 | 0.12 | 0.00 | 0.88 |
| [15,6,5] 2 anc | f=0.99 all w=1024 | paper-pZL | 1.73e-13 | 57 | 0.26 | 0.22 | 0.52 |
| [15,6,5] 2 anc | f=0.99 all w=64 | paper-pZL | 8.30e-15 | 65 | 0.10 | 0.00 | 0.90 |
| [15,6,5] 2 anc | f=0.99 idle w=exact | paper-pZL | 5.44e-12 | 51 | 0.17 | 0.00 | 0.83 |
| [15,6,5] 2 anc | f=0.99 idle+gate w=exact | paper-pZL | 2.49e-16 | 71 | 0.16 | 0.00 | 0.84 |
| [15,6,5] 2 anc | f=1.0 all w=exact | paper-pZL | 8.06e-18 | 77 | 0.24 | 0.76 | 0.00 |
| [15,9,3] | none | paper-pZL | 4.73e-09 | 37 | 0.13 | 0.00 | 0.87 |
| [15,9,3] | f=0.9 idle w=exact | paper-pZL | 1.82e-09 | 39 | 0.13 | 0.00 | 0.87 |
| [15,9,3] | f=0.99 all w=exact | paper-pZL | 4.30e-11 | 47 | 0.10 | 0.01 | 0.90 |
| [15,9,3] | f=0.99 all w=64 | paper-pZL | 1.06e-10 | 45 | 0.11 | 0.53 | 0.36 |
| [15,9,3] | f=0.99 idle+gate w=exact | paper-pZL | 4.48e-11 | 47 | 0.09 | 0.08 | 0.82 |
| [15,9,3] | f=1.0 all w=exact | paper-pZL | 2.25e-12 | 53 | 0.09 | 0.91 | 0.00 |
| Hamming [15,11,3] | none | paper-pZL | 4.46e-09 | 37 | 0.12 | 0.00 | 0.88 |
| Hamming [15,11,3] | f=0.9 all w=exact | paper-pZL | 4.82e-10 | 41 | 0.14 | 0.00 | 0.86 |
| Hamming [15,11,3] | f=0.9 idle w=exact | paper-pZL | 1.97e-09 | 39 | 0.10 | 0.00 | 0.90 |
| Hamming [15,11,3] | f=0.99 all w=exact | paper-pZL | 6.03e-11 | 45 | 0.16 | 0.00 | 0.84 |
| Hamming [15,11,3] | f=0.99 all w=1024 | paper-pZL | 6.20e-10 | 41 | 0.11 | 0.80 | 0.09 |
| Hamming [15,11,3] | f=0.99 all w=64 | paper-pZL | 1.29e-10 | 45 | 0.07 | 0.44 | 0.49 |
| Hamming [15,11,3] | f=0.99 idle w=exact | paper-pZL | 1.70e-09 | 39 | 0.11 | 0.00 | 0.89 |
| Hamming [15,11,3] | f=0.99 idle+gate w=exact | paper-pZL | 5.88e-11 | 45 | 0.16 | 0.00 | 0.84 |
| Hamming [15,11,3] | f=1.0 all w=exact | paper-pZL | 1.77e-12 | 53 | 0.10 | 0.90 | 0.00 |
