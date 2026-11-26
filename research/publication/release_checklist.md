<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Release checklist

Status (2026-11-25, M6): release candidate prepared, awaiting the owner's review and G-PUBLIC. The AI assistant ticked only the items it verified in the M6 session, and the evidence follows each item. The two owner items stay unticked. Nothing is published or pushed without explicit owner approval.

Update (2026-11-26, D-017): the repository was pushed and is public at https://github.com/mohamedbechirkefi/fare-dynamic-pricing since 2026-11-25, so the sentence above now concerns the release (tag, GitHub release, DOI or preprint), none of which exists. The demo is to be hosted at https://fare-dynamic-pricing.kefimohamedbechir.workers.dev (Cloudflare Workers static assets, free plan, deployed by the coordinator). No box was ticked or unticked in this update.

- [x] **All registered experiments reported (including failed, null and exploratory).**
  - `research/experiment_registry.csv` lists EXP-001 to EXP-003, and each has `report.md` and a compiled `report.pdf` (7, 7 and 6 pages).
  - No registered experiment failed or was abandoned: 925,000 runs, 0 failed (`results/confirmatory/logs/`).
  - The exploratory checks are reported, labelled, in manuscript section 5.4 and journal J-0012.
- [x] **Manuscript complete; PDF compiled and visually inspected.**
  - Built by `PYTHONPATH=src .venv/bin/python scripts/build_pdfs.py --png-dir <scratch>`: `research/paper/manuscript.pdf`, 17 pages, 302,856 bytes.
  - All 17 pages were rendered at 60 ppi and inspected. The inspection covered pages, citations, tables, figures and equations.
  - Fixes R-1 and R-2 are in `reproducibility_report.md` section 4.
  - Metadata (pypdf): the title is set, there is no e-mail address and no local path.
  - Remaining issue: the Figure 3 text is small (owner item in `author_review.md`).
- [x] **`manuscript.tex` regenerated from `manuscript.md`.** The CONTRIBUTING pandoc command exited 0 on 2026-11-25 after the last manuscript edit.
- [x] **Artifact manifest complete; every figure and number traceable.**
  - 24 entries and 103 path references resolve (`reproducibility_report.md` section 3).
  - Raw files: 47 of 47 hashes match.
  - `python -m fare.audit` found 0 untraced numbers in the manuscript (455), the supplementary file (420) and the three reports (199, 268 and 209).
- [x] **Clean-clone reproduction recorded in `reproducibility_report.md`.**
  - Tests: 151 passed.
  - Smoke run: identical apart from ids and timings.
  - Demo: `A11Y-CHECK PASS`.
  - Export: deterministic (0 changed files).
- [x] **Demo built, offline after load, keyboard usable, responsive, fails closed on malformed results.**
  - The clean-clone run of `node tools/a11y_check.mjs dist` passed: keyboard 53 of 53, 360 px overflow 0 px, offline after first load, `A11Y-CHECK PASS`.
  - The fail-closed check is in the M5 record (`progress.md`), with the build unchanged.
- [x] **README, Medium and LinkedIn drafts use identical verified numbers and labels.** `tests/test_text_consistency.py` (6 tests, new at M6) passes: every number in `README.md`, `articles/*.md`, `demo/README.md` and the `CITATION.cff` abstract appears in the manuscript, with 1 documented exception, the fixture size in `demo/README.md`. The demo itself is covered by `tests/test_demo_export.py`.
- [ ] **Secret scan, personal-identifier scan and licence scan clean.** Verified at M6 (`git ls-files`, 235 tracked files at the start):
  - 0 e-mail addresses;
  - 0 tokens, keys or private-key headers;
  - 0 `.env` files;
  - no dependency licence outside the permissive list (`dependency_licences.md`).

  Not ticked, because absolute local paths remain in tracked files that may not be edited. At M6 there were 7: the frozen protocols (4 files), `CLAUDE.md`, and the append-only `progress.md` and `research/decision_log.md`. On 2026-11-26 (owner answer B9, D-017) `CLAUDE.md` was scrubbed, so 6 remain, all frozen or append-only (`reproducibility_report.md` section 6). These files are already public; the owner chose not to rewrite history.
- [ ] Owner review complete (`author_review.md`).
- [ ] Owner approval to publish recorded in `research/decision_log.md`.

## Version and date at the release (owner answer B8, 2026-11-26)

- `CITATION.cff` keeps `version: 0.1.0-rc1` and has no `date-released` until the release.
- At the release, `version` becomes `0.1.0` and `date-released` is set to the release day.
- `pyproject.toml` keeps its current version (`0.2.0`, set before M6), because changing it would change the lockfile and the recorded environments. The brief's general default names `0.0.0`; this repository's `pyproject.toml` already read `0.2.0` and is left unchanged.

## Release notes (draft)

- Figure 3 of the manuscript (24 rows, the EXP-003 forest plot) prints its labels at about 5 to 6 point on A4 and is readable when zoomed; it is kept as the committed, checksummed result (owner answer B11).
- External build and check tools are used but not redistributed: pandoc (GPL-2.0-or-later), Google Chrome (accessibility check of the demo), the Libertinus Serif font (SIL OFL 1.1, embedded as a subset in the PDFs) and the MPL-2.0 test and build tools hypothesis and lightningcss, as listed in `dependency_licences.md` (owner answer B13).
- The demo is a static page hosted at https://fare-dynamic-pricing.kefimohamedbechir.workers.dev (Cloudflare Workers static assets, free plan); the repository is https://github.com/mohamedbechirkefi/fare-dynamic-pricing.
