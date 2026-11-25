<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-002 report: sensitivity to price elasticity and demand-to-capacity tightness

**Status: CONFIRMATORY, complete (frozen matrix run in full, 0 failed runs).** All numbers are simulated and hold only within the model of `research/protocol.md`. Every number is copied from committed files: `summary.json`, `metrics.csv`, `arm_summary.csv` and `run_manifest.json` in this folder, and `results/confirmatory/logs/`.

## 1. Identification

| Item | Value |
|---|---|
| Experiment | EXP-002 |
| Report date | 2026-11-25 |
| Report version | 1.1 (M4, 2026-11-25: evidence audit and interpretation revisions listed in section 9, "M4 revisions") |
| Status | confirmatory, complete |
| Authorship | Mohamed Bechir Kefi (owner-approved, C3). The AI assistant (Claude Code) ran the experiment and composed this report from committed results (D-011, D-012). It is disclosed and is not an author. |
| Protocol | `research/experiments/EXP-002/protocol.md` v1.0, SHA-256 `7ffbc666ffd6465791d09e10ee3a3014002a513c90a876bf65c6e8ea4d2f6ab9` |
| Config | canonical SHA-256 `df7da4d68172d469301e6b46d70628dede3cfa255ee660898ceedf6d30d62856` |
| Provenance revision | `4204eac0776f4a04e512ef5ce92a10eefa5c5252` |
| Run set | `EXP-002-con-config-20261124T233503Z` |

## 2. Executive summary

- **Question.** How do Delta_OCC and Delta_DRP, the revenue differences against a fixed price re-tuned in each cell, vary with valuation dispersion (sigma_v in {0.25, 0.5, 1.0}) and with demand-to-capacity tightness (kappa in {1.0, 2.0, 4.0})?
- **Method.**
  - 9 cells, each re-tuned (36 configurations per family on 500 tuning streams) and evaluated on 4,000 streams.
  - A paired sign-flip permutation test per contrast, with Holm adjustment over the 18 contrasts.
  - Paired bootstrap 95% intervals.
  - Interaction contrasts with an independent stratified bootstrap.
- **Outcome.** All 18 contrasts reject H0 after Holm, but the sign depends on the cell.
  - The dynamic rules lose to the fixed price in all three kappa = 1.0 cells: OCC -0.54% to -1.72%, DRP -4.81% to -11.41%.
  - They also lose in sv1.0-k2.0: OCC -0.83%, DRP -3.37%.
  - They gain in the other five cells: +1.70% to +8.87%.
  - For every sigma_v and both arms, Delta at kappa = 4.0 exceeds Delta at kappa = 1.0, with 95% intervals that exclude 0.
- **Principal caveat.** 8 tuned optima lie on a grid edge. Every raw permutation p-value sits at its floor, 1/10001.

## 3. Rationale

- Gallego and van Ryzin (1994) show that the optimal price depends on stock and remaining time, and that the finite-scale gap to a fixed price depends on the demand function and on how demand compares with stock.
- The master prompt requires sensitivity to elasticity and capacity (section 10).
- Valuation dispersion sets the purchase elasticity. The kappa factor sets how often stock binds.

## 4. Hypotheses and operational definitions

- **Hypotheses.** For each cell c and j in {OCC, DRP}: H0_{j,c}: Delta_{j,c} = 0, against H1_{j,c}: Delta_{j,c} != 0. There are 18 contrasts.
- **Test.** A paired sign-flip permutation p-value (10,000 permutations, seed 20261124), Holm-adjusted at family-wise alpha 0.05.
- **Intervals.** Paired bootstrap 95% intervals, with SESOI classification at 1% of mean FIX* revenue in the cell.
- **Claimed pattern** ("dynamic rules gain more when capacity is tight"). It is contradicted if, within each sigma_v, Delta at kappa = 4.0 is not larger than at kappa = 1.0. This is judged on the 95% independent stratified bootstrap interval of the difference of differences (10,000 resamples, seed 20261124, descriptive, no multiplicity adjustment).
- **Metrics.** As in the EXP-001 protocol, section 13.

