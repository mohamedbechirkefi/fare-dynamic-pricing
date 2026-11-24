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
