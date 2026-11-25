<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-001 report: tuned dynamic rules versus the best fixed price at the base scenario

**Status: CONFIRMATORY, complete (frozen matrix run in full, 0 failed runs).** All numbers are simulated and hold only within the model of `research/protocol.md`. They are not evidence about any real market, airline, hotel or proprietary pricing system. Every number is copied from committed result files: `summary.json`, `metrics.csv`, `arm_summary.csv` and `run_manifest.json` in this folder, and `results/confirmatory/logs/`.

## 1. Identification

| Item | Value |
|---|---|
| Experiment | EXP-001 |
| Report date | 2026-11-25 |
| Report version | 1.1 (M4, 2026-11-25: evidence audit and interpretation revisions listed in section 9, "M4 revisions") |
| Status | confirmatory, complete |
| Authorship | Mohamed Bechir Kefi (owner-approved, C3). The AI assistant (Claude Code) ran the experiment and composed this report from committed results under the owner's decision of 2026-11-25 (D-011, D-012). It is disclosed and is not an author. |
| Protocol | `research/experiments/EXP-001/protocol.md` v1.0, SHA-256 `06f939d8fd59389a3438cd539f862a36ed4d47275137b50aeb3ffdc233df2ec2`; main protocol `d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1` |
| Config | `research/experiments/EXP-001/config.json`, canonical SHA-256 `592a197632390bb9ab8fdcf7e95555e3bb590c921faba573175c4dcaa9cffc76` |
| Provenance revision | `4204eac0776f4a04e512ef5ce92a10eefa5c5252` (no tracked file modified at run time) |
| Run set | `EXP-001-con-config-20261124T233503Z` |

## 2. Executive summary

- **Question.** At the base scenario, does a tuned occupancy rule (OCC) or a tuned demand-responsive rule (DRP) change expected revenue per selling season, compared with the tuned fixed price (FIX)? All three face identical demand streams and get equal tuning budgets.
- **Method.**
  - Each family was tuned on 500 tuning streams, with 36 configurations each.
  - Each was then evaluated on 4,000 held-out evaluation streams.
  - Paired revenue differences were analysed with Bonferroni-adjusted 97.5% paired percentile bootstrap intervals.
- **Outcome.** Both dynamic rules earned more than the tuned fixed price.
  - OCC: +407.04 currency units per season, 97.5% interval [373.17, 440.17], +3.47% of FIX* revenue.
  - DRP: +462.08, 97.5% interval [426.03, 498.13], +3.94%.
  - H0 is rejected for both.
  - Both effects are classified "detectable and practically relevant" against the SESOI of 1% of mean FIX* revenue.
  - Neither gain exceeds 5%, so the planning expectation is not contradicted.
  - The tuning-grid sensitivity arm (FIX6) changes neither the sign nor the class.
- **Principal caveat.** The gain is relative to a fixed price tuned on correctly specified demand, with myopic buyers. EXP-002 shows that the sign depends on the market cell. EXP-003 shows that the base-tuned rules lose to the base-tuned fixed price when demand falls to 0.6 times the tuning level.

## 3. Rationale and literature

Gallego and van Ryzin (1994, Management Science 40(8):999-1020; full text opened) prove that fixed-price policies are asymptotically optimal for expected revenue as the volume of expected sales grows. This makes a well-tuned fixed price the principled baseline. It leaves open how much simple, model-free dynamic rules gain or lose at moderate scale (C = 100), with demand shocks and heterogeneous buyers.

Elmaghraby and Keskinocak (2003; abstract opened) review this setting.

The gap addressed here is a matched comparison, with equal tuning budgets, of simple rule families against that baseline (`research/literature_review.md`).

## 4. Hypotheses and operational definitions

- **Estimand.** For j in {OCC, DRP}, Delta_j = E[R(j*, S) - R(FIX*, S)] over the base-cell evaluation streams S, in currency units per season.
- **Hypotheses.** H0_j: Delta_j = 0. H1_j: Delta_j != 0.
- **Decision rule.** Reject H0_j when the 97.5% paired percentile bootstrap interval excludes 0. The bootstrap uses 10,000 resamples and seed 20261124. Over the two contrasts, the family-wise alpha is 0.05.
- **Classification.** Effects are classified against the SESOI, 1% of mean FIX* revenue.
- **What contradicts H1_j.** An interval that includes 0. A gain above 5% of FIX* revenue would contradict the planning expectation.
- **Policies** (protocol section 4):
  - FIX(p): p_t = p.
  - OCC(p0, k): p_t = clip(p0 exp(k (f_t - e_t)), 30, 600).
  - DRP(p0, eta): a multiplicative update toward the target rate x_t / (T - t + 1).
