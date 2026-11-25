<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Reproducibility report

Status (2026-11-25, M6): clean-clone reproduction performed by the AI assistant (Claude Code) on the owner's machine. Actual commands and outputs follow; nothing below is a planned value. Machine: Apple M1 Pro laptop, macOS, shared with other sessions, so timings are indicative only. At most 2 workers were used.

## 1. Clean clone

- **Clone.** `git clone -q <repository> <scratch>/clone`, a local clone of the then-current HEAD, with no network access needed. The scratch folder lies outside the repository and was deleted afterwards.
- **Revision.** `ecbbca355328ac986413ea2e319a9dab2dff0ac6` (commit "M5: interactive experience ...").
- **Date.** 2026-11-25.
- **Git-ignored inputs absent from the clone.** `results/raw/` (the confirmatory raw outputs, 47 files) and `demo/node_modules`. The clone therefore tests what a third party receives.

| Step | Command (in the clone) | Actual output |
|---|---|---|
| Locked install | `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` | 14 packages installed from `uv.lock` (numpy 2.5.4, jsonschema 4.26.0, pytest 9.2.0, hypothesis 6.170.15 and their dependencies); a second run printed `Audited 14 packages in 4ms` |
| Python | `.venv/bin/python --version` | `Python 3.12.1` |
| Test suite | `.venv/bin/python -m pytest -q` | `151 passed in 22.03s` (wall clock 27.0 s, cold caches) |
| Smoke reproduction | `PYTHONPATH=src .venv/bin/python -m fare.cli smoke --no-report --out <scratch>/smoke` | `EXPLORATORY run set EXP-001-exp-smoke-20261125T191754Z: 0 tuning + 125 evaluation runs, 0 failed, 0.10 s, peak RSS 44.1 MiB` |
| Smoke comparison | field-by-field comparison of the new `result.json` with the committed `results/exploratory/EXP-001-exp-smoke-20261124T233439Z/result.json` | `config.json` byte-identical; in `result.json`, 137 differing leaves, all of them identifiers or timings: 125 `run_id`, 5 `eval_s`, 5 `stream_generation_s`, `created_utc`, `run_set_id`. Every metric, stream hash, price and sale is identical (tolerance 0) |
| Demo install | `cd demo && npm ci --prefer-offline` (Node v22.23.3, offline cache) | `added 53 packages in 1s` |
| Demo tests | `npm test` | `Test Files 2 passed (2)`, `Tests 31 passed (31)` |
| Demo build | `npm run build` | `dist/index.html 0.99 kB`, `dist/assets/sandbox.worker-B08EYJ0Z.js 6.04 kB`, `dist/assets/index-BHY9J5mL.css 7.02 kB`, `dist/assets/index-CIQDcuSr.js 251.80 kB`, `built in 311ms` (same asset hashes as the M5 build) |
| Accessibility and offline check | `node tools/a11y_check.mjs dist` | 9 PASS lines (results render with 3 experiment panels; contrast light and dark; keyboard 53 of 53; focus indicator; 360 px overflow 0px; reduced motion 0 running; no request leaves the origin; offline after first load, sandbox 200 seasons) and `A11Y-CHECK PASS` |
| Export determinism | `PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py`, then `git status --short` | `wrote demo/public/data/results.json (138087 bytes)`; `git status` printed nothing (0 changed files); `export_demo_data.py --check` printed `results.json is up to date` |

**Clean-clone findings.** None. Every step passed in the first clone, so no fix was needed for the clone itself. The fixes below came from the other M6 checks; they are re-checked in a second fresh clone (section 4).

## 2. Committed results regenerated from the raw outputs (working repository)

The raw outputs are git-ignored and exist only on the owner's machine (`results/raw/confirmatory/`).

- **Raw integrity.** The SHA-256 of every raw file matched `raw_manifest` in the three `summary.json` files: 47 of 47.
- **Regeneration.** `PYTHONPATH=src .venv/bin/python -m fare.summary --result results/raw/confirmatory/<run_set_id>/result.json --out <scratch>/regen/EXP-00N` (EXP-003 with `--exp001-summary research/experiments/EXP-001/summary.json`) took 46.6 s for the three experiments. In the outputs:
  - `metrics.csv` and `arm_summary.csv` are byte-identical for all three experiments;
  - in `summary.json` only the output-path list `figures` differs, as at M4;
  - the forest figures differ by the M6 layout fix only (section 3, finding R-1), and their embedded data description (`<desc>`) is identical.

