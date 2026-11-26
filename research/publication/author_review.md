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
   - The manuscript front matter (`research/paper/manuscript.md`, lines 1 to 6) has the author line "Mohamed Bechir Kefi, independent researcher" (owner answer B3, 2026-11-26).
   - `CITATION.cff` (`authors` with `affiliation: "Independent researcher"`, `title`, `version`, `repository-code`).
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

- Publication: the repository was pushed and is public since 2026-11-25 (this sentence was corrected on 2026-11-26; at M6 nothing had been pushed). Whether to release, tag or publish anything further is undecided (B18); no release, tag or DOI exists.
- Licence: the licence files are unchanged and any licence change is the owner's decision (D-001).
- Owner-only facts: answered by the owner on 2026-11-26 (repository URL, demo URL, funding, competing interests, author line and affiliation); see the section below.
- Release date: `CITATION.cff` has no `date-released` (coordinator default under the owner's "Next" of 2026-11-25), and re-adding it belongs to the owner's publication step.
- Version label: `CITATION.cff` now reads version `0.1.0-rc1` and carries the approved manuscript title (decision D-016); the owner may choose another label at release.
- Committed PDFs: the five PDFs are committed next to their sources (D-016), and the owner may instead prefer to build them only at release.
- Redrawn figures: the three forest figures were redrawn at M6 to fix clipped labels with the data unchanged (D-016), and the owner should confirm the new layout.
- Small figure text: Figure 3 of the manuscript (24 rows) prints at about 5 to 6 point on A4, readable only when zoomed, and the owner may want a larger layout before any print use.
- Source versions: Su (2007) was checked against the author's submitted version, not the version of record, and the owner may want the version of record checked before submission.
- Remaining local paths: the frozen protocols (`research/protocol.md`, `research/experiments/EXP-00N/protocol.md`) and the append-only `progress.md` and `research/decision_log.md` still name absolute paths on the owner's machine; `CLAUDE.md` was scrubbed on 2026-11-26 (owner answer B9; list in `reproducibility_report.md` section 6).
- Toolchain licence: pandoc (GPL-2.0-or-later) is used as an external build tool and is not distributed, which the owner may want to note in a release.

### Remaining owner placeholders (file and line)

Updated 2026-11-26 after the owner's answers. The repository URL, demo URL, funding, competing-interest and affiliation placeholders listed at M6 are filled (README, manuscript sections 10 and 11, `CITATION.cff`, `articles/medium.md`, `articles/linkedin.md`, `demo/README.md`, `demo/src/App.tsx`). What remains:

- This file: every box above (owner only).
- `CITATION.cff`: `date-released` absent and `version` `0.1.0-rc1` until the release (B8).

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-approvals-2026-11-26.md`, outside this repository). Applied by the AI assistant in decision D-017. No box above was ticked.

- **A1.** Out-of-date "nothing pushed" sentences corrected in `README.md`, `release_checklist.md`, this file and `articles/`. Append-only records were not edited.
- **B1.** Repository URL https://github.com/mohamedbechirkefi/fare-dynamic-pricing in the README, manuscript section 10, articles, demo footer and `CITATION.cff` (`repository-code`).
- **B2.** Demo URL https://fare-dynamic-pricing.kefimohamedbechir.workers.dev; `demo/wrangler.jsonc` (assets only, `./dist`); hosting stated in `demo/README.md`. Deployment is done by the coordinator, not by this repository.
- **B3.** Author line "Mohamed Bechir Kefi, independent researcher" in the manuscript, supplementary file, the three experiment reports, README, articles and demo footer; `CITATION.cff` `affiliation: "Independent researcher"`. `pyproject.toml` has no authors field and was not changed. Frozen protocols were not edited.
- **B4.** Manuscript section 11: "No funding was received." and "The author declares no competing interests."; the same in the README.
- **B6, B7.** The title was already owner-approved (D-014) and `CITATION.cff` already carries it; nothing changed.
- **B8.** Recorded in `release_checklist.md`.
- **B9.** `CLAUDE.md` scrubbed; remaining paths listed in `reproducibility_report.md` section 6.
- **B10.** The committed PDFs stay.
- **B11, B13.** Release-note sentences in `release_checklist.md` (Figure 3 small labels; external tools not redistributed).
- **B14.** The source labels (Su (2007) author version; Elmaghraby and Keskinocak (2003) abstract only) are accepted as stated in the manuscript.
- **R-FARE-1.** The redrawn forest-figure layout belongs to the owner's full-text review (B16) and stays open.

Still open (owner only): B15 article drafts and their titles; B16 the full-text review of the manuscript and the sign-off of every box above (including R-FARE-1); B18 the release, tag and any DOI or preprint. No protocol freeze is pending in this repository.
