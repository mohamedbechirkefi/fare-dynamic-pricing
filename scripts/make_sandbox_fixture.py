# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Write the fixture that checks the browser sandbox against the Python engine.

Output: demo/src/fixtures/engine_fixture.json, read by demo/src/engine.test.ts.

1. Exact cases. Demand streams from the Python generator (keys with
   experiment number 900, outside the registered experiments 1 to 3, so no
   research stream is reused) and two hand-built streams, each simulated by
   fare.simulate.simulate under several policies. The TypeScript port replays
   the same arrivals and must reproduce posted prices, sales, stock and the
   metrics within a relative tolerance of 1e-9 (integers exactly).
2. Distribution check. Summary statistics of 1,000 Python streams per
   scenario (arrivals and FIX revenue). The TypeScript generator uses a
   different random-number generator, so only distributions can agree; the
   test allows 4 combined standard errors.

Compute: about four seconds on one core. Deterministic; no timestamps.
Usage: PYTHONPATH=src .venv/bin/python scripts/make_sandbox_fixture.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fare.metrics import compute_metrics  # noqa: E402
from fare.params import ScenarioParams  # noqa: E402
from fare.policies import DRP, FIX, OCC, policy_to_dict  # noqa: E402
from fare.simulate import simulate  # noqa: E402
from fare.streams import SeedKey, generate_stream, make_stream  # noqa: E402

OUT = ROOT / "demo" / "src" / "fixtures" / "engine_fixture.json"
FIXTURE_EXPERIMENT = 900
N_DIST = 1000

SCENARIOS = {
    "base": {},
    "loose": {"kappa": 1.0, "sigma_v": 1.0},
    "tight-reversed": {"kappa": 4.0, "sigma_v": 0.25, "arrival_profile": "linear_reversed"},
    "no-shocks-low": {"sigma_M": 0.0, "surge_prob": 0.0, "demand_scale": 0.6},
}
POLICIES = [FIX(139.61019515838322), OCC(159.24286822139882, 4.0), DRP(100.47545726038321, 0.1),
            OCC(120.0, 0.0), DRP(120.0, 0.0), DRP(250.0, 1.0), OCC(40.0, 8.0), FIX(700.0)]


def case(name: str, sp: ScenarioParams, stream) -> dict:
    out = {"name": name, "scenario": sp.to_dict(), "T": stream.T,
           "arrivals": [[int(p), int(g), float(v)] for p, g, v in zip(stream.period, stream.segment, stream.valuation)],
           "runs": []}
    for pol in POLICIES:
        o = simulate(stream, sp, pol)
        m = compute_metrics(o, sp)
        out["runs"].append({"policy": policy_to_dict(pol), "prices": [float(x) for x in o.prices],
                            "sales": [int(x) for x in o.sales], "stock": [int(x) for x in o.stock],
                            "metrics": {k: m[k] for k in ("revenue", "units_sold", "sell_through", "availability",
                                                          "stockout_period", "price_volatility", "consumer_surplus",
                                                          "mean_price_paid")}})
    return out


def moments(xs: list[float]) -> dict:
    n = len(xs)
    mu = sum(xs) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (n - 1))
    return {"n": n, "mean": mu, "sd": sd}


def main() -> int:
    cases = []
    for ci, (name, scen) in enumerate(SCENARIOS.items()):
        sp = ScenarioParams.from_dict(scen)
        for i in range(2):
            cases.append(case(f"{name}-stream{i}", sp, generate_stream(sp, SeedKey(FIXTURE_EXPERIMENT, ci, 0, i))))
    sp = ScenarioParams(T=4, C=3)
    cases.append(case("hand-sellout", sp, make_stream(4, [(1, 0, 150.0), (1, 1, 90.0), (2, 1, 400.0), (2, 0, 141.0),
                                                           (2, 0, 200.0), (4, 1, 500.0)])))
    cases.append(case("hand-no-demand", sp, make_stream(4, [])))
    dist = []
    for ci, (name, scen) in enumerate(SCENARIOS.items()):
        sp = ScenarioParams.from_dict(scen)
        arr, rev, val = [], [], []
        for i in range(N_DIST):
            s = generate_stream(sp, SeedKey(FIXTURE_EXPERIMENT, 50 + ci, 0, i))
            arr.append(float(s.n_arrivals))
            rev.append(simulate(s, sp, POLICIES[0], check=False).revenue)
            if s.n_arrivals:
                val.append(float(s.valuation.mean()))
        dist.append({"name": name, "scenario": sp.to_dict(), "fix_policy": policy_to_dict(POLICIES[0]),
                     "arrivals": moments(arr), "fix_revenue": moments(rev), "mean_valuation": moments(val)})
    doc = {"generator": "scripts/make_sandbox_fixture.py", "engine": "fare.simulate.simulate, fare.streams.generate_stream",
           "tolerance_relative": 1e-9, "distribution_z_max": 4.0, "cases": cases, "distribution": dist}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, separators=(",", ":"), allow_nan=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes, {len(cases)} cases, {len(dist)} distributions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
