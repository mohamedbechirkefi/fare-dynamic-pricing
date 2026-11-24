# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""M3 pre-run metric validation (exploratory, not evidence).

Hand-built demand streams with known outcomes; every metric of
research/experiments/EXP-001/protocol.md section 13 (and protocol section 6) is
computed by the production code and compared with the value derived by hand
from the protocol definitions. No generated stream and no evaluation stream is
used. Prints a JSON record; exit status 1 if any check fails.

    PYTHONPATH=src .venv/bin/python experiments/exploratory/metric_validation.py
"""

import json
import math
import sys

import numpy as np

from fare.metrics import compute_metrics
from fare.params import ScenarioParams
from fare.policies import DRP, FIX, OCC
from fare.simulate import simulate, simulate_reference
from fare.stats import classify, holm, summarise
from fare.streams import SEG_H, SEG_L, DemandStream

checks = []


def check(case, name, got, want, tol=1e-9):
    if want is None or got is None:
        ok = got is None and want is None
    else:
        ok = abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))
    checks.append({"case": case, "metric": name, "expected": want, "computed": got, "ok": bool(ok)})


def stream(T, periods, segs, vals):
    return DemandStream(T=T, period=np.array(periods, np.int64), segment=np.array(segs, np.int8),
                        valuation=np.array(vals, float), multiplier=1.0, surge=np.zeros(T, bool))


# Case A: T = 3, C = 2, FIX(100). Period 1: L v=150 buys (surplus 50). Period 2: H v=80 leaves,
# L v=120 buys (surplus 20), stock reaches 0. Period 3: H v=300 finds no stock.
spA = ScenarioParams(T=3, C=2)
sA = stream(3, [1, 2, 2, 3], [SEG_L, SEG_H, SEG_L, SEG_H], [150, 80, 120, 300])
for sim in (simulate, simulate_reference):
    m = compute_metrics(sim(sA, spA, FIX(100.0)), spA)
    case = f"A-{sim.__name__}"
    for k, v in {"revenue": 200, "units_sold": 2, "sell_through": 1.0, "arrivals": 4, "availability": 0.75,
                 "stockout_period": 2, "price_volatility": 0.0, "consumer_surplus": 70, "total_surplus": 270,
                 "mean_price_paid": 100, "mean_price_paid_L": 100, "mean_price_paid_H": None,
                 "buyers_L": 2, "buyers_H": 0}.items():
        check(case, k, m[k], v)

# Case B: no arrivals. Availability is defined as 1; stock never runs out, stock-out period T + 1.
mB = compute_metrics(simulate(stream(3, [], [], []), spA, FIX(100.0)), spA)
for k, v in {"revenue": 0, "sell_through": 0.0, "availability": 1.0, "stockout_period": 4,
             "consumer_surplus": 0, "mean_price_paid": None}.items():
    check("B-no-arrivals", k, mB[k], v)

# Case C: OCC(100, k=1), no sales: p_t = 100 exp(-(t-1)/3); volatility = (1/2)(1/3 + 1/3) = 1/3.
oC = simulate(stream(3, [], [], []), spA, OCC(100.0, 1.0))
for t, p in enumerate(oC.prices, 1):
    check("C-occ-prices", f"p_{t}", p, 100 * math.exp(-(t - 1) / 3))
check("C-occ-volatility", "price_volatility", compute_metrics(oC, spA)["price_volatility"], 1 / 3)

# Case D: DRP(100, eta=1), C = 3, T = 3, no sales. r_hat starts at C/T = 1.
# After t=1: r_hat = 0.7, r* = 3/3 = 1, p_2 = 100 (1.2 / 1.5) = 80.
# After t=2: r_hat = 0.49, r* = 3/2, p_3 = 80 (0.99 / 2.0) = 39.6.
spD = ScenarioParams(T=3, C=3)
oD = simulate(stream(3, [], [], []), spD, DRP(100.0, 1.0))
for t, p in enumerate([100.0, 80.0, 39.6], 1):
    check("D-drp-prices", f"p_{t}", oD.prices[t - 1], p)

# Case E: segment prices. T = 2, C = 5, OCC(100, k=1): p_1 = 100; one sale in t=1 gives
# f = 0.2, e = 0.5, p_2 = 100 exp(-0.3). Buyers: t=1 H v=200; t=2 L v=90 (buys, 90 >= 74.08).
spE = ScenarioParams(T=2, C=5)
mE = compute_metrics(simulate(stream(2, [1, 2], [SEG_H, SEG_L], [200, 90]), spE, OCC(100.0, 1.0)), spE)
p2 = 100 * math.exp(-0.3)
for k, v in {"revenue": 100 + p2, "mean_price_paid_H": 100, "mean_price_paid_L": p2,
             "consumer_surplus": 100 + (90 - p2), "sell_through": 0.4,
             "price_volatility": 0.3, "stockout_period": 3}.items():
    check("E-segments", k, mE[k], v)

# Statistics used by the frozen decision rules. Holm, m = 4: sorted p 0.01, 0.02, 0.04, 0.5
# give 4(0.01) = 0.04, 3(0.02) = 0.06, 2(0.04) = 0.08, 0.5 (monotone).
s = summarise(np.full(10, 5.0), 0.975, 1000, 1)
check("F-stats", "constant-diff mean", s.mean_diff, 5.0)
check("F-stats", "constant-diff boot lo", s.boot_ci[0], 5.0)
for i, (want, got) in enumerate(zip([0.04, 0.08, 0.06, 0.5], holm([0.01, 0.04, 0.02, 0.5]))):
    check("F-stats", f"holm[{i}]", got, want)
cls = {"rel": classify((10, 30), 20, 5), "below": classify((1, 3), 2, 5), "eq": classify((-3, 3), 0, 5),
       "inc": classify((-1, 9), 4, 5)}
expected = {"rel": "detectable_practically_relevant", "below": "detectable_below_sesoi",
            "eq": "practically_equivalent", "inc": "inconclusive"}
for k in cls:
    checks.append({"case": "F-classify", "metric": k, "expected": expected[k], "computed": cls[k],
                   "ok": cls[k] == expected[k]})

out = {"label": "exploratory", "purpose": "M3 metric validation on hand-built known cases",
       "n_checks": len(checks), "n_failed": sum(not c["ok"] for c in checks), "checks": checks}
print(json.dumps(out, indent=1, default=float))
sys.exit(1 if out["n_failed"] else 0)
