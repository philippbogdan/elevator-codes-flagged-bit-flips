"""Decoders and Monte-Carlo sampling for the physical circuits."""
from __future__ import annotations

import time

import numpy as np
import stim
from ldpc import BpOsdDecoder
from ldpc.ckt_noise.dem_matrices import detector_error_model_to_check_matrices

# BP+OSD settings: arXiv:2601.10786 does not state them; we use the common
# "BP+OSD-CS order 7, product-sum BP" configuration of Roffe et al. (2020).
BPOSD_DEFAULT = dict(bp_method="product_sum", max_iter=100, osd_method="osd_cs", osd_order=7)


class DemDecoder:
    def __init__(self, dem: stim.DetectorErrorModel, **kw):
        self.dem = dem
        m = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges=True)
        self.H = m.check_matrix.tocsr()
        self.L = m.observables_matrix.tocsr()
        self.priors = np.array(m.priors, dtype=float)
        opts = dict(BPOSD_DEFAULT)
        opts.update(kw)
        self.opts = opts
        self.dec = BpOsdDecoder(self.H, error_channel=list(self.priors), **opts)

    def decode_batch(self, dets: np.ndarray) -> np.ndarray:
        """dets: (shots, n_det) bool -> predicted observables (shots, n_obs) bool."""
        out = np.zeros((dets.shape[0], self.L.shape[0]), dtype=bool)
        for i in range(dets.shape[0]):
            if not dets[i].any():
                continue
            e = self.dec.decode(dets[i].astype(np.uint8))
            out[i] = (self.L @ e) % 2
        return out


def sample_failures(circuit: stim.Circuit, shots: int, seed: int, decoder: DemDecoder | None = None,
                    batch: int = 20000, max_fail: int | None = None) -> dict:
    """Sample `shots` shots (stopping early once max_fail failures are seen)."""
    if decoder is None:
        dem = circuit.detector_error_model(decompose_errors=False, approximate_disjoint_errors=True)
        decoder = DemDecoder(dem)
    sampler = circuit.compile_detector_sampler(seed=seed)
    done = fails = 0
    t0 = time.time()
    while done < shots:
        b = min(batch, shots - done)
        dets, obs = sampler.sample(b, separate_observables=True)
        pred = decoder.decode_batch(dets)
        fails += int(np.any(pred != obs, axis=1).sum())
        done += b
        if max_fail is not None and fails >= max_fail:
            break
    return dict(shots=done, fails=fails, seconds=time.time() - t0)


def per_round_per_lq(fails: int, shots: int, rounds: int, k: int) -> float:
    """Invert P_fail = 1 - (1 - p)^(rounds*k)."""
    P = fails / shots
    if P >= 1:
        return float("nan")
    return 1.0 - (1.0 - P) ** (1.0 / (rounds * k))


def wilson(fails: int, shots: int, z: float = 1.96) -> tuple[float, float]:
    if shots == 0:
        return (0.0, 1.0)
    p = fails / shots
    den = 1 + z * z / shots
    centre = (p + z * z / (2 * shots)) / den
    half = z * np.sqrt(p * (1 - p) / shots + z * z / (4 * shots * shots)) / den
    return max(0.0, centre - half), min(1.0, centre + half)
