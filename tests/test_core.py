"""Core invariants.  Run:  .venv/bin/python -m pytest -q tests"""
import os
import sys

import numpy as np
import pytest
import stim

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elevator.blocklevel import BlockModel  # noqa: E402
from elevator.circuits import build_circuit  # noqa: E402
from elevator.codes import load_code  # noqa: E402
from elevator.known_answers import code_capacity_erasures, repetition_code  # noqa: E402
from elevator.overhead import candidates, min_overhead  # noqa: E402


def test_outer_codes():
    for nm, (n, k, d) in {"15_9_3": (15, 9, 3), "15_6_5": (15, 6, 5), "16_3_8": (16, 3, 8)}.items():
        c = load_code(nm)
        assert (c.n, c.k, c.d) == (n, k, d)


@pytest.mark.parametrize("mem", ["X", "Z"])
@pytest.mark.parametrize("n_anc", [1, 2])
def test_circuits_deterministic(mem, n_anc):
    c, _ = build_circuit(load_code("15_6_5"), 3, mem, n_anc=n_anc, n_outer=2)
    assert not c.compile_detector_sampler().sample(20, append_observables=True).any()


def _dem_dict(dem):
    out = {}
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        key = tuple(sorted(str(t) for t in inst.targets_copy()))
        p = inst.args_copy()[0]
        q = out.get(key, 0.0)
        out[key] = q * (1 - p) + p * (1 - q)
    return out


@pytest.mark.parametrize("idle", [("edge", "cnot"), ("edge", "cnot", "op")])
def test_blocklevel_equals_physical(idle):
    code = load_code("15_9_3")
    c, s = build_circuit(code, 3, "Z", p_x=1e-4, n_outer=2, idle_ctx=idle)
    a = _dem_dict(c.detector_error_model(approximate_disjoint_errors=True))
    b = _dem_dict(stim.DetectorErrorModel(BlockModel(s, 1e-4, idle_ctx=idle).dem_text()))
    assert set(a) == set(b)
    assert max(abs(a[k] - b[k]) / a[k] for k in a) < 1e-4


def test_circuit_distance():
    for nm, d in [("15_9_3", 3), ("15_6_5", 5)]:
        c, _ = build_circuit(load_code(nm), 3, "Z", p_x=1e-3, n_outer=2)
        errs = c.search_for_undetectable_logical_errors(
            dont_explore_detection_event_sets_with_size_above=6, dont_explore_edges_with_degree_above=6,
            dont_explore_edges_increasing_symptom_degree=False, canonicalize_circuit_errors=True)
        assert len(errs) == d


def test_known_answer_repetition():
    r = code_capacity_erasures(repetition_code(5), 5)
    assert all(r[s]["failures"] == 0 for s in range(5))
    assert 2 * r[5]["failures"] == r[5]["patterns"]


def test_figure1_from_fits():
    c = min_overhead(1e-12, candidates(1e-3, 1e6), "elevator")
    assert abs(c.overhead - 88.0) < 1e-9 and c.d == 17
    c = min_overhead(1e-12, candidates(1e-3, 2e6), "elevator")
    assert abs(c.overhead - 16 * 33 / 9) < 1e-9


@pytest.mark.parametrize("nm,d", [("15_9_3", 3), ("15_6_5", 5), ("16_3_8", 8)])
def test_local_path_circuits(nm, d):
    """The shortest-path ancilla gives deterministic circuits of full circuit distance."""
    code = load_code(nm)
    for mem in ("X", "Z"):
        c0, _ = build_circuit(code, 3, mem, p_x=0.0, p_z=0.0, mode="local", n_outer=2, idle_ctx=("edge", "cnot"))
        assert not c0.compile_detector_sampler().sample(10, append_observables=True).any()
    c, _ = build_circuit(code, 3, "Z", p_x=1e-3, mode="local", n_outer=2, idle_ctx=("edge", "cnot"))
    errs = c.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=4, dont_explore_edges_with_degree_above=4,
        dont_explore_edges_increasing_symptom_degree=False, canonicalize_circuit_errors=True)
    assert len(errs) == d


