<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-003 protocol: robustness of the base comparison to demand misspecification

**Status: DRAFT v0.2 (2026-11-24). Planned; not frozen.** Owner-approved amendments of 2026-11-24 applied except the tuning-grid item, which awaits the owner's ruling before the freeze (G-FREEZE; see `research/protocol.md`, "Amendments before freeze"). Not executed. Depends on EXP-001 tuned configurations (the configurations, not the evaluation results). This is the sensitivity analysis designated as able to invalidate the main interpretation.

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

Unit: one evaluation stream within a misspecified cell. Six cells, all other parameters at base: (1) demand level x 0.6, (2) x 0.8, (3) x 1.25, (4) x 1.6 (multiplying A); (5) reversed segment arrival profiles (H early, L late); (6) no shocks (sigma_M = 0, no surges). Policies: FIX*, OCC*, DRP* from EXP-001 tuning, not re-tuned; reference FIX re-tuned per cell (36 prices, 500 tuning streams of that cell).

## 7. Seeds and sample size

Spawn key (3, cell, role, index); 4,000 evaluation streams per cell (indices 0 to 3999); 500 tuning streams per cell (indices 0 to 499) for the reference only. The base-cell policies are tuned on the EXP-001 tuning-stream keys (1, 0, 0, 0 to 499), re-derived inside this experiment rather than read from an EXP-001 result file (pinned D-006 choice). The pilot (J-0005) implies n between 257 and 3,435 for the 1% SESOI at two-sided alpha = 0.025 and power 0.89; n = 4,000 covers all cells.

## 8. Compute budget

Base tuning re-derived: 3 x 36 x 500 = 54,000 runs. Misspecified cells: 6 x (4 x 4,000 + 36 x 500) = 204,000 runs. Total 258,000 runs (`fare.cli run --plan`). Wall-clock cap: 15 minutes.

## 9. Metrics, uncertainty, exclusions, stopping

As EXP-001 sections 13, 14 and 16; 95% paired bootstrap intervals per cell, no multiplicity adjustment (descriptive robustness), with the invalidation rule above fixed in advance.

## 10. Anticipated failure modes

Large shifts may push all policies to price bounds; reported. Reversed arrival order may favour fixed prices strongly; reported as found.

## 11. Reproducibility commands

Run from the repository root. The package is imported from `src/` (`PYTHONPATH=src`); `UV` is `/Users/bechir/research/labs/.tools/py/bin/uv` on the owner's machine.

```
export PYTHONPATH=src
$UV sync --frozen --python /usr/local/bin/python3
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli test
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --plan --config research/experiments/EXP-003/config.json
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --config research/experiments/EXP-003/config.json
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli report --result results/confirmatory/<run_set_id>/result.json --pdf
```

`run` writes `results/confirmatory/<run_set_id>/` (result.json, run_manifest.json, config.json) and refuses the config unless the protocol, the main protocol and this exact config are recorded as frozen (`research/experiment_registry.csv`, `research/freeze.json`).

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24.md`, FARE section); applied in draft v0.2 (decision D-008).

1. Stream counts: 500 tuning and 4,000 evaluation streams per cell (sections 6 to 8). Applied.
2. Tuning grids: not applied; the draft grid stands until the owner rules. The base tuning used here gives interior pilot optima under the proposed widened grid.
3. The re-derived base tuning and its run count are pinned (sections 7 and 8). Applied.
4. Commands: section 11 names the implemented CLI. Applied.
