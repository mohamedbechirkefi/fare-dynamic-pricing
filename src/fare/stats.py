# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Paired uncertainty methods (research/protocol.md sections 5 and 7).

The independent unit is the demand stream; every method here works on the
vector of per-stream paired differences d_i = R(policy, S_i) - R(FIX, S_i).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np


def _as_diffs(d) -> np.ndarray:
    d = np.asarray(d, dtype=float)
    if d.ndim != 1 or len(d) < 2:
        raise ValueError("need a 1-D array of at least two paired differences")
    if not np.all(np.isfinite(d)):
        raise ValueError("paired differences must be finite")
    return d


def bootstrap_ci(d, level: float, n_resamples: int = 10_000, seed: int = 0) -> tuple[float, float]:
    """Stream-level percentile bootstrap interval of the mean paired difference."""
    d = _as_diffs(d)
    if not 0 < level < 1:
        raise ValueError("level must lie in (0, 1)")
    rng = np.random.default_rng(seed)
    n = len(d)
    means = np.empty(n_resamples)
    chunk = 1000
    for s in range(0, n_resamples, chunk):
        m = min(chunk, n_resamples - s)
        idx = rng.integers(0, n, size=(m, n))
        means[s : s + m] = d[idx].mean(axis=1)
    a = (1 - level) / 2
    lo, hi = np.quantile(means, [a, 1 - a])
    return float(lo), float(hi)


def _t_pdf(x: np.ndarray, df: float) -> np.ndarray:
    c = math.lgamma((df + 1) / 2) - math.lgamma(df / 2) - 0.5 * math.log(df * math.pi)
    return np.exp(c - (df + 1) / 2 * np.log1p(x * x / df))


def t_cdf(x: float, df: float) -> float:
    """Student t CDF by composite Simpson integration of the density."""
    if df <= 0:
        raise ValueError("df must be positive")
    if x == 0:
        return 0.5
    ax = abs(x)
    n = 4000
    g = np.linspace(0.0, ax, n + 1)
    f = _t_pdf(g, df)
    h = ax / n
    area = h / 3 * (f[0] + f[-1] + 4 * f[1:-1:2].sum() + 2 * f[2:-1:2].sum())
    return 0.5 + area if x > 0 else 0.5 - area


def t_quantile(q: float, df: float) -> float:
    """Student t quantile by bisection on t_cdf (accurate to about 1e-9)."""
    if not 0 < q < 1:
        raise ValueError("q must lie in (0, 1)")
    if q == 0.5:
        return 0.0
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-10:
            break
    return (lo + hi) / 2


def paired_t_ci(d, level: float) -> tuple[float, float]:
    d = _as_diffs(d)
    n = len(d)
    se = d.std(ddof=1) / math.sqrt(n)
    q = t_quantile(1 - (1 - level) / 2, n - 1)
    m = float(d.mean())
    return m - q * se, m + q * se


def sign_flip_pvalue(d, n_perm: int = 10_000, seed: int = 0) -> float:
    """Two-sided paired sign-flip permutation p-value for mean(d) = 0, with the
    (1 + count) / (1 + n_perm) correction."""
    d = _as_diffs(d)
    rng = np.random.default_rng(seed)
    obs = abs(d.mean())
    count = 0
    chunk = 1000
    for s in range(0, n_perm, chunk):
        m = min(chunk, n_perm - s)
        signs = rng.choice((-1.0, 1.0), size=(m, len(d)))
        count += int(np.count_nonzero(np.abs((signs * d).mean(axis=1)) >= obs - 1e-12))
    return (1 + count) / (1 + n_perm)


def holm(pvalues) -> list[float]:
    """Holm step-down adjusted p-values (monotone, capped at 1)."""
    p = np.asarray(pvalues, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="stable")
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def classify(ci: tuple[float, float], estimate: float, sesoi: float) -> str:
    """Classification of research/protocol.md section 5 (sesoi > 0, absolute)."""
    lo, hi = ci
    if sesoi <= 0:
        raise ValueError("sesoi must be positive")
    if lo > 0 or hi < 0:
        return "detectable_practically_relevant" if abs(estimate) > sesoi else "detectable_below_sesoi"
    if -sesoi < lo and hi < sesoi:
        return "practically_equivalent"
    return "inconclusive"


@dataclass(frozen=True)
class PairedSummary:
    n: int
    mean_diff: float
    sd_diff: float
    d_z: float | None
    boot_ci: tuple[float, float]
    t_ci: tuple[float, float]
    level: float

    def to_dict(self) -> dict:
        return asdict(self)


def summarise(d, level: float, n_resamples: int = 10_000, seed: int = 0) -> PairedSummary:
    d = _as_diffs(d)
    sd = float(d.std(ddof=1))
    if sd == 0.0:
        m = float(d.mean())
        return PairedSummary(len(d), m, 0.0, None, (m, m), (m, m), level)
    return PairedSummary(len(d), float(d.mean()), sd, float(d.mean() / sd),
                         bootstrap_ci(d, level, n_resamples, seed), paired_t_ci(d, level), level)


def normal_quantile(q: float) -> float:
    """Standard normal quantile by bisection on math.erf."""
    if not 0 < q < 1:
        raise ValueError("q must lie in (0, 1)")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def required_n(sd_diff: float, effect: float, alpha: float, power: float) -> int:
    """Normal-approximation sample size for a two-sided paired test."""
    if effect <= 0 or sd_diff < 0:
        raise ValueError("effect must be > 0 and sd_diff >= 0")
    z = normal_quantile(1 - alpha / 2) + normal_quantile(power)
    return int(math.ceil((z * sd_diff / effect) ** 2))
