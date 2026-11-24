<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-003 protocol: robustness of the base comparison to demand misspecification

**Status: DRAFT v0.1 (2026-11-24). Planned; protocol draft awaiting owner freeze (G-FREEZE).** Not executed. Depends on EXP-001 tuned configurations (the configurations, not the evaluation results). This is the sensitivity analysis designated as able to invalidate the main interpretation.

## 1. Precise question

When the three policies tuned at the base cell face a market whose demand differs from the tuning distribution, does the sign and class of Delta_OCC and Delta_DRP found in EXP-001 persist?

## 2. Mechanism

A tuned fixed price embeds a forecast of demand; if demand is higher or lower than forecast, it cannot adapt. OCC and DRP partly adapt through observed sales, but their tuned parameters also embed the base forecast. Misspecification therefore separates "dynamic rules are better" from "dynamic rules are better only when the forecast is right" or "only when it is wrong".

## 3. Rationale

In practice a pricing rule is tuned on a model or history and applied to a future that differs from it. den Boer's work on dynamic pricing and learning (thesis, Vrije Universiteit Amsterdam, 2013; front matter opened, content not reviewed for this protocol) addresses pricing under demand uncertainty; it is cited only as background until its content is read.

## 4. Competing explanations

A gain under misspecification may come from FIX being tuned for the wrong level rather than from any merit of dynamic structure. A re-tuned FIX reference per cell (tuned on that cell's own tuning streams) separates the cost of misspecification from policy structure.

## 5. Hypotheses and invalidation criterion

For each misspecified cell c and j in {OCC, DRP}: Delta_{j,c} = E[R(j*_base, S_c) - R(FIX*_base, S_c)]. Pre-specified invalidation rule for EXP-001's interpretation: if, in either moderate-shift cell (demand level times 0.8 or times 1.25), the 95% interval of Delta_{j,c} lies entirely on the opposite side of zero from the EXP-001 point estimate of Delta_j (when EXP-001 rejected H0_j), then the EXP-001 result for policy j is reported as specific to correct specification. If EXP-001 did not reject H0_j, this experiment is reported descriptively only.

## 6. Unit, scope and variables

Unit: one evaluation stream within a misspecified cell. Six cells, all other parameters at base: (1) demand level x 0.6, (2) x 0.8, (3) x 1.25, (4) x 1.6 (multiplying A); (5) reversed segment arrival profiles (H early, L late); (6) no shocks (sigma_M = 0, no surges). Policies: FIX*, OCC*, DRP* from EXP-001 tuning, not re-tuned; reference FIX re-tuned per cell (36 prices, 100 tuning streams of that cell).

## 7. Seeds and sample size

Spawn key (3, cell, role, index); 300 evaluation streams per cell; 100 tuning streams per cell for the reference only.

## 8. Compute budget

6 x (3 x 300 + 36 x 100 + 300) = 28,800 runs. Wall-clock cap: 15 minutes.

## 9. Metrics, uncertainty, exclusions, stopping

As EXP-001 sections 13, 14 and 16; 95% paired bootstrap intervals per cell, no multiplicity adjustment (descriptive robustness), with the invalidation rule above fixed in advance.

## 10. Anticipated failure modes

Large shifts may push all policies to price bounds; reported. Reversed arrival order may favour fixed prices strongly; reported as found.

## 11. Reproducibility commands (planned)

```
uv run python -m fare.cli run --exp EXP-003 --config research/experiments/EXP-003/config.json
uv run python -m fare.cli report --exp EXP-003
```
