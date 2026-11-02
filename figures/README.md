# Figures from the saved evidence

The figures show the modelled qubit saving, the flag requirements behind it and the dependence on the phase model at two noise levels. [`figures.py`](../scripts/figures.py) rebuilds PNG and SVG versions from the included circuits and results after `analyze.py` has refreshed the summary; [REPRODUCE.md](../REPRODUCE.md) gives the common command.

| Figure | What it shows and where to check it |
|---|---|
| [Memory saving](memory-saving.png), [SVG](memory-saving.svg) | Equal logical storage using the actual qubit layouts from `elevator/circuits.py`. The selected codes and counts are in [headline.md](../results/summary/headline.md). Lines show CNOT connections used during a round, not simultaneous gates or physical device dimensions. |
| [Flag requirements](flag-requirements.png), [SVG](flag-requirements.svg) | Exact-timing efficiencies on the left and timing windows at 99% efficiency on the right, from the `paper-pZL` headline selections. Deep blue is paper codes; amber includes Hamming, whose counts assume the published phase formula scales to those codes. Circles show central all-location estimates, both idle-only diamonds are centred at 90%, and upward stems end at counts selected using the upper bit-flip bound. |
| [Noise and target](noise-and-target.png), [SVG](noise-and-target.svg) | Four paper-code selections at a fixed target of 10^-12 errors per inner round per logical qubit, with 99% exact all-location flags, bias 10^6 and no false alarms. Two phase models are compared at each noise level using the upper bit-flip bound. All bars are graphite, with direct model labels and a shared scale from 0 to 600 physical qubits per logical qubit. |

In figure 2, the neutral circle and diamond in the legend identify flag coverage by shape; their colour does not identify a code set. The all-location circles are slightly offset horizontally to keep coincident points visible, while both idle-only diamonds sit exactly on the 90% tick. Connecting segments guide the eye between tested settings on categorical axes. The upper stems can select a different code or distance from the central points.

## Fixed-target selections

Each bar in figure 3 gives the smallest physical-qubit count per logical qubit among evaluated candidates whose upper bit-flip rate plus modelled phase-flip rate is at most 10^-12. The candidates are [15,9,3] with one logical ancilla and [15,6,5] with one or two; Hamming codes are outside this comparison. The odd-distance scans run from 13 to 61 at p_Z = 10^-3 and from 13 to 301 at p_Z = 10^-2, including transfers beyond simulated distances. Bias is fixed at 10^6, giving p_X = 10^-9 and 10^-8 respectively.

| p_Z | Phase model | Physical qubits / logical qubit | Code | Logical ancillas per memory | Selected d_Z | Sampled source d_Z |
|---|---|---:|---|---:|---:|---:|
| 10^-3 | Paper phase fits | 58.7 | [15,9,3] | 1 | 17 | 17 |
| 10^-3 | This work's phase model | 51.6 | [15,9,3] | 1 | 15 | 15 |
| 10^-2 | Paper phase fits | 269.3 | [15,6,5] | 1 | 51 | 33 |
| 10^-2 | This work's phase model | 524.2 | [15,6,5] | 2 | 93 | 33 |

Both higher-noise selections transfer bit-flip estimates from sampled d_Z = 33 to the selected distance. The lower-noise pair uses its sampled distances. All four rates are model estimates at a target below direct sampling. Code, distance and ancilla count can change between selections, so the bars compare minima within this scan, without establishing a global optimum or holding the device fixed.

All four bars use 99% exact all-location flags and no false alarms. The 90% setting used in the first figure has no qualifying higher-noise candidate under this work's phase model at this target. Figure 3 therefore shows the dependence on phase-model choice at fixed flag conditions.

The renderer rebuilds the candidate rates using the analysis procedure and checks all 32 central and upper-bound rate floors against `numbers.json["fig2_this_work"]`, along with the counts at the upper-bound floors, before selecting the four bars. Those floor counts need not equal the smallest count at the fixed target. The [rate-floor tables](../results/summary/README.md#noise-and-error-target) retain the broader target evidence, alongside the [paper-model bias reconstruction](../results/summary/fig1_this_work_paper-pZL.md) and [fitted-model reconstruction](../results/summary/fig1_this_work_this-work-pZL.md).

All-location flags include gates, preparation and readout, whose signals are assumed. Exact timing resolves the before/after-CNOT location; a one-layer window does not. Upper-bound selections include bit-flip sampling uncertainty within the model, not uncertainty in the phase model or hardware assumptions. [Methods](../docs/methods.md) gives those limits.