def test_perfect_flags_exact_below_distance():
    """Exactly timed perfect flags: fewer than d flagged events never contain a logical."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    from perfect_flags_exact import ALL, f0b
    from elevator.flags import FlagConfig, FlagModel
    from elevator.schedule import ElevatorSchedule
    code = load_code("15_9_3")
    bm = BlockModel(ElevatorSchedule(code, 5, n_anc=1, n_outer=2), 1e-9, idle_ctx=("edge", "cnot"))
    fm = FlagModel(bm, FlagConfig.make(1.0, classes=ALL, window=0))
    rng = np.random.default_rng(0)
    assert f0b(fm, 2, 20000, rng)[0] == 0.0
    assert f0b(fm, 3, 20000, rng)[0] > 0.0


def test_strata_caps_against_decoder():
    """Analytic stratum bounds (scripts/strata_caps.py): the merged DEM of [15,6,5] has no undetectable
    logical of <= 4 columns, the class-count reconstruction gives the decoder's own column costs, and
    no decoded sample of a stratum bounded by 0 fails."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import strata_caps as SC
    from elevator.flagstudy import _build
    from elevator.strata import StrataSampler
    spec = dict(code="15_6_5", n_anc=1, d=9, mode="full", idle_ctx=["edge", "cnot"], n_outer=5, p_x=1e-8,
                flag=dict(f=0.99, classes=["idle", "gate", "prep", "meas"], window=0, false_rate=0.0))
    code, sched, bm, fm, dec, ss = _build(spec)
    assert SC.dem_distance_at_least(bm) >= 5
    rec = dict(code="15_6_5", n_anc=1, n_outer=5, idle="edge,cnot", d_code=5, d_dem_lb=5,
               signature=SC.signature(bm), n_col=bm.n_col)
    SC._DIRECT[("15_6_5", 1, 5, "edge,cnot", 9)] = (SC.col_counts(bm), 5)
    eff = [0.99] * 4
    caps = SC.caps_for(rec, 9, 1e-8, eff, [(1, 1), (1, 2), (2, 0)])
    assert caps["1,1"] == 0.0 and caps["1,2"] == 0.0
    # the decoder's background column costs equal the reconstruction from class counts
    n, _ = SC.counts_at(rec, 9)
    x = 1e-8 * SC.CLASS_X
    xbg = x * (1 - np.array(eff)) / (1 - 2 * x * np.array(eff))
    lg = n[:bm.n_col] @ np.log1p(-2 * xbg)
    assert np.allclose(lg, dec.lg_col_bg, rtol=1e-6, atol=1e-12)
    rng = np.random.default_rng(1)
    for a, b in ((1, 1), (1, 2)):
        for _ in range(60):
            flips, wins = StrataSampler(fm).sample(a, b, rng)
            det, obs = fm.syndrome(flips)
            if det.any() or obs.any():
                assert np.array_equal(dec.decode(det, wins), obs)


def test_false_flag_bounds_against_decoder():
    """scripts/false_flag_bounds.py: with exact timing and r = 1e-6 a single flagged event is never
    mistaken (bound 0), and no decoded (0,1) sample with false flags fails."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    from false_flag_bounds import bounds_for
    from elevator.flagstudy import _build
    spec = dict(kind="strata", code="15_9_3", n_anc=1, d=5, mode="full", compress=False, idle_ctx=["edge", "cnot"],
                n_outer=3, p_x=1e-9, decoder="mle_excl",
                flag=dict(f=0.99, classes=["idle", "gate", "prep", "meas"], window=0, false_rate=1e-6))
    b = bounds_for(spec)
    assert b["0,1"] == 0.0 and 0.0 <= b["1,0"] <= 1.0 and 0.0 <= b["0,2"] <= 1.0
    code, sched, bm, fm, dec, ss = _build(spec)
    rng = np.random.default_rng(2)
    for _ in range(150):
        flips, wins = ss.sample(0, 1, rng)
        det, obs = fm.syndrome(flips)
        if det.any() or obs.any():
            assert np.array_equal(dec.decode(det, wins), obs)
