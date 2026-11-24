<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-002 protocol: sensitivity to price elasticity and demand-to-capacity tightness

**Status: DRAFT v0.1 (2026-11-24). Planned; protocol draft awaiting owner freeze (G-FREEZE).** Not executed. Depends on EXP-001 code and analysis pipeline (not on its results).

## 1. Precise question

How do the paired revenue differences Delta_OCC and Delta_DRP (relative to the tuned fixed price), and the secondary metrics, vary with buyer valuation dispersion (which sets price elasticity) and with the ratio of expected arrivals to capacity?

## 2. Mechanism

With low valuation dispersion (high elasticity near the median), small price changes move demand strongly, so a dynamic rule's adjustments matter more and errors cost more. With loose capacity (kappa = 1.0) stock rarely binds and the value of reacting to scarcity is small; with tight capacity (kappa = 4.0) scarcity is frequent and timing of high-valuation arrivals matters.

## 3. Rationale

Gallego and van Ryzin (1994) show that the optimal price depends on stock and remaining time and that a fixed price is asymptotically optimal; the gap at finite scale depends on the demand function and the ratio of demand to stock. The master prompt requires "sensitivity to elasticity and capacity" (section 10).

## 4. Competing explanations

Cell-to-cell differences may reflect the tuning grid fitting some cells better than others (for example a tuned optimum at a grid edge), not policy structure. Every tuned configuration and whether it lies at a grid edge is reported.

## 5. Hypotheses

Descriptive-confirmatory: for each cell c and j in {OCC, DRP}, H0_{j,c}: Delta_{j,c} = 0 versus H1_{j,c}: Delta_{j,c} != 0. 18 contrasts; Each contrast gets a p-value from a paired sign-flip permutation test (10,000 permutations, fixed seed); Holm adjustment over the 18 p-values at family-wise alpha = 0.05. Paired bootstrap 95% intervals are reported alongside. Contradicting result for a claimed pattern ("dynamic rules gain more when capacity is tight"): Delta at kappa = 4.0 not larger than at kappa = 1.0 within each sigma_v, judged on the interval of the difference of differences.

## 6. Estimand

Delta_{j,c} and the relative effect per cell; and the interaction contrasts (Delta at kappa = 4.0 minus Delta at kappa = 1.0) per sigma_v.

## 7. Unit, scope and variables

Unit: one evaluation stream within a cell. Factors: sigma_v in {0.25, 0.5, 1.0}; kappa in {1.0, 2.0, 4.0}; all other parameters at base. Point price elasticity of the purchase probability at the tuned FIX price is computed numerically and reported per cell so the elasticity levels are interpretable. Dependent variables as EXP-001.

## 8. Treatment, control and baseline

As EXP-001, re-tuned independently in each cell (36 configurations per family on 100 tuning streams per cell). Not re-tuning would make FIX a strawman.

## 9. Seeds and sample size

Spawn key (2, cell, role, index), cells 0 to 8 in row-major order (sigma_v outer, kappa inner); 100 tuning and 300 evaluation streams per cell. Same power rationale per contrast as EXP-001 before Holm adjustment; the adjusted analysis has less power, accepted and disclosed.

## 10. Compute budget

9 cells x (10,800 + 900) = 105,300 runs. Wall-clock cap: 40 minutes.

## 11. Metrics, uncertainty, exclusions, stopping

As EXP-001 sections 13, 14 and 16.

## 12. Anticipated failure modes

Degenerate cells (kappa = 1.0 with sigma_v = 1.0 may sell out rarely, making all policies close to identical); tuned optima at grid edges in extreme cells. Both reported, the grid is not changed after evaluation.

## 13. Reproducibility commands (planned)

```
uv run python -m fare.cli run --exp EXP-002 --config research/experiments/EXP-002/config.json
uv run python -m fare.cli report --exp EXP-002
```