- **Metric formulas.** These are in protocol section 13.

## 5. Methodology

- **Model.** The synthetic market of `research/protocol.md` section 3, with these base parameters:
  - T = 60 periods and C = 100 units.
  - kappa = 2.0, sigma_v = 0.5 and sigma_M = 0.25.
  - Surges: probability 0.05, length 3, factor 1.8.
  - Segment shares 0.7 / 0.3 and segment medians 100 / 200.
  - Price bounds [30, 600].
  - Buyers are myopic and have unit demand.
  - Streams are pre-generated and replayed under every policy (common random numbers).
- **Data.** Synthetic only (C1, D-002). The data manifest `data/manifest.json` has SHA-256 `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee`.
- **Tuning.** Tuning streams have spawn keys (1, 0, 0, 0..499) under entropy 20261124. Each family has 36 configurations:
  - FIX: 36 geometric prices in [40, 400].
  - OCC: 6 geometric p0 values times k in {0.25, 0.5, 1, 2, 4, 8}.
  - DRP: the same 6 p0 values times eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1.0}.

  The highest mean revenue is selected, and ties go to the lowest index. FIX6 is FIX re-tuned on the 6 shared p0 values.
- **Evaluation.** 4,000 streams with spawn keys (1, 0, 1, 0..3999).
- **Hardware and software.** Apple M1 Pro, macOS 15.3.1, on a machine shared with other sessions (D-010). Python 3.12.1, numpy 2.5.4, jsonschema 4.26.0 and fare 0.2.0.
- **Budget.** 73,000 runs, against a 15-minute wall-clock cap.

## 6. Implementation verification

- **Test suite before the run.** 143 passed at the provenance revision.
- **What the tests cover.**
  - Invariants: stock conservation, non-negative stock, price bounds, no sale when sold out, no sale below price. These are checked inside every simulation.
  - Policy nesting: k = 0 and eta = 0 reproduce FIX.
  - A differential test against a buyer-by-buyer oracle.
  - Hand-computed examples and property tests.
- **Pre-run checks (exploratory).**
  - J-0007 smoke run: 125 runs, 0 failures, nesting exact.
  - J-0008 metric validation (`results/exploratory/metric_validation.json`): 58 hand-derived checks, 0 failed.
- **Faithfulness.**
  - No run failed or violated an invariant.
  - The report generator rebuilt the price-path figure from the recorded seed key. It checked the regenerated stream's SHA-256 and the revenue against the result file, and both matched.

## 7. Execution record

- **Command.** `PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-001/config.json --out results/raw/confirmatory`. This was followed by `fare.cli report` and `fare.summary` (see `reproduction.md`).
- **Timing.**
  - Start 2026-11-24T23:35:03Z and end 2026-11-24T23:35:37Z (`run_manifest.json`).
  - The wrapper logged completion at 23:35:47Z with exit status 0.
  - Runtime was 34.5 s and peak RSS 396.5 MiB.
  - EXP-002 ran concurrently as the second worker.
- **Runs.** 57,000 tuning runs and 16,000 evaluation runs (4 arms x 4,000), equal to the planned 73,000. None failed or were dropped.
- **Run IDs.** `EXP-001-con-config-20261124T233503Z/base/<arm>/eval<index>`. Each run records its seed key and its stream SHA-256.
- **Deviations and decisions.** None touches the protocol, the config, the seeds, the exclusions or the analysis.
  1. D-010: the raw output (21,532,968 bytes) is in the git-ignored `results/raw/confirmatory/`, not in `results/confirmatory/`, because it exceeds the 20 MB commit limit.
  2. D-010: the aggregates come from `fare.summary`, which was added and tested before any confirmatory output and applies only the frozen rules.
  3. D-011 and D-012: this report was composed after the run session, under the owner's approval of 2026-11-25 ("approve all recommendations, RIGGED A", item 4), from committed results only.

## 8. Results

**Tuned configurations.** No selection lies on a grid edge.

| Arm | Selected | Mean tuning revenue |
|---|---|---|
| FIX | FIX(p = 139.61) | 11,672.0 |
| OCC | OCC(p0 = 159.24, k = 4) | 12,141.6 |
| DRP | DRP(p0 = 100.48, eta = 0.1) | 12,200.8 |
| FIX6 | FIX(p = 159.24) | 11,262.0 |

