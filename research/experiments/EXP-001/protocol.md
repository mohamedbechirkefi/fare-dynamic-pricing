<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-001 protocol: tuned dynamic rules versus the best fixed price at the base scenario

**Status: FROZEN v1.0 (owner-approved 2026-11-24). Not yet run.** Owner-approved amendments of 2026-11-24 applied, including the second-round tuning-grid ruling (see `research/protocol.md`, "Amendments before freeze"). Frozen by the owner's approval; hashes in `research/freeze.json` (G-FREEZE). Not executed. Study-level context: `research/protocol.md`.

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

- Control and baseline: FIX(p*), p* chosen from 36 geometric prices in [40, 400] by mean revenue on 500 tuning streams.
- Treatments: OCC(p0*, k*) and DRP(p0*, eta*), each chosen from 36 configurations (6 geometric p0 in [40, 400] times 6 sensitivity values: k in {0.25, 0.5, 1, 2, 4, 8}, eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1.0}) on the same 500 tuning streams.

## 10. Sampling and seed plan

`numpy.random.SeedSequence(entropy=20261124, spawn_key=(1, cell, role, index))`, experiment 1, cell 0, role 0 (tune) indices 0 to 499, role 1 (eval) indices 0 to 3999. Each stream is generated once, serialised with its hash, and replayed under every policy.

## 11. Sample-size rationale

n = 4,000 evaluation streams (owner-approved amendment). The pilot on tuning streams (J-0003) gives SDs of the paired revenue differences of 655 (OCC) and 871 (DRP); the 1% SESOI (about 116) then needs n = 384 and 680 at two-sided alpha = 0.025 and power 0.89 (normal approximation). n = 4,000 covers these with a wide margin for the pilot's own uncertainty (50 streams).

## 12. Fixed compute budget

Tuning: 3 families x 36 configurations x 500 streams = 54,000 runs. Evaluation: 3 x 4,000 = 12,000 runs. Tuning-grid sensitivity: 6 x 500 + 4,000 = 7,000 runs. Total 73,000 runs (`fare.cli run --plan`). Wall-clock cap: 15 minutes on the audited laptop; exceeding it is recorded as a deviation, not a reason to cut runs.

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

Tuning-grid sensitivity: FIX re-tuned on the same 6 starting prices available to OCC and DRP (arm FIX6); Delta_j recomputed. A change of sign or class is reported and the main result is then attributed to grid resolution.

## 16. Exclusion and stopping rules

As `research/protocol.md` section 8: no outcome-based exclusion; failures recorded; any invariant violation stops the experiment and triggers a full rerun after the fix, with a dated deviation note; fixed n, single analysis.

## 17. Anticipated failure modes

- Tuned optimum at the edge of a grid (p* or p0* = 40 or 400, k* = 0.25 or 8, eta* = 0.025 or 1.0): reported as a finding under the grid-edge rule of `research/protocol.md` section 4 (a DRP lower edge is read as a rule close to eta = 0, which is the fixed price); the grid is not extended after the freeze.
- DRP oscillation (price hitting bounds repeatedly): visible in price volatility and price-path figures.
- Bootstrap intervals degenerate if all paired differences are zero (possible if tuned k* or eta* is tiny): reported as exact equality.

## 18. Smoke checks (exploratory, before the freeze)

Base cell, 5 tuning streams, one hand-set configuration per family, plus edge cases (zero demand, C = 1, all valuations below p_min, kappa = 20). Checks: invariants, nesting (k = 0 and eta = 0 reproduce FIX exactly), runtime. Labelled exploratory; never reported as evidence.

## 19. Reproducibility commands

Run from the repository root. The package is imported from `src/` (`PYTHONPATH=src`); `UV` is `/Users/bechir/research/labs/.tools/py/bin/uv` on the owner's machine.

```
export PYTHONPATH=src
$UV sync --frozen --python /usr/local/bin/python3
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli test
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli smoke
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --plan --config research/experiments/EXP-001/config.json
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --config research/experiments/EXP-001/config.json
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli report --result results/confirmatory/<run_set_id>/result.json --pdf
```

`run` writes `results/confirmatory/<run_set_id>/` (result.json, run_manifest.json, config.json) and refuses the config unless the protocol, the main protocol and this exact config are recorded as frozen (`research/experiment_registry.csv`, `research/freeze.json`).

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24.md`, FARE section); applied in draft v0.2 (decision D-008).

1. Stream counts: 500 tuning and 4,000 evaluation streams (sections 9 to 12). Applied.
2. Tuning grids: not applied in the first round (could not be applied as written); resolved in the second round below.
3. Entropy pinned at 20261124 (section 10); other pinned choices in `research/protocol.md` section 13. Applied.
4. Commands: section 19 names the implemented CLI. Applied.

## Amendments before freeze, second round (owner-approved 2026-11-24)

Owner answer "Approve all", 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24b.md`, section 2): "Keep the widened grids within the equal tuning budget. Report optima on a grid edge as a finding (a DRP responsiveness of 0 means the dynamic rule reduces to a fixed price). Freeze." Applied before any confirmatory data (decision D-009).

5. Tuning grids widened within the equal budget (section 9), sensitivity arm FIX6 (section 15), run counts updated (section 12). Applied.
6. Grid-edge optima reported as findings (section 17; rule in `research/protocol.md` section 4). Applied.