## 3. Data manifest, artifact manifest and links

| Check | Command or method | Result |
|---|---|---|
| Data manifest | SHA-256 of `data/manifest.json`, compared with the hash recorded in the three `run_manifest.json` and `summary.json` files and in `EXP-001/reproduction.md` | `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee` in all 7 places. The manifest lists no downloaded dataset (synthetic data only), so there is no data file to hash |
| Artifact manifest | every `path`, `result_path` and `generator_script` in `artifact_manifest.json`, after expanding `EXP-NNN`, `<cell>` and brace lists | 24 entries; 103 path references resolve; 33 of them point to the three git-ignored raw `result.json` files, which are present locally and hash-checked |
| Relative links | `.venv/bin/python scripts/check_links.py` (new; tested in `tests/test_links_refs.py`) | `46 Markdown files, 60 links, 0 unresolved` |
| Bibliography | `tests/test_links_refs.py` | 4 bib entries, 4 listed references, each matched by first author, year and DOI; every body citation is listed; no `[@key]` left. The uncited dataset entry was removed |
| Numbers in README, articles and CITATION | `tests/test_text_consistency.py` (new); `python -m fare.audit` | Every number appears in the manuscript (1 documented exception: "1,000", the size of the sandbox fixture, in `demo/README.md`). Trace: manuscript 455, supplementary 420, reports 199, 268 and 209, README 18, articles 24, 4 and 1, CITATION 5 numbers, 0 untraced. In `demo/README.md`, 3 numbers were checked and 1 untraced: the same fixture size |

## 4. M6 fixes and the fresh-clone re-check

| ID | Finding | Fix |
|---|---|---|
| R-1 | The three forest figures were clipped: the axis caption ran past the right edge, and in EXP-003 the long row labels were cut on the left. | `src/fare/summary.py` `forest_svg` sizes the label column to the longest label and splits the caption over two lines. The figures were regenerated from the raw outputs, and the data are unchanged (section 2). |
| R-2 | In the PDF build, image captions printed "Figure 1: Figure 1.", table cells were centred and justified, and long hashes ran out of table cells. | Typst rules in the new `scripts/build_pdfs.py`. The Markdown is unchanged. |
| R-3 | Absolute home-directory paths appeared in `README.md`, `CONTRIBUTING.md`, `demo/README.md`, `research/feasibility.md`, `EXP-001/reproduction.md` and `src/fare/report.py`. | Replaced by paths relative to the repository (`../.tools/`) or by a description. `report.py` reads `FARE_TOOLS_DIR` or the sibling `.tools/` folder. |

The fresh-clone re-check of the committed release candidate is recorded in section 5.

## 5. Fresh-clone re-check after the M6 commit

A second fresh clone was made of the M6 commit `bef6384` (2026-11-25) and deleted afterwards.

| Step | Actual output |
|---|---|
| `uv sync --frozen --all-groups --all-extras` | 14 packages installed |
| `.venv/bin/python -m pytest -q` | `161 passed in 3.85s` |
| `.venv/bin/python scripts/check_links.py` | `47 Markdown files, 60 links, 0 unresolved` |
| `fare.cli smoke --no-report` and comparison | `0 tuning + 125 evaluation runs, 0 failed, 0.10 s, peak RSS 43.4 MiB`; differences only in 125 `run_id`, 5 `eval_s`, 5 `stream_generation_s`, `created_utc`, `run_set_id` |
| `scripts/export_demo_data.py`, then `git status --short` | `wrote demo/public/data/results.json (138087 bytes)`; 0 changed files |
| `npm ci --prefer-offline`, `npm test`, `npm run build` | `added 53 packages`; `Tests 31 passed (31)`; `index-CIQDcuSr.js 251.80 kB` |
| `node tools/a11y_check.mjs dist` | `A11Y-CHECK PASS` |
| `scripts/build_pdfs.py` | Without the toolchain next to the clone, it stops with "pandoc or the tools Python (typst package) is not available", the intended message. With `FARE_TOOLS_DIR` pointing to the shared toolchain, the five PDFs are rebuilt at the committed sizes (302,856, 187,283, 152,207, 141,051 and 120,206 bytes); they differ from the committed files in 58 bytes (manuscript) and 96 bytes (EXP-003 report), the embedded build timestamp and identifiers |