**Arm means over 4,000 evaluation streams** (revenue SD in brackets; `arm_summary.csv`):

| Arm | Revenue | Sell-through | Availability | Price volatility | Consumer surplus proxy | Total surplus proxy | Mean stock-out period |
|---|---|---|---|---|---|---|---|
| FIX | 11,715.6 (2,262.1) | 0.839 | 0.969 | 0 | 7,743.2 | 19,458.8 | 58.11 |
| OCC | 12,122.6 (2,667.8) | 0.932 | 0.994 | 0.0439 | 8,885.1 | 21,007.7 | 60.31 |
| DRP | 12,177.6 (2,574.6) | 0.985 | 0.983 | 0.0288 | 8,966.9 | 21,144.6 | 59.11 |
| FIX6 | 11,306.0 (2,836.5) | 0.710 | 0.993 | 0 | 6,725.8 | 18,031.8 | 60.34 |

A stock-out period of 61 (T + 1) means the stock never ran out.

**Primary contrasts** (n = 4,000 paired streams; 97.5% intervals; `metrics.csv`):

| Contrast | Mean diff | Bootstrap 97.5% | Paired t 97.5% | Relative | SD of diff | Class |
|---|---|---|---|---|---|---|
| OCC - FIX | 407.04 | [373.17, 440.17] | [373.30, 440.79] | +3.47% | 951.7 | detectable, practically relevant |
| DRP - FIX | 462.08 | [426.03, 498.13] | [426.14, 498.02] | +3.94% | 1,013.7 | detectable, practically relevant |
| OCC - FIX6 (sensitivity) | 816.60 | [789.75, 843.30] | [789.51, 843.70] | +7.22% | 764.4 | detectable, practically relevant |
| DRP - FIX6 (sensitivity) | 871.64 | [836.47, 905.82] | [836.83, 906.44] | +7.71% | 981.7 | detectable, practically relevant |

**Secondary contrasts** (descriptive, 95%, no multiplicity adjustment):

| Contrast | Sell-through | Availability | Consumer surplus proxy | Total surplus proxy |
|---|---|---|---|---|
| OCC - FIX | +0.093 [0.090, 0.096] | +0.025 [0.023, 0.027] | +1,141.8 [1,108.5, 1,174.9] | +1,548.9 [1,510.2, 1,587.7] |
| DRP - FIX | +0.146 [0.142, 0.151] | +0.014 [0.012, 0.016] | +1,223.7 [1,171.4, 1,275.0] | +1,685.8 [1,632.0, 1,739.8] |

**Mean price paid.**
- FIX: 139.61.
- OCC: 128.78 overall; L 129.28, H 127.86.
- DRP: 123.23 overall; L 115.59, H 130.96.

**Figures.**
- `figures/fig-EXP-001-forest-revenue.svg`: mean paired revenue differences with 97.5% bootstrap intervals and a grey band of plus or minus the SESOI.
- `figures/fig-EXP-001-base-diff.svg`: one dot per stream, n = 4,000 per arm.
- `figures/fig-EXP-001-base-price.svg`: price paths on evaluation stream 0.

## 9. Interpretation

- **What was measured.**
  - On this stream distribution, the tuned OCC and DRP rules earn 3.47% and 3.94% more revenue per season than the best of 36 fixed prices. Both intervals are far from 0.
  - Pairing matters. The revenue SD under FIX is 2,262.1, while the paired-difference SDs are 951.7 and 1,013.7.
- **How the gain arises.** This is a model-dependent inference from the secondary metrics and from an exploratory split (M4, J-0012).
  - On average, the dynamic arms sell more units (sell-through +0.093 and +0.146) at a lower mean price paid, and raise the consumer surplus proxy by 1,141.8 and 1,223.7.
  - The exploratory split by tercile of realised arrivals (policy-independent; `results/exploratory/m4_audit_sensitivity.json`, B3) shows that the mean gain is concentrated in the top tercile: OCC +1,063.5 and DRP +936.0 there, against +118.1 and +315.1 in the bottom tercile and +43.5 and +136.8 in the middle one. In the top tercile FIX sold out before the deadline in 85.5% of streams, and the rules' sell-through is essentially the same as FIX's.
  - Two channels therefore operate. In low-demand streams the rules sell stock that the fixed price leaves to perish. In high-demand streams, where most of the average gain arises, they earn more from the same units by raising prices when stock runs short. Version 1.0 of this report attributed the gain to the first channel only; that reading was incomplete and is withdrawn.
  - The rules do not gain on every stream: they lose to FIX on 36.375% (OCC) and 32.15% (DRP) of the 4,000 evaluation streams (B3).
