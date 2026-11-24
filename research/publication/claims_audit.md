<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Claims audit

Status (2026-11-24): no claims exist; `research/claims_register.csv` holds the header only.

Checklist, applied to every claim before any release:

- [ ] Each numerical claim maps to experiment ID, run IDs, config or protocol hash and a result path.
- [ ] Each external claim maps to a source marked "opened" in `research/literature_review.md`.
- [ ] Denominators, units, precision, uncertainty and sample counts cross-checked against raw outputs.
- [ ] No causal, real-world, airline personalisation or fare-prediction claim.
- [ ] Simulated, exploratory and confirmatory results labelled distinctly.
- [ ] Second review pass that argues against the preferred hypothesis completed and recorded.
