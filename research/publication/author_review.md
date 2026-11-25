<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Owner review checklist

Status (2026-11-25): pending. Only the owner ticks the boxes in this file. Facts recorded so far, without ticking: the owner froze the protocols v1.0 on 2026-11-24 (D-009) and approved the manuscript title and the funding, competing-interest and AI-use statements on 2026-11-25 (D-014). The owner's full-text review of the manuscript is the main item below. On 2026-11-25 (M5) the AI assistant unticked the first box, which an agent had ticked in the freeze session (D-015).

- [ ] Protocols frozen by the owner (version and hash recorded): EXP-001, EXP-002, EXP-003 (v1.0, 2026-11-24, `research/freeze.json`, D-009).
- [ ] Authorship and affiliation metadata approved (no invented affiliation or funding).
- [ ] AI-assistance disclosure reviewed and accurate.
- [ ] Every registered experiment has a truthful standalone report.
- [ ] Claims audit reviewed.
- [ ] Limitations and claims boundary reviewed.
- [ ] Publication, push or release explicitly approved (or not).

M6 check (2026-11-25): no box in this file was ticked at the start of M6, so none was unticked. The AI assistant ticked nothing.

## Prepared for the owner (M6, 2026-11-25)

The AI assistant prepared this section. It decides nothing, and every box above stays for the owner.

### What to read for each box

1. **Protocols frozen.**
   - Read `research/freeze.json` (the approval quotes and the hashes).
   - Read decision D-009 in `research/decision_log.md`.
   - Run `PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-001/config.json`, which prints `frozen` true. Do the same for EXP-002 and EXP-003.
2. **Authorship and affiliation metadata.**
   - The manuscript front matter (`research/paper/manuscript.md`, lines 1 to 6) has the author "Mohamed Bechir Kefi" and states no affiliation.
   - `CITATION.cff` (`authors`, `title`, `version`).
   - The PDF metadata of `research/paper/manuscript.pdf`: title and author, with no e-mail address.
3. **AI-assistance disclosure.** Read `research/paper/manuscript.md` section 11, "AI assistance", the "Authorship" row of each report's section 1, and the last sentence of the `CITATION.cff` abstract.
4. **Truthful standalone reports.** Read `research/experiments/EXP-001/report.md`, `EXP-002/report.md` and `EXP-003/report.md`, or the matching `report.pdf` files: the status line, section 9 (M4 revisions) and section 10 (limitations) of each.
5. **Claims audit.** Read `research/claims_register.csv` (C-001 to C-015, E-001 to E-004), `research/publication/claims_audit.md`, `research/publication/evidence_audit.md` (sections 2 and 3; section 3 records the M6 source checks) and `research/publication/review_pass_2.md`.
6. **Limitations and claims boundary.**
   - Read `research/paper/manuscript.md` sections 7 and 8, and `research/limitations.md`.
   - Read the scope paragraph of `README.md` and the closing paragraphs of `articles/medium.md` and `articles/linkedin.md`.
7. **Publication, push or release.**
   - Read `research/publication/release_checklist.md` (status line and the evidence for each item).
   - Read `research/publication/reproducibility_report.md` and `research/publication/dependency_licences.md`.
   - The manuscript is easiest to review as `research/paper/manuscript.pdf` (17 pages).

### Open decisions for this repository

- Publication: whether to push, release, tag or publish anything is undecided (G-PUBLIC); M6 prepared a release candidate and released nothing.
- Licence: the licence files are unchanged and any licence change is the owner's decision (D-001).
- Owner-only facts: the repository URL, the demo URL, funding, competing interests, the author line and any affiliation are not decided by any instruction and must come from the owner.
- Release date: `CITATION.cff` has no `date-released` (coordinator default under the owner's "Next" of 2026-11-25), and re-adding it belongs to the owner's publication step.
- Version label: `CITATION.cff` now reads version `0.1.0-rc1` and carries the approved manuscript title (decision D-016); the owner may choose another label at release.
- Committed PDFs: the five PDFs are committed next to their sources (D-016), and the owner may instead prefer to build them only at release.
- Redrawn figures: the three forest figures were redrawn at M6 to fix clipped labels with the data unchanged (D-016), and the owner should confirm the new layout.
- Small figure text: Figure 3 of the manuscript (24 rows) prints at about 5 to 6 point on A4, readable only when zoomed, and the owner may want a larger layout before any print use.
- Source versions: Su (2007) was checked against the author's submitted version, not the version of record, and the owner may want the version of record checked before submission.
- Remaining local paths: the frozen protocols (`research/protocol.md`, `research/experiments/EXP-00N/protocol.md`), the session rules in `CLAUDE.md` and the append-only `progress.md` and `research/decision_log.md` still name absolute paths on the owner's machine; the frozen and append-only files cannot be edited, and `CLAUDE.md` is the owner's instruction file.
- Toolchain licence: pandoc (GPL-2.0-or-later) is used as an external build tool and is not distributed, which the owner may want to note in a release.

### Remaining owner placeholders (file and line)

- `research/paper/manuscript.md` line 293: "URL: placeholder, to be added by the owner if and when the repository is released".
- `research/paper/manuscript.md` line 308: "Funding and competing interests. To be stated by the owner before any release."
- `README.md` line 33: "Demo URL: placeholder, to be added by the owner if and when the demo is published."
- `README.md` line 54: "Repository URL: placeholder, ...", and "Funding and competing interests: to be stated by the owner before any release."
- `articles/medium.md` line 49: repository and demo URL placeholders.
- `articles/linkedin.md` line 12: "repository link placeholder, demo link placeholder".
- `demo/src/App.tsx` line 61: "Repository URL: placeholder, ..." in the page footer.
- `research/paper/manuscript.md` line 4 (`author:`) and `CITATION.cff` `authors`: an affiliation is not stated and is left to the owner.
- This file: every box above.

