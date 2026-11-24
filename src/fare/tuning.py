# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Equal-budget tuning grids and selection (research/protocol.md section 4).

Each family gets 36 configurations evaluated on the same tuning streams; the
configuration with the highest mean revenue wins (ties: lowest index).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .metrics import compute_metrics
from .params import ScenarioParams
from .policies import DRP, FIX, OCC, Policy
from .simulate import simulate
from .streams import DemandStream

# Draft v0.1 sensitivity values: the defaults, kept so that the pre-freeze
# exploratory configs (which do not name a grid) reproduce unchanged.
OCC_K = (0.5, 1.0, 2.0, 4.0)
DRP_ETA = (0.1, 0.25, 0.5, 1.0)
# Frozen v1.0 sensitivity values (owner-approved amendment 2026-11-24, D-008):
# widened so that the pilot optima are interior. The confirmatory configs name
# them explicitly ("occ_k", "drp_eta") together with p0_n = 6.
OCC_K_V1 = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
DRP_ETA_V1 = (0.025, 0.05, 0.1, 0.25, 0.5, 1.0)


def geometric(lo: float, hi: float, n: int) -> list[float]:
    return [float(v) for v in np.geomspace(lo, hi, n)]


def grid(family: str, *, lo: float = 40.0, hi: float = 400.0, fix_n: int = 36, p0_n: int = 9,
         occ_k: Sequence[float] = OCC_K, drp_eta: Sequence[float] = DRP_ETA) -> list[Policy]:
    """Configuration list in index order (p0 outer, sensitivity inner)."""
    if family == "FIX":
        return [FIX(p) for p in geometric(lo, hi, fix_n)]
    if family == "OCC":
        return [OCC(p0, float(k)) for p0 in geometric(lo, hi, p0_n) for k in occ_k]
    if family == "DRP":
        return [DRP(p0, float(e)) for p0 in geometric(lo, hi, p0_n) for e in drp_eta]
    raise ValueError(f"unknown family {family!r}")


@dataclass(frozen=True)
class TuningResult:
    family: str
    configs: list[Policy]
    mean_revenue: np.ndarray       # per configuration
    best_index: int
    at_grid_edge: bool

    @property
    def best(self) -> Policy:
        return self.configs[self.best_index]


def revenue_matrix(configs: Sequence[Policy], streams: Sequence[DemandStream], sp: ScenarioParams,
                   sim: Callable = simulate) -> np.ndarray:
    """Revenue for every (configuration, stream) pair; shape (n_configs, n_streams)."""
    R = np.empty((len(configs), len(streams)))
    for i, pol in enumerate(configs):
        for j, s in enumerate(streams):
            R[i, j] = sim(s, sp, pol).revenue
    return R


def select(family: str, configs: list[Policy], R: np.ndarray) -> TuningResult:
    means = R.mean(axis=1)
    best = int(np.flatnonzero(means == means.max())[0])  # ties: lowest index
    edge = _at_edge(family, configs, best)
    return TuningResult(family, configs, means, best, edge)


def _at_edge(family: str, configs: list[Policy], i: int) -> bool:
    pol = configs[i]
    if family == "FIX":
        ps = [c.p for c in configs]
        return pol.p in (min(ps), max(ps))
    p0s = [c.p0 for c in configs]
    sens = [c.k if family == "OCC" else c.eta for c in configs]
    s = pol.k if family == "OCC" else pol.eta
    return pol.p0 in (min(p0s), max(p0s)) or s in (min(sens), max(sens))


def tune(family: str, streams: Sequence[DemandStream], sp: ScenarioParams, **grid_kw) -> TuningResult:
    configs = grid(family, **grid_kw)
    return select(family, configs, revenue_matrix(configs, streams, sp))


__all__ = ["grid", "tune", "select", "revenue_matrix", "TuningResult", "compute_metrics"]
