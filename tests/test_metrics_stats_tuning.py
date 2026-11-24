# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
import math

import numpy as np
import pytest

from fare.metrics import price_volatility, stockout_period
from fare.params import ScenarioParams
from fare.policies import DRP, FIX, OCC
from fare.stats import (bootstrap_ci, classify, holm, normal_quantile, paired_t_ci, required_n,
                        sign_flip_pvalue, summarise, t_cdf, t_quantile)
from fare.streams import SeedKey, generate_stream
from fare.tuning import geometric, grid, revenue_matrix, select, tune


def test_price_volatility_hand():
    assert price_volatility(np.array([100.0, 200.0, 100.0])) == pytest.approx(math.log(2))
    assert price_volatility(np.array([50.0])) == 0.0


def test_stockout_period():
    assert stockout_period(np.array([3, 2, 0, 0]), 3) == 2
    assert stockout_period(np.array([3, 2, 1, 1]), 3) == 4


def test_t_quantiles_against_tables():
    assert t_quantile(0.975, 10) == pytest.approx(2.228138852, abs=1e-6)
    assert t_quantile(0.975, 1) == pytest.approx(12.70620474, abs=1e-4)
    assert t_quantile(0.025, 29) == pytest.approx(-2.045229642, abs=1e-6)
    assert t_cdf(0.0, 5) == 0.5


def test_normal_quantile_and_required_n():
    assert normal_quantile(0.975) == pytest.approx(1.959963985, abs=1e-8)
    # n = ((z_.9875 + z_.89) * sd / effect)^2 with sd = effect / 0.2
    n = required_n(sd_diff=5.0, effect=1.0, alpha=0.025, power=0.89)
    assert 290 <= n <= 310
    with pytest.raises(ValueError):
        required_n(1.0, 0.0, 0.05, 0.8)


def test_bootstrap_constant_and_deterministic():
    d = np.full(30, 2.5)
    assert bootstrap_ci(d, 0.95, 500, 1) == (2.5, 2.5)
    rng = np.random.default_rng(3)
    x = rng.normal(1.0, 1.0, 200)
    a = bootstrap_ci(x, 0.95, 2000, 11)
    assert a == bootstrap_ci(x, 0.95, 2000, 11)
    lo, hi = paired_t_ci(x, 0.95)
    assert abs(a[0] - lo) < 0.05 and abs(a[1] - hi) < 0.05


def test_bootstrap_coverage_differential():
    """Differential check against the t interval on normal data: over 200
    replicates both 95% intervals cover the true mean at similar rates."""
    rng = np.random.default_rng(5)
    cb = ct = 0
    for i in range(200):
        x = rng.normal(0.3, 1.0, 60)
        lo, hi = bootstrap_ci(x, 0.95, 1000, i)
        cb += lo <= 0.3 <= hi
        lo, hi = paired_t_ci(x, 0.95)
        ct += lo <= 0.3 <= hi
    assert 0.88 <= cb / 200 <= 0.99 and 0.88 <= ct / 200 <= 0.99


@pytest.mark.parametrize("bad", [[1.0], [[1.0, 2.0]], [1.0, float("nan")]])
def test_stats_reject_bad_input(bad):
    with pytest.raises(ValueError):
        bootstrap_ci(bad, 0.95)


def test_sign_flip():
    assert sign_flip_pvalue(np.zeros(20), 999, 0) == 1.0
    assert sign_flip_pvalue(np.full(20, 1.0), 999, 0) < 0.01


def test_holm():
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, 0.9]) == pytest.approx([1.0, 1.0])


@pytest.mark.parametrize("ci,est,cls", [
    ((5.0, 20.0), 12.0, "detectable_practically_relevant"),
    ((1.0, 6.0), 3.0, "detectable_below_sesoi"),
    ((-4.0, 4.0), 0.0, "practically_equivalent"),
    ((-4.0, 30.0), 8.0, "inconclusive"),
    ((-20.0, -11.0), -15.0, "detectable_practically_relevant"),
])
def test_classify(ci, est, cls):
    assert classify(ci, est, 10.0) == cls


def test_summarise_zero_variance():
    s = summarise(np.zeros(10), 0.95, 100)
    assert s.sd_diff == 0.0 and s.d_z is None and s.boot_ci == (0.0, 0.0)


def test_grids():
    for fam in ("FIX", "OCC", "DRP"):
        g = grid(fam)
        assert len(g) == 36
    f = grid("FIX")
    assert f[0].p == pytest.approx(40.0) and f[-1].p == pytest.approx(400.0)
    assert geometric(40, 400, 9)[4] == pytest.approx(math.sqrt(40 * 400))
    o = grid("OCC")
    assert (o[0].p0, o[0].k, o[1].k) == (pytest.approx(40.0), 0.5, 1.0)
    with pytest.raises(ValueError):
        grid("DP")


def test_select_ties_and_edges():
    cfgs = [FIX(50.0), FIX(100.0), FIX(200.0)]
    R = np.array([[1.0, 1.0], [3.0, 3.0], [3.0, 3.0]])
    tr = select("FIX", cfgs, R)
    assert tr.best_index == 1 and not tr.at_grid_edge
    tr = select("FIX", cfgs, np.array([[5.0], [1.0], [1.0]]))
    assert tr.best_index == 0 and tr.at_grid_edge
    occ = [OCC(p0, k) for p0 in (50.0, 100.0, 200.0) for k in (0.5, 1.0, 2.0)]
    R = np.zeros((9, 1))
    R[4, 0] = 9.0  # OCC(100, 1): interior in both dimensions
    assert select("OCC", occ, R).best_index == 4 and not select("OCC", occ, R).at_grid_edge
    R = np.zeros((9, 1))
    R[5, 0] = 9.0  # OCC(100, 2): k at the grid edge
    assert select("OCC", occ, R).at_grid_edge


def test_tuning_picks_the_best_mean():
    sp = ScenarioParams()
    streams = [generate_stream(sp, SeedKey(5, 0, 0, i)) for i in range(4)]
    tr = tune("FIX", streams, sp)
    R = revenue_matrix(grid("FIX"), streams, sp)
    assert tr.best_index == int(np.argmax(R.mean(axis=1)))
    assert tr.mean_revenue[tr.best_index] == pytest.approx(R.mean(axis=1).max())
