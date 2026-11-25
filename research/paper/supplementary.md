<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Supplementary material

Companion to `research/paper/manuscript.md` (version M4, 2026-11-25). Independent research, preprint draft, not peer-reviewed. All results are simulated. Every number is taken from the committed files named in each section; the number trace (`python -m fare.audit`) and the evidence audit (`research/publication/evidence_audit.md`) cover this file.

## S1. Complete experimental matrix

| Experiment | Cells | Arms | Tuning | Evaluation streams per cell | Runs (tuning + evaluation) | Status |
|---|---|---|---|---|---|---|
| EXP-001 | base | FIX, OCC, DRP, FIX6 | 36 configurations x 500 streams per family; FIX6 6 x 500 | 4,000 | 57,000 + 16,000 = 73,000 | confirmatory, complete, 0 failed |
| EXP-002 | 9 ($\sigma_v \in \{0.25, 0.5, 1.0\}$ x $\kappa \in \{1.0, 2.0, 4.0\}$) | FIX, OCC, DRP, re-tuned per cell | 36 x 500 per family per cell | 4,000 | 486,000 + 108,000 = 594,000 | confirmatory, complete, 0 failed |
| EXP-003 | 6 (demand x0.6, x0.8, x1.25, x1.6; reversed arrivals; no shocks) | FIX, OCC, DRP tuned at base; FIX re-tuned per cell | base tuning re-derived (3 x 36 x 500) plus 36 x 500 per cell for the reference | 4,000 | 162,000 + 96,000 = 258,000 | confirmatory, complete, 0 failed |

Run sets: `EXP-001-con-config-20261124T233503Z`, `EXP-002-con-config-20261124T233503Z`, `EXP-003-con-config-20261124T233547Z`. Source: `research/experiments/EXP-NNN/summary.json` (`counts`).

## S2. Extended tables

### S2.1 EXP-001 arm means (n = 4,000 per arm; revenue SD in brackets)

Source: `research/experiments/EXP-001/arm_summary.csv`.

| Arm | Policy | Revenue | Sell-through | Availability | Price volatility | Consumer surplus proxy | Total surplus proxy | Mean stock-out period |
|---|---|---|---|---|---|---|---|---|
| FIX | FIX(139.61) | 11,715.6 (2,262.1) | 0.839 | 0.969 | 0 | 7,743.2 | 19,458.8 | 58.11 |
| OCC | OCC(159.24, 4) | 12,122.6 (2,667.8) | 0.932 | 0.994 | 0.0439 | 8,885.1 | 21,007.7 | 60.31 |
| DRP | DRP(100.48, 0.1) | 12,177.6 (2,574.6) | 0.985 | 0.983 | 0.0288 | 8,966.9 | 21,144.6 | 59.11 |
| FIX6 | FIX(159.24) | 11,306.0 (2,836.5) | 0.710 | 0.993 | 0 | 6,725.8 | 18,031.8 | 60.34 |

A stock-out period of 61 means the stock never ran out.

### S2.2 EXP-002 tuned configurations

Source: `research/experiments/EXP-002/summary.json` (`tuning`, `grid_edge_findings`).

| Cell | FIX | OCC | DRP |
|---|---|---|---|
| sv0.25-k1.0 | 88.09 | (100.48, 0.5) | (100.48, 0.025) edge |
| sv0.25-k2.0 | 122.40 | (159.24, 8) edge | (100.48, 0.1) |
| sv0.25-k4.0 | 170.07 | (252.38, 4) | (159.24, 0.1) |
| sv0.5-k1.0 | 100.48 | (100.48, 0.25) edge | (100.48, 0.025) edge |
| sv0.5-k2.0 | 139.61 | (159.24, 4) | (100.48, 0.1) |
| sv0.5-k4.0 | 193.99 | (252.38, 4) | (159.24, 0.1) |
| sv1.0-k1.0 | 170.07 | (159.24, 0.25) edge | (252.38, 0.025) edge |
| sv1.0-k2.0 | 221.27 | (252.38, 0.5) | (252.38, 0.025) edge |
| sv1.0-k4.0 | 307.45 | (400, 8) edge | (252.38, 0.1) |

### S2.3 EXP-002 arm means (n = 4,000 per arm)

Source: `research/experiments/EXP-002/arm_summary.csv`.

