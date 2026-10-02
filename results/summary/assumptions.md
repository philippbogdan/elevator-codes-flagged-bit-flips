
## Assumptions of the flag model and their measured effect (phase flips: this-work-pZL)

p_XL per round per logical qubit at d_Z = 15, p_X = 1e-9 (stratified estimate), and the minimum overhead at p_Z = 1e-3, eta = 1e6, 1e-12 over [15,9,3], [15,6,5] (1 and 2 ancillas).


### flag classes (which locations raise flags)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| idle | exact | 0.99 | 0 | erasure | 8.69e-13 [8.0e-13, 9.6e-13] | - | - | 51.6 ([15,9,3], d=15) |
| idle+gate | exact | 0.99 | 0 | erasure | 1.23e-14 [4.9e-15, 3.1e-14] | - | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | - | - | 51.6 ([15,9,3], d=15) |
| idle | exact | 0.9 | 0 | erasure | 1.05e-12 [9.7e-13, 1.2e-12] | 3.99e-17 [1.4e-17, 4.4e-14] | - | 77.3 ([15,6,5], d=15) |
| idle+gate | exact | 0.9 | 0 | erasure | 1.68e-13 [1.5e-13, 1.8e-13] | - | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.9 | 0 | erasure | 1.61e-13 [1.5e-13, 1.8e-13] | - | - | 51.6 ([15,9,3], d=15) |

### timing window (ticks; one inner round = 4, one outer round ~600-1100)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | - | - | 51.6 ([15,9,3], d=15) |
| all | 1 | 0.99 | 0 | erasure | 1.59e-14 [7.9e-15, 7.5e-14] | - | 1.30e-22 [7.3e-23, 3.2e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 4 | 0.99 | 0 | erasure | 3.15e-14 [1.9e-14, 9.5e-14] | - | 7.26e-21 [1.3e-21, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 16 | 0.99 | 0 | erasure | 2.48e-14 [8.4e-15, 9.2e-14] | - | 7.22e-21 [1.3e-21, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 0 | erasure | 3.52e-14 [1.6e-14, 8.4e-14] | - | 2.87e-20 [1.1e-20, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 256 | 0.99 | 0 | erasure | 1.48e-13 [1.1e-13, 2.1e-13] | - | 7.27e-21 [1.3e-21, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 1024 | 0.99 | 0 | erasure | 1.40e-13 [9.9e-14, 2.0e-13] | - | 1.54e-20 [4.3e-21, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 4096 | 0.99 | 0 | erasure | 1.67e-13 [1.2e-13, 2.3e-13] | - | 4.53e-20 [9.7e-21, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| idle | exact | 0.99 | 0 | erasure | 8.69e-13 [8.0e-13, 9.6e-13] | - | - | 51.6 ([15,9,3], d=15) |
| idle | 64 | 0.99 | 0 | erasure | 9.73e-13 [9.0e-13, 1.1e-12] | - | 1.21e-17 [7.4e-18, 5.2e-14] (transferred) | 82.2 ([15,6,5] 2 anc, d=15) |
| idle | 4096 | 0.99 | 0 | erasure | 1.14e-12 [1.0e-12, 1.3e-12] | - | 3.09e-17 [8.0e-18, 5.2e-14] (transferred) | 82.2 ([15,6,5] 2 anc, d=15) |

### event model: erasure (X with prob. 1/2) vs heralded X

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| idle | exact | 0.99 | 0 | erasure | 8.69e-13 [8.0e-13, 9.6e-13] | - | - | 51.6 ([15,9,3], d=15) |
| idle | exact | 0.99 | 0 | herald | - | - | - | - |
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | - | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 0 | herald | - | - | - | - |
| all | 64 | 0.99 | 0 | erasure | 3.52e-14 [1.6e-14, 8.4e-14] | - | 2.87e-20 [1.1e-20, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 0 | herald | - | - | - | - |

### false flags per qubit per tick (f = 0.99, flags on all locations, exact / 64 ticks)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | - | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 1e-10 | erasure | - | - | - | 93.5 ([15,6,5] 2 anc, d=17) |
| all | exact | 0.99 | 1e-08 | erasure | - | - | - | 93.5 ([15,6,5] 2 anc, d=17) |
| all | exact | 0.99 | 1e-06 | erasure | - | - | - | 93.5 ([15,6,5] 2 anc, d=17) |
| all | 64 | 0.99 | 0 | erasure | 3.52e-14 [1.6e-14, 8.4e-14] | - | 2.87e-20 [1.1e-20, 3.1e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 1e-10 | erasure | - | - | 7.24e-21 [1.3e-21, 1.7e-10] | 82.2 ([15,6,5] 2 anc, d=15) |
| all | 64 | 0.99 | 1e-08 | erasure | - | - | 7.23e-21 [1.3e-21, 1.7e-10] | 82.2 ([15,6,5] 2 anc, d=15) |
| all | 64 | 0.99 | 1e-06 | erasure | - | - | 7.92e-23 [3.6e-23, 1.8e-10] | 82.2 ([15,6,5] 2 anc, d=15) |

### false flags at the operating point of arXiv:2607.01375 (f = 0.8-0.9, windows 4-16 ticks)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| idle | 4 | 0.8 | 1e-09 | erasure | - | - | - | - |
| idle | 4 | 0.8 | 1e-07 | erasure | - | - | - | - |
| idle | 4 | 0.8 | 1e-06 | erasure | - | - | - | - |
| all | 4 | 0.8 | 1e-09 | erasure | - | - | - | - |
| all | 4 | 0.8 | 1e-07 | erasure | - | - | - | - |
| all | 4 | 0.8 | 1e-06 | erasure | - | - | - | - |

### idle-noise reading (bit flips at d_Z = 17; the literal reading also raises the phase flips, see REPORT)

| flags on | window | f | [15,9,3] noop / literal | [15,6,5] noop / literal | [15,6,5] 2 anc noop / literal |
|---|---|---|---|---|---|
| none | exact | 0.0 | 4.14e-12 / 1.12e-11 | 5.73e-16 / - | - / - |
| idle | exact | 0.99 | 1.18e-12 / 1.62e-12 | - / - | - / - |
| all | exact | 0.9 | 2.18e-13 / - | - / - | - / - |
| all | exact | 0.99 | 2.75e-14 / - | - / - | - / - |
| all | 64 | 0.99 | 4.78e-14 / - | - / - | 4.16e-20 / - |
| all | 1024 | 0.99 | 1.90e-13 / - | - / - | 2.26e-20 / - |
