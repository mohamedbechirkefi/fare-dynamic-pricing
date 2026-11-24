# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
import math

import numpy as np
import pytest

from fare.params import ParameterError, ScenarioParams
from fare.streams import (SEG_H, SEG_L, DemandStream, SeedKey, arrival_profiles, generate_stream,
                          make_stream, surge_mask)


@pytest.mark.parametrize("bad", [
    {"T": 0}, {"T": 2.5}, {"C": -1}, {"kappa": -0.1}, {"w_L": 1.5}, {"m_L": 0.0},
    {"sigma_v": -1.0}, {"surge_prob": 2.0}, {"surge_len": 0}, {"surge_factor": 0.0},
    {"p_min": 0.0}, {"p_min": 100.0, "p_max": 50.0}, {"kappa": float("nan")},
    {"arrival_profile": "zigzag"}, {"demand_scale": float("inf")},
])
def test_invalid_parameters_rejected(bad):
    with pytest.raises(ParameterError):
        ScenarioParams(**bad)


def test_unknown_parameter_rejected():
    with pytest.raises(ParameterError):
        ScenarioParams.from_dict({"kapa": 2.0})


def test_round_trip_and_expected_arrivals():
    sp = ScenarioParams(kappa=1.5, demand_scale=0.8, C=50)
    assert ScenarioParams.from_dict(sp.to_dict()) == sp
    assert sp.expected_arrivals == pytest.approx(60.0)


@pytest.mark.parametrize("kind", ["linear", "linear_reversed", "flat"])
def test_profiles_sum_to_one(kind):
    a, b = arrival_profiles(60, kind)
    assert a.sum() == pytest.approx(1.0) and b.sum() == pytest.approx(1.0)
    assert np.all(a > 0) and np.all(b > 0)


def test_linear_profile_directions():
    aL, aH = arrival_profiles(10, "linear")
    assert np.all(np.diff(aL) < 0) and np.all(np.diff(aH) > 0)
    rL, rH = arrival_profiles(10, "linear_reversed")
    assert np.allclose(rL, aH) and np.allclose(rH, aL)


def test_stream_is_deterministic_in_key():
    sp = ScenarioParams()
    a = generate_stream(sp, SeedKey(1, 0, 0, 3))
    b = generate_stream(sp, SeedKey(1, 0, 0, 3))
    c = generate_stream(sp, SeedKey(1, 0, 1, 3))
    assert a.sha256() == b.sha256()
    assert a.sha256() != c.sha256()
    assert np.array_equal(a.valuation, b.valuation)


def test_stream_structure():
    sp = ScenarioParams()
    s = generate_stream(sp, SeedKey(1, 0, 0, 0))
    assert np.all(np.diff(s.period) >= 0)
    assert s.period.min() >= 1 and s.period.max() <= sp.T
    assert set(np.unique(s.segment)) <= {SEG_L, SEG_H}
    assert np.all(s.valuation > 0)
    b = s.period_bounds()
    assert b[0] == 0 and b[-1] == s.n_arrivals and len(b) == sp.T + 1


def test_mean_arrivals_close_to_design():
    """Across 200 streams, mean arrivals are close to A times the surge uplift
    (each period is in a surge with probability 1 - 0.95^3)."""
    sp = ScenarioParams()
    n = np.array([generate_stream(sp, SeedKey(9, 0, 0, i)).n_arrivals for i in range(200)])
    q = 1 - (1 - sp.surge_prob) ** sp.surge_len
    expected = sp.expected_arrivals * (1 + q * (sp.surge_factor - 1))
    assert abs(n.mean() - expected) / expected < 0.06


def test_segment_order_late_buyers_are_high():
    sp = ScenarioParams(sigma_M=0.0, surge_prob=0.0)
    s = generate_stream(sp, SeedKey(9, 1, 0, 0))
    early = s.segment[s.period <= 20]
    late = s.segment[s.period > 40]
    assert (early == SEG_H).mean() < (late == SEG_H).mean()


def test_zero_demand_stream_is_empty():
    s = generate_stream(ScenarioParams(kappa=0.0), SeedKey(1, 90, 0, 0))
    assert s.n_arrivals == 0


def test_no_shock_multiplier_is_one():
    s = generate_stream(ScenarioParams(sigma_M=0.0, surge_prob=0.0), SeedKey(1, 0, 0, 0))
    assert s.multiplier == 1.0 and not s.surge.any()


def test_surge_mask_lengths():
    sp = ScenarioParams(T=10, surge_prob=1.0, surge_len=3)
    m = surge_mask(np.random.default_rng(0), sp)
    assert m.all() and len(m) == 10


@pytest.mark.parametrize("arr", [
    [(0, 0, 10.0)], [(4, 0, 10.0)], [(2, 0, 1.0), (1, 0, 1.0)], [(1, 2, 10.0)], [(1, 0, -1.0)],
    [(1, 0, float("nan"))],
])
def test_bad_hand_streams_rejected(arr):
    with pytest.raises(ValueError):
        make_stream(3, arr)


@pytest.mark.parametrize("key", [(-1, 0, 0, 0), (1, 0, 0, 1.5)])
def test_bad_seed_key(key):
    with pytest.raises(ValueError):
        SeedKey(*key)


def test_prepared_tables():
    s = make_stream(2, [(1, SEG_L, 50.0), (1, SEG_H, 120.0), (1, SEG_L, 80.0), (2, SEG_H, 10.0)])
    ps = s.prepared
    assert ps.sorted_v[0] == [50.0, 80.0, 120.0]
    assert ps.suf_v[0] == [250.0, 200.0, 120.0, 0.0]
    assert ps.suf_L[0] == [2, 1, 0, 0]
    assert ps.n_at_or_above(1, 80.0) == 2
    assert ps.n_at_or_above(2, 10.0) == 1
    assert math.isclose(sum(ps.order_v[0]), 250.0)
