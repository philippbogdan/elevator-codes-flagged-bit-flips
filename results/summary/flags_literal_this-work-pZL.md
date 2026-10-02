
## Flagged bit flips, p_X = 1e-09 (reading: idle=edge,cnot,op); phase flips from this-work-pZL

### Minimum qubit overhead at p_Z = 1e-3, eta = 1e6, target 1e-12 per round per logical qubit

Central estimate (conservative: bit-flip rate at its 95% upper bound) and the chosen code/d_Z.

Per code: minimum overhead ('n.r.' = simulated but not reaching the target, '-' = not simulated), then p_XL at d_Z = 15 per round per logical qubit [95% CI] (sampled logical failures behind it); these p_X = 1e-9 values lie below direct-sampling reach and come from the stratified estimator (model: Poisson strata, held-out check in validation.md).

| flags on | window (ticks) | f | false flags /qubit/tick | best overhead (central) | code, d_Z | p_XL | best (conservative) | [15,9,3] | [15,6,5] | [15,6,5] 2 anc | [15,9,3] p_XL(d=15) | [15,6,5] p_XL(d=15) | [15,6,5] 2 anc p_XL(d=15) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | exact | 0.0 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| all | exact | 0.9 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | 82.2 (d=15) | - | - | - |
| all | exact | 0.99 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | 82.2 (d=15) | - | - | - |
| all | exact | 1.0 | 0 | 51.6 | [15,9,3], 15 | 1.70e-17 | 51.6 | 51.6 (d=15) | 77.3 (d=15) | 82.2 (d=15) | - | - | - |
| all | 64 | 0.99 | 0 | 51.6 | [15,9,3], 15 | 7.60e-14 | 51.6 | 51.6 (d=15) | 77.3 (d=15) | 82.2 (d=15) | - | - | - |
| all | 1024 | 0.99 | 0 | 51.6 | [15,9,3], 15 | 3.00e-13 | 51.6 | 51.6 (d=15) | 77.3 (d=15) | 82.2 (d=15) | - | - | - |
| idle | exact | 0.5 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 0.8 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 0.9 | 0 | 77.3 | [15,6,5], 15 | 9.44e-17 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 0.95 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 0.98 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 0.99 | 0 | 77.3 | [15,6,5], 15 | 5.96e-17 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 0.995 | 0 | 77.3 | [15,6,5], 15 | 1.10e-15 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
| idle | exact | 1.0 | 0 | 77.3 | [15,6,5], 15 | 5.91e-17 | 77.3 | n.r. | 77.3 (d=15) | - | - | - | - |