| Cell | Arm | Revenue | Sell-through | Availability | Price volatility | Consumer surplus proxy |
|---|---|---|---|---|---|---|
| sv0.25-k1.0 | FIX | 7,254.0 | 0.823 | 0.967 | 0 | 4,919.5 |
| sv0.25-k1.0 | OCC | 7,129.0 | 0.745 | 0.995 | 0.0053 | 4,679.9 |
| sv0.25-k1.0 | DRP | 6,905.3 | 0.804 | 0.996 | 0.0123 | 5,430.9 |
| sv0.25-k2.0 | FIX | 10,776.4 | 0.880 | 0.959 | 0 | 5,475.4 |
| sv0.25-k2.0 | OCC | 11,591.5 | 0.970 | 0.993 | 0.0928 | 5,852.4 |
| sv0.25-k2.0 | DRP | 11,732.0 | 0.990 | 0.979 | 0.0288 | 5,575.3 |
| sv0.25-k4.0 | FIX | 15,491.3 | 0.911 | 0.961 | 0 | 4,978.5 |
| sv0.25-k4.0 | OCC | 16,018.7 | 0.952 | 1.000 | 0.0486 | 5,072.5 |
| sv0.25-k4.0 | DRP | 15,754.1 | 0.994 | 0.982 | 0.0310 | 4,978.6 |
| sv0.5-k1.0 | FIX | 6,873.7 | 0.684 | 0.994 | 0 | 6,348.4 |
| sv0.5-k1.0 | OCC | 6,836.7 | 0.699 | 0.995 | 0.0027 | 6,548.0 |
| sv0.5-k1.0 | DRP | 6,393.7 | 0.764 | 0.997 | 0.0137 | 7,576.0 |
| sv0.5-k2.0 | FIX | 11,756.6 | 0.842 | 0.969 | 0 | 7,755.4 |
| sv0.5-k2.0 | OCC | 12,192.1 | 0.934 | 0.994 | 0.0439 | 8,864.2 |
| sv0.5-k2.0 | DRP | 12,247.7 | 0.986 | 0.983 | 0.0290 | 8,931.7 |
| sv0.5-k4.0 | FIX | 17,221.2 | 0.888 | 0.960 | 0 | 8,476.6 |
| sv0.5-k4.0 | OCC | 18,315.2 | 0.958 | 0.996 | 0.0458 | 9,203.8 |
| sv0.5-k4.0 | DRP | 18,272.0 | 0.995 | 0.979 | 0.0285 | 9,024.7 |
| sv1.0-k1.0 | FIX | 7,141.9 | 0.420 | 1.000 | 0 | 11,223.4 |
| sv1.0-k1.0 | OCC | 7,021.5 | 0.467 | 1.000 | 0.0029 | 12,099.1 |
| sv1.0-k1.0 | DRP | 6,326.8 | 0.475 | 1.000 | 0.0279 | 12,458.4 |
| sv1.0-k2.0 | FIX | 14,067.0 | 0.636 | 0.997 | 0 | 18,573.8 |
| sv1.0-k2.0 | OCC | 13,950.7 | 0.607 | 1.000 | 0.0054 | 18,124.5 |
| sv1.0-k2.0 | DRP | 13,593.1 | 0.754 | 0.999 | 0.0158 | 21,144.8 |
| sv1.0-k4.0 | FIX | 24,916.0 | 0.810 | 0.975 | 0 | 26,870.6 |
| sv1.0-k4.0 | OCC | 25,952.6 | 0.947 | 0.998 | 0.0887 | 30,323.6 |
| sv1.0-k4.0 | DRP | 25,855.0 | 0.991 | 0.983 | 0.0273 | 30,624.9 |

Availability values shown as 1.000 are rounded; the exact means are in the source file.

### S2.4 EXP-003 arm mean revenue (n = 4,000; SD in brackets)

Source: `research/experiments/EXP-003/arm_summary.csv`. The base-tuned FIX is FIX(139.61) in every cell.

| Cell | FIX (base-tuned) | OCC | DRP | FIX re-tuned (price) |
|---|---|---|---|---|
| demand x0.6 | 7,580.2 (2,200.1) | 7,468.5 (2,388.4) | 7,383.3 (2,635.1) | 8,071.2 (1,892.7), p = 107.31 |
| demand x0.8 | 9,851.2 (2,447.6) | 9,983.6 (2,605.2) | 10,075.6 (2,669.4) | 10,023.0 (2,263.5), p = 130.72 |
| demand x1.25 | 13,096.1 (1,534.9) | 14,223.8 (2,423.6) | 14,183.4 (2,304.3) | 13,404.5 (2,025.7), p = 149.10 |
| demand x1.6 | 13,752.7 (747.3) | 16,285.4 (2,261.5) | 16,142.4 (2,197.1) | 15,326.4 (2,325.7), p = 170.07 |
| reversed arrivals | 11,739.5 (2,223.7) | 12,596.9 (2,399.0) | 11,720.0 (2,419.5) | 11,739.5 (2,223.7), p = 139.61 |
| no shocks | 11,313.5 (1,220.0) | 11,501.6 (1,078.4) | 11,750.9 (1,000.9) | 11,640.4 (770.0), p = 122.40 |

### S2.5 Secondary contrasts