## 5. Methodology

- **Model.** The model of `research/protocol.md` section 3, with all parameters at base except sigma_v and kappa.
- **Cells and seeds.**
  - Cells are indexed 0 to 8 in row-major order (sigma_v outer, kappa inner).
  - Spawn keys are (2, cell, role, index): tuning indices 0 to 499, evaluation indices 0 to 3999.
- **Grids and tuning.** The grids and the tuning rule are those of EXP-001, re-tuned in each cell.
- **Data, hardware and software.** As in EXP-001. The data manifest SHA-256 is `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee`.
- **Budget.** 594,000 runs, against a 40-minute cap.

## 6. Implementation verification

- **Shared checks.** The test suite (143 passed), the smoke run (J-0007) and the metric validation (J-0008, 58 checks, 0 failed) are the same as for EXP-001.
- **Statistics code.** The Holm and interaction computations are those of `fare.report`. `fare.summary` reuses them with the frozen seeds, and its values match the raw report tables.
- **Failures.** No run failed or violated an invariant.

## 7. Execution record

- **Command.** `PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-002/config.json --out results/raw/confirmatory`.
- **Timing.**
  - Start 2026-11-24T23:35:03Z and end 2026-11-24T23:39:32Z (manifest).
  - The wrapper logged completion at 23:40:24Z with exit status 0.
  - Runtime was 268.8 s and peak RSS 698.5 MiB.
  - The run was the second worker, beside EXP-001 and then EXP-003.
- **Runs.** 486,000 tuning runs and 108,000 evaluation runs (9 cells x 3 arms x 4,000), equal to the planned 594,000. None failed or were dropped.
- **Deviations and decisions.** None touches the protocol, the config, the seeds or the analysis.
  - D-010: the raw output (147,753,410 bytes) is git-ignored under `results/raw/confirmatory/`, and the aggregates come from `fare.summary`.
  - D-011 and D-012: this report was composed from committed results under the owner's approval of 2026-11-25.
- **Elasticity values (omission in version 1.0, resolved in M4).** The protocol asks for the point price elasticity at the tuned FIX price in each cell. `fare.cli report` printed them in the git-ignored raw report (`results/raw/confirmatory/EXP-002-con-config-20261124T233503Z/report/report.md`, SHA-256 `9548aee6799102b0a414486414e5aaec039791a881146343f48b46267910e082`), so version 1.0 did not quote them. In M4 they were copied into a committed file and re-derived deterministically from the scenario parameters, with agreement to the printed precision (`results/exploratory/m4_audit_sensitivity.json`, `audit.EXP-002_elasticity`, J-0012). They are reported in section 8.

## 8. Results

**Tuned configurations.** "Edge" marks a selection on a grid edge.

| Cell | FIX | OCC | DRP |
|---|---|---|---|
| sv0.25-k1.0 | p = 88.09 | p0 = 100.48, k = 0.5 | p0 = 100.48, eta = 0.025 (edge) |
| sv0.25-k2.0 | p = 122.40 | p0 = 159.24, k = 8 (edge) | p0 = 100.48, eta = 0.1 |
| sv0.25-k4.0 | p = 170.07 | p0 = 252.38, k = 4 | p0 = 159.24, eta = 0.1 |
| sv0.5-k1.0 | p = 100.48 | p0 = 100.48, k = 0.25 (edge) | p0 = 100.48, eta = 0.025 (edge) |
| sv0.5-k2.0 | p = 139.61 | p0 = 159.24, k = 4 | p0 = 100.48, eta = 0.1 |
| sv0.5-k4.0 | p = 193.99 | p0 = 252.38, k = 4 | p0 = 159.24, eta = 0.1 |
| sv1.0-k1.0 | p = 170.07 | p0 = 159.24, k = 0.25 (edge) | p0 = 252.38, eta = 0.025 (edge) |
| sv1.0-k2.0 | p = 221.27 | p0 = 252.38, k = 0.5 | p0 = 252.38, eta = 0.025 (edge) |
| sv1.0-k4.0 | p = 307.45 | p0 = 400, k = 8 (edge: price-high and sensitivity-high) | p0 = 252.38, eta = 0.1 |

