<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-003 report: robustness of the base comparison to demand misspecification

**Status: CONFIRMATORY, complete (frozen matrix run in full, 0 failed runs).** All numbers are simulated and hold only within the model of `research/protocol.md`. Every number is copied from committed files: `summary.json`, `metrics.csv`, `arm_summary.csv` and `run_manifest.json` in this folder, `research/experiments/EXP-001/summary.json`, and `results/confirmatory/logs/`.

## 1. Identification

| Item | Value |
|---|---|
| Experiment | EXP-003 |
| Report date | 2026-11-25 |
| Report version | 1.0 (M3) |
| Status | confirmatory, complete |
| Authorship | Mohamed Bechir Kefi (owner-approved, C3). The AI assistant (Claude Code) ran the experiment and composed this report from committed results (D-011, D-012). It is disclosed and is not an author. |
| Protocol | `research/experiments/EXP-003/protocol.md` v1.0, SHA-256 `b1e2a2f8931bada91fd5f4589f0fa8bd50004db6c05d568c9354f43f14a510fd` |
| Config | canonical SHA-256 `3c25c10c1cfcacf1103e6613b195c58c5ce0afd675556efa290f8b380ca039fd` |
| Provenance revision | `4204eac0776f4a04e512ef5ce92a10eefa5c5252` |
| Run set | `EXP-003-con-config-20261124T233547Z` |

## 2. Executive summary

- **Question.** When the three policies tuned at the base cell face a market whose demand differs from the tuning distribution, do the sign and class of the EXP-001 contrasts persist?
- **Method.**
  - The base tuning is re-derived from the EXP-001 tuning-stream keys.
  - Six misspecified cells: demand x0.6, x0.8, x1.25 and x1.6; reversed segment arrival order; no shocks.
  - Each cell has 4,000 evaluation streams and a FIX reference re-tuned in that cell.
  - The pre-specified invalidation rule is applied to the x0.8 and x1.25 cells.
- **Outcome.**
  - The invalidation rule is not triggered for OCC or DRP. In both moderate-shift cells, both base-tuned rules still beat the base-tuned FIX, with 95% intervals above 0.
  - At x0.6, both rules lose to the base-tuned FIX.
  - With reversed arrivals, DRP is practically equivalent to FIX.
- **Principal caveat.** Against a fixed price re-tuned to the true demand, the rules lose at x0.6, and OCC also loses at x0.8 and without shocks.

## 3. Rationale

A pricing rule is tuned on a model or forecast and then applied to a future that differs from it. A fixed price embeds a demand forecast. OCC and DRP adapt partly through observed sales, but their parameters also embed the base forecast.

den Boer's thesis (2013; front matter opened) addresses pricing under demand uncertainty. It is cited only as background, because its content was not reviewed.

## 4. Hypotheses and operational definitions

- **Contrast.** For each misspecified cell c and j in {OCC, DRP}: Delta_{j,c} = E[R(j*_base, S_c) - R(FIX*_base, S_c)], with paired bootstrap 95% intervals and no multiplicity adjustment.
- **Invalidation rule** (fixed in advance). If EXP-001 rejected H0_j, and in demand x0.8 or x1.25 the 95% interval of Delta_{j,c} lies entirely on the opposite side of zero from the EXP-001 point estimate, then the EXP-001 result for j is reported as specific to correct specification.
- **If EXP-001 did not reject H0_j.** The experiment is descriptive only for j.
- **Re-tuned reference.** The contrasts against the re-tuned FIX (FIX_retuned) separate the cost of misspecification from policy structure. They are descriptive.

## 5. Methodology

- **Scenarios.** All parameters are at base except the shifted factor:
  - demand_scale 0.6, 0.8, 1.25 or 1.6 (multiplies expected arrivals);
  - reversed linear arrival profiles;
  - sigma_M = 0 with no surges (no shocks).
- **Base tuning.** Re-derived on spawn keys (1, 0, 0, 0..499), as pinned (D-006), with the same grids as EXP-001.
- **Re-tuned FIX.** 36 prices on 500 tuning streams of each cell, with spawn keys (3, cell, 0, index).
- **Evaluation.** Spawn keys (3, cell, 1, 0..3999).
- **Data, hardware and software.** As in EXP-001. The data manifest SHA-256 is `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee`.
- **Budget.** 258,000 runs, against a 15-minute cap.

## 6. Implementation verification