The descriptive 95% contrasts of sell-through, availability, consumer surplus proxy and total surplus proxy for every cell and arm are in `research/experiments/EXP-NNN/metrics.csv` (one row per cell, arm, comparator and metric). They are not reproduced here to avoid a second copy.

## S3. Configurations and hashes

| Item | Path | SHA-256 |
|---|---|---|
| Study protocol v1.0 | `research/protocol.md` | `d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1` |
| EXP-001 protocol v1.0 | `research/experiments/EXP-001/protocol.md` | `06f939d8fd59389a3438cd539f862a36ed4d47275137b50aeb3ffdc233df2ec2` |
| EXP-002 protocol v1.0 | `research/experiments/EXP-002/protocol.md` | `7ffbc666ffd6465791d09e10ee3a3014002a513c90a876bf65c6e8ea4d2f6ab9` |
| EXP-003 protocol v1.0 | `research/experiments/EXP-003/protocol.md` | `b1e2a2f8931bada91fd5f4589f0fa8bd50004db6c05d568c9354f43f14a510fd` |
| EXP-001 config (canonical) | `research/experiments/EXP-001/config.json` | `592a197632390bb9ab8fdcf7e95555e3bb590c921faba573175c4dcaa9cffc76` |
| EXP-002 config (canonical) | `research/experiments/EXP-002/config.json` | `df7da4d68172d469301e6b46d70628dede3cfa255ee660898ceedf6d30d62856` |
| EXP-003 config (canonical) | `research/experiments/EXP-003/config.json` | `3c25c10c1cfcacf1103e6613b195c58c5ce0afd675556efa290f8b380ca039fd` |
| Data manifest | `data/manifest.json` | `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee` |

Code revision of all confirmatory runs: `4204eac0776f4a04e512ef5ce92a10eefa5c5252` (no tracked file modified). Seeds: `SeedSequence(entropy = 20261124, spawn_key = (experiment, cell, role, index))`; bootstrap and permutation seed 20261124.

## S4. Robustness results

### S4.1 Per-stream distribution (exploratory, M4)

Share of the 4,000 evaluation streams on which the rule earns less than FIX (the base-tuned FIX in EXP-003), and the median paired revenue difference. Source: `results/exploratory/m4_audit_sensitivity.json` (B3, J-0012). Post hoc and descriptive.

| Experiment | Cell | OCC share of streams lost | OCC median difference | DRP share of streams lost | DRP median difference |
|---|---|---|---|---|---|
| EXP-001 | base | 36.375% | +230.2 | 32.15% | +362.8 |
| EXP-002 | sv0.25-k1.0 | 75.3% | -272.9 | 80.1% | -553.5 |
| EXP-002 | sv0.25-k2.0 | 16.3% | +695.8 | 12.7% | +917.5 |
| EXP-002 | sv0.25-k4.0 | 34.8% | +438.7 | 46.6% | +93.5 |
| EXP-002 | sv0.5-k1.0 | 63.1% | -46.3 | 87.1% | -520.3 |
| EXP-002 | sv0.5-k2.0 | 33.4% | +277.7 | 30.9% | +415.7 |
| EXP-002 | sv0.5-k4.0 | 20.8% | +930.5 | 24.4% | +894.6 |
| EXP-002 | sv1.0-k1.0 | 64.9% | -139.2 | 90.8% | -810.4 |
| EXP-002 | sv1.0-k2.0 | 62.8% | -138.8 | 73.6% | -504.2 |
| EXP-002 | sv1.0-k4.0 | 33.6% | +607.0 | 35.7% | +646.6 |
| EXP-003 | demand x0.6 | 55.8% | -104.9 | 56.7% | -178.6 |
| EXP-003 | demand x0.8 | 42.6% | +126.8 | 38.4% | +263.7 |
| EXP-003 | demand x1.25 | 21.9% | +748.3 | 21.4% | +815.0 |
| EXP-003 | demand x1.6 | 8.75% | +2,478.6 | 8.675% | +2,284.3 |
| EXP-003 | reversed arrivals | 14.4% | +698.1 | 53.2% | -68.2 |
| EXP-003 | no shocks | 38.0% | +169.1 | 26.4% | +442.3 |

Even where the mean gain is positive and relevant, the rules lose on a fifth to a third of streams in most cells; the means summarise a wide distribution.

### S4.2 Tuning-stream decomposition (exploratory, M4, in-sample)

Mean tuning revenue on the 500 tuning streams of each cell. "Resolution" is FIX at the rule's selected $p_0$ minus the best of 36 fixed prices (zero or negative); "responsiveness" is the rule minus FIX at its own $p_0$. Their sum is the rule's tuning-stream advantage over the best fixed price. Source: `results/exploratory/m4_audit_sensitivity.json` (B1, J-0012). In-sample and selection-biased for every family; not a frozen analysis.

