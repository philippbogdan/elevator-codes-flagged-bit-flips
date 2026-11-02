# Reference data

The parity-check matrices in [outer-codes/](outer-codes/) fix the two main outer codes, so the reported qubit savings can be checked against the same code definitions. Rows are checks and columns are repetition blocks. [`codes.py`](../elevator/codes.py) loads these matrices and contains the [16,3,8] matrix from the same source; it constructs Hamming and extended Hamming alternatives algebraically. [`test_core.py`](../tests/test_core.py) checks the paper-code dimensions and distances.

## Papers

| Reference | Contribution |
|---|---|
| Peter Shanahan and Diego Ruiz, [Elevator Codes: Concatenation for resource-efficient quantum memory under biased noise, arXiv:2601.10786v2](https://arxiv.org/abs/2601.10786v2) | Circuit layout, noise channels, published error fits and Appendix C parity-check matrices. |
| Filippo Ferrari, Joachim Cohen, Vincenzo Savona and Fabrizio Minganti, [Bit flips are erasures in dissipative cat qubits, arXiv:2607.01375v1](https://arxiv.org/abs/2607.01375v1) | Idle-qubit event flags and the distinction between an event and a certain X error. |
| Madelyn Cain, Chen Zhao, Hengyun Zhou, Nadine Meister, J. Pablo Bonilla Ataides, Arthur Jaffe, Dolev Bluvstein and Mikhail D. Lukin, [Correlated decoding of logical algorithms with transversal gates, arXiv:2403.03272v2](https://arxiv.org/abs/2403.03272v2) | Context for decoding correlated circuit errors through transversal gates. |

The papers use arXiv's non-exclusive licence to distribute. They are linked here, not included or relicensed. The matrix files are plain numerical transcriptions of Appendix C of the first paper, whose source file is `apssamp.tex`; no paper text, figures or source archive is bundled. The [16,3,8] matrix comes from its `fig:parity-check-16-3-8` figure.

## SHA-256 checksums

The PDF digests identify the exact reference versions. Downloading a PDF is optional; reproduction uses the included numerical matrices and formulas in the code.

| Input | SHA-256 |
|---|---|
| [2601.10786v2.pdf](https://arxiv.org/pdf/2601.10786v2) | `097686888d4b26bba4f81f7c73a5c299f83466fe68c93348ad85c2846f95e2a7` |
| [2607.01375v1.pdf](https://arxiv.org/pdf/2607.01375v1) | `4493e198030df06d5379c3f6ccbfe45ef283112f8b86a71026f0dde484c84614` |
| [2403.03272v2.pdf](https://arxiv.org/pdf/2403.03272v2) | `6430f97406fbf2b8ee80c6e5c0c0b8ffceb0858d385858f6157dfb2b4dfc38d3` |
| [H_15_9_3.txt](outer-codes/H_15_9_3.txt) | `27b4a08c82f4f4f6b8c063b68549cf186848d940e4c6eff557020e5500190d73` |
| [H_15_6_5.txt](outer-codes/H_15_6_5.txt) | `199c7fa6c3c6461841d77fa228fd303a76c4977fec33d95fdc28dd75b7d835e8` |

## Licences

Original code, results, figures and text use [CC0 1.0](../LICENSE). The numerical matrix transcriptions retain the source attribution above. Dependencies are installed separately and are not bundled; the repository's dedication does not replace their terms.

| Dependency | Licence |
|---|---|
| Stim 1.16.0 and sinter 1.16.0 | Apache-2.0 |
| PyMatching 2.4.0 | Apache-2.0 |
| ldpc 2.4.1 | MIT |
| NumPy | BSD-3-Clause |
| SciPy, including its HiGHS interface | BSD-3-Clause; HiGHS uses MIT |
| Matplotlib | Matplotlib licence, based on the Python Software Foundation licence |
| pytest | MIT |

Exact package pins are in [`requirements.txt`](../requirements.txt). No dependency code is bundled or covered by the repository's CC0 dedication.
