# COMPLETE.md outline (working notes; the final file is generated from results/summary)

1. Deliverable 1 — simulation and decoder
   - Stim circuits for [15,9,3], [15,6,5] (1 and 2 ancillas), [16,3,8]; X and Z memories;
     Table-I noise; determinism and circuit distance tests (tests/test_core.py).
   - Flagged bit flips: efficiency per class, false-flag rate, timing window; event model.
   - Decoder: exact MLE with window exclusivity (= ML at leading order: decoder_optimality.json).
   - Assumptions and their measured effects: classes (idle / idle+gate / all), erasure vs
     heralded, false flags, noise reading (noop vs literal), windows (aligned, equal ticks).
2. Deliverable 2 — published results reproduced (reproduction.md, fig*_from_paper_fits.png).
3. Deliverable 3 — overhead measured
   a. p_Z = 1e-3, eta = 1e6, 1e-12: f in [0, 1] x window exact..4096 ticks, both codes.
   b. eta 4e4..1e7.
   c. p_Z = 1e-2: lowest reachable rate and its overhead per flag setting.
4. Deliverable 4 — FINDINGS.md, REPORT.md, ./reproduce.sh.
5. Measurables: fidelity, known answers, statistics (CIs, held-out), overhead vs 88 and the
   p_Z = 1e-2 floors, frontier, limits.
