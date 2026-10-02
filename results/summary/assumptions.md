
## Assumptions of the flag model and their measured effect (phase flips: this-work-pZL)

p_XL per round per logical qubit at d_Z = 15, p_X = 1e-9 (stratified estimate), and the minimum overhead at p_Z = 1e-3, eta = 1e6, 1e-12 over [15,9,3], [15,6,5] (1 and 2 ancillas).


### flag classes (which locations raise flags)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| idle | exact | 0.99 | 0 | erasure | 8.69e-13 [8.0e-13, 9.6e-13] | 5.57e-17 [2.3e-17, 4.1e-14] | - | 51.6 ([15,9,3], d=15) |
| idle+gate | exact | 0.99 | 0 | erasure | 1.23e-14 [4.9e-15, 3.1e-14] | 3.15e-20 [5.6e-21, 2.7e-14] | 1.49e-22 [5.6e-23, 2.0e-14] (transferred) | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | 2.06e-22 [9.5e-23, 2.1e-14] | - | 51.6 ([15,9,3], d=15) |
| idle | exact | 0.9 | 0 | erasure | 1.05e-12 [9.7e-13, 1.2e-12] | 3.99e-17 [1.4e-17, 4.4e-14] | - | 77.3 ([15,6,5], d=15) |
| idle+gate | exact | 0.9 | 0 | erasure | 1.68e-13 [1.5e-13, 1.8e-13] | 3.88e-18 [1.1e-18, 1.4e-14] | 7.87e-19 [1.6e-19, 9.0e-15] (transferred) | 51.6 ([15,9,3], d=15) |
| all | exact | 0.9 | 0 | erasure | 1.61e-13 [1.5e-13, 1.8e-13] | 5.42e-18 [1.9e-18, 1.3e-14] | - | 51.6 ([15,9,3], d=15) |

### timing window (ticks; one inner round = 4, one outer round ~600-1100)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | 2.06e-22 [9.5e-23, 2.1e-14] | - | 51.6 ([15,9,3], d=15) |
| all | 1 | 0.99 | 0 | erasure | 1.59e-14 [7.9e-15, 7.5e-14] | 4.64e-22 [2.9e-22, 8.7e-14] | 5.11e-23 [1.9e-23, 9.1e-14] | 51.6 ([15,9,3], d=15) |
| all | 4 | 0.99 | 0 | erasure | 3.15e-14 [1.9e-14, 9.5e-14] | 1.93e-20 [3.5e-21, 8.5e-14] | 5.48e-23 [2.3e-23, 9.1e-14] | 51.6 ([15,9,3], d=15) |
| all | 16 | 0.99 | 0 | erasure | 2.48e-14 [8.4e-15, 9.2e-14] | 3.07e-22 [1.5e-22, 8.7e-14] | 7.30e-21 [1.4e-21, 8.9e-14] | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 0 | erasure | 3.52e-14 [1.6e-14, 8.4e-14] | 3.84e-20 [1.1e-20, 8.5e-14] | 1.44e-20 [4.0e-21, 8.9e-14] | 51.6 ([15,9,3], d=15) |
| all | 256 | 0.99 | 0 | erasure | 1.48e-13 [1.1e-13, 2.1e-13] | 5.75e-20 [2.0e-20, 8.5e-14] | 1.28e-16 [2.3e-17, 8.7e-14] | 51.6 ([15,9,3], d=15) |
| all | 1024 | 0.99 | 0 | erasure | 1.40e-13 [9.9e-14, 2.0e-13] | 3.50e-22 [1.8e-22, 8.7e-14] | 3.77e-20 [6.8e-21, 8.9e-14] | 51.6 ([15,9,3], d=15) |
| all | 4096 | 0.99 | 0 | erasure | 1.67e-13 [1.2e-13, 2.3e-13] | - | 1.54e-20 [4.3e-21, 8.9e-14] | 51.6 ([15,9,3], d=15) |
| idle | exact | 0.99 | 0 | erasure | 8.69e-13 [8.0e-13, 9.6e-13] | 5.57e-17 [2.3e-17, 4.1e-14] | - | 51.6 ([15,9,3], d=15) |
| idle | 64 | 0.99 | 0 | erasure | 9.73e-13 [9.0e-13, 1.1e-12] | 6.81e-17 [2.8e-17, 8.1e-14] | 1.30e-17 [4.4e-18, 8.5e-14] | 77.3 ([15,6,5], d=15) |
| idle | 4096 | 0.99 | 0 | erasure | 1.14e-12 [1.0e-12, 1.3e-12] | - | 3.43e-17 [8.3e-18, 8.5e-14] | 82.2 ([15,6,5] 2 anc, d=15) |

### event model: erasure (X with prob. 1/2) vs heralded X

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| idle | exact | 0.99 | 0 | erasure | 8.69e-13 [8.0e-13, 9.6e-13] | 5.57e-17 [2.3e-17, 4.1e-14] | - | 51.6 ([15,9,3], d=15) |
| idle | exact | 0.99 | 0 | herald | - | - | - | - |
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | 2.06e-22 [9.5e-23, 2.1e-14] | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 0 | herald | - | - | - | - |
| all | 64 | 0.99 | 0 | erasure | 3.52e-14 [1.6e-14, 8.4e-14] | 3.84e-20 [1.1e-20, 8.5e-14] | 1.44e-20 [4.0e-21, 8.9e-14] | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 0 | herald | - | - | - | - |

### false flags per qubit per tick (f = 0.99, flags on all locations, exact / 64 ticks)

| flags on | window | f | false flags | alternative | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | minimum overhead |
|---|---|---|---|---|---|---|---|---|
| all | exact | 0.99 | 0 | erasure | 2.03e-14 [1.1e-14, 3.8e-14] | 2.06e-22 [9.5e-23, 2.1e-14] | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 1e-10 | erasure | 7.02e-15 [2.5e-15, 8.2e-11] | - | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 1e-08 | erasure | 2.04e-14 [1.1e-14, 7.9e-11] | - | - | 51.6 ([15,9,3], d=15) |
| all | exact | 0.99 | 1e-06 | erasure | 2.50e-14 [1.4e-14, 7.9e-11] | - | - | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 0 | erasure | 3.52e-14 [1.6e-14, 8.4e-14] | 3.84e-20 [1.1e-20, 8.5e-14] | 1.44e-20 [4.0e-21, 8.9e-14] | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 1e-10 | erasure | 1.60e-14 [7.9e-15, 7.9e-11] | - | 7.24e-21 [1.3e-21, 1.7e-10] | 51.6 ([15,9,3], d=15) |
| all | 64 | 0.99 | 1e-08 | erasure | 3.84e-14 [2.4e-14, 7.9e-11] | - | 7.23e-21 [1.3e-21, 1.7e-10] | 51.6 ([15,9,3], d=15) |
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
| none | exact | 0.0 | 4.10e-12 / 1.12e-11 | 5.73e-16 / - | - / - |
| idle | exact | 0.99 | 1.18e-12 / 1.62e-12 | 9.11e-17 / - | - / - |
| all | exact | 0.9 | 2.18e-13 / - | 8.80e-18 / - | - / - |
| all | exact | 0.99 | 2.75e-14 / - | 3.39e-22 / - | - / - |
| all | 64 | 0.99 | 4.78e-14 / - | 6.23e-20 / - | 4.16e-20 / - |
| all | 1024 | 0.99 | 1.90e-13 / - | 5.94e-22 / - | 2.26e-20 / - |
