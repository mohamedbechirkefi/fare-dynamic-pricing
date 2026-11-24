# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
import math

import pytest

from fare.params import ScenarioParams
from fare.policies import DRP, FIX, OCC, PolicyError, policy_from_dict, policy_to_dict


@pytest.mark.parametrize("make", [
    lambda: FIX(0.0), lambda: FIX(-5.0), lambda: FIX(float("nan")), lambda: OCC(100.0, -1.0),
    lambda: OCC(0.0, 1.0), lambda: DRP(100.0, -0.1), lambda: DRP(100.0, 0.5, weight=0.0),
    lambda: DRP(100.0, float("inf")),
])
def test_invalid_policy_parameters(make):
    with pytest.raises(PolicyError):
        make()


def test_policy_dict_round_trip_and_errors():
    for p in (FIX(120.0), OCC(90.0, 2.0), DRP(80.0, 0.5)):
        assert policy_from_dict(policy_to_dict(p)) == p
    with pytest.raises(PolicyError):
        policy_from_dict({"family": "DP", "params": {}})
    with pytest.raises(PolicyError):
        policy_from_dict({"family": "FIX", "params": {"price": 1.0}})


def test_fix_is_clipped_to_bounds():
    sp = ScenarioParams(p_min=30.0, p_max=600.0)
    assert FIX(10.0).controller(sp).price(1, 100) == 30.0
    assert FIX(900.0).controller(sp).price(1, 100) == 600.0


def test_occ_hand_computed():
    sp = ScenarioParams(T=60, C=100)
    c = OCC(100.0, 2.0).controller(sp)
    # t = 31: e = 0.5; x = 30: f = 0.7 -> 100 * exp(2 * 0.2)
    assert c.price(31, 30) == pytest.approx(100.0 * math.exp(0.4))
    # behind schedule lowers the price
    assert c.price(31, 90) == pytest.approx(100.0 * math.exp(2 * (0.1 - 0.5)))
    # clipping
    assert OCC(500.0, 8.0).controller(sp).price(1, 0) == 600.0


def test_drp_hand_computed():
    sp = ScenarioParams(T=3, C=2)
    c = DRP(100.0, 1.0).controller(sp)
    assert c.price(1, 2) == 100.0
    c.observe(1, 2, 1)
    r_hat = 0.3 * 1 + 0.7 * (2 / 3)
    r_star = 2 / 3
    assert c.price(2, 1) == pytest.approx(100.0 * (r_hat + 0.5) / (r_star + 0.5))


def test_drp_moves_in_the_right_direction():
    sp = ScenarioParams(T=10, C=10)
    up = DRP(100.0, 0.5).controller(sp)
    up.observe(1, 10, 5)  # selling faster than required
    down = DRP(100.0, 0.5).controller(sp)
    down.observe(1, 10, 0)  # selling slower than required
    assert up.price(2, 5) > 100.0 > down.price(2, 10)


def test_drp_respects_bounds_under_extreme_feedback():
    sp = ScenarioParams(T=5, C=1000, p_min=30.0, p_max=600.0)
    c = DRP(500.0, 2.0).controller(sp)
    for t in range(1, 6):
        c.observe(t, 1000, 1000)
        assert 30.0 <= c.price(t + 1, 0) <= 600.0
