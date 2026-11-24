# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Simulator: golden examples, invariants, edge states and differential tests."""

import dataclasses
import math

import numpy as np
import pytest
from hypothesis import given, settings

from conftest import market
from fare.metrics import compute_metrics
from fare.params import ScenarioParams
from fare.policies import DRP, FIX, OCC
from fare.simulate import InvariantViolation, check_invariants, simulate, simulate_reference
from fare.streams import SEG_H, SEG_L, SeedKey, generate_stream, make_stream

GOLD_SP = ScenarioParams(T=3, C=2, p_min=30.0, p_max=600.0)
GOLD_STREAM = make_stream(3, [(1, SEG_L, 50.0), (1, SEG_H, 120.0),
                              (2, SEG_L, 150.0), (2, SEG_L, 90.0), (2, SEG_H, 200.0),
                              (3, SEG_H, 300.0)])


@pytest.mark.parametrize("sim", [simulate, simulate_reference])
def test_golden_fix(sim):
    o = sim(GOLD_STREAM, GOLD_SP, FIX(100.0))
    m = compute_metrics(o, GOLD_SP)
    assert o.prices.tolist() == [100.0, 100.0, 100.0]
    assert o.sales.tolist() == [1, 1, 0]
    assert o.stock.tolist() == [2, 1, 0, 0]
    assert m["revenue"] == 200.0
    assert m["consumer_surplus"] == pytest.approx(20.0 + 50.0)
    assert m["availability"] == pytest.approx(3 / 6)
    assert m["stockout_period"] == 2
    assert m["sell_through"] == 1.0
    assert m["price_volatility"] == 0.0
    assert (m["buyers_L"], m["buyers_H"]) == (1, 1)
    assert m["mean_price_paid_L"] == 100.0 and m["mean_price_paid_H"] == 100.0


@pytest.mark.parametrize("sim", [simulate, simulate_reference])
def test_golden_occ(sim):
    o = sim(GOLD_STREAM, GOLD_SP, OCC(100.0, 1.0))
    p2 = 100.0 * math.exp(0.5 - 1 / 3)
    p3 = 100.0 * math.exp(1.0 - 2 / 3)
    assert o.prices == pytest.approx([100.0, p2, p3])
    assert o.sales.tolist() == [1, 1, 0]
    assert o.revenue == pytest.approx(100.0 + p2)
    assert o.consumer_surplus == pytest.approx(20.0 + 150.0 - p2)
    m = compute_metrics(o, GOLD_SP)
    vol = (abs(math.log(p2 / 100.0)) + abs(math.log(p3 / p2))) / 2
    assert m["price_volatility"] == pytest.approx(vol)


@pytest.mark.parametrize("sim", [simulate, simulate_reference])
def test_golden_drp(sim):
    o = sim(GOLD_STREAM, GOLD_SP, DRP(100.0, 1.0))
    r_hat = 0.3 + 0.7 * (2 / 3)
    p2 = 100.0 * (r_hat + 0.5) / (2 / 3 + 0.5)
    assert o.prices[:2] == pytest.approx([100.0, p2])
    assert o.revenue == pytest.approx(100.0 + p2)


def test_no_demand_state():
    sp = ScenarioParams(T=5, C=4)
    for pol in (FIX(100.0), OCC(100.0, 2.0), DRP(100.0, 1.0)):
        o = simulate(make_stream(5, []), sp, pol)
        m = compute_metrics(o, sp)
        assert m["revenue"] == 0.0 and m["units_sold"] == 0
        assert m["availability"] == 1.0
        assert m["stockout_period"] == 6
        assert m["mean_price_paid"] is None and m["mean_price_paid_L"] is None
        assert o.stock.tolist() == [4] * 6


def test_drp_lowers_price_without_demand():
    sp = ScenarioParams(T=10, C=10)
    o = simulate(make_stream(10, []), sp, DRP(200.0, 1.0))
    assert np.all(np.diff(o.prices) <= 0) and o.prices[-1] < 200.0


def test_sold_out_state():
    sp = ScenarioParams(T=4, C=2)
    s = make_stream(4, [(1, SEG_H, 500.0)] * 5 + [(2, SEG_H, 500.0), (4, SEG_L, 500.0)])
    for pol in (FIX(100.0), OCC(100.0, 3.0), DRP(100.0, 1.0)):
        for sim in (simulate, simulate_reference):
            o = sim(s, sp, pol)
            m = compute_metrics(o, sp)
            assert o.sales.tolist() == [2, 0, 0, 0]
            assert o.stock.tolist() == [2, 0, 0, 0, 0]
            assert m["stockout_period"] == 1
            assert m["availability"] == pytest.approx(2 / 7)


def test_zero_capacity():
    sp = ScenarioParams(T=3, C=0)
    o = simulate(make_stream(3, [(1, 0, 500.0)]), sp, OCC(100.0, 1.0))
    m = compute_metrics(o, sp)
    assert m["revenue"] == 0.0 and m["sell_through"] == 0.0 and m["availability"] == 0.0