- **Shared checks.** As in EXP-001: 143 tests, the smoke run (J-0007) and the metric validation (J-0008).
- **Base tuning.** The re-derived base tuning selects the same configurations as EXP-001, with identical mean tuning revenues: FIX(139.61) 11,672.0, OCC(159.24, 4) 12,141.6, DRP(100.48, 0.1) 12,200.8. None lies on a grid edge.
- **Failures.** No run failed.

## 7. Execution record

- **Command.** `PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-003/config.json --out results/raw/confirmatory`.
- **Timing.**
  - Start 2026-11-24T23:35:47Z and end 2026-11-24T23:38:29Z (manifest).
  - The wrapper logged completion at 23:39:18Z with exit status 0.
  - Runtime was 161.1 s and peak RSS 587.0 MiB.
  - The run followed EXP-001 in the same worker, while EXP-002 ran in parallel.
- **Runs.** 162,000 tuning runs and 96,000 evaluation runs (6 cells x 4 arms x 4,000), equal to the planned 258,000. None failed or were dropped.
- **Deviations and decisions.** None touches the protocol, the config, the seeds or the analysis.
  - D-010: the raw output (132,230,945 bytes) is git-ignored, and the aggregates come from `fare.summary`, which reads the EXP-001 verdict from `research/experiments/EXP-001/summary.json`.
  - D-011 and D-012: this report was composed from committed results.

## 8. Results

**Re-tuned FIX per cell** (the base-tuned FIX is p = 139.61 everywhere):

| Cell | Re-tuned FIX |
|---|---|
| demand-x0.6 | p = 107.31 |
| demand-x0.8 | p = 130.72 |
| demand-x1.25 | p = 149.10 |
| demand-x1.6 | p = 170.07 |
| reversed-arrivals | p = 139.61 (the same price as the base FIX, so its contrasts equal those against FIX) |
| no-shocks | p = 122.40 |

No selection lies on a grid edge.

**Arm mean revenue** (n = 4,000; SD in brackets; `arm_summary.csv`):

| Cell | FIX (base-tuned) | OCC | DRP | FIX re-tuned |
|---|---|---|---|---|
| demand-x0.6 | 7,580.2 (2,200.1) | 7,468.5 (2,388.4) | 7,383.3 (2,635.1) | 8,071.2 (1,892.7) |
| demand-x0.8 | 9,851.2 (2,447.6) | 9,983.6 (2,605.2) | 10,075.6 (2,669.4) | 10,023.0 (2,263.5) |
| demand-x1.25 | 13,096.1 (1,534.9) | 14,223.8 (2,423.6) | 14,183.4 (2,304.3) | 13,404.5 (2,025.7) |
| demand-x1.6 | 13,752.7 (747.3) | 16,285.4 (2,261.5) | 16,142.4 (2,197.1) | 15,326.4 (2,325.7) |
| reversed-arrivals | 11,739.5 (2,223.7) | 12,596.9 (2,399.0) | 11,720.0 (2,419.5) | 11,739.5 (2,223.7) |
| no-shocks | 11,313.5 (1,220.0) | 11,501.6 (1,078.4) | 11,750.9 (1,000.9) | 11,640.4 (770.0) |

