# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Synthetic demand-stream generator (ingestion layer).

A stream is the full sequence of buyer arrivals of one selling season: arrival
period, segment and valuation, in arrival order. Buyers are myopic, so a stream
does not depend on the pricing policy and is replayed identically under every
policy (common random numbers).

Seeds: numpy SeedSequence(entropy=PROJECT_ENTROPY, spawn_key=(experiment, cell,
role, index)), role 0 = tune, 1 = eval (research/protocol.md section 7).
"""

from __future__ import annotations

import hashlib
from bisect import bisect_left
from dataclasses import dataclass
from functools import cached_property

import numpy as np

from . import GENERATOR_VERSION
from .params import ScenarioParams

PROJECT_ENTROPY = 20261124  # fixed project entropy (decision D-006)
ROLE_TUNE = 0
ROLE_EVAL = 1
SEG_L = 0
SEG_H = 1


@dataclass(frozen=True)
class SeedKey:
    experiment: int
    cell: int
    role: int
    index: int

    def __post_init__(self) -> None:
        for name in ("experiment", "cell", "role", "index"):
            v = getattr(self, name)
            if not isinstance(v, (int, np.integer)) or v < 0:
                raise ValueError(f"seed key field {name} must be a non-negative integer, got {v!r}")

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (int(self.experiment), int(self.cell), int(self.role), int(self.index))

    def seed_sequence(self) -> np.random.SeedSequence:
        return np.random.SeedSequence(entropy=PROJECT_ENTROPY, spawn_key=self.as_tuple())


@dataclass(frozen=True)
class DemandStream:
    """Arrivals of one season. Arrays are aligned and sorted by arrival order."""

    T: int
    period: np.ndarray      # int64, values in 1..T, non-decreasing
    segment: np.ndarray     # int8, SEG_L or SEG_H
    valuation: np.ndarray   # float64, > 0 (currency)
    multiplier: float       # realised stream-level demand multiplier M
    surge: np.ndarray       # bool, length T, True where a surge is active
    seed_key: tuple[int, int, int, int] | None = None

    def __post_init__(self) -> None:
        n = len(self.period)
        if len(self.segment) != n or len(self.valuation) != n:
            raise ValueError("period, segment and valuation must have equal length")
        if n:
            if self.period.min() < 1 or self.period.max() > self.T:
                raise ValueError("arrival periods must lie in 1..T")
            if np.any(np.diff(self.period) < 0):
                raise ValueError("arrivals must be sorted by period")
            if not np.all(np.isfinite(self.valuation)) or np.any(self.valuation < 0):
                raise ValueError("valuations must be finite and non-negative")
            if not np.all(np.isin(self.segment, (SEG_L, SEG_H))):
                raise ValueError("segments must be 0 (L) or 1 (H)")

    @property
    def n_arrivals(self) -> int:
        return int(len(self.period))

    def period_bounds(self) -> np.ndarray:
        """Index bounds b with arrivals of period t in [b[t-1], b[t])."""
        return np.searchsorted(self.period, np.arange(1, self.T + 2), side="left")

    @cached_property
    def prepared(self) -> "PreparedStream":
        """Per-period sorted views, built once and reused by every policy."""
        return PreparedStream.build(self)

    def sha256(self) -> str:
        h = hashlib.sha256()
        h.update(GENERATOR_VERSION.encode())
        h.update(np.int64(self.T).tobytes())
        h.update(np.ascontiguousarray(self.period, dtype=np.int64).tobytes())
        h.update(np.ascontiguousarray(self.segment, dtype=np.int8).tobytes())
        h.update(np.ascontiguousarray(self.valuation, dtype=np.float64).tobytes())
        return h.hexdigest()


class PreparedStream:
    """Per-period lookup tables for the fast simulator.

    For period t (0-based list index t - 1): `order_v`/`order_seg` keep arrival
    order; `sorted_v` holds valuations ascending; `suf_v[i]` and `suf_L[i]` are
    the sum of valuations and the number of L buyers among sorted_v[i:].
    """

    __slots__ = ("order_v", "order_seg", "sorted_v", "suf_v", "suf_L")

    def __init__(self, order_v, order_seg, sorted_v, suf_v, suf_L) -> None:
        self.order_v, self.order_seg = order_v, order_seg
        self.sorted_v, self.suf_v, self.suf_L = sorted_v, suf_v, suf_L

    @classmethod
    def build(cls, s: "DemandStream") -> "PreparedStream":
        b = s.period_bounds()
        ov, os_, sv, sufv, sufl = [], [], [], [], []
        for t in range(s.T):
            v = s.valuation[b[t] : b[t + 1]]
            g = s.segment[b[t] : b[t + 1]]
            order = np.argsort(v, kind="stable")
            vs, gs = v[order], g[order]
            ov.append(v.tolist())
            os_.append(g.tolist())
            sv.append(vs.tolist())
            sufv.append(np.concatenate([np.cumsum(vs[::-1])[::-1], [0.0]]).tolist())
            sufl.append(np.concatenate([np.cumsum((gs == SEG_L)[::-1])[::-1], [0]]).astype(int).tolist())
        return cls(ov, os_, sv, sufv, sufl)

    def n_at_or_above(self, t: int, p: float) -> int:
        vs = self.sorted_v[t - 1]
        return len(vs) - bisect_left(vs, p)


def arrival_profiles(T: int, kind: str) -> tuple[np.ndarray, np.ndarray]:
    """Per-period arrival shares a_L(t), a_H(t), each summing to one.

    "linear": a_L(t) proportional to T + 1 - t (decreasing), a_H(t) proportional
    to t (increasing). "linear_reversed" swaps them (EXP-003 cell 5). "flat" is
    uniform for both. The linear shape is an implementation choice (D-006); the
    draft protocol says only "L decreasing, H increasing".
    """
    t = np.arange(1, T + 1, dtype=float)
    inc = t / t.sum()
    dec = (T + 1 - t) / (T + 1 - t).sum()
    if kind == "linear":
        return dec, inc
    if kind == "linear_reversed":
        return inc, dec
    if kind == "flat":
        flat = np.full(T, 1.0 / T)
        return flat, flat.copy()
    raise ValueError(f"unknown arrival profile {kind!r}")


def surge_mask(rng: np.random.Generator, params: ScenarioParams) -> np.ndarray:
    """Each period starts a surge with probability surge_prob; a surge lasts
    surge_len periods; overlapping surges do not compound."""
    starts = rng.random(params.T) < params.surge_prob
    active = np.zeros(params.T, dtype=bool)
    for s in np.flatnonzero(starts):
        active[s : s + params.surge_len] = True
    return active


def generate_stream(params: ScenarioParams, key: SeedKey) -> DemandStream:
    """Generate one demand stream. Deterministic in (params, key)."""
    rng = np.random.default_rng(key.seed_sequence())
    sm = params.sigma_M
    M = float(rng.lognormal(mean=-0.5 * sm * sm, sigma=sm)) if sm > 0 else 1.0
    surge = surge_mask(rng, params)
    intensity_t = np.where(surge, params.surge_factor, 1.0)
    a_L, a_H = arrival_profiles(params.T, params.arrival_profile)
    A = params.expected_arrivals
    lam = np.stack([
        M * A * params.w_L * a_L * intensity_t,
        M * A * (1.0 - params.w_L) * a_H * intensity_t,
    ])  # shape (2, T)
    counts = rng.poisson(lam)  # shape (2, T)
    medians = (params.m_L, params.m_H)
    periods, segments, vals = [], [], []
    for t in range(params.T):
        nL, nH = int(counts[0, t]), int(counts[1, t])
        n = nL + nH
        if n == 0:
            continue
        seg = np.concatenate([np.full(nL, SEG_L, np.int8), np.full(nH, SEG_H, np.int8)])
        seg = seg[rng.permutation(n)]  # random arrival order within the period
        med = np.where(seg == SEG_L, medians[0], medians[1])
        z = rng.standard_normal(n)
        v = med * np.exp(params.sigma_v * z)
        periods.append(np.full(n, t + 1, np.int64))
        segments.append(seg)
        vals.append(v)
    if periods:
        period = np.concatenate(periods)
        segment = np.concatenate(segments)
        valuation = np.concatenate(vals)
    else:
        period = np.zeros(0, np.int64)
        segment = np.zeros(0, np.int8)
        valuation = np.zeros(0, float)
    return DemandStream(T=params.T, period=period, segment=segment, valuation=valuation,
                        multiplier=M, surge=surge, seed_key=key.as_tuple())


def make_stream(T: int, arrivals: list[tuple[int, int, float]]) -> DemandStream:
    """Build a hand-specified stream from (period, segment, valuation) tuples,
    already in arrival order. Used for golden examples and edge cases."""
    if arrivals:
        p, s, v = zip(*arrivals)
    else:
        p, s, v = (), (), ()
    return DemandStream(T=T, period=np.asarray(p, np.int64), segment=np.asarray(s, np.int8),
                        valuation=np.asarray(v, float), multiplier=1.0,
                        surge=np.zeros(T, bool))