- **Alternatives considered.**
  - **Grid resolution.** FIX6 earns 11,306.0, against 11,715.6 for FIX, so the 36-price FIX is the stronger baseline. Against FIX6, both contrasts keep their sign and class. Under the frozen rule, the result is therefore not attributed to grid resolution.
  - **Noise-chasing.** It would show up as losses, and none appear at this cell.
  - **Specificity to the tuning distribution.** This is tested in EXP-003, where the invalidation rule is not triggered.
- **Relation to the literature.** Gains of a few percent at C = 100 with shocks are consistent with a small, finite-scale gap to the asymptotically optimal fixed price (Gallego and van Ryzin, 1994). The asymptotic regime is not tested here.
- **Expected versus observed.** The planning expectation was a small gain, at most 5%. The observed gains are 3.47% and 3.94%.
- **Verdict under the frozen rule.** H0_OCC and H0_DRP are rejected. Both effects are detectable and practically relevant. The FIX6 sensitivity changes neither the sign nor the class.
- **M4 revisions (2026-11-25, version 1.1).** The frozen verdict is unchanged. Changes:
  1. Evidence audit (`research/publication/evidence_audit.md`): every number in this report was checked against the raw outputs; no mismatch was found here.
  2. The mechanism paragraph above was revised after the exploratory tercile split (J-0012, B3).
  3. Internal replication (exploratory, B2): the EXP-002 cell with the base parameters (sv0.5-k2.0) selects the same configurations on independent tuning and evaluation streams and gives +435.5 and +491.1; the differences from this report's estimates are +28.4 [-13.3, 70.2] (OCC) and +29.0 [-15.3, 73.4] (DRP), normal 95% intervals.
  4. Grid resolution (exploratory, B1): on the tuning streams the rules' advantage over the best of 36 fixed prices (+469.7 OCC, +528.8 DRP) combines a price-resolution loss (FIX at the rule's own p0 is 410.0 and 1,810.1 below the best fixed price) with a larger responsiveness gain (+879.6 and +2,338.9). This agrees with the frozen FIX6 check.
  5. Second review pass: the frozen FIX6 check could not have reversed a positive result. FIX6 chooses among 6 of FIX's 36 prices, so its tuning revenue cannot exceed FIX's, and the contrast against FIX6 is expected to be larger (it is: +816.6 and +871.6). The check is reported as frozen, but it carries little evidential weight; item 4 is the more informative check on grid resolution. Recorded in section 10.

## 10. Threats to validity

- **Internal.**
  - Selection noise from 500 tuning streams. Selection used tuning streams only, so evaluating the selected policies on held-out streams is unbiased.
  - No grid edge binds at the base cell.
- **External.**
  - Synthetic market only.
  - Myopic buyers with unit demand; strategic buyers are excluded (Su, 2007).
  - One seller, arbitrary parameters, no costs and zero salvage.
- **Construct.** Revenue is the tuning objective. The consumer surplus proxy depends on synthetic valuations.
- **Statistical.**
  - One cell, with 4,000 independent streams.
  - The bootstrap and paired t intervals agree closely.
  - The alpha control covers the two primary contrasts only.
  - The FIX6 sensitivity is one-sided by construction (section 9, M4 revisions, item 5).
  - The M4 checks (J-0012) are exploratory and were computed after the results were seen.
- **Hardware.** The machine was shared and loaded, so runtime is not a result.

## 11. Conclusion and next experiment

In this simulated base market, tuned OCC and DRP each raise expected revenue per season over the best tuned fixed price, by 3.47% and 3.94%. The 97.5% intervals exclude 0, and both effects exceed the 1% SESOI. This answers RQ1 for the base cell only.

Two results qualify it. The sign reverses in loose-capacity cells (EXP-002), and the rules lose when demand falls to 0.6 times the forecast (EXP-003).

Possible follow-ups would need a new EXP ID and the owner's approval: strategic buyers, or a known-model dynamic-programming reference.

## 12. Reproduction appendix

See `reproduction.md` in this folder.

References (verified):
- Gallego, G. and van Ryzin, G. (1994), Management Science 40(8):999-1020, DOI 10.1287/mnsc.40.8.999 (full text opened).
- Elmaghraby, W. and Keskinocak, P. (2003), Management Science 49(10):1287-1309 (abstract opened).
- Su, X. (2007) (abstract opened).

Details are in `research/literature_review.md`.
