<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Second review pass: arguing against the preferred reading (M4)

**Date.** 2026-11-25. **Performed by.** The AI assistant (Claude Code), as internal quality control under master prompt 11.5. This is not external peer review, and the owner has not yet reviewed it.

**Object.** `research/paper/manuscript.md` (M4 draft), the three experiment reports (v1.1) and the claims register.

**Preferred reading under challenge.** "Tuned simple dynamic pricing rules earn more than a well-tuned fixed price." This reading is the headline of EXP-001 (C-001, C-002). The pass asks what else could explain the results, where the text says more than the evidence, and whether anything was left out.

Each item gives the challenge, the evidence, a verdict (holds, partly holds or rejected) and what changed.

## 1. Strongest alternative readings

### 1.1 The base cell is a favourable choice

- **Challenge.** The base parameters ($\kappa = 2$: arrivals twice capacity) were chosen by the study, and a tight market favours dynamic rules. Leading with the base-cell gain overstates the general case.
- **Evidence.** The base parameters were fixed before any data (protocol v0.1, frozen v1.0). Still, only 5 of 9 EXP-002 cells favour the rules, and all three loose-capacity cells reverse the sign (C-004, C-005).
- **Verdict.** Partly holds. The parameters were not cherry-picked after the data, but the base cell is not representative of the grid.
- **Change.** The abstract and conclusion now present the result as conditional and give the losses in the same sentence as the gains. The manuscript title names "simple dynamic pricing rules", not dynamic pricing in general.

### 1.2 The gain is a response to demand uncertainty, not to dynamic structure

- **Challenge.** If a fixed price knew the stream's demand level, the rules might have nothing left to add.
- **Evidence.** Without shocks (EXP-003), the rules gain little or lose against a correctly re-tuned fixed price (OCC -1.19%, DRP +0.95%, C-013). At the base cell, most of the mean gain arises in the top tercile of realised arrivals (B3, C-010).
- **Verdict.** Holds. In this model the rules' value is mainly a hedge against demand shocks.
- **Change.** Section 6 of the manuscript now states this as a mechanism. The EXP-001 report's mechanism paragraph was rewritten (item 2.1).

### 1.3 The losses are artifacts of the rules' coarse starting-price grid

- **Challenge.** This is the symmetric challenge, against the negative findings. The rules choose among 6 starting prices, while FIX chooses among 36. A rule that cannot start at the right price could lose for that reason alone.
- **Evidence.** The exploratory tuning-stream decomposition (B1, C-011) splits each rule's advantage into a price-resolution part and a responsiveness part. For OCC in sv0.25-k1.0 and sv1.0-k2.0, the responsiveness part is positive (+60.2, +89.7), and the loss comes from resolution (-166.7, -172.3). For DRP in the loose-capacity cells, the response itself loses: -462.4 of -462.4 in sv0.5-k1.0 and -543.2 of -812.7 in sv1.0-k1.0. EXP-002 registered no FIX6 arm, so the frozen analysis cannot check this.
- **Verdict.** Partly holds. Two of the 8 negative contrasts, both OCC, are weak evidence against the occupancy rule's structure. The DRP losses are not artifacts. B1 is in-sample on the tuning streams.
- **Change.** EXP-002 report section 9, manuscript Table 8 and limitations item 18. C-005 now carries the caveat.

### 1.4 The frozen lower-edge reading is wrong for DRP

- **Challenge.** The protocol reads a DRP optimum at $\eta = 0.025$ as "close to a fixed price". If so, a large DRP loss at that edge is puzzling.
- **Evidence.** At $\eta = 0.025$, DRP's mean price paid is 81.6 against $p_0$ = 100.48 (sv0.5-k1.0) and 130.7 against 252.38 (sv1.0-k1.0) (C-012). The update compounds over 60 periods, and with loose capacity the clearance target is never met, so the price keeps falling.
- **Verdict.** Holds. The frozen reading is true of the parameter and false of the realised prices.
- **Change.** The frozen reading is kept, because it is frozen, and the contradiction is disclosed in the EXP-002 report (sections 8 and 9), the manuscript (sections 5.2 and 6) and limitations item 17.

### 1.5 The EXP-001 grid-resolution check could not have failed

- **Challenge.** FIX6 chooses among a subset of FIX's prices, so it cannot do better than FIX on the tuning streams. The contrast against FIX6 can therefore only grow, and "no change of sign or class" was guaranteed in advance for a positive result.
- **Evidence.** The contrasts against FIX6 are +816.6 and +871.6, larger than against FIX, as expected.
- **Verdict.** Holds. The check is reported as frozen, but it carries little evidential weight.
- **Change.** EXP-001 report section 9 (M4 revisions, item 5) and section 10; manuscript Tables 7 and 8; C-003 limitation.

### 1.6 The invalidation test is weaker than it looks

- **Challenge.** EXP-003's rule compares the base-tuned rules with a base-tuned fixed price that is misspecified in the same way. Passing the rule shows that the rules degrade less than the fixed price. It does not show that they keep a structural advantage.
- **Evidence.** Against the re-tuned fixed price, both x0.8 contrasts are within the SESOI (-0.39%, +0.52%). At x0.8 the re-tuned fixed price earns 10,023.0 against 9,851.2 for the base-tuned one.
- **Verdict.** Holds.
- **Change.** EXP-003 report section 9 (M4 revisions, item 2) and section 10; manuscript sections 5.3 and 6; C-007 limitation.

### 1.7 Tightness or price level?

