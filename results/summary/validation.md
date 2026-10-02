
## Held-out check of the stratified estimator under flags

Same configuration, two estimators: direct Monte Carlo (all events sampled) and the stratified estimator used at p_X = 1e-9 (truncated at a+b <= kmax).  Per shot, 95% intervals.

| code | p_X | f | flags on | window | direct P_fail [95% CI] | stratified [95% CI] | agree |
|---|---|---|---|---|---|---|---|
| [15,6,5] | 3e-07 | 1.0 | all | 1024 | 0.000e+00 [0.00e+00, 1.23e-05] | 0.000e+00 [5.69e-23, 1.76e-05] | yes |
| [15,6,5] 2 anc | 3e-07 | 0.9 | all | exact | 0.000e+00 [0.00e+00, 1.14e-05] | 3.497e-08 [1.21e-08, 9.04e-07] | yes |
| [15,9,3] | 3e-07 | 0.9 | all | exact | 5.750e-05 [3.83e-05, 8.63e-05] | 6.841e-05 [6.06e-05, 7.92e-05] | yes |
| [15,9,3] | 3e-07 | 0.99 | idle | exact | 3.375e-04 [2.85e-04, 3.99e-04] | 3.322e-04 [3.08e-04, 3.61e-04] | yes |
| [15,9,3] | 3e-07 | 0.99 | all | 64 | 1.750e-05 [8.48e-06, 3.61e-05] | 1.306e-05 [7.43e-06, 2.67e-05] | yes |

5 of 5 configurations agree within the 95% intervals.


### The p_X = 1e-9 estimates predicting held-out direct samples

Stratum failure fractions measured at p_X = 1e-9 (the numbers behind the overheads) with exact intensities at the held-out p_X; the upper bound adds the truncated strata.

| code | p_X | f | flags on | window | direct P_fail [95% CI] | predicted from p_X = 1e-9 [lo, hi] | inside |
|---|---|---|---|---|---|---|---|
| [15,6,5] | 3e-07 | 1.0 | all | 1024 | 0.000e+00 [0.00e+00, 1.23e-05] | 1.432e-07 [3.93e-08, 2.24e-04] | yes |
| [15,9,3] | 3e-07 | 0.9 | all | exact | 5.750e-05 [3.83e-05, 8.63e-05] | 6.046e-05 [5.17e-05, 1.03e-04] | yes |
| [15,9,3] | 3e-07 | 0.99 | idle | exact | 3.375e-04 [2.85e-04, 3.99e-04] | 3.317e-04 [2.99e-04, 3.85e-04] | yes |
| [15,9,3] | 3e-07 | 0.99 | all | 64 | 1.750e-05 [8.48e-06, 3.61e-05] | 1.144e-05 [5.48e-06, 6.65e-05] | yes |

4 of 4 held-out direct-sampling points are inside the predicted interval.