**Revenue contrasts** (95% paired bootstrap; relative to the comparator's mean; `metrics.csv`):

| Cell | OCC - FIX | DRP - FIX | OCC - FIX re-tuned | DRP - FIX re-tuned |
|---|---|---|---|---|
| demand-x0.6 | -111.7 [-132.6, -90.9], -1.47% | -196.9 [-227.1, -166.7], -2.60% | -602.8 [-629.1, -577.0], -7.47% | -687.9 [-719.8, -655.7], -8.52% |
| demand-x0.8 | +132.4 [111.9, 153.4], +1.34% | +224.4 [197.2, 251.7], +2.28% | -39.4 [-63.5, -14.2], -0.39% (below SESOI) | +52.6 [23.9, 81.1], +0.52% (below SESOI) |
| demand-x1.25 | +1,127.6 [1,084.5, 1,171.2], +8.61% | +1,087.2 [1,044.4, 1,129.9], +8.30% | +819.3 [787.3, 852.0], +6.11% | +778.9 [744.8, 813.4], +5.81% |
| demand-x1.6 | +2,532.7 [2,473.6, 2,592.2], +18.42% | +2,389.7 [2,332.5, 2,447.7], +17.38% | +959.0 [924.2, 994.5], +6.26% | +816.0 [778.3, 853.8], +5.32% |
| reversed-arrivals | +857.3 [828.2, 886.6], +7.30% | -19.5 [-50.6, 10.7], -0.17% (practically equivalent) | +857.3 [828.2, 886.6], +7.30% | -19.5 [-50.6, 10.7], -0.17% (practically equivalent) |
| no-shocks | +188.1 [170.6, 205.6], +1.66% | +437.4 [414.6, 459.4], +3.87% | -138.8 [-158.6, -118.9], -1.19% | +110.5 [90.6, 130.0], +0.95% (below SESOI) |

Unless marked otherwise, each class is "detectable and practically relevant".

**Invalidation rule** (`summary.json`, `verdict`). EXP-001 rejected H0 for both arms, with point estimates +407.04 (OCC) and +462.08 (DRP), so the rule applies to both.

| Arm | demand-x0.8 interval | demand-x1.25 interval | Opposite side of zero? |
|---|---|---|---|
| OCC | [111.9, 153.4] | [1,084.5, 1,171.2] | no, no |
| DRP | [197.2, 251.7] | [1,044.4, 1,129.9] | no, no |

The rule is not triggered for either arm.

**Secondary metrics** (descriptive, `metrics.csv`).
- At x0.6, the rules sell far more stock than the base-tuned FIX: sell-through +0.234 (OCC) and +0.358 (DRP). They also raise the consumer surplus proxy by 2,727.8 and 3,929.7.
- At x1.6, availability rises by +0.159 and +0.171.

**Figures.**
- `figures/fig-EXP-003-forest-revenue.svg`: all 24 revenue contrasts with intervals.
- `figures/fig-EXP-003-<cell>-price.svg`: price paths on evaluation stream 0 of each cell.

## 9. Interpretation

- **Verdict under the frozen rule.** The EXP-001 result is not specific to correct specification under the moderate shifts tested. Both base-tuned rules keep a positive, detectable advantage at demand x0.8 and x1.25.
- **The advantage is asymmetric.**
  - It grows when demand is higher than forecast: +8.30% to +18.42% against the base-tuned FIX. Here the fixed price is too low and sells out early; at x1.6 the FIX availability is 0.807.
  - It reverses when demand is far lower than forecast (x0.6). Here the rules cut prices to clear stock and lose revenue compared with holding the base fixed price.
- **Against a fixed price re-tuned to the true demand.**
  - The rules still gain at x1.25 and x1.6 (+5.32% to +6.26%).
  - They lose clearly at x0.6 (-7.47% and -8.52%).
  - At x0.8 they are within the SESOI.
  - Without shocks, OCC loses (-1.19%) and DRP gains below the SESOI (+0.95%).
  - Part of the base advantage therefore reflects demand uncertainty itself: removing the shocks removes most of the gain over a correctly re-tuned fixed price.
- **Reversed arrivals.** When high-valuation buyers come early, DRP's sales-rate logic gives no gain (practically equivalent), while OCC gains +7.30%.
- **Expected versus observed.** The protocol anticipated that large shifts might push all policies to the price bounds, and that reversed arrivals might strongly favour fixed prices.
  - Neither price-bound failure appears in the arm means.
  - Reversed arrivals favour FIX only against DRP (equivalence), not against OCC.

## 10. Threats to validity

- **Statistical.** The intervals are unadjusted 95% intervals across 24 contrasts and are descriptive, except for the four used by the pre-specified rule.
- **Internal.** The base tuning is identical to EXP-001 by construction, so EXP-001 and EXP-003 share the same tuned policies. They do not share evaluation streams.
- **External and construct.** As in EXP-001. The shifts are one-factor-at-a-time and do not combine.

## 11. Conclusion and next experiment

The base-cell advantage of tuned OCC and DRP over the tuned fixed price survives a moderate demand-level misspecification (x0.8 and x1.25) under the frozen invalidation rule.

It does not survive a large shortfall in demand (x0.6). Against a fixed price re-tuned to the true demand, it is largely confined to demand above forecast.

A follow-up would need a new EXP ID: combined shifts, or tuning on a mixture of demand levels.

## 12. Reproduction appendix

See `reproduction.md` in this folder. References: Gallego and van Ryzin (1994); den Boer (2013, front matter only). Details are in `research/literature_review.md`.
