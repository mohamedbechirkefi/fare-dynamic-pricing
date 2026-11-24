# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Market simulator (simulation layer).

In period t the policy posts p_t given (t, x_t). Buyers of period t arrive in
stream order; a buyer buys one unit if v >= p_t and stock remains, otherwise
leaves for good. Unsold units perish after period T (zero salvage).

`simulate` is the production implementation (bisection on per-period sorted
valuations).
`simulate_reference` is a deliberately naive buyer-by-buyer loop used only as a
differential-test oracle. Both raise InvariantViolation on any breach of the
invariants listed in research/protocol.md section 8.
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass

import numpy as np

from .params import ScenarioParams
from .policies import Policy
from .streams import SEG_L, DemandStream


class InvariantViolation(RuntimeError):
    """A simulation invariant was breached: an implementation defect."""


@dataclass(frozen=True)
class SimOutcome:
    """Per-season trajectory and buyer-level aggregates."""

    prices: np.ndarray            # float64, length T: posted price p_t
    sales: np.ndarray             # int64, length T: units sold in period t
    stock: np.ndarray             # int64, length T + 1: x_1 .. x_{T+1}
    arrivals: np.ndarray          # int64, length T: arrivals in period t
    arrivals_with_stock: int      # buyers who found x > 0 at arrival
    revenue: float                # currency
    consumer_surplus: float       # currency, sum of (v - p) over buyers
    buyers_by_segment: tuple[int, int]
    paid_by_segment: tuple[float, float]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise InvariantViolation(msg)


def check_invariants(o: SimOutcome, sp: ScenarioParams, stream: DemandStream) -> None:
    """Stock conservation, non-negative stock, price bounds, no sale when sold
    out, no sale above demand, and accounting identities."""
    T = sp.T
    _check(len(o.prices) == T and len(o.sales) == T and len(o.stock) == T + 1, "trajectory lengths")
    _check(int(o.stock[0]) == sp.C, "x_1 must equal C")
    _check(bool(np.all(o.stock >= 0)), "stock must be non-negative")
    _check(bool(np.all(o.sales >= 0)), "sales must be non-negative")
    _check(bool(np.all(o.stock[1:] == o.stock[:-1] - o.sales)), "per-period stock conservation")
    _check(int(o.sales.sum()) == sp.C - int(o.stock[-1]), "total stock conservation")
    _check(bool(np.all(o.sales <= o.stock[:-1])), "no sale beyond stock (no sale when sold out)")
    _check(bool(np.all(o.sales <= o.arrivals)), "no more sales than arrivals")
    _check(bool(np.all(np.isfinite(o.prices))), "prices must be finite")
    _check(bool(np.all((o.prices >= sp.p_min) & (o.prices <= sp.p_max))), "prices within [p_min, p_max]")
    _check(int(o.arrivals.sum()) == stream.n_arrivals, "arrival accounting")
    _check(0 <= o.arrivals_with_stock <= stream.n_arrivals, "availability accounting")
    _check(sum(o.buyers_by_segment) == int(o.sales.sum()), "buyer accounting")
    rev = float(np.dot(o.prices, o.sales))
    _check(abs(rev - o.revenue) <= 1e-9 * max(1.0, abs(rev)), "revenue identity")
    _check(abs(sum(o.paid_by_segment) - o.revenue) <= 1e-9 * max(1.0, abs(rev)), "payment identity")
    _check(o.consumer_surplus >= -1e-9, "no buyer pays above valuation (surplus >= 0)")


def simulate(stream: DemandStream, sp: ScenarioParams, policy: Policy, *, check: bool = True) -> SimOutcome:
    """Fast simulator. In a period where demand at p_t does not exhaust stock,
    sales, surplus and segment counts follow from sorted valuations by bisection
    and suffix sums; arrival order is scanned only in the period where the last
    unit sells."""
    if stream.T != sp.T:
        raise ValueError(f"stream horizon {stream.T} != scenario horizon {sp.T}")
    T = sp.T
    ctl = policy.controller(sp)
    ps = stream.prepared
    prices = [0.0] * T
    sales = [0] * T
    stock = [0] * (T + 1)
    arrivals = [len(v) for v in ps.order_v]
    x = sp.C
    stock[0] = x
    found = 0
    cs = 0.0
    nL = nH = 0
    paidL = paidH = 0.0
    for t in range(1, T + 1):
        p = float(ctl.price(t, x))
        prices[t - 1] = p
        n = arrivals[t - 1]
        s = 0
        if n and x > 0:
            vs = ps.sorted_v[t - 1]
            i0 = bisect_left(vs, p)
            k = n - i0
            if k < x:  # stock survives the period: every arrival saw stock
                s = k
                found += n
                cs += ps.suf_v[t - 1][i0] - k * p
                l = ps.suf_L[t - 1][i0]
            else:
                l = 0
                ov, og = ps.order_v[t - 1], ps.order_seg[t - 1]
                for j in range(n):
                    v = ov[j]
                    if v >= p:
                        s += 1
                        cs += v - p
                        if og[j] == SEG_L:
                            l += 1
                        if s == x:
                            found += j + 1
                            break
            h = s - l
            nL += l
            nH += h
            paidL += l * p
            paidH += h * p
        sales[t - 1] = s
        x_start = x
        x -= s
        stock[t] = x
        ctl.observe(t, x_start, s)
    pr = np.asarray(prices)
    sa = np.asarray(sales, np.int64)
    out = SimOutcome(prices=pr, sales=sa, stock=np.asarray(stock, np.int64),
                     arrivals=np.asarray(arrivals, np.int64), arrivals_with_stock=found,
                     revenue=float(np.dot(pr, sa)), consumer_surplus=cs, buyers_by_segment=(nL, nH),
                     paid_by_segment=(paidL, paidH))
    if check:
        check_invariants(out, sp, stream)
    return out


def simulate_reference(stream: DemandStream, sp: ScenarioParams, policy: Policy) -> SimOutcome:
    """Naive buyer-by-buyer oracle; slow and obviously correct."""
    T = sp.T
    ctl = policy.controller(sp)
    prices, sales, stock, arrivals = [], [], [sp.C], [0] * T
    x = sp.C
    found, cs = 0, 0.0
    nb, paid = [0, 0], [0.0, 0.0]
    i, n = 0, stream.n_arrivals
    for t in range(1, T + 1):
        p = float(ctl.price(t, x))
        prices.append(p)
        s = 0
        x_start = x
        while i < n and int(stream.period[i]) == t:
            arrivals[t - 1] += 1
            if x > 0:
                found += 1
                v = float(stream.valuation[i])
                if v >= p:
                    x -= 1
                    s += 1
                    cs += v - p
                    g = int(stream.segment[i])
                    nb[g] += 1
                    paid[g] += p
            i += 1
        sales.append(s)
        stock.append(x)
        ctl.observe(t, x_start, s)
    pr = np.asarray(prices)
    sa = np.asarray(sales, np.int64)
    out = SimOutcome(prices=pr, sales=sa, stock=np.asarray(stock, np.int64),
                     arrivals=np.asarray(arrivals, np.int64), arrivals_with_stock=found,
                     revenue=float(np.dot(pr, sa)), consumer_surplus=cs,
                     buyers_by_segment=(nb[0], nb[1]), paid_by_segment=(paid[0], paid[1]))
    check_invariants(out, sp, stream)
    return out