def test_valuation_equal_to_price_buys():
    sp = ScenarioParams(T=1, C=1)
    o = simulate(make_stream(1, [(1, 0, 100.0)]), sp, FIX(100.0))
    assert o.sales.tolist() == [1] and o.consumer_surplus == 0.0


@given(market())
@settings(max_examples=400, deadline=None)
def test_invariants_and_differential(case):
    """Stock conservation, price bounds, no sale when sold out, and agreement of
    the fast simulator with the naive buyer-by-buyer oracle."""
    sp, stream, pol = case
    a = simulate(stream, sp, pol)
    b = simulate_reference(stream, sp, pol)
    assert np.all(a.prices >= sp.p_min) and np.all(a.prices <= sp.p_max)
    assert int(a.sales.sum()) == sp.C - int(a.stock[-1])
    assert np.all(a.stock >= 0)
    assert np.array_equal(a.prices, b.prices)
    assert np.array_equal(a.sales, b.sales)
    assert np.array_equal(a.stock, b.stock)
    assert a.arrivals_with_stock == b.arrivals_with_stock
    assert a.buyers_by_segment == b.buyers_by_segment
    assert a.consumer_surplus == pytest.approx(b.consumer_surplus, rel=1e-12, abs=1e-9)
    assert a.revenue == pytest.approx(b.revenue, rel=1e-12, abs=1e-9)


@given(market())
@settings(max_examples=200, deadline=None)
def test_nesting_is_exact(case):
    """k = 0 and eta = 0 reproduce FIX(p0) bit for bit."""
    sp, stream, pol = case
    p0 = pol.p if isinstance(pol, FIX) else pol.p0
    f = simulate(stream, sp, FIX(p0))
    for other in (OCC(p0, 0.0), DRP(p0, 0.0)):
        o = simulate(stream, sp, other)
        assert np.array_equal(o.prices, f.prices) and np.array_equal(o.sales, f.sales)
        assert o.revenue == f.revenue and o.consumer_surplus == f.consumer_surplus


@pytest.mark.parametrize("seed", range(20))
def test_differential_on_generated_streams(seed):
    sp = ScenarioParams()
    s = generate_stream(sp, SeedKey(7, 0, 0, seed))
    for pol in (FIX(40.0), FIX(150.0), OCC(60.0, 4.0), DRP(300.0, 1.0), DRP(100.0, 0.1)):
        a, b = simulate(s, sp, pol), simulate_reference(s, sp, pol)
        assert np.array_equal(a.sales, b.sales) and np.array_equal(a.prices, b.prices)
        assert a.arrivals_with_stock == b.arrivals_with_stock


@pytest.mark.parametrize("over", [
    {"kappa": 20.0}, {"kappa": 0.01}, {"C": 1}, {"T": 1}, {"sigma_v": 0.0}, {"sigma_v": 3.0},
    {"p_min": 100.0, "p_max": 100.0}, {"surge_prob": 1.0}, {"w_L": 0.0}, {"w_L": 1.0},
    {"m_L": 5.0, "m_H": 5.0, "sigma_v": 0.1},
])
def test_extreme_parameters_keep_invariants(over):
    sp = ScenarioParams(**over)
    s = generate_stream(sp, SeedKey(8, 0, 0, 0))
    for pol in (FIX(150.0), OCC(150.0, 4.0), DRP(150.0, 1.0)):
        o = simulate(s, sp, pol)  # raises InvariantViolation on any breach
        compute_metrics(o, sp)


def test_all_valuations_below_price_floor_sell_nothing():
    sp = ScenarioParams(m_L=5.0, m_H=5.0, sigma_v=0.1)
    s = generate_stream(sp, SeedKey(8, 1, 0, 0))
    assert s.valuation.max() < sp.p_min
    for pol in (FIX(30.0), OCC(30.0, 4.0), DRP(30.0, 1.0)):
        assert simulate(s, sp, pol).sales.sum() == 0


def test_invariant_checker_detects_corruption():
    o = simulate(GOLD_STREAM, GOLD_SP, FIX(100.0))
    bad_stock = dataclasses.replace(o, stock=np.array([2, 1, 1, 0]))
    bad_price = dataclasses.replace(o, prices=np.array([100.0, 700.0, 100.0]))
    bad_sale = dataclasses.replace(o, sales=np.array([1, 1, 1]), stock=np.array([2, 1, 0, -1]))
    bad_rev = dataclasses.replace(o, revenue=999.0)
    for bad in (bad_stock, bad_price, bad_sale, bad_rev):
        with pytest.raises(InvariantViolation):
            check_invariants(bad, GOLD_SP, GOLD_STREAM)


def test_horizon_mismatch_rejected():
    with pytest.raises(ValueError):
        simulate(make_stream(2, []), ScenarioParams(T=3), FIX(100.0))
