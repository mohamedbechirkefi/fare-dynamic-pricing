<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-002 protocol: sensitivity to price elasticity and demand-to-capacity tightness

**Status: FROZEN v1.0 (owner-approved 2026-11-24). Not yet run.** Owner-approved amendments of 2026-11-24 applied, including the second-round tuning-grid ruling (see `research/protocol.md`, "Amendments before freeze"). Frozen by the owner's approval; hashes in `research/freeze.json` (G-FREEZE). Not executed. Depends on EXP-001 code and analysis pipeline (not on its results).

## 1. Precise question

How do the paired revenue differences Delta_OCC and Delta_DRP (relative to the tuned fixed price), and the secondary metrics, vary with buyer valuation dispersion (which sets price elasticity) and with the ratio of expected arrivals to capacity?

## 2. Mechanism

With low valuation dispersion (high elasticity near the median), small price changes move demand strongly, so a dynamic rule's adjustments matter more and errors cost more. With loose capacity (kappa = 1.0) stock rarely binds and the value of reacting to scarcity is small; with tight capacity (kappa = 4.0) scarcity is frequent and timing of high-valuation arrivals matters.

## 3. Rationale

Gallego and van Ryzin (1994) show that the optimal price depends on stock and remaining time and that a fixed price is asymptotically optimal; the gap at finite scale depends on the demand function and the ratio of demand to stock. The master prompt requires "sensitivity to elasticity and capacity" (section 10).

## 4. Competing explanations

Cell-to-cell differences may reflect the tuning grid fitting some cells better than others (for example a tuned optimum at a grid edge), not policy structure. Every tuned configuration and whether it lies at a grid edge is reported.

## 5. Hypotheses

Descriptive-confirmatory: for each cell c and j in {OCC, DRP}, H0_{j,c}: Delta_{j,c} = 0 versus H1_{j,c}: Delta_{j,c} != 0. 18 contrasts; Each contrast gets a p-value from a paired sign-flip permutation test (10,000 permutations, fixed seed); Holm adjustment over the 18 p-values at family-wise alpha = 0.05. Paired bootstrap 95% intervals are reported alongside. Contradicting result for a claimed pattern ("dynamic rules gain more when capacity is tight"): Delta at kappa = 4.0 not larger than at kappa = 1.0 within each sigma_v, judged on the interval of the difference of differences. Interaction-contrast method: because the cells use different streams, the difference of differences is an independent-samples contrast. Its estimate is mean(d at kappa = 4.0) - mean(d at kappa = 1.0), with d the per-stream paired revenue differences (arm minus FIX) of each cell, and its interval is an independent stratified percentile bootstrap: streams are resampled with replacement within each cell separately, 10,000 resamples, fixed seed 20261124, 95% level, no multiplicity adjustment (6 interaction contrasts: 3 sigma_v values times 2 arms, descriptive). Implemented in `fare.stats.interaction_bootstrap_ci` and reported by `fare.cli report`.

## 6. Estimand

Delta_{j,c} and the relative effect per cell; and the interaction contrasts (Delta at kappa = 4.0 minus Delta at kappa = 1.0) per sigma_v.

## 7. Unit, scope and variables

Unit: one evaluation stream within a cell. Factors: sigma_v in {0.25, 0.5, 1.0}; kappa in {1.0, 2.0, 4.0}; all other parameters at base. Point price elasticity of the purchase probability at the tuned FIX price is computed numerically and reported per cell so the elasticity levels are interpretable. Dependent variables as EXP-001.

## 8. Treatment, control and baseline

As EXP-001, re-tuned independently in each cell (36 configurations per family on 500 tuning streams per cell, on the widened grids of `research/protocol.md` section 4). Not re-tuning would make FIX a strawman.

## 9. Seeds and sample size

Spawn key (2, cell, role, index), cells 0 to 8 in row-major order (sigma_v outer, kappa inner); 500 tuning and 4,000 evaluation streams per cell (tuning indices 0 to 499, evaluation indices 0 to 3999). The pilot (J-0004) implies n between 144 and 2,735 for the 1% SESOI at two-sided alpha = 0.025 and power 0.89 across the cells; n = 4,000 covers all of them. Same power rationale per contrast as EXP-001 before Holm adjustment; the adjusted analysis has less power, accepted and disclosed.

## 10. Compute budget

9 cells x (54,000 + 12,000) = 594,000 runs. Wall-clock cap: 40 minutes.

## 11. Metrics, uncertainty, exclusions, stopping

As EXP-001 sections 13, 14 and 16.

## 12. Anticipated failure modes

Degenerate cells (kappa = 1.0 with sigma_v = 1.0 may sell out rarely, making all policies close to identical); tuned optima at grid edges in extreme cells. Both reported. Edge optima are findings under the grid-edge rule of `research/protocol.md` section 4: a DRP optimum at eta = 0.025 is read as a rule close to eta = 0, where DRP reduces to a fixed price; the pre-freeze tuning-only check (J-0006) found 7 of 18 pilot optima of this experiment on an edge of the frozen grid. The grid is not changed after the freeze.

## 13. Reproducibility commands

Run from the repository root. The package is imported from `src/` (`PYTHONPATH=src`); `UV` is `/Users/bechir/research/labs/.tools/py/bin/uv` on the owner's machine.

```
export PYTHONPATH=src
$UV sync --frozen --python /usr/local/bin/python3
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli test
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --plan --config research/experiments/EXP-002/config.json
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --config research/experiments/EXP-002/config.json
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli report --result results/confirmatory/<run_set_id>/result.json --pdf
```

`run` writes `results/confirmatory/<run_set_id>/` (result.json, run_manifest.json, config.json) and refuses the config unless the protocol, the main protocol and this exact config are recorded as frozen (`research/experiment_registry.csv`, `research/freeze.json`).

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24.md`, FARE section); applied in draft v0.2 (decision D-008).

1. Stream counts: 500 tuning and 4,000 evaluation streams per cell (sections 8 to 10). Applied.
2. Tuning grids: not applied in the first round (could not be applied as written); resolved in the second round below. With the widened grid, 7 of the 18 pilot optima in this experiment's cells stay on a grid edge (`results/exploratory/grid_interior_check.json`).
3. Interaction-contrast method named (section 5). Applied.
4. Commands: section 13 names the implemented CLI. Applied.

## Amendments before freeze, second round (owner-approved 2026-11-24)

Owner answer "Approve all", 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24b.md`, section 2): "Keep the widened grids within the equal tuning budget. Report optima on a grid edge as a finding (a DRP responsiveness of 0 means the dynamic rule reduces to a fixed price). Freeze." Applied before any confirmatory data (decision D-009).

5. Tuning grids widened within the equal budget (section 8); run count unchanged (section 10). Applied.
6. Grid-edge optima reported as findings (sections 4 and 12). Applied.
