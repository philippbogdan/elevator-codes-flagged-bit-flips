# The problem

Dissipative cat qubits suffer bit flips (X) far more rarely than phase flips (Z). Elevator codes (arXiv:2601.10786v2, "Elevator Codes: Concatenation for resource-efficient quantum memory under biased noise", revised 21 September 2026) build a quantum memory for such qubits from two classical codes. The inner codes are phase-flip repetition codes of distance d_Z with bit-flip distance 1, so every physical bit flip is a logical X of its block. The outer code is a bit-flip code over n such blocks. One logical ancilla block moves down the column of blocks and measures each outer check through transversal logical gates: a CNOT and a SWAP (two CNOTs) where the check includes a block, a SWAP (three CNOTs) where it does not. There is a repetition-code syndrome round between consecutive logical operations, and at least d_Z rounds pass between the ancilla's preparation and its measurement. The decoding problem is the hypergraph these transversal CNOTs create; the paper decodes it with BP+OSD and simulates in Stim.

A separate result (arXiv:2607.01375v1, "Bit flips are erasures in dissipative cat qubits", 1 July 2026) shows that in a dissipative cat qubit every bit flip comes with a strong, time-localised burst of photons from the buffer mode. Photon counting or homodyne detection of the buffer's output can therefore flag when and where a bit flip happened, without interrupting the stabilisation.

No published work combining the two was found (arXiv and the citations of both papers, searched on 2 October 2026).

## To find

The qubit overhead (physical qubits, ancillas included, per logical qubit) of a quantum memory built from the [15,9,3] and [15,6,5] Elevator codes when bit flips are flagged as in arXiv:2607.01375 and the decoder uses the flags as erasure information, simulated in Stim, as a function of:

- **flag efficiency:** the probability that a bit flip is flagged, together with the rate of flags raised when no flip happened;
- **flag timing precision relative to the gates:** how precisely a flag places its flip within the schedule of repetition-code rounds and transversal CNOT layers.

## Given

- **The Elevator-code paper** (data/papers/, PDF and LaTeX source):
  - noise model (Appendix A, Table I): preparation and Z measurement fail with X at probability p_X; X-basis preparation and measurement fail with Z at p_Z; idle locations suffer Z at p_Z and X at p_X; a CNOT suffers IZ, ZI, ZZ at p_Z/3 each and IX, XI, XX at p_X/3 each; no Y errors. Noise bias eta = p_Z / (p_X + p_Y).
  - parity-check matrices of the outer codes (Appendix C; transcribed and checked in data/outer-codes/).
  - simulation protocol and fitted models (Appendix B): Z-type memory for 5 outer rounds (5 m d_Z inner rounds, m the number of outer checks) at 1e-6 <= p_X <= 1e-5 and d_Z = 9, 11, 13, 15, fitted to p_XL = d_Z^c (a p_X)^b with (a, b, c) = (37.18, 1.94, 2.33) for [15,9,3], (115.14, 2.76, 3.73) for [15,6,5] and (88.47, 2.86, 3.89) for [15,6,5] with two ancillas; X-type memory only for [15,9,3], one outer round, d_Z = 9, 11, 13, 5e-3 <= p_Z <= 1e-2, fitted to p_ZL = 0.12 (34.4 p_Z)^(0.94 (d_Z+1)/2), scaled by (n_b/16)(9/k) for the other codes. Logical error rates are per inner repetition-code round and per logical qubit, p_L = p_XL + p_ZL.
  - its overheads equal n_b (2 d_Z - 1) / k, with n_b the number of blocks including ancillas (16 with one ancilla); this reproduces its Figure 1.
- **Today's best published result**, from those fitted models, which reproduce the paper's Figures 1 and 2:
  - at p_Z = 1e-3 and eta = 1e6 (p_X = 1e-9), reaching 1e-12 per round takes 88 physical qubits per logical qubit ([15,6,5], d_Z = 17). The [15,9,3] code reaches 1e-12 only for eta above about 1.8e6, where it needs 58.7 (d_Z = 17). Thin surface codes need 125 and thin XZZX codes 145 at high bias (Figure 1).
  - at p_Z = 1e-2 and eta = 1e6, the fits bottom out near 2e-9 ([15,9,3]) and 2e-11 ([15,6,5], two ancillas), because the bit-flip term grows with d_Z. Neither code reaches 1e-12.
  - all of these are extrapolations: the bit-flip fits were sampled at p_X a thousand to ten thousand times above 1e-9, and the phase-flip fit only for [15,9,3] and only at p_Z >= 5e-3.
  - no code or data from the paper has been released (none found on 2 October 2026).
- **The flag physics** (arXiv:2607.01375v1, data/papers/, PDF and LaTeX source): an idle dissipative cat with g_2/2pi = 5 MHz, kappa_b/2pi = 100 MHz, kappa_a/2pi = kappa_phi/2pi = 5 to 10 kHz and 2 to 8 photons in the memory. A flip unfolds over a time of order 1/(kappa_a <a^dagger a>), and the buffer emission is concentrated at its start. With a realistic photodetector (efficiency 70 %, dark-count rate gamma_d/2pi = 1 kHz) the photon-count distributions with and without a flip stay well separated, and a threshold on the count trades missed flips against false flags. That paper uses eta for detector efficiency, not noise bias. It models idle qubits only: flags during gates, preparation and measurement are not established. Neither paper fixes gate or round durations.
- **Correlated decoding through transversal gates:** arXiv:2403.03272v2 (data/papers/), which the Elevator-code paper follows.
- **Software:** Stim 1.16.0 (tag v1.16.0, commit e2fc1ec, PyPI 22 May 2026), sinter 1.16.0, ldpc 2.4.1 (PyPI 8 December 2025), the BP+OSD implementation the paper cites.

## Why it is not routine

- Nothing is released: the circuits, the schedule, the noise and the decoding have to be rebuilt from the paper's text and made to reproduce its numbers before any new number can be trusted.
- What a bit flip does depends on when it happens relative to each transversal CNOT: an X on a control block before the CNOT also lands on the target block, an X after it does not. A flag that places the flip only within a window containing gates is consistent with several error histories, and flags can be missing or false.
- The decoding problem is a hypergraph, beyond matching, even without flags.
- The target rates lie far below what direct sampling of circuits with hundreds of qubits and hundreds of rounds can reach. Erasure information changes how the logical error rate scales with p_X, so neither the published fits nor any new extrapolation can be taken on trust.
- The flag statistics are established only for idle qubits, while the memory spends most of its time in gates and syndrome rounds.