**Grid-edge findings** (rule of `research/protocol.md` section 4). There are 8 edge optima.
- DRP is at the lower edge eta = 0.025 in 4 cells: sv0.25-k1.0, sv0.5-k1.0, sv1.0-k1.0 and sv1.0-k2.0.
- OCC is at the lower edge k = 0.25 in 2 cells: sv0.5-k1.0 and sv1.0-k1.0.
- OCC is at an upper edge in 2 cells: k = 8 in sv0.25-k2.0, and p0 = 400 with k = 8 in sv1.0-k4.0.

How these are read:
- Lower edges are read as rules close to the nesting point, where the rule is the fixed price FIX(p0). In those cells the dynamic rule adds little or nothing over a fixed price.
- At the upper edges, the contrast measures OCC as gridded and may understate it.
- M4 caveat on the frozen lower-edge reading (section 9, "M4 revisions"): at eta = 0.025 the DRP prices do not stay close to p0. The mean price paid is 84.3 against p0 = 100.48 in sv0.25-k1.0, 81.6 against 100.48 in sv0.5-k1.0, 130.7 against 252.38 in sv1.0-k1.0 and 176.7 against 252.38 in sv1.0-k2.0 (`arm_summary.csv`). The frozen reading is kept as frozen, but "close to a fixed price" holds for the parameter value, not for the realised prices.

**Purchase elasticity at the tuned FIX price** (protocol section 7; deterministic, no interval; values as printed by the confirmatory raw report and re-derived in M4):

| sigma_v | kappa = 1.0 | kappa = 2.0 | kappa = 4.0 |
|---|---|---|---|
| 0.25 | -1.253 | -1.993 | -2.156 |
| 0.5 | -1.047 | -1.557 | -2.121 |
| 1.0 | -0.955 | -1.123 | -1.345 |

The elasticity depends on the tuned price as well as on sigma_v, so sigma_v alone does not order the cells by elasticity. In the three kappa = 1.0 cells it is close to -1.

**Revenue contrasts against the re-tuned FIX.**
- n = 4,000 per cell; paired bootstrap 95% intervals.
- Every raw sign-flip p is 0.0001 (1/10001) and every Holm-adjusted p is 0.0018, so all 18 contrasts reject H0.
- Source: `summary.json` (`verdict`).

| Cell | FIX* mean revenue | OCC - FIX | Relative, class | DRP - FIX | Relative, class |
|---|---|---|---|---|---|
| sv0.25-k1.0 | 7,254.0 | -125.0 [-144.7, -105.3] | -1.72%, relevant | -348.7 [-373.5, -324.4] | -4.81%, relevant |
| sv0.25-k2.0 | 10,776.4 | +815.1 [786.5, 842.8] | +7.56%, relevant | +955.5 [928.9, 982.5] | +8.87%, relevant |
| sv0.25-k4.0 | 15,491.3 | +527.5 [493.6, 561.7] | +3.40%, relevant | +262.8 [223.0, 302.0] | +1.70%, relevant |
| sv0.5-k1.0 | 6,873.7 | -37.0 [-41.3, -32.6] | -0.54%, below SESOI | -480.0 [-496.3, -463.5] | -6.98%, relevant |
| sv0.5-k2.0 | 11,756.6 | +435.5 [405.8, 464.1] | +3.70%, relevant | +491.1 [459.5, 522.0] | +4.18%, relevant |
| sv0.5-k4.0 | 17,221.2 | +1,094.1 [1,054.8, 1,133.2] | +6.35%, relevant | +1,050.8 [1,008.5, 1,093.8] | +6.10%, relevant |
| sv1.0-k1.0 | 7,141.9 | -120.3 [-131.3, -109.5] | -1.69%, relevant | -815.0 [-834.2, -796.2] | -11.41%, relevant |
| sv1.0-k2.0 | 14,067.0 | -116.3 [-136.2, -95.8] | -0.83%, below SESOI | -473.8 [-502.3, -444.3] | -3.37%, relevant |
| sv1.0-k4.0 | 24,916.0 | +1,036.7 [964.6, 1,111.5] | +4.16%, relevant | +939.0 [866.4, 1,013.8] | +3.77%, relevant |

