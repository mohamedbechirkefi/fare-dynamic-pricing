<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# research/paper/figures/

Figures are generated once, from versioned results, and reused in place. The manuscript (M4) therefore references the experiment figures directly, and this folder holds no copies that could go stale:

| Manuscript figure | Artifact ID | Path |
|---|---|---|
| Figure 1 | F-EXP-001-forest | `research/experiments/EXP-001/figures/fig-EXP-001-forest-revenue.svg` |
| Figure 2 | F-EXP-002-forest | `research/experiments/EXP-002/figures/fig-EXP-002-forest-revenue.svg` |
| Figure 3 | F-EXP-003-forest | `research/experiments/EXP-003/figures/fig-EXP-003-forest-revenue.svg` |

All three are written by `src/fare/summary.py`. They regenerate byte-identically from the raw outputs (M4 audit).
