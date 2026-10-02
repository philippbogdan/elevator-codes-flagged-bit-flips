"""Task specs (JSON) for Monte-Carlo runs, executed locally or on the clusters.

A task is a dict with
  kind      : 'phys'  (physical Stim circuit, flags off)
  code, d, memory ('X'|'Z'), p_x, p_z, n_anc, mode, n_outer, idle_ctx
  decoder   : dict(name='bposd'|'bplsd', **options)
  shots     : max shots;  max_fail : stop after this many failures
  seed      : base seed
Results: dict(task..., shots, fails, rounds, k, seconds).
"""
from __future__ import annotations

import hashlib
import json
import os
import time

import numpy as np

from ldpc import BpLsdDecoder, BpOsdDecoder
from ldpc.ckt_noise.dem_matrices import detector_error_model_to_check_matrices

from .circuits import build_circuit
from .codes import load_code
from .repcode import sample_rep


def task_id(spec: dict) -> str:
    s = json.dumps({k: spec[k] for k in sorted(spec) if k not in ("shots", "max_fail")}, sort_keys=True)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def make_decoder(dem, dspec: dict):
    m = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges=True)
    H = m.check_matrix.tocsr()
    L = m.observables_matrix.tocsr()
    pri = list(np.array(m.priors, dtype=float))
    opts = {k: v for k, v in dspec.items() if k != "name"}
    if dspec["name"] == "bposd":
        dec = BpOsdDecoder(H, error_channel=pri, **opts)
    elif dspec["name"] == "bplsd":
        dec = BpLsdDecoder(H, error_channel=pri, **opts)
    else:
        raise ValueError(dspec["name"])
    return dec, L


def run_phys_shard(spec: dict, shots: int, seed: int) -> dict:
    code = load_code(spec["code"])
    c, s = build_circuit(code, spec["d"], spec["memory"], p_x=spec.get("p_x", 0.0),
                         p_z=spec.get("p_z", 0.0), n_anc=spec.get("n_anc", 1),
                         mode=spec.get("mode", "full"), n_outer=spec.get("n_outer"),
                         idle_ctx=tuple(spec.get("idle_ctx", ("edge", "cnot", "op"))),
                         compress=bool(spec.get("compress", False)),
                         anc_scale=float(spec.get("anc_scale", 1.0)))
    dem = c.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
    dec, L = make_decoder(dem, spec["decoder"])
    sampler = c.compile_detector_sampler(seed=seed)
    t0 = time.time()
    fails = done = 0
    batch = int(spec.get("batch", 2000))
    max_fail = spec.get("max_fail")
    while done < shots:
        b = min(batch, shots - done)
        dets, obs = sampler.sample(b, separate_observables=True)
        for i in range(b):
            if dets[i].any():
                e = dec.decode(dets[i].astype(np.uint8))
                pred = (L @ e) % 2
            else:
                pred = np.zeros(obs.shape[1], dtype=np.uint8)
            if np.any(pred != obs[i]):
                fails += 1
        done += b
        if max_fail is not None and fails >= max_fail:
            break
    return dict(shots=done, fails=fails, rounds=s.n_rounds, k=code.k, seconds=time.time() - t0)


def run_rep_shard(spec: dict, shots: int, seed: int) -> dict:
    t0 = time.time()
    r = sample_rep(spec["d"], spec["rounds"], spec["p_z"], shots, seed, extra_idle=spec.get("extra_idle", 0.0))
    return dict(shots=r["shots"], fails=r["fails"], rounds=spec["rounds"], k=1, seconds=time.time() - t0)


def run_direct_block_shard(spec: dict, shots: int, seed: int) -> dict:
    """Direct Monte Carlo of the block-level flagged Z memory (validation of the strata estimator)."""
    from .flagstudy import _build
    from .flags import direct_mc
    t0 = time.time()
    code, sched, bm, fm, dec, ss = _build(spec)
    r = direct_mc(fm, dec, shots, seed)
    return dict(shots=r["shots"], fails=r["fails"], rounds=sched.n_rounds, k=code.k, seconds=time.time() - t0)


def run_shard(args):
    spec, shots, seed = args
    if spec["kind"] == "direct_block":
        return run_direct_block_shard(spec, shots, seed)
    if spec["kind"] == "phys":
        return run_phys_shard(spec, shots, seed)
    if spec["kind"] == "rep":
        return run_rep_shard(spec, shots, seed)
    raise ValueError(spec["kind"])


def run_task(spec: dict, procs: int, out_path: str, shard_shots: int | None = None) -> dict:
    """Run a task in shards over `procs` processes; checkpoint cumulative counts."""
    from multiprocessing import Pool
    shots_total = int(spec["shots"])
    max_fail = spec.get("max_fail")
    shard = shard_shots or max(1, min(shots_total // max(procs, 1), int(spec.get("shard", 20000))))
    state = dict(spec=spec, shots=0, fails=0, seconds=0.0, rounds=None, k=None, shards=0)
    if os.path.exists(out_path):
        try:
            old = json.load(open(out_path))
            if old.get("spec") == spec:
                state = old
        except Exception:
            pass
    base_seed = int(spec.get("seed", 0)) * 1000003
    with Pool(procs) as pool:
        while state["shots"] < shots_total and (max_fail is None or state["fails"] < max_fail):
            remaining = shots_total - state["shots"]
            n = max(1, min(procs, -(-remaining // shard)))
            args = []
            for i in range(n):
                sh = min(shard, remaining - i * shard)
                if sh <= 0:
                    break
                args.append((spec, sh, base_seed + state["shards"] + i))
            for r in pool.map(run_shard, args, chunksize=1):
                state["shots"] += r["shots"]
                state["fails"] += r["fails"]
                state["seconds"] += r["seconds"]
                state["rounds"] = r["rounds"]
                state["k"] = r["k"]
                for key in ("extra",):
                    if key in r:
                        state.setdefault(key, []).append(r[key])
            state["shards"] += len(args)
            tmp = out_path + ".tmp"
            json.dump(state, open(tmp, "w"))
            os.replace(tmp, out_path)
    return state
