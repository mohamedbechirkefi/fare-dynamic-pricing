<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Claims audit

Status (2026-11-25, M4): applied by the AI assistant to every row of `research/claims_register.csv` (C-001 to C-015, E-001 to E-004). The owner's review of the register is pending and belongs to M6. Details are in `research/publication/evidence_audit.md` and `research/publication/review_pass_2.md`.

- [x] **Numerical claims are mapped.** Each numerical claim gives its experiment and run set (`result_id`), config hash, figure or table, manuscript section and evidence path. Each number in it traces to a committed result file (`python -m fare.audit`, 0 untraced).
- [x] **External claims are mapped.** Each external claim maps to a source in `research/literature_review.md`, marked full text, abstract only or front matter only. No unverified source is cited.
- [x] **Numbers are cross-checked against the raw outputs.** This covers denominators, units, precision, uncertainty and sample counts: 880 arm values, 174 contrast rows and 46 bootstrap replays, all exact.
- [x] **No out-of-boundary claim.** No causal, real-world, airline personalisation or fare-prediction claim appears in the manuscript, the reports or the register.
- [x] **Labels are distinct.** Simulated, exploratory and confirmatory results are labelled separately. C-009 to C-011 are exploratory, and C-006, C-008, C-012 to C-015 are descriptive.
- [x] **Second review pass done.** It argued against the preferred hypothesis and is recorded in `review_pass_2.md`.
- [x] **Qualified claims.** C-003, C-005 and C-007 carry the M4 qualifications: the one-sided FIX6 check, p0 resolution, and the equally misspecified benchmark.
- [x] **Removed or unsupported claims.**
  - Withdrawn: the EXP-001 v1.0 mechanism sentence (finding F-2). It had no register row and is replaced by C-010.
  - Corrected: the EXP-002 v1.0 sign count (F-1).
- [ ] **Owner review** of the register and of this audit.