- **Challenge.** The interaction pattern ("the gain grows with tightness") could reflect the tuned price level, or the elasticity at that price, rather than tightness itself.
- **Evidence.** The elasticity at the tuned fixed price changes with $\kappa$ as well as with $\sigma_v$ (-0.955 to -2.156; C-015). Both factors move together by design.
- **Verdict.** Holds as a caution. The design cannot separate them.
- **Change.** C-006 limitation; manuscript Table 8; EXP-002 report section 10.

## 2. Overgeneralisation and unsupported statements

### 2.1 Mechanism in the EXP-001 report

- **Problem.** Version 1.0 said the gain "comes from selling stock that the fixed price leaves to perish, not from charging more on average". The tercile split shows that the largest gains arise where FIX sells out and sell-through is unchanged.
- **Verdict.** The statement was incomplete.
- **Change.** It was withdrawn and replaced by a two-channel description (EXP-001 report v1.1, section 9).

### 2.2 "Dynamic pricing" in conclusions

- **Problem.** The draft conclusion spoke of "the value of simple dynamic pricing".
- **Change.** It now says "for these two rule families" and notes that other rules, including a known-model optimal policy, were not tested.

### 2.3 Significance language

- **Problem.** "All 18 contrasts reject H0" reads as strong evidence. With 4,000 paired streams, any effect of practical size is rejected, and every raw p-value sits at the permutation floor.
- **Change.** Manuscript section 5.2 now says that the information is in the signs, effect sizes and SESOI classes.

### 2.4 Averages hide frequent losses

- **Problem.** Even at the base cell, the rules lose on 36.375% (OCC) and 32.15% (DRP) of streams (B3).
- **Change.** These shares are reported in the EXP-001 report, the manuscript (Table 6) and supplementary S4.1.

### 2.5 External claims

- **Problem.** The draft said Gallego and van Ryzin (1994) prove that fixed prices "built from" the deterministic bound are optimal. The source as read states that simple fixed-price policies are asymptotically optimal.
- **Change.** The wording now follows the source. Three of the four references were read as abstracts only, and the manuscript marks them so.

### 2.6 Gains against the re-tuned fixed price

- **Problem.** A draft of the abstract and conclusion said that, against a fixed price re-tuned to the true demand, the rules gain "only when demand exceeds the forecast".
- **Evidence.** With reversed arrivals, the re-tuned price equals the base price and OCC gains +7.30%. Without shocks, DRP gains +0.95%, which is detectable but below the SESOI.
- **Change.** The statements now say that the practically relevant gains are confined to demand above the forecast and, for OCC, to reversed arrivals. This applies to the abstract, sections 5.3 and 9, Table 8 and the evidence-audit scope table.

## 3. Stale figures, leakage and missing runs

### 3.1 Stale figures

- **Check.** `fare.summary` was rerun on the raw outputs into a scratch directory.
- **Result.** `metrics.csv`, `arm_summary.csv` and the three forest figures are byte-identical to the committed files. The 17 committed price-path and per-stream figures are byte-identical to the figures in the raw reports.
- **Design.** The manuscript references the experiment figures in place, so no copy can go stale.
- **Verdict.** No stale figure.

### 3.2 Leakage

- **Stream separation.**
  - Tuning and evaluation streams are separated by the spawn-key role (0 or 1). The runner refuses exploratory configs that use role 1.
  - EXP-003 re-derives the base tuning from EXP-001's tuning keys and evaluates on its own keys (experiment 3).
  - EXP-002 uses experiment key 2.
  - No evaluation stream was generated before the freeze (freeze record).
- **One disclosed exposure.** Before the freeze, primary-contrast values on tuning streams were seen with an earlier grid, and the owner chose the widened grids with these values available (C4).
- **Verdict.** This is a mild forking-paths risk on the grid choice, not leakage of held-out data. It is already disclosed, and it is now repeated in the manuscript (section 4.1).

### 3.3 Missing failed runs

- **Planned runs.** The recount from the raw outputs gives 16,000 + 108,000 + 96,000 evaluation runs, all with status ok. The three exit statuses are 0, and there was no other confirmatory attempt (`results/confirmatory/logs/exit_status.jsonl`).
- **Exploratory runs.** The smoke and pilot runs are journaled (J-0002 to J-0007).
- **M4 failures.** The first execution of the M4 script failed on an empty cell. It is recorded in J-0012.
- **Verdict.** No run is missing from the record.

## 4. Points examined and rejected

- **"FIX is a strawman."** Rejected. FIX is re-tuned in every cell on 36 prices with the same tuning streams. At the base cell it is the strongest fixed baseline available: FIX6 earns less, 11,306.0 against 11,715.6.
- **"Selection on tuning streams inflates the rule contrasts."** Rejected for the confirmatory contrasts, because evaluation streams are held out. The tuning optimism (B4) is in any case small: at the base cell it is +43.6 for FIX, -19.0 for OCC and -23.2 for DRP.
- **"The two analyses of EXP-001 disagree."** Rejected. The bootstrap and paired t intervals agree to within about 1 currency unit (Table 2).
- **"The base result is a fluke of one stream set."** Rejected. EXP-002 sv0.5-k2.0 reproduces it on independent streams, with differences of +28.4 [-13.3, 70.2] and +29.0 [-15.3, 73.4] (B2).

## 5. Net effect on conclusions

- **Unchanged.** No frozen verdict changes: H0 is rejected for both EXP-001 contrasts, all 18 EXP-002 contrasts reject, and the EXP-003 rule is not triggered.
- **Changed.** The interpretation is narrower than in the M3 reports:
  1. The base-cell gain is conditional on scarcity and on demand above the forecast, and in this model it acts mainly as a hedge against demand shocks.
  2. The DRP losses with loose capacity come from its clearance target.
  3. Two OCC losses may be grid artifacts.
  4. The FIX6 and EXP-003 robustness checks are weaker than their frozen wording suggests.
