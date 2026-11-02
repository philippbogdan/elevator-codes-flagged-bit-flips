# Flagged bit flips cut the modelled quantum-memory qubit count by a third

Quantum memories protect logical qubits using many physical qubits. [Elevator codes](https://arxiv.org/abs/2601.10786v2) combine repetition blocks with an outer code against phase-dominated noise. A flag locates a possible bit-flip event. Stim simulations and a HiGHS decoder predict **one third fewer qubits** with these signals.

The modelled count falls from **88.0 to 58.7** with 90% exact flags everywhere, gates included, and no false alarms, using the paper's phase-flip fits at $`p_Z=10^{-3}`$, bias $`p_Z/p_X=10^6`$ and a target of $`10^{-12}`$ errors per inner round per logical qubit.

![Three graphite [15,6,5] circuit layouts without flags above two deep-blue [15,9,3] layouts with 90% exact all-location flags, all at equal scale. Each memory contains 528 physical qubits including ancillas, and each row stores 18 logical qubits. The rows contain 1,584 and 1,056 physical qubits, labelled 88.0 and 58.7 per logical qubit.](figures/memory-saving.png)

Both rows store 18 logical qubits, using three unflagged [15,6,5] memories in graphite above and two [15,9,3] memories with 90% exact all-location flags in deep blue below. Each memory contains 528 physical qubits including ancillas, giving modelled counts of 88.0 and 58.7 per logical qubit with no false alarms and the paper's phase-flip fits.

Gate flags are unproven; the [cat-qubit proposal](https://arxiv.org/abs/2607.01375v1) covers idle qubits.

Extending the phase-flip formula to Hamming codes gives **35.7 at 99%** and **30.9 with perfect flags**, under the same assumptions. Idle-only flags give no saving with the paper codes and phase fits.

![Two plots of physical qubits per logical qubit, with paper codes in deep blue and a set including Hamming in amber. Left, exact all-location flags give 58.7 for paper codes at the tested 80%, 90%, 99% and 100% settings, while the expanded set reaches 35.7 at 99% and 30.9 at 100%. Both idle-only diamonds are centred on the 90% tick, at 88.0 and 51.0, with the amber all-location circle nearby at 48.0. Right, at 99% efficiency, 1,024- and 4,096-layer windows raise the expanded-set count to 40.6 centrally, with stems up to 48.0 using the upper bit-flip bound.](figures/flag-requirements.png)

Exact-timing efficiencies are shown on the left and timing windows at 99% efficiency on the right, at the headline noise and target with no false alarms and the paper's phase-flip fits. Deep blue denotes paper codes and amber includes Hamming, with circles for central all-location estimates, diamonds centred at 90% for idle-only estimates and upward stems for counts selected using the upper bit-flip bound.

[Headline values](results/summary/headline.md), [efficiency estimates](results/summary/README.md#flag-requirements) and [non-dominated settings](results/summary/README.md#code-selection).

Using this work's phase-flip model instead of the paper's fits, the paper-code count falls from **77.3 physical qubits per logical qubit without flags to 51.6 with 90% exact all-location flags**, gates included. The noise, bias, error target and absence of false alarms are the same as in the headline comparison. [Bias dependence](results/summary/README.md#noise-and-error-target).

![Four graphite horizontal bars on a shared scale from 0 to 600 physical qubits per logical qubit. At p_Z = 10^-3, the paper phase fits select 58.7 and this work's phase model selects 51.6; at p_Z = 10^-2, they select 269.3 and 524.2. Each bar has a direct model label and value. All four use paper codes, 99% exact all-location flags, bias 10^6, no false alarms and a target of 10^-12 errors per inner round per logical qubit, with the upper bit-flip bound and distance transfers for the higher-noise pair.](figures/noise-and-target.png)

The bars compare the paper codes under two phase models at $`p_Z=10^{-3}`$ and $`10^{-2}`$, with 99% exact all-location flags, bias $`10^6`$, no false alarms and a fixed target of $`10^{-12}`$ errors per inner round per logical qubit. These [model estimates](figures/README.md) use the upper bit-flip bound and transfers beyond simulated distances at higher noise, with the target below direct sampling.

## Assumptions made

- [Gate, preparation and readout flags](docs/methods.md#flags) are assumed.
- [False alarms](docs/methods.md#false-flags) are absent from the headline.
- [Rare rates and transfers](docs/methods.md#rare-bit-flip-rates) are modelled; the target is below direct sampling.
- [Ancilla motion and idle noise](docs/methods.md#circuit-ambiguities) remain circuit choices.

## How to use it

Reuse the [circuits and decoder](elevator/), [raw results](results/) and [task specifications](tasks/). [Reproduction](REPRODUCE.md) covers the laptop rebuild and full computation; [methods](docs/methods.md) and [references](data/) explain the assumptions and provenance. Original material is free to use under [CC0 1.0](LICENSE); dependencies retain their own terms.
