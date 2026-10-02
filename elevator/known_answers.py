"""Known-answer checks for the flag-aware decoders (GOAL.md, 'Known answers').

KA1  A distance-d repetition code with every flip flagged corrects d - 1 flips
     (arXiv:2607.01375): code capacity, every erasure pattern of size <= d-1 and every
     flip pattern on it, decoded by the same integer-program MLE used in the study; and
     at circuit level, the block-level elevator memory whose outer code is the [d,1,d]
     repetition code, with flagged flips injected at random locations.
KA2  An [n,k,d] outer code with perfect flags and no other noise corrects every pattern
     of up to d-1 erased blocks: enumeration over all block subsets (and all flip
     patterns) at code capacity, and over all block subsets at circuit level, with the
     erasures placed as flagged flips on the blocks' data qubits in one round.
For size-d patterns that cover a logical, an ML decoder fails with probability 1/2:
the enumeration reports that fraction to show the bound is tight.
"""
from __future__ import annotations

import itertools

import numpy as np
import scipy.sparse as sp

from .codes import OuterCode, gf2_nullspace, information_set, load_code
from .mle import costs_from_probs, mle_solve


def repetition_code(d: int) -> OuterCode:
    H = np.zeros((d - 1, d), dtype=np.uint8)
    for i in range(d - 1):
        H[i, i] = H[i, i + 1] = 1
    return OuterCode(f"rep{d}", H)


def code_capacity_erasures(code: OuterCode, max_size: int, p_bg: float = 1e-9) -> dict:
    """Enumerate erasure sets E (|E| <= max_size) and all flips on E.

    Decoder: MLE over all n bits with cost 0 on erased bits and log((1-p)/p) elsewhere.
    Logical failure: residual (truth xor correction) is a nonzero codeword."""
    n = code.n
    H = sp.csc_matrix(code.H.astype(np.int64))
    G = code.G
    out = {}
    for size in range(0, max_size + 1):
        n_pat = n_fail = n_sets_bad = 0
        for E in itertools.combinations(range(n), size):
            p = np.full(n, p_bg)
            p[list(E)] = 0.5
            w = costs_from_probs(p)
            bad = False
            for bits in itertools.product([0, 1], repeat=size):
                x = np.zeros(n, dtype=np.uint8)
                x[list(E)] = bits
                s = (code.H @ x) % 2
                xh = mle_solve(H, w, s.astype(np.uint8))
                r = (x ^ xh) % 2
                fail = bool(r.any())          # residual is a codeword (syndrome matched)
                n_pat += 1
                n_fail += fail
                bad |= fail
            n_sets_bad += bad
        out[size] = dict(patterns=n_pat, failures=n_fail,
                         sets=int(sum(1 for _ in itertools.combinations(range(n), size))),
                         sets_with_failure=n_sets_bad)
    return out


def circuit_erasure_blocks(code: OuterCode, d_inner: int = 3, max_size: int | None = None,
                           rounds_frac=(0.3, 0.5, 0.7), seed: int = 0) -> dict:
    """Circuit level: flagged flips on all d_inner data qubits' t0 location of one block
    each (exact timing, perfect flags, no other noise), for every subset of data blocks."""
    from .blocklevel import BlockModel, IDLE
    from .flags import ExclusiveMleDecoder, FlagConfig, FlagModel
    from .schedule import ElevatorSchedule
    if max_size is None:
        max_size = code.d - 1
    sched = ElevatorSchedule(code, d_inner, n_anc=1, n_outer=5)
    bm = BlockModel(sched, 1e-9, idle_ctx=("edge", "cnot"))
    fm = FlagModel(bm, FlagConfig.make(1.0, classes=("idle", "gate", "prep", "meas"), window=0))
    dec = ExclusiveMleDecoder(fm)
    L = bm.loc
    rng = np.random.default_rng(seed)
    # rounds: pick round ticks t0 (first tick of each inner round)
    round_ticks = []
    tick = 0
    for seg, content in sched.iter_contents():
        if seg[0] == "round":
            round_ticks.append((tick, list(content)))
            tick += 4
        else:
            ops = seg[1]
            if ops:
                from .schedule import op_cnots
                tick += max(len(op_cnots(k, a, b)) for k, a, b in ops)
    out = {}
    for frac in rounds_frac:
        t0, content = round_ticks[int(frac * (len(round_ticks) - 1))]
        row_of_block = {content[r][1]: r for r in range(bm.P) if content[r][0] == "D"}
        for size in range(0, max_size + 1):
            res = out.setdefault(size, dict(sets=0, failures=0, patterns=0))
            for E in itertools.combinations(range(code.n), size):
                # one flagged flip (X forced) on data qubit 0 of each block's row at tick t0
                idx = []
                for b in E:
                    r = row_of_block[b]
                    q = bm.dq(r, 0)
                    m = np.nonzero((L.qubit == q) & (L.tick == t0))[0]
                    assert len(m) == 1 and L.slot[m[0]] >= 0
                    idx.append(m[0])
                idx = np.array(idx, dtype=np.int64)
                res["sets"] += 1
                for bits in itertools.product([0, 1], repeat=size):
                    xs = np.array(bits, dtype=bool)
                    flips, wins = fm._realise(idx, rng, force_flag=np.ones(size, bool), force_x=xs)
                    det, obs = fm.syndrome(flips)
                    pred = dec.decode(det, wins) if det.any() else np.zeros_like(obs)
                    res["patterns"] += 1
                    res["failures"] += int(np.any(pred != obs))
    return out


def circuit_random_flagged(code: OuterCode, d_inner: int, k: int, n_samples: int, seed: int = 0,
                           force_x: bool = True) -> dict:
    """Circuit level: k flagged events at random locations (all classes, exact timing),
    X forced on each (worst case), no other noise."""
    from .blocklevel import BlockModel
    from .flags import ExclusiveMleDecoder, FlagConfig, FlagModel
    from .schedule import ElevatorSchedule
    sched = ElevatorSchedule(code, d_inner, n_anc=1, n_outer=5)
    bm = BlockModel(sched, 1e-9, idle_ctx=("edge", "cnot"))
    fm = FlagModel(bm, FlagConfig.make(1.0, classes=("idle", "gate", "prep", "meas"), window=0))
    dec = ExclusiveMleDecoder(fm)
    rng = np.random.default_rng(seed)
    ok_locs = np.nonzero(bm.loc.slot >= 0)[0]
    fails = 0
    for _ in range(n_samples):
        idx = rng.choice(ok_locs, size=k, replace=False)
        xs = np.ones(k, bool) if force_x else rng.random(k) < 0.5
        flips, wins = fm._realise(idx, rng, force_flag=np.ones(k, bool), force_x=xs)
        det, obs = fm.syndrome(flips)
        pred = dec.decode(det, wins) if det.any() else np.zeros_like(obs)
        fails += int(np.any(pred != obs))
    return dict(k=k, samples=n_samples, failures=fails)
