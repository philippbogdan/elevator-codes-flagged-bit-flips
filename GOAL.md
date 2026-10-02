# Goal

Establish how far flagged bit flips can cut the qubit overhead of an Elevator-code quantum memory, as a function of flag efficiency and flag timing precision relative to the gates, with every number as trustworthy as the problem allows and reproducible from one command. Aspire to the best that could exist, not a good one: the published overheads in PROBLEM.md are a floor, not a target.

## Specific

1. **A simulation and decoder** in Stim for the [15,9,3] and [15,6,5] Elevator-code memories (X-type and Z-type memory, in the configurations the paper reports) under the paper's noise model. Flagged bit flips are added, with flag efficiency, false-flag rate and flag timing precision as parameters, and the decoder uses the flags as erasure information. Any other assumption the flag model needs, flags during gates, preparation and measurement included, is stated, and its effect on the overhead is measured.
2. **The published results reproduced:** with flags switched off, the paper's fitted models at its sampled points and the overheads of its Figures 1 and 2.
3. **The overhead measured** for both codes:
   - at p_Z = 1e-3 and noise bias 1e6: the qubit overhead per logical qubit needed to reach 1e-12 per inner round, across flag efficiency from 0 to 1 and timing precision from finer than one CNOT layer to coarser than one outer-code round;
   - the same against noise bias from 4e4 to 1e7, as in Figure 1;
   - at p_Z = 1e-2 and noise bias 1e6: the lowest logical error rate reachable, and its overhead, across the same flag settings.
4. **`FINDINGS.md`** (what the work establishes, each claim with its evidence), **`REPORT.md`** (each criterion against the published floor, what failed, what remains open), and one command that regenerates every number.

## Measurable

Every number is checked against references this work does not produce.

- **Fidelity to the source:** with flags off, logical error rates agree with the paper's fitted models at its sampled parameters within 95 % confidence intervals or a factor of 2, whichever is wider, and the overheads agree with its Figures 1 and 2. Any disagreement is explained by evidence, not tuned away.
- **Known answers:** where a flag model has a known answer, the decoder meets it exactly. A distance-d repetition code with every flip flagged corrects d - 1 flips, as arXiv:2607.01375 states. An [n, k, d] outer code with perfect flags and no other noise corrects every pattern of up to d - 1 erased blocks, checked by enumeration.
- **Statistics:** every logical error rate carries a confidence interval from enough logical failures to support it. Every number below direct sampling reach is labelled as extrapolated, gives its model, and shows that model predicting held-out sampled points under flags.
- **Overhead:** physical qubits, ancillas included, per logical qubit at each target, against the published 88 (p_Z = 1e-3, noise bias 1e6, 1e-12) and the published reachable floors at p_Z = 1e-2.
- **The frontier:** the non-dominated set of overhead, logical error rate, flag efficiency required and timing precision required, across codes, decoders and every alternative you tried. After every success, push it outward on whichever criterion is furthest from its limit.
- A limit belongs to the problem only with evidence: an overhead floor derived from errors that flags cannot reveal, a bound from the code's own distance, or a decoder shown to be optimal for its flag model. Anything else is an open problem to attack.

## Relevant

Architects of cat-qubit memories have to decide whether detecting the buffer's photons is worth building, and how efficient and how fast that detection must be. Code designers want to know whether flags let a higher-rate outer code serve at lower noise bias, or push the memory past the bit-flip wall at high phase-flip rates.

## Done

Done means `COMPLETE.md` shows, through the measurements above, that all four deliverables hold, the flag-free simulation reproduces the published results, the overhead is measured across the whole range of flag efficiency and timing precision, and every remaining limit belongs to the problem itself. There is no deadline and no other way to finish.

## Rules

- Every choice is yours.
- Never invent results or references; label estimates as estimates.
- Contact nobody and publish nothing: no email, posts, issue comments, pushes or pull requests.
- Work only inside this directory; do not read or search local files elsewhere. The internet is yours.
- Commit as you go, so the repository alone can resume the work. Do not edit PROBLEM.md or GOAL.md.
- The machine: Apple M4, 10 cores, 16 GB memory, no FP64 GPU, shared with six other long runs and its owner's own work. Memory has a hard limit: when its use passes 75 %, the largest process any run started here is stopped. The disk is nearly full, with well under 10 GB free for all the runs together, so keep data and environments here small.
- Heavy computation goes out with `gpurun`, run from inside this directory: DoC's GPU cluster, DoC's shared CPU server (batch1) and its Condor pool of idle lab machines, and Imperial's RCS CX3 cluster (CPUs and GPUs). `gpurun --help` lists what each place offers, its limits and how to ask for what a job needs; without a place named, gpurun picks one that is free now. Each place keeps its own copy of this directory with its own .venv, and results come back by themselves when a job ends. Copies back skip files over 200 MB and stop when less than 8 GB of disk is free here; `gpurun pull` fetches a file when it is needed here.
