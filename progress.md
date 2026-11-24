<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: M0 session (bootstrap, feasibility, M1 drafts)

**Milestone.** M0, plus the M1 drafts that M0 asks for. Performed by the AI assistant (Claude Code) following `master_prompt.md` and the shared M0 brief. No confirmatory experiment was run.

**Starting state.** `git status`: on branch main, nothing to commit, working tree clean. One commit (e8fbf0c, the master prompt and the owner's licence package).

**Decisions.** D-001 to D-005 in `research/decision_log.md` (licence is the owner's choice; synthetic-only data; zero-cost Typst toolchain; dependency cap 2026-11-10; draft protocol choices pending freeze).

**Commands and actual outputs.**

```
$ sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize
Apple M1 Pro
10
17179869184
$ sw_vers
ProductName:  macOS
ProductVersion:  15.3.1
BuildVersion:  24D70
$ df -h /Users/bechir/research/labs | tail -1
/dev/disk3s1   460Gi   312Gi   127Gi    71%    3.1M  1.3G    0%   /System/Volumes/Data
$ /usr/local/bin/python3 --version
Python 3.12.1
$ .tools/py/bin/uv --version
uv 0.9.5 (d5f39331a 2025-10-21)
$ .tools/py/bin/typst --version
no such file or directory   (typst exists only as a Python package)
$ .tools/py/bin/python -c "import typst, pypdf, PIL; ..."
typst 0.15.0 / pypdf 6.20.0 / pillow 11.3.0
$ .tools/pandoc --version | head -1
pandoc 3.6.3
$ /Users/bechir/research/helix/.tools/node/bin/node --version
v22.23.3
$ git --version
git version 2.42.1
$ which tex pdflatex xelatex tectonic
tex not found / pdflatex not found / xelatex not found / tectonic not found
```

```
$ uv lock --python /usr/local/bin/python3
Using CPython 3.12.1 interpreter at: /usr/local/bin/python3
Resolved 16 packages in 9ms
(uv.lock records exclude-newer = "2026-11-10T00:00:00Z"; latest upload-time among locked files 2026-11-06)
Locked: numpy 2.5.4, jsonschema 4.26.0, pytest 9.2.0, hypothesis 6.170.15 (plus transitive dependencies)
$ uv sync --frozen --python /usr/local/bin/python3
exit 0; imports checked: numpy 2.5.4, jsonschema 4.26.0, hypothesis 6.170.15, pytest 9.2.0
```

Exploratory toolchain check (journal entry J-0001, not research evidence):

```
$ pandoc research/paper/manuscript.md -s -t typst -o <scratch>/manuscript.typ ; typst.compile(...)
typst.TypstError: font fallback list must not be empty          (FAILURE: default template emits font: ())
$ pandoc ... -t typst -V mainfont="Libertinus Serif" ; typst.compile(...)
compile s 0.13 ; pages 3                                         (success; PDF kept in session scratch only, not committed)
$ pandoc research/paper/manuscript.md -s -t latex   (with SPDX header prepended)
exit 0 ; research/paper/manuscript.tex 125 lines (generated, not compiled: no TeX)
```

Web sources opened (details and SHA-256 of retrieved PDFs in `research/literature_review.md`): Gallego and van Ryzin 1994 (full text), Gallego and van Ryzin 1997 (abstract), Elmaghraby and Keskinocak 2003 (abstract), Su 2007 (abstract), den Boer 2013 thesis (front matter), Antonio et al. 2019 (full article). Failed: Bitran and Caldentey survey PDF (HTTP 404). Unverified: den Boer 2015 survey, Talluri and van Ryzin 2004 book.

**Draft protocol hashes (SHA-256, draft v0.1, not frozen; will change if edited before the freeze).**

- research/protocol.md: 1ca28cf1f46d8ddabbb8ae5aeae138ea0e8e7b754410029fc78d1b2e68e24a14
- research/experiments/EXP-001/protocol.md: 0066a421e09217a7184f92a1de3e3c1f24dafd4c74b6b41e2706350fd283b984
- research/experiments/EXP-002/protocol.md: de6aa076d43f02bf341e642a3f370d5022a7fee03d7f6c43f1d972025f541e09
- research/experiments/EXP-003/protocol.md: a7b83e766343b301f42615a36ed9e5b23b878a53b984b862182207d5bc0810e4

**Files created.** CLAUDE.md, roadmap.md, progress.md, README.md, CITATION.cff, pyproject.toml, uv.lock; research/{protocol.md, feasibility.md, decision_log.md, literature_review.md, limitations.md, claims_register.csv (header only), experiment_journal.jsonl, experiment_registry.csv}; research/experiments/EXP-001..003/protocol.md; research/paper/{manuscript.md (headings only), manuscript.tex (generated), references.bib, supplementary.md, figures/README.md}; research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}; data/manifest.json; README.md in results/, src/, tests/, experiments/, demo/, articles/. **Changed:** CONTRIBUTING.md (appended section 6, development commands). Licence files untouched.

**Tests.** None exist yet (no code). No test count is claimed.

**Failures and deviations.** (1) No `typst` executable in `.tools/py/bin` as the brief stated; the Python package is used. (2) Default pandoc Typst template fails to compile without `mainfont`; fixed by passing `-V mainfont="Libertinus Serif"`. (3) Bitran and Caldentey survey not retrievable (404). (4) `.gitignore` (part of the owner's licence package) does not ignore generated `research/paper/manuscript.typ` and `.pdf`; left unchanged, so those must not be committed until the owner decides.

**Outstanding risks.** See `research/feasibility.md` section 7 (null-effect likelihood, arbitrary parameters, unequal tuning resolution, myopic buyers, no TeX, borrowed Node).

**Owner decisions needed.**
1. Freeze (or amend) `research/protocol.md` and the three EXP protocols (G-FREEZE), including: primary metric revenue; nondirectional H1; SESOI 1%; n = 300 streams; equal 36-configuration tuning budget; base parameters.
2. Confirm synthetic-only data (D-002) and that the hotel booking dataset stays unused (its data licence is unconfirmed).
3. Whether the optional scale-sensitivity experiment and dynamic-programming reference arm are in scope.
4. Whether `.gitignore` may be extended to cover generated paper build files.
5. Authorship metadata for the manuscript.

**Next action.** M2: implement the demand-stream generator, FIX baseline, simulator and invariant tests (stock conservation, price bounds, no-demand, sold-out, policy nesting), then OCC and DRP, output schema and run manifests; run an exploratory smoke on tuning streams only.

## 2026-11-24: M2 session (core implementation; exploratory smoke and pilot)

**Milestone.** M2, core implementation, carried out while the freeze is pending. The work was done by the AI assistant (Claude Code), following `master_prompt.md` and the shared M2 brief. No confirmatory run was made. No protocol was frozen or edited. Nothing was pushed.

**Starting state.** `git status`: on branch main, nothing to commit, working tree clean. HEAD was 8aaa494.

**Implemented (`src/fare/`).**
- `params.py`: validated scenario parameters with units.
- `streams.py`: seeded demand-stream generator with `SeedSequence` spawn keys (experiment, cell, role, index), stream SHA-256 and prepared per-period tables.
- `policies.py`: the FIX baseline, then OCC and DRP.
- `simulate.py`: fast simulator, naive reference oracle and invariant checker.
- `metrics.py`: protocol metrics and purchase elasticity.
- `tuning.py`: equal-budget grids, selection with ties going to the lowest index, and a grid-edge flag.
- `stats.py`: paired bootstrap, paired t (its own t quantile, since there is no scipy), sign-flip permutation, Holm, SESOI classification and required n.
- `runner.py`: config to results. It refuses a confirmatory config while the protocol is unfrozen. It refuses an exploratory config that touches evaluation streams. It refuses overlapping stream sets.
- `schema.py` and `schemas/result.schema.json`: result schema 1.0.0, validated at export and import, with semantic checks.
- `manifest.py`: run manifest with config hash, seeds, git revision, dirty flag, OS, CPU, versions, runtime and peak RSS. Its freeze check compares the registry hash with the on-disk protocol hash.
- `report.py`: Markdown tables, metrics CSV, SVG figures (price paths re-simulated and checked against the recorded stream hash) and a Holm table across cells. It renders PDFs through pandoc to Typst.
- `cli.py`: `smoke`, `run` (with `--plan`), `report` (with `--pdf`) and `test`.

**Configs.**
- `research/experiments/EXP-00N/config.json`: the planned confirmatory configs. The CLI refuses them.
- `experiments/smoke.json`.
- `experiments/exploratory/pilot-exp00N.json`: tuning streams 0 to 49 for tuning and 50 to 99 for evaluation.

**Decisions.** D-006 (implementation choices where the protocol is silent) and D-007 (proposed amendments, not decided).

**Commands and actual outputs.**

```
$ PYTHONPATH=src uv run --frozen --python /usr/local/bin/python3 python -m fare.cli test
133 passed in 5.90s            (after the elasticity test; 132 passed before it)
133 passed in 1.74s            (final run before the last commit, revision f3218eb plus documentation changes)
$ PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-001/config.json
REFUSED: EXP-001: protocol 'research/experiments/EXP-001/protocol.md' is not frozen (G-FREEZE). ...
planned: EXP-001 12,900 runs; EXP-002 105,300; EXP-003 39,600   (same refusal for EXP-002 and EXP-003)
$ uv lock --offline --python /usr/local/bin/python3
Updated fare-dynamic-pricing v0.0.0 -> v0.2.0      (no dependency change; uv lock --check passes)
```

Final exploratory runs at revision f3218eb (clean tracked tree), commands from `CONTRIBUTING.md` section 6:

```
EXPLORATORY run set EXP-001-exp-smoke-20261124T161050Z: 0 tuning + 125 evaluation runs, 0 failed, 0.09 s, peak RSS 43.6 MiB
EXPLORATORY run set EXP-001-exp-pilot-exp001-20261124T161050Z: 5850 tuning + 200 evaluation runs, 0 failed, 0.47 s, peak RSS 51.6 MiB
EXPLORATORY run set EXP-002-exp-pilot-exp002-20261124T161051Z: 48600 tuning + 1350 evaluation runs, 0 failed, 3.93 s, peak RSS 62.1 MiB
EXPLORATORY run set EXP-003-exp-pilot-exp003-20261124T161055Z: 16200 tuning + 1200 evaluation runs, 0 failed, 1.76 s, peak RSS 56.2 MiB
```

**Exploratory measurements.** These are planning inputs for the owner, not findings. Source: `results/exploratory/pilot_summary.json` and journal entries J-0002 to J-0005.
- **Runtime per run.** Each simulation run (one policy, one season) took 0.055 to 0.19 ms during tuning. Measured all-inclusive time, with stream generation, metrics and bootstrap, was 0.09 to 0.26 ms per run. The range comes from five repeats this session on a machine shared with other sessions. The EXP-002 pilot wall time was 4.1, 6.5, 11.4, 5.7 and 3.9 s on the same work. Outputs were identical across repeats, because they are deterministic.
- **Projected full draft matrix.** 157,800 runs. The committed summary projects 9.0 s from the tuning rate and 13.4 s all-inclusive. A repeat made while the machine was loaded gave up to 41 s. All of these are far under the protocol's one CPU-hour cap.
- **Seed spread.** Over 5 smoke streams in the base cell, revenue for the hand-set FIX(150) had mean 10,560 and SD 3,522: the between-stream spread is about a third of the mean, so pairing is essential. Pilot SDs of the paired revenue differences in the base cell (n = 50) were 655 for OCC minus FIX and 871 for DRP minus FIX.
- **Seed count.** For the 1% SESOI (115.9) at two-sided alpha 0.025, the required n at power 0.89 is 384 (OCC) and 680 (DRP), so the planned n = 300 is inadequate. Across the EXP-002 cells the range is 144 to 2,735, and across the EXP-003 cells 257 to 3,435. See D-007, item 1.
- **Degenerate cases.**
  - Zero demand and all valuations below p_min give identical zero outcomes under every policy, by design.
  - With C = 1, the 1% SESOI is below one currency unit and is meaningless. That cell is a code check only.
  - Nesting holds exactly: OCC with k = 0 and DRP with eta = 0 equal FIX on every smoke stream.
  - No pilot cell had all-zero paired differences.
  - Tuned optima sit at grid edges in every pilot cell: DRP at eta = 0.1, and OCC at k = 4 or k = 0.5. See D-007, item 3.
- **Purchase elasticity** at the tuned FIX price across the EXP-002 cells: -1.05 to -2.16.

**Failures and deviations during the session.**
1. In the first fast simulator, a period in which demand exactly equals the remaining stock was handled wrongly: it counted later arrivals in that period as having found stock. The differential test against the reference oracle caught this before any recorded run, and the fix is `k < x`.
2. The first `report --pdf` attempt failed because relative paths were passed to pandoc with a different working directory. It was fixed by resolving the paths. A 4-page PDF of the EXP-001 pilot report then compiled. Generated `.typ` and `.pdf` files were deleted and are not committed, because `.gitignore` is the owner's (M0 open item 4).
3. Untracked output directories made every later manifest report "dirty". The flag now counts tracked files only (`dirty_tracked_files`). Exploratory outputs from before that fix, the elasticity commit and the repository-relative path fix were deleted and regenerated at f3218eb. Before that fix, the smoke manifest recorded an absolute local config path.
4. One test, which asserted that the 36-price FIX grid weakly dominates the 9-price grid, was removed before it was run: the 9 prices are not a subset of the 36, so the claim is false.

**Not done.**
- The EXP-002 interaction-contrast interval (D-007, item 7).
- Individual experiment reports (11.3): no experiment has been executed confirmatorily.
- No change to `.gitignore` or to the licence files.
- No demo UI (M5).

**Changed files.** `src/fare/*`, `tests/*`, `experiments/*`, `research/experiments/EXP-00N/config.json`, `results/exploratory/*`, `pyproject.toml` (version, pytest config), `uv.lock` (project version only), `research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv (status), limitations.md}`, `roadmap.md`, `progress.md`, `README.md`, `CONTRIBUTING.md` (section 6), `data/manifest.json`, `src/README.md`, `tests/README.md`, `results/README.md` and `experiments/README.md`.

**Outstanding risks.**
- The pilot sample-size estimates rest on n = 50 tuning streams.
- Grid-edge optima mean that the draft comparison partly measures the grids.
- Runtime measurements are noisy on the shared machine.

**Owner decisions needed (in addition to the M0 list).** D-007, items 1 to 7: n, tuning streams, grids, the DRP target-rate reading, pinning the D-006 choices, command names and the interaction-contrast method. After those, freeze the protocols (G-FREEZE).

**Next action.** After the owner's decisions and freeze:
1. Update the configs to the frozen values.
2. Implement the interaction contrast.
3. Run EXP-001 to EXP-003 confirmatorily (M3).
4. Write each 11.3 report as its experiment finishes.

## 2026-11-24: Freeze session (owner-approved amendments; freeze not performed)

**Milestone.** M1 freeze, following `/Users/bechir/research/labs/_shared/FREEZE-brief.md` and the FARE section of `/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24.md`. Performed by the AI assistant (Claude Code). No confirmatory run. Nothing pushed.

**Starting state.** `git status`: on branch main, clean; HEAD 88fdddf.

**Decisions.** D-008: five of the six approved FARE amendments applied, plus C3 authorship; the grid amendment could not be applied as written; the freeze was therefore not performed.

**What changed.**
- Protocols to draft v0.2 with dated "Amendments before freeze (owner-approved 2026-11-24)" sections: 500 tuning and 4,000 evaluation streams; no DP reference and no scale experiment; D-006 choices and the DRP target reading pinned; EXP-002 interaction method named; commands fixed.
- Configs: tuning count 500, evaluation count 4,000 (grid unchanged).
- Code: configurable sensitivity grids (`occ_k`, `drp_eta`; unknown grid keys refused; draft defaults kept so pre-freeze configs reproduce); the tuning-grid sensitivity arm is named after its price count (FIX9 draft, FIX6 v1.0); `stats.interaction_bootstrap_ci` and a report table for the EXP-002 interaction contrasts; freeze guard extended: a confirmatory run needs the registry hash, a `research/freeze.json` record of the experiment protocol, the main protocol and the canonical config hash, all matching the files on disk; `manifest.build_freeze_record` writes that record.
- Records: registry (draft v0.2, not frozen, not yet run), decision log, journal J-0006, roadmap, README, CITATION.cff and manuscript authorship ("Mohamed Bechir Kefi", AI assistant disclosed, not an author); `manuscript.tex` regenerated by pandoc.

**Commands and actual outputs.**

```
$ PYTHONPATH=src .venv/bin/python experiments/exploratory/grid_interior_check.py > results/exploratory/grid_interior_check.json
summary: draft-v0.1 20 of 20 optima on a grid edge; v1.0 (D-007 grid) 7 of 20 on an edge
$ PYTHONPATH=src .venv/bin/python experiments/exploratory/grid_widening_probe.py > results/exploratory/grid_widening_probe.json
3.67 s user; DRP eta = 0 selected in sv0.5-k1.0 and sv1.0-k1.0
$ PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-00N/config.json
EXP-001 74,500 runs; EXP-002 594,000; EXP-003 258,000
$ PYTHONPATH=src .venv/bin/python -m fare.cli test
138 passed in 1.86s
$ PYTHONPATH=src .venv/bin/python -m fare.cli run --config research/experiments/EXP-00N/config.json
REFUSED (exit 3) for all three: registry protocol hash missing or different from the protocol on disk
```

**Draft v0.2 hashes (SHA-256, not frozen).**

- research/protocol.md: efdd6d19f4a3db7f332c8323959b160a82254cd799647a392ef38e42327abc6c
- research/experiments/EXP-001/protocol.md: 43d4c0865d67c389e1fbdce7412733e1096f16627000c29e9a50e224e2533c37
- research/experiments/EXP-002/protocol.md: f21c664a5ee6240bf8c8a75a59bcc23f0c0b9f9f6e7fb1d64451c5b4fe6120d9
- research/experiments/EXP-003/protocol.md: 2891e10f1fe10a8513600448f6953e7345c6c9b8308855b7a4e8abc70695ea77

**Failures and deviations.** The grid amendment's stated goal (interior pilot optima) is not met by the proposed grid in 7 of 20 pilot cases, and cannot be met for DRP in two cells whose optimum is eta = 0. Item stopped per the brief; no freeze record written, because freezing would fix a grid the owner asked to change.

**Outstanding risks.** The EXP-002 result file at n = 4,000 is roughly 100 MB (D-007, item 1); per-run storage under the git-ignored `results/raw/` must be settled before M3.

**Owner decisions needed.** The tuning-grid ruling, options (a) to (c) in D-008. After it: set the grid in the protocol text and configs, then write `research/freeze.json` with `fare.manifest.build_freeze_record`, record the hashes in the registry, and check that `run` accepts the frozen configs.

**Next action.** Owner ruling on the grid; then the freeze; then M3 when the coordinator schedules it.