"Relevant" means detectable and practically relevant. "Below SESOI" means detectable but below the SESOI.

**Interaction contrasts.** Delta(kappa = 4.0) - Delta(kappa = 1.0), 95% independent stratified bootstrap, n = 4,000 and 4,000:

| sigma_v | OCC | DRP |
|---|---|---|
| 0.25 | +652.4 [613.9, 691.5] | +611.5 [564.6, 658.1] |
| 0.5 | +1,131.1 [1,091.7, 1,171.1] | +1,530.8 [1,485.1, 1,576.5] |
| 1.0 | +1,157.0 [1,083.4, 1,232.3] | +1,754.1 [1,679.5, 1,831.4] |

**Secondary metrics.** The descriptive 95% contrasts for sell-through, availability and the surplus proxies, in every cell, are in `metrics.csv`. Two patterns stand out.
- DRP raises the consumer surplus proxy in every cell where its interval excludes 0. In sv0.25-k4.0 it is +0.087 [-31.621, 32.187].
- OCC lowers sell-through in sv0.25-k1.0 (-0.078 [-0.080, -0.077]) and in sv1.0-k2.0 (-0.029 [-0.030, -0.028]).

**Figures.**
- `figures/fig-EXP-002-forest-revenue.svg`: all 18 revenue contrasts with intervals and SESOI bands.
- `figures/fig-EXP-002-<cell>-price.svg`: price paths on evaluation stream 0 of each cell.

## 9. Interpretation

- **What was measured.** The advantage found at the base cell is not general, even within the model.
  - With loose capacity (kappa = 1.0), both dynamic rules earn less than a well-tuned fixed price at every dispersion level. DRP loses most: -11.41% at sigma_v = 1.0.
  - With tighter capacity, both rules gain, by up to +8.87%.
- **The kappa = 1.0 cells and the edges.** In these cells the tuning pushed both families toward their least responsive grid values: DRP to eta = 0.025 in all three, and OCC to k = 0.25 in two. Under the frozen reading, the tuning itself prefers a near-fixed price there. M4 qualifies the rest of this paragraph as follows.
  - The fixed price in these cells sits where the purchase elasticity is close to -1 (-1.253, -1.047, -0.955). In this model that is the price that maximises expected revenue per arriving buyer when stock does not bind, so there is little scarcity for a dynamic rule to exploit.
  - Even at eta = 0.025, DRP marks prices down well below p0 (mean price paid 81.6 against 100.48 in sv0.5-k1.0, 130.7 against 252.38 in sv1.0-k1.0). Its target rate asks it to sell the remaining stock by the deadline, and with loose capacity that target is out of reach, so the multiplicative update keeps lowering the price over 60 periods. The DRP losses are therefore a property of the rule's clearance target, not small residual noise.
  - An exploratory decomposition on the tuning streams (J-0012, B1; in-sample) splits each rule's advantage into a price-resolution part (FIX at the rule's own p0 minus the best of 36 fixed prices) and a responsiveness part (the rule minus FIX at its own p0). For DRP, the responsiveness part is the whole loss in sv0.5-k1.0 (-462.4), most of it in sv1.0-k1.0 (-543.2 of -812.7) and about half in sv0.25-k1.0 (-162.0 of -328.6). For OCC in sv0.25-k1.0 and in sv1.0-k2.0 the responsiveness part is positive (+60.2 and +89.7) and the loss comes from the coarser p0 grid (-166.7 and -172.3).
