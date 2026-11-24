<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE: pricing policies in a simulated booking market

**Status: M0 (bootstrap and feasibility), 2026-11-24. No experiments have run and there are no findings.**

**Question.** How do demand and inventory policies affect prices and availability in a simulated market?

**Why it matters.** Sellers of perishable capacity (seats, rooms) change prices as stock and time run out. Theory shows that a well-chosen fixed price can be close to optimal when sales volumes are large. FARE asks, in a transparent and reproducible simulation, what simple dynamic rules change for revenue, availability, price stability and buyers, and how fragile any difference is.

**What exists now.** Control files, a feasibility audit, a targeted literature and dataset review, a draft protocol (not frozen) and three registered, planned experiments. No simulator code yet.

| Experiment | Question | Status |
|---|---|---|
| EXP-001 | Tuned occupancy and demand-responsive rules versus the best fixed price, base scenario | planned (protocol draft, awaiting owner freeze) |
| EXP-002 | Sensitivity to price elasticity and demand-to-capacity tightness | planned (protocol draft, awaiting owner freeze) |
| EXP-003 | Robustness to demand misspecification (can invalidate EXP-001's interpretation) | planned (protocol draft, awaiting owner freeze) |

**Navigation.** `research/protocol.md` (study protocol, draft), `research/experiments/EXP-NNN/protocol.md`, `research/feasibility.md`, `research/literature_review.md`, `research/limitations.md`, `roadmap.md`, `progress.md`.

**Scope and exclusions.** Synthetic data only. No airline or hotel personalisation claims, no live scraping, no actual fare predictions, no claims about proprietary systems. Zero cost: no paid APIs, data, compute or hosting.

**Quick start (development).**

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
```

Experiment commands will be added in M2.

**Licence.** FARE Source-Available Non-Commercial Research License v1.0 (`LicenseRef-FARE-NC-Research-1.0`); see `LICENSE` and `NOTICE.md`. Not an OSI open-source licence. Third-party material keeps its own terms.

**Citation.** See `CITATION.cff`.