| Experiment | Cell | Best of 36 FIX | Best of 6 FIX | OCC: resolution, responsiveness | DRP: resolution, responsiveness |
|---|---|---|---|---|---|
| EXP-001 | base | 11,672.0 | 11,262.0 | -410.0, +879.6 | -1,810.1, +2,338.9 |
| EXP-002 | sv0.25-k1.0 | 7,095.8 | 6,929.2 | -166.7, +60.2 | -166.7, -162.0 |
| EXP-002 | sv0.25-k2.0 | 10,736.3 | 9,865.1 | -1,337.7, +2,146.2 | -871.2, +1,828.7 |
| EXP-002 | sv0.25-k4.0 | 15,577.9 | 15,236.4 | -9,600.9, +10,112.4 | -341.5, +589.2 |
| EXP-002 | sv0.5-k1.0 | 6,762.6 | 6,762.6 | 0.0, -26.0 | 0.0, -462.4 |
| EXP-002 | sv0.5-k2.0 | 11,707.4 | 11,278.5 | -428.9, +863.0 | -1,833.3, +2,291.7 |
| EXP-002 | sv0.5-k4.0 | 17,098.1 | 15,670.8 | -3,743.0, +4,948.0 | -1,427.3, +2,568.2 |
| EXP-002 | sv1.0-k1.0 | 7,097.4 | 7,061.8 | -35.6, -99.3 | -269.5, -543.2 |
| EXP-002 | sv1.0-k2.0 | 14,087.2 | 13,914.9 | -172.3, +89.7 | -172.3, -280.9 |
| EXP-002 | sv1.0-k4.0 | 24,864.1 | 23,557.9 | -1,652.9, +2,518.7 | -1,306.2, +2,152.3 |

The large resolution parts (for example -9,600.9 for OCC in sv0.25-k4.0) occur where the rule starts far from the best fixed price and its response moves the price a long way; they show that a rule's $p_0$ is not its typical price, so the decomposition is informative mainly where the response is weak (the lower-edge cells).

### S4.3 Internal replication and tuning optimism (exploratory, M4)

- EXP-002 sv0.5-k2.0 minus EXP-001, mean paired revenue difference: OCC +28.4 [-13.3, 70.2], DRP +29.0 [-15.3, 73.4] (normal 95%, independent samples; B2).
- Evaluation minus tuning mean revenue of the selected configuration at the base cell: FIX +43.6, OCC -19.0, DRP -23.2, FIX6 +44.0 (B4). Across EXP-002 cells it ranges from -86.6 to +222.7. Evaluation streams are held out, so this optimism does not bias the confirmatory contrasts.

## S5. Experiment report links

| Experiment | Report | Reproduction | Machine-readable outputs |
|---|---|---|---|
| EXP-001 | `research/experiments/EXP-001/report.md` (v1.1) | `research/experiments/EXP-001/reproduction.md` | `summary.json`, `metrics.csv`, `arm_summary.csv`, `run_manifest.json`, `figures/` |
| EXP-002 | `research/experiments/EXP-002/report.md` (v1.1) | `research/experiments/EXP-002/reproduction.md` | as above |
| EXP-003 | `research/experiments/EXP-003/report.md` (v1.1) | `research/experiments/EXP-003/reproduction.md` | as above |

Report PDFs are not built yet (release-candidate milestone).

## S6. Deviations from the frozen protocol and owner decisions

None of the items below changes a protocol, a configuration, a seed, an exclusion rule or an analysis rule.

| Item | Decision | What happened |
|---|---|---|
| Raw output location | D-010 | Raw outputs (21.5 MB, 147.8 MB, 132.2 MB) were written to the git-ignored `results/raw/confirmatory/` instead of `results/confirmatory/`, above the 20 MB commit limit; their SHA-256 hashes are committed. |
| Aggregation module | D-010 | `fare.summary`, added and tested before any confirmatory output, applies only the frozen rules. |
| Execution conditions | D-010 | EXP-002 ran as a second worker on a shared, loaded machine; all runs stayed within the frozen wall-clock caps. |
| Holm tables printed for EXP-001 and EXP-003 | D-010 | The generic report prints them; Holm is frozen only for EXP-002, so they are not reported. |
| Reports written after the run session | D-011, D-012 | The owner approved writing the 11.3 reports from committed results only (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4); the coordinator wrote them. |
| Pre-freeze exploratory values | freeze record C4 | Primary-contrast values on tuning streams (n = 50, an earlier grid) were seen before the freeze and are disclosed. |
| Scope cuts | D-008 (owner) | No dynamic-programming reference policy and no scale-sensitivity experiment. |
| M4 interpretation and audit | D-013 | Exploratory checks J-0012; report corrections (EXP-002 sign count) and interpretation revisions; no verdict changed. |
