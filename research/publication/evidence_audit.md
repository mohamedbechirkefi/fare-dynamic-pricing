<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5, M4)

**Date.** 2026-11-25. **Performed by.** The AI assistant (Claude Code). This is internal quality control, not external review. The owner's review is pending (`author_review.md`).

**Scope.** Every number in these documents:
- `research/paper/manuscript.md` and `supplementary.md`;
- the three experiment reports (v1.1) and their `reproduction.md` files;
- `research/publication/review_pass_2.md`;
- the claims register.

The audit checks each number against the committed evidence and the raw confirmatory outputs. It also checks each external claim against the sources actually read.

**Tools and records.**
- **Recomputation.** `experiments/exploratory/m4_audit_sensitivity.py` writes `results/exploratory/m4_audit_sensitivity.json`, section `audit` (journal J-0012).
- **Number trace.** `python -m fare.audit` (module `src/fare/audit.py`, tested in `tests/test_audit.py`).
- **Keyed table check.** `experiments/audit/keyed_table_check.py`.
- **Regeneration.** `fare.summary` was rerun into a scratch directory.

## 1. Checks and outcomes

| Check | Method | Outcome |
|---|---|---|
| Raw output integrity | SHA-256 of every raw file against `summary.json` `raw_manifest` | 47 of 47 files match |
| Run counts and failures | Recount of runs and statuses from the raw `result.json` files | 16,000, 108,000 and 96,000 evaluation runs, all ok; 925,000 runs in total with tuning; 3 exit statuses 0, no other confirmatory attempt |
| Arm summaries | Independent recomputation of mean and SD of 8 metrics per cell and arm | 880 values, maximum relative discrepancy 0.0 |
| Contrasts | Independent recomputation of n, mean, SD, paired t interval and relative effect for every row of `metrics.csv` | 174 rows, maximum relative discrepancy 0.0 |
| Uncertainty | Replay of every revenue bootstrap interval with the frozen seed 20261124 and 10,000 resamples | 46 of 46 intervals identical |
| Classification | SESOI classes recomputed from the committed intervals and the comparator mean | 0 mismatches |
| Interval levels | Level column of `metrics.csv` against the text | 0.975 for the four EXP-001 revenue contrasts, 0.95 elsewhere, as stated |
| Denominators | Relative effects recomputed as the mean difference over the comparator's mean on the same paired streams | match (part of the contrast check) |
| Units | Text against the metric definitions | Revenue and surplus proxies in abstract currency units per season; shares dimensionless; raw sizes in decimal MB (21.5, 147.8, 132.2); peak memory in MiB (396.5 = 415,727,616 bytes) |
| Regeneration | `fare.summary` rerun on the raw outputs | `metrics.csv`, `arm_summary.csv` and the 3 forest figures byte-identical; `summary.json` identical except the output path list (`figures`) |
| Figures | Committed price-path and per-stream figures against the raw report figures | 17 of 17 byte-identical; the manuscript references them in place (no copies) |
| Number trace | Every decimal number and comma-grouped integer in the documents, matched at the displayed precision to a value in a committed JSON or CSV evidence file | manuscript 455, supplementary 420, reports 199, 268 and 208, review pass 64: 0 untraced after the fixes below |
| Keyed table check | Manuscript Tables 2, 3 and 5 against the exact `metrics.csv` row for each cell, arm and comparator | 92 checks, 0 mismatches |
| EXP-002 elasticities | Values printed in the git-ignored raw report re-derived from the scenario parameters | 9 of 9 agree to the printed precision |
| Count statements | Signs of the 18 EXP-002 and 12 EXP-003 revenue intervals counted by script | EXP-002: 8 below 0, 10 above; EXP-003 against base-tuned FIX: 2 below 0, 9 above, 1 including 0 |

**Limits of these checks.**
- The number trace shows that a number exists in the evidence. It does not show that the number is quoted for the right quantity. That was checked by the keyed table check for the main tables and by reading for the prose.
- Small numbers such as 0.5 match many stored values, so the trace is weak for them.
- Integers below 1,000 are not traced automatically; counts such as "8 negative" were checked by script (last row).

## 2. Findings and fixes

