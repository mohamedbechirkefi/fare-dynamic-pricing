# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Per-season metrics (research/experiments/EXP-001/protocol.md section 13).

All metrics are per evaluation stream. Units: currency for revenue, surplus and
prices; dimensionless for sell-through, availability and volatility; periods
for the stock-out period.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from .params import ScenarioParams
from .simulate import SimOutcome

METRIC_NAMES = (
    "revenue", "units_sold", "sell_through", "arrivals", "availability", "stockout_period",
    "price_volatility", "consumer_surplus", "total_surplus", "mean_price_paid",
    "mean_price_paid_L", "mean_price_paid_H", "buyers_L", "buyers_H",
)


def price_volatility(prices: np.ndarray) -> float:
    """(1 / (T - 1)) * sum_{t=2..T} |ln p_t - ln p_{t-1}|; 0 when T = 1."""
    if len(prices) < 2:
        return 0.0
    lp = np.log(prices)
    return float(np.abs(np.diff(lp)).sum() / (len(prices) - 1))


def stockout_period(stock: np.ndarray, T: int) -> int:
    """min{t : x_{t+1} = 0}, or T + 1 if stock never reaches zero during the
    season. With C = 0 the stock is zero before period 1; this returns 1."""
    zero = np.flatnonzero(stock[1:] == 0)
    return int(zero[0]) + 1 if len(zero) else T + 1


def _mean_or_none(total: float, n: int) -> float | None:
    return total / n if n > 0 else None


def compute_metrics(o: SimOutcome, sp: ScenarioParams) -> dict[str, Any]:
    units = int(o.sales.sum())
    arrivals = int(o.arrivals.sum())
    revenue = float(o.revenue)
    m = {
        "revenue": revenue,
        "units_sold": units,
        "sell_through": units / sp.C if sp.C > 0 else 0.0,
        "arrivals": arrivals,
        "availability": o.arrivals_with_stock / arrivals if arrivals > 0 else 1.0,
        "stockout_period": stockout_period(o.stock, sp.T),
        "price_volatility": price_volatility(o.prices),
        "consumer_surplus": float(o.consumer_surplus),
        "total_surplus": revenue + float(o.consumer_surplus),
        "mean_price_paid": _mean_or_none(revenue, units),
        "mean_price_paid_L": _mean_or_none(o.paid_by_segment[0], o.buyers_by_segment[0]),
        "mean_price_paid_H": _mean_or_none(o.paid_by_segment[1], o.buyers_by_segment[1]),
        "buyers_L": int(o.buyers_by_segment[0]),
        "buyers_H": int(o.buyers_by_segment[1]),
    }
    for k, v in m.items():
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError(f"metric {k} is not finite: {v}")
    return m


def purchase_probability(sp: ScenarioParams, p: float) -> float:
    """P(v >= p) for a buyer drawn from the segment mixture (weights w_L, 1 - w_L)."""
    if p <= 0:
        raise ValueError("price must be positive")
    if sp.sigma_v == 0:
        return sp.w_L * float(sp.m_L >= p) + (1 - sp.w_L) * float(sp.m_H >= p)
    s = sp.sigma_v * math.sqrt(2.0)
    surv = lambda m: 0.5 * math.erfc((math.log(p) - math.log(m)) / s)
    return sp.w_L * surv(sp.m_L) + (1 - sp.w_L) * surv(sp.m_H)


def purchase_elasticity(sp: ScenarioParams, p: float, h: float = 1e-4) -> float | None:
    """Point elasticity d ln P(v >= p) / d ln p by central difference in ln p
    (EXP-002 protocol section 7). None when undefined (P = 0 or sigma_v = 0)."""
    if sp.sigma_v == 0:
        return None
    up, dn = purchase_probability(sp, p * math.exp(h)), purchase_probability(sp, p * math.exp(-h))
    if up <= 0 or dn <= 0:
        return None
    return (math.log(up) - math.log(dn)) / (2 * h)
