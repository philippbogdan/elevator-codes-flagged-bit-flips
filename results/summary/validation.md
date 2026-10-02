
## Held-out check of the stratified estimator under flags

Same configuration, two estimators: direct Monte Carlo (all events sampled) and the stratified estimator used at p_X = 1e-9 (truncated at a+b <= kmax).  Per shot, 95% intervals.

| code | p_X | f | flags on | window | direct P_fail [95% CI] | stratified [95% CI] | agree |
|---|---|---|---|---|---|---|---|

0 of 0 configurations agree within the 95% intervals.


### The p_X = 1e-9 estimates predicting held-out direct samples

Stratum failure fractions measured at p_X = 1e-9 (the numbers behind the overheads) with exact intensities at the held-out p_X; the upper bound adds the truncated strata.

| code | p_X | f | flags on | window | direct P_fail [95% CI] | predicted from p_X = 1e-9 [lo, hi] | inside |
|---|---|---|---|---|---|---|---|

0 of 0 held-out direct-sampling points are inside the predicted interval.