| ID | Where | Finding | Fix |
|---|---|---|---|
| F-1 | EXP-002 report v1.0, section 9 | "7 negative and 11 positive" contrasts; the committed results give 8 and 10. The claims register (C-004) already said 8 and 10. | Corrected in v1.1, with a dated note. |
| F-2 | EXP-001 report v1.0, section 9 | The mechanism statement ("the gain comes from selling stock that the fixed price leaves to perish, not from charging more on average") is contradicted in part by the exploratory tercile split: most of the gain arises where FIX sells out and sell-through is unchanged (B3). | Withdrawn; replaced by a two-channel description. |
| F-3 | EXP-002 report v1.0 | The protocol requires the per-cell elasticity, but the values were only in a git-ignored file. | Copied with provenance into the committed audit JSON, re-derived, and reported. |
| F-4 | `research/experiment_registry.csv` | Status still said "11.3 report not yet written". | Updated. The protocol-hash column is untouched, and the freeze guard still reports all three experiments frozen. |
| F-5 | `README.md`, `CITATION.cff` | Status said that no confirmatory experiment had run and that there were "no findings yet". | Status lines updated. Findings are not added to the README before M5. |
| F-6 | `research/limitations.md`, `claims_audit.md`, `artifact_manifest.json`, `research/paper/figures/README.md` | Headers or status lines from M0 or M3 were stale. | Updated. |
| F-7 | Manuscript draft, section 2 | The draft said fixed-price policies "built from" the deterministic bound are asymptotically optimal; the source as read says "simple, fixed price policies are asymptotically optimal". | Wording follows the source. |
| F-8 | Claims register | Rows lacked a result id, config hash, figure or table and manuscript section. | Columns added; 15 result claims and 4 external claims. |
| F-9 | Draft shares | Two shares fell exactly on a rounding half (0.3215, 0.08675), so a one-decimal percentage was ambiguous. | Exact values are given (32.15%, 8.675%). |
| F-10 | EXP-001 report, FIX6 | The frozen grid-resolution check is one-sided by construction (review pass, item 1.5). | Disclosed in the report, the manuscript and the claims register; verdict unchanged. |
| F-11 | EXP-003 report | The invalidation rule's benchmark is equally misspecified (review pass, item 1.6). | Disclosed; verdict unchanged. |

No number in a frozen artifact (protocols, configs, freeze record) was changed. No confirmatory result was recomputed in a way that replaces a committed value.

## 3. External claims

| Claim | Source | Access | Status in the manuscript |
|---|---|---|---|
| E-001: fixed-price policies are asymptotically optimal as expected sales grow; the optimal price depends on remaining stock and time | Gallego and van Ryzin (1994) | Full text retrieved (author-hosted PDF, SHA-256 in `literature_review.md`). The statements used appear in the abstract, which was checked. | Cited as read |
| E-004: the deterministic bound gives asymptotically optimal heuristics in the network case | Gallego and van Ryzin (1997) | Abstract only | Marked "abstract only read" |
| E-002: review of dynamic pricing with inventory; airlines and hotels as the classical setting | Elmaghraby and Keskinocak (2003) | Abstract only | Marked "abstract only read" |
| E-003: strategic customers change price paths and welfare | Su (2007) | Abstract only | Marked "abstract only read" |
| Existence of work on pricing and learning | den Boer (2013) thesis | Front matter only | Named as existing work, explicitly not cited for content |

Unverified sources in `literature_review.md` (den Boer 2015, Talluri and van Ryzin 2004, Bitran and Caldentey) are not cited. Every entry in `references.bib` that the manuscript cites is in the reference list. The hotel booking dataset (Antonio et al., 2019) is in the bibliography file, but the manuscript does not cite it, because no dataset was used.

## 4. Strength and scope of evidence per conclusion

| Conclusion | Evidence | Strength | Scope |
|---|---|---|---|
| The rules beat FIX at the base cell (C-001, C-002) | Confirmatory, frozen rule, n = 4,000, replicated on independent streams (B2) | Strong within the model | One parameter cell |
| The sign depends on the cell; losses with loose capacity (C-004, C-005) | Confirmatory, Holm, n = 4,000 per cell | Strong for the signs; two OCC losses are weak against the rule's structure (B1) | 9 cells of one model |
| The gain grows with tightness (C-006) | Descriptive interaction contrasts | Moderate (descriptive; tightness and price level move together) | 3 dispersion levels |
| Robust to moderate misspecification (C-007) | Confirmatory rule | Moderate (the benchmark is equally misspecified) | Two one-factor shifts |
| Lost under a large shortfall; against a re-tuned FIX, relevant gains only above forecast and, for OCC, with reversed arrivals (C-008, C-013) | Descriptive | Moderate (unadjusted 95%) | Six one-factor shifts |
| The gain is mostly a hedge against demand shocks (C-010, C-013) | Exploratory split plus the no-shocks cell | Suggestive | Base cell |
