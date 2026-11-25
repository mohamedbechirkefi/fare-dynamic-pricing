<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE: pricing policies in a simulated booking market

**Status: M4 (interpretation) done locally on 2026-11-25. The frozen matrix ran in full (M3, 925,000 runs, 0 failed); experiment reports, evidence audit and a preprint-draft manuscript exist. All results are simulated. The README findings section, the demo and the articles are prepared in M5. Nothing has been published.**

**Question.** How do demand and inventory policies affect prices and availability in a simulated market?

**Why it matters.** Sellers of perishable capacity (seats, rooms) change prices as stock and time run out. Theory shows that a well-chosen fixed price can be close to optimal when sales volumes are large. FARE asks, in a transparent and reproducible simulation, what simple dynamic rules change for revenue, availability, price stability and buyers, and how fragile any difference is.

**What exists now.** Control files, a feasibility audit, a targeted literature and dataset review, a protocol frozen as v1.0 (`research/freeze.json`) and three registered, frozen experiments. Also implemented: the core package `src/fare/`, with a demand-stream generator, the fixed-price baseline, occupancy and demand-responsive rules, a simulator with invariant checks and a reference oracle, metrics, equal-budget tuning, paired statistics, a runner, a JSON result schema, run manifests, a freeze guard and a report generator, plus a number-trace audit tool. 147 tests pass (2026-11-25).

| Experiment | Question | Status |
|---|---|---|
| EXP-001 | Tuned occupancy and demand-responsive rules versus the best fixed price, base scenario | confirmatory, complete; report `research/experiments/EXP-001/report.md` |
| EXP-002 | Sensitivity to price elasticity and demand-to-capacity tightness | confirmatory, complete; report `research/experiments/EXP-002/report.md` |
| EXP-003 | Robustness to demand misspecification (can invalidate EXP-001's interpretation) | confirmatory, complete; report `research/experiments/EXP-003/report.md` |

**Navigation.** `research/paper/manuscript.md` (preprint draft, not peer-reviewed), `research/publication/evidence_audit.md`, `research/protocol.md` (study protocol, frozen v1.0), `research/experiments/EXP-NNN/protocol.md`, `research/feasibility.md`, `research/literature_review.md`, `research/limitations.md`, `roadmap.md`, `progress.md`.

**Scope and exclusions.** Synthetic data only. No airline or hotel personalisation claims, no live scraping, no actual fare predictions, no claims about proprietary systems. Zero cost: no paid APIs, data, compute or hosting.

**Quick start (development).**

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen --python /usr/local/bin/python3
export PYTHONPATH=src
uv run --frozen python -m fare.cli test                     # test suite
uv run --frozen python -m fare.cli smoke                    # exploratory smoke run -> results/exploratory/
uv run --frozen python -m fare.cli run --plan --config research/experiments/EXP-001/config.json
uv run --frozen python -m fare.cli report --result results/exploratory/<run_set_id>/result.json
```

`run` accepts the frozen confirmatory configs in `research/experiments/EXP-NNN/config.json` only while they, the protocols and `research/freeze.json` agree; any changed config or protocol is refused.

**Licence.** FARE Source-Available Non-Commercial Research License v1.0 (`LicenseRef-FARE-NC-Research-1.0`); see `LICENSE` and `NOTICE.md`. Not an OSI open-source licence. Third-party material keeps its own terms.

**Citation.** See `CITATION.cff`.
