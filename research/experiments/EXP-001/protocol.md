<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-001 protocol: tuned dynamic rules versus the best fixed price at the base scenario

**Status: DRAFT v0.1 (2026-11-24). Planned; protocol draft awaiting owner freeze (G-FREEZE).** Not executed. Parameter values are planning proposals. Study-level context: `research/protocol.md`.

## 1. Precise question

At the base scenario, does a tuned occupancy rule (OCC) or a tuned demand-responsive rule (DRP) change expected revenue per selling season relative to the tuned fixed price (FIX), under identical demand streams and equal tuning budgets?

## 2. Mechanism

With a fixed stock and a deadline, the value of a unit depends on remaining stock and remaining time. A fixed price cannot react when a demand shock or a late arrival of high-valuation buyers makes stock scarce (leaving revenue unearned) or when demand is weak (leaving stock to perish). OCC reacts to the gap between the fraction sold and the fraction of time elapsed; DRP reacts to the gap between the observed and the required sales rate. Either can also overreact to noise.

## 3. Rationale from verified sources

Gallego and van Ryzin (1994, Management Science 40(8):999-1020, DOI 10.1287/mnsc.40.8.999; full text opened) formulate finite-horizon pricing of a fixed stock with price-sensitive stochastic demand, show structural monotonicity of the optimal price in stock and remaining time, and prove that simple fixed-price policies are asymptotically optimal as the volume of expected sales tends to infinity. This makes the fixed price a principled baseline and leaves open how much simple, model-free dynamic rules gain or lose at moderate scale with shocks and heterogeneous buyers. Elmaghraby and Keskinocak (2003, Management Science 49(10):1287-1309; abstract opened) review dynamic pricing with inventory considerations and identify perishable, short-run-fixed capacity (airlines, hotels) as the classical setting. See `research/literature_review.md`.

## 4. Competing explanations

- Any measured gain could come from finer tuning resolution, not policy structure (tested by the tuning-grid sensitivity, section 15).
- Any gain could be specific to the tuning distribution (tested in EXP-003).
- Any loss could come from noise-chasing by the dynamic rules rather than from the absence of value in dynamic pricing.

## 5. Hypotheses

For j in {OCC, DRP}: H0_j: Delta_j = 0; H1_j: Delta_j != 0, where Delta_j = E[R(j*, S) - R(FIX*, S)] over evaluation streams S of the base cell.

**What would contradict H1_j:** a Bonferroni-adjusted 97.5% paired bootstrap interval for Delta_j that includes zero.

## 6. Estimand

Delta_j in currency units per selling season, and the relative effect Delta_j / E[R(FIX*, S)], both over the base-cell stream distribution, for policies tuned on independent tuning streams.

## 7. Experimental unit and simulation scope

Unit: one evaluation demand stream (one seed) of the base cell. Scope: the synthetic market of `research/protocol.md` section 3; base parameters T = 60, C = 100, kappa = 2.0, sigma_v = 0.5, sigma_M = 0.25, surge probability 0.05, surge length 3, surge factor 1.8, segment shares 0.7 / 0.3, segment medians 100 / 200, price bounds [30, 600].

## 8. Variables

- Independent: pricing policy family (FIX, OCC, DRP), each at its tuned configuration.
- Dependent: revenue (primary); sell-through, availability, stock-out period, price volatility, consumer surplus proxy, total surplus proxy, mean price paid by segment (secondary).
- Held constant: all scenario parameters; demand stream per unit (common random numbers).

## 9. Treatment, control and baseline

- Control and baseline: FIX(p*), p* chosen from 36 geometric prices in [40, 400] by mean revenue on 100 tuning streams.
- Treatments: OCC(p0*, k*) and DRP(p0*, eta*), each chosen from 36 configurations (9 geometric p0 in [40, 400] times 4 sensitivity values) on the same 100 tuning streams.

## 10. Sampling and seed plan

`numpy.random.SeedSequence(entropy=<fixed project entropy>, spawn_key=(1, cell, role, index))`, experiment 1, cell 0, role 0 (tune) indices 0 to 99, role 1 (eval) indices 0 to 299. Each stream is generated once, serialised with its hash, and replayed under every policy.

## 11. Sample-size rationale

n = 300 evaluation streams: about 89% power for d_z = 0.2 at two-sided alpha = 0.025 per contrast (normal approximation). An exploratory pilot on tuning streams only may revise n before the freeze.

## 12. Fixed compute budget

Tuning: 3 families x 36 configurations x 100 streams = 10,800 runs. Evaluation: 3 x 300 = 900 runs. Tuning-grid sensitivity: 9 x 100 + 300 = 1,200 runs. Wall-clock cap: 15 minutes on the audited laptop; exceeding it is recorded as a deviation, not a reason to cut runs.

## 13. Metric formulas and units

- Revenue R = sum over sales of p_t (currency units).
- Sell-through = (C - x_{T+1}) / C.
- Availability = (arrivals with x > 0 at arrival) / (arrivals); 1 if no arrivals.
- Stock-out period = min{t : x_{t+1} = 0}, or T + 1.
- Price volatility = (1 / (T - 1)) sum_{t=2..T} |ln p_t - ln p_{t-1}|.
- Consumer surplus proxy = sum over buyers (v_i - p_paid,i) (currency units).
- Total surplus proxy = R + consumer surplus proxy.
- Mean price paid by segment = mean p_paid over buyers of that segment (undefined and reported as missing if no buyer).

## 14. Uncertainty method

Stream-level paired percentile bootstrap, 10,000 resamples, fixed seed; 97.5% intervals for the two primary contrasts (Bonferroni), 95% for secondary metrics; paired t intervals as a cross-check; per-stream distributions exported. Classification against SESOI = 1% of mean FIX* revenue as in `research/protocol.md` section 5.

## 15. Sensitivity test inside this experiment

Tuning-grid sensitivity: FIX re-tuned on the same 9 starting prices available to OCC and DRP; Delta_j recomputed. A change of sign or class is reported and the main result is then attributed to grid resolution.

## 16. Exclusion and stopping rules

As `research/protocol.md` section 8: no outcome-based exclusion; failures recorded; any invariant violation stops the experiment and triggers a full rerun after the fix, with a dated deviation note; fixed n, single analysis.

## 17. Anticipated failure modes

- Tuned optimum at the edge of a grid (p* = 40 or 400, or k* or eta* at an extreme): reported; the grid is not extended after seeing evaluation results.
- DRP oscillation (price hitting bounds repeatedly): visible in price volatility and price-path figures.
- Bootstrap intervals degenerate if all paired differences are zero (possible if tuned k* or eta* is tiny): reported as exact equality.

## 18. Smoke checks (exploratory, before the freeze)

Base cell, 5 tuning streams, one hand-set configuration per family, plus edge cases (zero demand, C = 1, all valuations below p_min, kappa = 20). Checks: invariants, nesting (k = 0 and eta = 0 reproduce FIX exactly), runtime. Labelled exploratory; never reported as evidence.

## 19. Reproducibility commands (to be implemented in M2; names are planned, not yet existing)

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
uv run python -m fare.cli smoke --exp EXP-001
uv run python -m fare.cli run --exp EXP-001 --config research/experiments/EXP-001/config.json
uv run python -m fare.cli report --exp EXP-001
```
