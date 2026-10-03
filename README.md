# Flagged bit flips in Elevator-code quantum memories

Signals that reveal where bit flips occurred could cut the qubits needed by a third.
At the [main noise setting](results/summary/headline.md), that is the model estimate
for the paper's codes when 90% of events are flagged at every stage, including gates,
with exact timing and no false alarms. Whether gates can provide such flags remains open.

The question was how much these signals, called flags, could reduce the hardware needed
to protect quantum information, even when flags miss events or give an imprecise time.
This study combines Elevator codes with a proposal for detecting bit flips in cat qubits.
That proposal covers idle qubits only.

Idle-only flags give no clear qubit saving for the paper's codes at this setting.
A different code can help. Less precise timing can increase errors even when the qubit
count stays unchanged. These are estimates from simulations and models, with the rarest
errors beyond direct sampling.

Start with [FINDINGS.md](FINDINGS.md). The [report](REPORT.md) covers comparisons and
open questions, [COMPLETE.md](COMPLETE.md) maps results to the original goals, and the
[methods](docs/methods.md) explain the assumptions. [Results](results/summary/) contains
the tables and plots. The code is in [elevator/](elevator/) and [scripts/](scripts/).

To regenerate the analysis from the saved results, run from the repository root:

```sh
./reproduce.sh analysis
```

Requires Bash and `uv`. On first use, the script creates a Python 3.12 environment and
installs its dependencies, including Stim. This rewrites the generated reports, tables
and plots. `RUNNER=local ./reproduce.sh all` also runs simulations and checks, reusing
matching saved results. A fresh simulation run is substantial, about 1,500 core-hours
according to the script.

The source papers are *Elevator Codes: Concatenation for resource-efficient quantum
memory under biased noise*, *Bit flips are erasures in dissipative cat qubits*, and
*Correlated decoding of logical algorithms with transversal gates*. Links and versions
are in [data/README.md](data/README.md). The included code matrices were transcribed
from Appendix C of the Elevator Codes paper. The papers themselves are not included.
Their licences are not recorded here. The code is [MIT licensed](LICENSE),
copyright Philipp Bogdan.