- **The base parameters.** The base-parameter cell sv0.5-k2.0 (+435.5 and +491.1, on EXP-002's own streams) agrees with EXP-001 (+407.04 and +462.08).
- **Claimed pattern.** "Dynamic rules gain more when capacity is tight" is supported descriptively for every sigma_v and both arms. Every interaction interval excludes 0.
- **Alternative explanations.**
  - Grid fit differs across cells. The upper-edge OCC optima in sv0.25-k2.0 and sv1.0-k4.0 may understate OCC there.
  - The lower-edge optima suggest that the grid's floor, not policy structure, drives part of the loss at kappa = 1.0. A grid that includes eta = 0 or k = 0 would nest the fixed price exactly, but the protocol froze the grid.
  - Grid resolution (M4). EXP-002 has no FIX6 arm, so the tuning-grid sensitivity of EXP-001 was not registered here. The exploratory decomposition above indicates that the OCC losses in sv0.25-k1.0 (-1.72%) and sv1.0-k2.0 (-0.83%) reflect the 6-value p0 grid rather than the occupancy response. These two contrasts are therefore weak evidence against OCC's structure, although they stand as frozen verdicts.
- **Expected versus observed.**
  - The protocol anticipated degenerate cells near kappa = 1.0 with sigma_v = 1.0. In fact sv1.0-k1.0 is far from degenerate: DRP loses 815.0.
  - The protocol expected edge optima in extreme cells. 8 occurred, against 7 of 18 in the pre-freeze tuning-only check.
- **Verdict under the frozen rule.** H0_{j,c} is rejected for all 18 contrasts at family-wise alpha 0.05 (Holm). The directions are mixed: 8 negative and 10 positive (corrected in M4; version 1.0 said 7 and 11, see `research/publication/evidence_audit.md`, finding F-1). The tightness pattern holds in all 6 interaction contrasts (descriptive).
- **M4 revisions (2026-11-25, version 1.1).** No frozen verdict changes. Changes:
  1. Evidence audit (`research/publication/evidence_audit.md`, finding F-1): the count of negative and positive contrasts was wrong in version 1.0 (7 and 11); the committed results give 8 and 10. Corrected above.
  2. The per-cell elasticities are reported (section 8).
  3. The interpretation of the kappa = 1.0 cells and the alternative explanations were revised with the exploratory decomposition (J-0012, B1) and the realised DRP prices at eta = 0.025.
  4. Internal replication (exploratory, B2): sv0.5-k2.0 and EXP-001 select the same configurations on independent streams and differ by +28.4 [-13.3, 70.2] (OCC) and +29.0 [-15.3, 73.4] (DRP).

## 10. Threats to validity

- **Statistical.**
  - With 10,000 permutations, the smallest attainable p-value is 1/10001. All 18 raw p-values sit at this floor, so the Holm values (0.0018) are bounds.
  - The adjusted analysis covers the 18 cell contrasts. The interaction contrasts and secondary metrics are not adjusted.
- **Internal.**
  - Edge optima in 8 of the 27 tuned selections.
  - Selection noise from 500 tuning streams per cell.
- **External and construct.** As in EXP-001: a synthetic market, myopic buyers, arbitrary parameters and a proxy welfare measure.
- **Elasticity axis.** The per-cell elasticities are now reported (section 8). They show that sigma_v and kappa do not move elasticity independently, because the tuned price changes with both. The factor "elasticity" in the research question is therefore operationalised by sigma_v, with the realised elasticity as a descriptive covariate.
- **Exploratory checks.** The M4 decomposition (J-0012, B1) is in-sample on the tuning streams and was computed after the results were seen.

## 11. Conclusion and next experiment

Within the model, the sign of the gain from simple dynamic pricing over a tuned fixed price depends on market conditions.
- With loose capacity (kappa = 1.0) it is negative for both rules at every valuation dispersion.
- With moderate or tight capacity it is positive, apart from sv1.0-k2.0.
- The gain grows with capacity tightness for every dispersion level.

A follow-up would need a new EXP ID: a grid that includes the nesting values k = 0 and eta = 0.

## 12. Reproduction appendix

See `reproduction.md` in this folder. References as in the EXP-001 report and `research/literature_review.md`.
