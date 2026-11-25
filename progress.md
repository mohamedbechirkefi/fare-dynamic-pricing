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

## 2026-11-24: Ratification session (second-round ruling; freeze completed)

**Milestone.** M1 freeze, following `/Users/bechir/research/labs/_shared/RATIFY-brief.md` and section 2 of `/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24b.md` ("Approve all"). Performed by the AI assistant (Claude Code). No confirmatory run. Nothing pushed. FARE has no ratified follow-on choice (section 3) and no new pre-data rule (section 4).

**Starting state.** `git status`: on branch main, clean; HEAD a3ce6d4.

**Decisions.** D-009: widened grids within the equal budget, grid-edge reporting rule, freeze v1.0.

**What changed.**
- Commit 1d0fcfc: protocols to frozen v1.0 text (grids in section 4, grid-edge rule in section 4, FIX6 arm, EXP-001 run count 73,000, second-round amendment sections); configs name `p0_n` 6, `occ_k`, `drp_eta`; `fare.tuning.edge_labels`, `fare.report.grid_edge_findings` and a report section; tests updated (real protocols frozen, frozen configs accepted, changed configs refused, plan counts, grid-edge findings).
- Second commit: `research/freeze.json` (built with `fare.manifest.build_freeze_record`, revision 1d0fcfc), registry v1.0 hashes and status, decision log, roadmap (M1 gate passed), README, limitations, CONTRIBUTING (one comment line in section 6), author review checklist.

**Commands and actual outputs.**

```
$ PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-00N/config.json
EXP-001 total_runs 73000; EXP-002 594000; EXP-003 258000
$ PYTHONPATH=src .venv/bin/python -m pytest -q        (before the freeze record existed)
2 failed, 139 passed   (the two tests that require the freeze record; expected)
$ PYTHONPATH=src .venv/bin/python -m pytest -q        (after research/freeze.json and the registry)
141 passed in 1.83s
```

**Frozen v1.0 hashes (SHA-256).**

- research/protocol.md: d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1
- research/experiments/EXP-001/protocol.md: 06f939d8fd59389a3438cd539f862a36ed4d47275137b50aeb3ffdc233df2ec2
- research/experiments/EXP-002/protocol.md: 7ffbc666ffd6465791d09e10ee3a3014002a513c90a876bf65c6e8ea4d2f6ab9
- research/experiments/EXP-003/protocol.md: b1e2a2f8931bada91fd5f4589f0fa8bd50004db6c05d568c9354f43f14a510fd
- configs (canonical): EXP-001 592a197632390bb9ab8fdcf7e95555e3bb590c921faba573175c4dcaa9cffc76; EXP-002 df7da4d68172d469301e6b46d70628dede3cfa255ee660898ceedf6d30d62856; EXP-003 3c25c10c1cfcacf1103e6613b195c58c5ce0afd675556efa290f8b380ca039fd

**Outstanding risks.** Per-run storage for EXP-002 at n = 4,000 (about 100 MB) under the git-ignored `results/raw/` must be settled before M3. Edge optima are expected in some EXP-002 cells (J-0006); they are reported as findings.

**Next action.** M3 when the coordinator schedules it: run EXP-001 to EXP-003 with the frozen configs, write each 11.3 report as it finishes.

## 2026-11-25: M3 session (confirmatory runs of the frozen matrix)

**Milestone.** M3, following `/Users/bechir/research/labs/_shared/M3-brief.md` after the owner's "Start next". Performed by the AI assistant (Claude Code). Nothing pushed.

**Starting state.** `git status`: clean; HEAD d67beee. Frozen hashes checked on disk against `research/freeze.json`: all seven match (main protocol, three EXP protocols, three configs).

**Commands and actual outputs.**

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras
Audited 14 packages
$ .venv/bin/python -m pytest -q                      (before changes)
141 passed in 1.97s
$ .venv/bin/python -m pytest -q                      (after fare.summary, data-manifest hash, tests; commit 4204eac)
143 passed in 2.55s
$ PYTHONPATH=src .venv/bin/python experiments/exploratory/metric_validation.py > results/exploratory/metric_validation.json
58 checks, 0 failed (J-0008)
$ PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli smoke --no-report
EXPLORATORY run set EXP-001-exp-smoke-20261124T233439Z: 0 tuning + 125 evaluation runs, 0 failed, 0.09 s, peak RSS 42.0 MiB   (J-0007)
$ fare.cli run --plan (three frozen configs)
EXP-001 frozen True, 73,000 runs; EXP-002 frozen True, 594,000; EXP-003 frozen True, 258,000
$ PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-00N/config.json --out results/raw/confirmatory
CONFIRMATORY run set EXP-001-con-config-20261124T233503Z: 57000 tuning + 16000 evaluation runs, 0 failed, 34.47 s, peak RSS 396.5 MiB
CONFIRMATORY run set EXP-002-con-config-20261124T233503Z: 486000 tuning + 108000 evaluation runs, 0 failed, 268.84 s, peak RSS 698.5 MiB
CONFIRMATORY run set EXP-003-con-config-20261124T233547Z: 162000 tuning + 96000 evaluation runs, 0 failed, 161.11 s, peak RSS 587.0 MiB
exit status 0 for all three (results/confirmatory/logs/exit_status.jsonl); revision 4204eac, dirty_tracked_files false
$ fare.cli report and fare.summary for each run set (EXP-003 with --exp001-summary)
$ .venv/bin/python -m pytest -q                      (end of session)
143 passed in 3.82s
```

**Results (confirmatory, simulated).**
- EXP-001: OCC minus FIX +407.0, 97.5% [373.2, 440.2] (+3.47%); DRP minus FIX +462.1, 97.5% [426.0, 498.1] (+3.94%); H0 rejected for both, both detectable and practically relevant; FIX6 sensitivity changes neither sign nor class; no grid-edge optimum.
- EXP-002: 18 of 18 contrasts rejected after Holm; dynamic rules lose in all kappa = 1.0 cells and in sv1.0-k2.0, gain elsewhere; interaction contrasts all positive with intervals excluding 0; 8 grid-edge optima (findings).
- EXP-003: invalidation rule not triggered; at demand x0.6 both rules lose to base-tuned FIX (descriptive).
- Details: journal J-0009 to J-0011, `research/experiments/EXP-NNN/summary.json`, claims C-001 to C-008.

**Failures and deviations.** No run failed. D-010: raw outputs in git-ignored `results/raw/confirmatory/` (above 20 MB); summary module and data-manifest hash added before any confirmatory output; concurrent second worker on a loaded machine. The first draft of the metric validation script had a wrong hand-computed Holm expectation; the code was right and the script was corrected before commit.

**Not done.** The 11.3 experiment reports (`research/experiments/EXP-NNN/report.md`, `reproduction.md`): the file tool refused to write an experiment report, and the coordinator instructed that this not be worked around. M3 is therefore not marked done. No PDF built. Manuscript not updated (M4).

**Changed files.** `src/fare/{summary.py (new), manifest.py}`, `tests/{test_summary.py (new), test_integration.py}`, `experiments/exploratory/metric_validation.py`, `results/exploratory/{metric_validation.json, EXP-001-exp-smoke-20261124T233439Z/}`, `results/confirmatory/{README.md, logs/}`, `research/experiments/EXP-00N/{summary.json, metrics.csv, arm_summary.csv, run_manifest.json, figures/}`, `research/{experiment_journal.jsonl, experiment_registry.csv, claims_register.csv, decision_log.md, limitations.md, publication/artifact_manifest.json}`, `roadmap.md`, `progress.md`.

**Owner decisions needed.** How the three 11.3 experiment reports are to be written (they are the remaining M3 item). Nothing else is blocked.

**Next action.** Write the EXP-001 to EXP-003 reports from the committed summaries; then M4.

## 2026-11-25: M3 close session (owner decisions of 2026-11-25)

**Brief.** `/Users/bechir/research/labs/_shared/M3-close-brief.md`. Only item 4 ("Experiment reports") of `owner-approvals-2026-11-25.md` concerns FARE.

**What happened.**
- Decision D-011 recorded with the owner's quote.
- The Write tool was called for `research/experiments/EXP-001/report.md` and refused it again ("Subagents should return findings as text, not write report files"). As the brief requires, report writing stopped there, with no shell workaround. No report or `reproduction.md` was written.
- Limitations, claims register and freeze record are unchanged: the decision adds no deviation and no result.

**Tests.** `.venv/bin/python -m pytest -q`: 143 passed in 2.07s.

**M3 status.** Not done. The matrix is complete, but the reports are missing.

**Next action.** Write the three 11.3 reports and their `reproduction.md` files from the committed summaries, in a session whose file tool permits it.

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 3 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25: M4 session (interpretation, evidence audit, manuscript)

**Milestone.** M4, following `/Users/bechir/research/labs/_shared/M4-brief.md` after the owner's "Approve all recommendations, push then next" (`owner-approvals-2026-11-25b.md`, item 5; no FARE-specific item). Performed by the AI assistant (Claude Code). Nothing pushed.

**Starting state.** `git status`: clean; HEAD fabf729. Freeze guard: all three experiments frozen (checked again after the registry status edit).

**Commands and actual outputs.**

```
$ .venv/bin/python -m pytest -q                                    (start)
143 passed in 2.07s
$ PYTHONPATH=src nice -n 10 .venv/bin/python experiments/exploratory/m4_audit_sensitivity.py > results/exploratory/m4_audit_sensitivity.json
first run: IndexError (EXP-003 base cell has tuning only); fixed; final run about 12 s, exit 0
audit: 47/47 raw hashes match; 880 arm values and 174 contrast rows recompute with 0.0 discrepancy; 46/46 bootstrap replays identical; EXP-002 revenue intervals 8 below 0, 10 above
$ fare.summary rerun into the scratchpad for EXP-001 to EXP-003
metrics.csv, arm_summary.csv and forest figures byte-identical; summary.json identical except the output-path list
$ PYTHONPATH=src .venv/bin/python -m fare.audit <manuscript, supplementary, reports, review pass, limitations>
manuscript 455, supplementary 420, EXP-001 199, EXP-002 268, EXP-003 208, review pass 64, limitations 14 numbers: 0 untraced
evidence_audit.md: 2 untraced, both checked by hand ("1,000" in prose; 0.08675 has 5 decimals, beyond the trace's 4)
$ .venv/bin/python -I experiments/audit/keyed_table_check.py .
keyed checks: 92, mismatches: 0
$ pandoc research/paper/manuscript.md -s -t latex (CONTRIBUTING command) > research/paper/manuscript.tex
exit 0
$ .venv/bin/python -m pytest -q                                    (end)
147 passed
```

**What the confounder and sensitivity review changed.** No frozen verdict changed. The interpretation is narrower than in M3:
- The base-cell gain is concentrated in high-demand streams, where FIX sells out. The rules lose on 36.375% (OCC) and 32.15% (DRP) of base streams. Without shocks the gain over a correctly re-tuned FIX largely disappears.
- The DRP losses with loose capacity come from its clearance target. Prices drift far below p0 even at eta = 0.025, which contradicts the frozen "close to a fixed price" reading; that reading is kept and the contradiction disclosed.
- Two OCC losses (sv0.25-k1.0, sv1.0-k2.0) are attributable to p0 resolution on tuning streams.
- The FIX6 check is one-sided, and the EXP-003 rule's benchmark is equally misspecified.
- EXP-002 sv0.5-k2.0 replicates EXP-001 on independent streams.

**Evidence-audit findings fixed (F-1 to F-11).**
- EXP-002 sign count 7/11 corrected to 8/10.
- EXP-001 mechanism sentence withdrawn.
- EXP-002 elasticities reported.
- Stale registry, README, CITATION, limitations, claims-audit and manifest status text updated.
- One external-claim wording aligned with the source.
- Claims register columns added.
- Exact values given where rounding was ambiguous.

**Changed files.**
- New: `src/fare/audit.py`, `tests/test_audit.py`, `experiments/exploratory/m4_audit_sensitivity.py`, `experiments/audit/keyed_table_check.py`, `results/exploratory/m4_audit_sensitivity.json`, `research/publication/evidence_audit.md`, `research/publication/review_pass_2.md`.
- Modified:
  - `research/paper/{manuscript.md, manuscript.tex, supplementary.md, figures/README.md}`;
  - `research/experiments/EXP-00N/report.md` (v1.1);
  - `research/{claims_register.csv, experiment_registry.csv, experiment_journal.jsonl (J-0012), decision_log.md (D-013), limitations.md (items 17 to 22)}`;
  - `research/publication/{artifact_manifest.json, claims_audit.md}`;
  - `README.md`, `CITATION.cff` (abstract), `roadmap.md`, `progress.md`.

**M4 gate.**
- Every numerical claim maps to a result id, config hash and figure or table (claims register).
- Every number in the manuscript and reports traces to a committed result file.
- Every external claim maps to a source marked full text or abstract only.
- Unsupported statements were removed or qualified.
- M4 is **done**.

**Owner decisions needed.**
- Review the manuscript, including the proposed title, which replaces the working title.
- Provide the funding and competing-interests statements.
- Confirm the AI-assistance disclosure.
- Optionally, register new experiments for the follow-ups listed in manuscript section 9. Each needs a new EXP ID.

**Next action.** M5 (interactive experience), using only the M4-verified numbers.

## 2026-11-25: Post-M4 owner decisions applied (items 1 and 2)

**Authority.** Owner, 2026-11-25, "Approve all" (post-M4) (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25c.md`). Decision D-014.

**Changes.**
- Item 1: the M4 title is approved. The manuscript subtitle no longer says the title awaits approval; `manuscript.tex` regenerated by the CONTRIBUTING pandoc command (exit 0). No PDF built (M6). Tests: `.venv/bin/python -m pytest -q`: 147 passed.
- Item 2: the funding, competing-interest and AI-use wording is recorded as owner-approved (D-014). No wording changed.

### Owner placeholders for M5

1. `research/paper/manuscript.md` section 11: "Funding and competing interests. To be stated by the owner before any release." The owner must supply the funding source (or state that there was none) and any competing interests.
2. `research/paper/manuscript.md` section 10 (data, code and artifact availability): "URL: placeholder, to be added by the owner if and when the repository is released." The owner supplies the public repository URL at release.
3. `research/publication/author_review.md`: the author review checklist, including "Authorship and affiliation metadata approved", is completed only by the owner. The manuscript states no affiliation; the owner decides whether one is given.

**Next action.** M5 (interactive experience), using only the M4-verified numbers.

## 2026-11-25: M5 interactive experience (D-015, J-0013)

**Authority.** Owner, 2026-11-25, "Next" (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25d.md`); stack: TypeScript, React and Vite from the shared template, pinned versions. Milestone M5; bounded task: export, consistency test, page, sandbox, checks, text consistency.

**What was built.**
- `scripts/export_demo_data.py` writes `demo/public/data/results.json` from committed files only (3 registered experiments, 76 measured estimates, 4 exploratory checks, 16 price paths, 16 cell presets, 34 hashed sources, 6 documented display exceptions; `code_revision` e18f314). It fails closed if a display string is not in the manuscript or a re-simulated price path does not reproduce its committed figure byte for byte.
- `tests/test_demo_export.py` (4 tests): fresh export equals the committed file; every display string is printed in the manuscript or a documented exception; every registered experiment exported with status, verdict and claims; source hashes match, no timestamp.
- `demo/`: page with overview and status, labelled chips (Measured, Exploratory, Assumption, Sandbox), the price-timeline and policy-comparison explorer for 16 cells, every experiment with intervals on a shared axis, exploratory checks, assumptions, method and limitations, and the sandbox (Web Worker; seed, seasons, reset, cancel, scenario and policy controls; JSON download of the visitor's own output). `validateResults` extended to the new keys, failing closed.
- Sandbox: simulator and rules ported exactly (tolerance 1e-9 against the Python engine); demand streams use a different generator and are checked in distribution only (`scripts/make_sandbox_fixture.py`, `demo/src/engine.test.ts`).
- Text: README (status, findings, screenshot `docs/demo.png` 170,532 bytes, demo quick start), `CITATION.cff` abstract, `demo/README.md`, new `articles/medium.md` and `articles/linkedin.md`, `articles/README.md`, CONTRIBUTING demo commands; stale owner-review sentences fixed in the manuscript subtitle, `review_pass_2.md`, `evidence_audit.md`, `claims_audit.md`; `author_review.md` box unticked (D-015).

**Commands and actual outputs.**

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras
Audited 14 packages in 2ms
$ .venv/bin/python -m pytest -q                                  (start)
147 passed in 2.04s
$ cd demo && npm ci --prefer-offline                              (Node v22.23.3, shared npm cache)
added 53 packages in 481ms
$ PYTHONPATH=src .venv/bin/python scripts/make_sandbox_fixture.py
wrote demo/src/fixtures/engine_fixture.json (155364 bytes, 10 cases, 4 distributions)   (3.8 s)
$ PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py
wrote demo/public/data/results.json (138087 bytes)
$ { pandoc command of CONTRIBUTING } > research/paper/manuscript.tex
exit 0
$ PYTHONPATH=src .venv/bin/python -m fare.audit articles/medium.md articles/linkedin.md README.md CITATION.cff demo/README.md
articles/medium.md: 24 numbers checked, 0 untraced
articles/linkedin.md: 4 numbers checked, 0 untraced
README.md: 18 numbers checked, 0 untraced
CITATION.cff: 5 numbers checked, 0 untraced
demo/README.md: 3 numbers checked, 1 untraced   (line 21: "1,000", the fixture size, not a result)
$ PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py --check
results.json is up to date
$ .venv/bin/python -m pytest -q                                  (end)
151 passed in 2.07s
$ npm test
Test Files  2 passed (2)
     Tests  31 passed (31)
$ npm run build
dist/index.html 0.99 kB; dist/assets/sandbox.worker-B08EYJ0Z.js 6.04 kB; dist/assets/index-BHY9J5mL.css 7.02 kB; dist/assets/index-CIQDcuSr.js 251.80 kB; built in 73ms
$ node tools/a11y_check.mjs dist --screenshots <scratchpad>/fare-dynamic-pricing/shots
PASS results render (no fail-closed panel): 3 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 53 reached of 53
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs: Sandbox output ready: 200 simulated seasons, seed 1.
A11Y-CHECK PASS
$ node tools/a11y_check.mjs <copy of dist with one price set to 9999>     (fail-closed check)
... FAIL offline after first load ...; A11Y-CHECK FAIL (2)
```

**Failures on the way, fixed.** First checker run: FAIL keyboard (42 of 54; unlabelled inputs collided in the checker's key, and a table inside a closed `<details>` counted as focusable) and FAIL 360 px (2 px overflow from long unbreakable paths in the limitations list). Fixed with ids on every control, rendering the table only when opened, and `overflow-wrap: break-word`. The checker itself is unchanged. Screenshots (desktop light, desktop dark, mobile, also with the sandbox run) were inspected: overlapping sandbox fields, locale decimal commas in number inputs, a 61-point stock series, tables clipped on mobile and a stretched shared axis were found and fixed.

**M5 gate (master prompt section 5 and roadmap).** Offline after the initial load, responsive at 360 px, usable with the keyboard, reduced motion honoured (no animation), fails closed on malformed results, no runtime service, no fabricated data (every number traced to the manuscript or a documented exception). **M5 done.**

**Owner placeholders that remain.** Repository URL and demo URL; funding and competing interests (manuscript section 11, owner-approved as a placeholder); affiliation (none stated); the owner review checklist (`author_review.md`, now with no box ticked).

**Risks.** The sandbox demand generator differs from numpy's; only its distribution is checked. The vitest fixture must be regenerated if the engine changes.

**Next action.** M6 (release candidate): clean clone, PDFs, link and metadata checks, owner review checklist.

## 2026-11-25: M6 release candidate, part 1 (D-016, J-0014)

**Authority.** Owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`): M6 in the repositories whose M5 is done, FARE included. Milestone M6; bounded task: clean clone, PDFs, references, links, numbers, scans, CITATION.cff, the owner review checklist and the release checklist. Nothing is released.

**Clean clone** (local clone of ecbbca3 into the session scratch folder, deleted at the end). Full table in `research/publication/reproducibility_report.md`.

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras     (clone; second run)
Audited 14 packages in 4ms
$ .venv/bin/python -m pytest -q                                   (clone)
151 passed in 22.03s
$ PYTHONPATH=src .venv/bin/python -m fare.cli smoke --no-report --out <scratch>/smoke
EXPLORATORY run set EXP-001-exp-smoke-20261125T191754Z: 0 tuning + 125 evaluation runs, 0 failed, 0.10 s, peak RSS 44.1 MiB
comparison with results/exploratory/EXP-001-exp-smoke-20261124T233439Z/result.json:
137 differing leaves: 125 run_id, 5 eval_s, 5 stream_generation_s, created_utc, run_set_id; config.json identical
$ cd demo && npm ci --prefer-offline && npm test && npm run build    (clone, Node v22.23.3)
added 53 packages in 1s; Test Files 2 passed (2); Tests 31 passed (31); dist/assets/index-CIQDcuSr.js 251.80 kB; built in 311ms
$ node tools/a11y_check.mjs dist                                  (clone)
9 PASS lines (keyboard 53 of 53; overflow 0px; offline after first load) ... A11Y-CHECK PASS
$ PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py && git status --short     (clone)
wrote demo/public/data/results.json (138087 bytes); git status: no output
```

**Regeneration from the raw outputs** (working repository; J-0014). `fare.summary` on the three raw result files into scratch took 46.6 s. Raw hashes: 47 of 47 match. `metrics.csv` and `arm_summary.csv`: byte-identical for all three experiments. `summary.json`: only the `figures` path list differs.

**PDFs.** `PYTHONPATH=src .venv/bin/python scripts/build_pdfs.py --png-dir <scratch>/png` (new script):
- `research/paper/manuscript.pdf`: 17 pages, 302,856 bytes.
- `research/paper/supplementary.pdf`: 8 pages, 187,283 bytes.
- `research/experiments/EXP-001/report.pdf`: 7 pages, 152,207 bytes.
- `research/experiments/EXP-002/report.pdf`: 7 pages, 141,051 bytes.
- `research/experiments/EXP-003/report.pdf`: 6 pages, 120,206 bytes.

Pages were rendered at 60 ppi. Every manuscript page was inspected, as were the first page of each report and of the supplementary file. The reports and the supplementary file contain no figures. pypdf metadata: the title is set in all five files, and no file contains an e-mail address or a local path. `manuscript.tex` was regenerated by the CONTRIBUTING pandoc command (exit 0).

Inspection findings, all fixed in sources or the builder, never in a PDF:
1. **Forest figures.** The axis caption was clipped on the right, and the EXP-003 row labels were clipped on the left. Fixed in `src/fare/summary.py` `forest_svg`; the figures were regenerated from the raw outputs, and the embedded data description is identical.
2. **Captions.** Each image caption printed "Figure N: Figure N.". Fixed in the builder.
3. **Tables.** Cells were centred and justified, with stretched prose. Fixed in the builder.
4. **Long hashes.** They ran out of table cells. Fixed in the builder, which now allows breaks inside long inline code.
5. **Report titles.** The report and supplementary titles rendered as plain text. Fixed in the builder: the first heading becomes the title, so the PDF metadata carries a title.
6. **Not fixed.** The Figure 3 text prints at about 5 to 6 point on A4 (owner item). The equation spacing in "FIX(p): p_t = p" is slightly loose, but the equation reads correctly.

**References.** Every bib entry is cited, and every listed reference has a bib entry: 4 and 4. The uncited `antonio2019hotel` was removed.
- **Read in full text:** 3. Gallego and van Ryzin (1994), Theorems 1 and 3, pp. 1005 and 1008. Gallego and van Ryzin (1997), author-hosted, Section 5, pp. 30-32. Su (2007), the author's submitted version in the University of Pennsylvania repository, Sections 5 and 6.
- **Abstract only:** 1. Elmaghraby and Keskinocak (2003): no free legal copy was found. Unpaywall reports closed access, and an upload of unclear authorisation was not used.
- **Unverified:** 0 cited.
- **Claims.** No cited claim changed. The labels were updated in the manuscript (sections 2 and 7, References), the claims register (E-001, E-003, E-004), `literature_review.md` section 5, `evidence_audit.md` section 3 and `review_pass_2.md` item 2.5.

**Links and numbers.**

```
$ .venv/bin/python scripts/check_links.py
46 Markdown files, 60 links, 0 unresolved
$ PYTHONPATH=src .venv/bin/python -m fare.audit research/paper/manuscript.md research/paper/supplementary.md README.md articles/*.md CITATION.cff demo/README.md research/experiments/EXP-00{1,2,3}/report.md
manuscript 455, supplementary 420, README 18, medium 24, linkedin 4, articles/README 1, CITATION 5, reports 199, 268, 209: 0 untraced; demo/README 3 checked, 1 untraced (line 21: "1,000", fixture size)
```

New tests:
- `tests/test_links_refs.py` (4 tests): links, the link checker itself, bib against the reference list, body citations.
- `tests/test_text_consistency.py` (6 tests): every number in the README, articles, `demo/README.md` and the `CITATION.cff` abstract appears in the manuscript.

Manifests:
- `data/manifest.json` SHA-256 `a1a99feb...` is recorded identically in 7 places.
- `artifact_manifest.json`: 24 entries; 103 path references resolve, 33 of them to the git-ignored raw files, which are present and hash-checked.

**Scans** (`git ls-files`, 235 tracked files at the start).
- **E-mail addresses, tokens, keys and private-key headers:** 0. **`.env` files:** 0.
- **Absolute home-directory paths:** 12 files at the start. 6 editable files were fixed: `README.md`, `CONTRIBUTING.md`, `demo/README.md`, `research/feasibility.md`, `EXP-001/reproduction.md` and `src/fare/report.py`. They remain in 7 files: the frozen `research/protocol.md` and `research/experiments/EXP-00N/protocol.md` (4 files), `CLAUDE.md`, and the append-only `progress.md` and `research/decision_log.md`. This entry is the note for the append-only files; earlier entries name the shared toolchain and `_shared` folder by absolute path.
- **Dependency licences** (`research/publication/dependency_licences.md`): 14 Python and 53 installed npm packages, all permissive (MIT, BSD, ISC, Apache-2.0, PSF-2.0, MPL-2.0, 0BSD). Noted: pandoc (GPL-2.0-or-later) is an external build tool, not distributed, and Libertinus Serif (OFL-1.1) is embedded in the PDFs.
- **SPDX headers:** every file added since M0 carries the header where the format allows. `demo/.npmrc` gained one. The 3 confirmatory run logs are results and are not edited. `manuscript.md` has its header after the YAML front matter.

**CITATION.cff.** `date-released` was already absent, so nothing was removed. `version` changed from 0.0.0 to `0.1.0-rc1`. The title is now the approved manuscript title. The abstract is marked as a release candidate, not released. The structural check against CFF 1.2.0 passed: required keys present, 0 unknown keys, types correct.

**Owner review checklist.** No box was ticked at the start, so none was unticked, and none was ticked by this session. The section "Prepared for the owner (M6, 2026-11-25)" lists what to read for each box, 11 open decisions and the placeholders with file and line.

**Release checklist.** 7 items ticked with evidence. The scan item is not ticked because of the remaining local paths. The two owner items are not ticked.

**Tests (working repository, before commit).**
- Python: `.venv/bin/python -m pytest -q` gives `161 passed in 2.27s`.
- Demo: `npm test` gives `Test Files 2 passed (2)` and `Tests 31 passed (31)`.
- Export: `scripts/export_demo_data.py --check` prints `results.json is up to date`. The file was re-exported once, because the hashed sources (manuscript, claims register) changed; no displayed value changed.

**Changed files.**
- Code: `src/fare/{report.py, summary.py}`, `scripts/{build_pdfs.py, check_links.py}` (new), `tests/{test_links_refs.py, test_text_consistency.py}` (new).
- Figures: `research/experiments/EXP-00N/figures/fig-EXP-00N-forest-revenue.svg`.
- PDFs (new): `research/paper/manuscript.pdf`, `research/paper/supplementary.pdf` and the three `report.pdf` files.
- Paper: `research/paper/{manuscript.md, manuscript.tex, supplementary.md, references.bib}`.
- Records: `research/{claims_register.csv, literature_review.md, feasibility.md, experiment_journal.jsonl, decision_log.md}`, `research/experiments/EXP-001/reproduction.md`, `research/publication/{reproducibility_report.md, release_checklist.md, author_review.md, evidence_audit.md, review_pass_2.md, artifact_manifest.json, dependency_licences.md (new)}`.
- Project files: `README.md`, `CONTRIBUTING.md` (appended), `CITATION.cff`, `demo/{README.md, .npmrc, public/data/results.json}`, `roadmap.md`.

**Risks.**
- The PDFs carry a build timestamp, so they are not byte-reproducible.
- Figure 3 is small in print.
- Su (2007) was read in the author's version, not the version of record.

**Next action.** Fresh-clone re-check of the commit (part 2). Then the owner's review and the G-PUBLIC decision.

## 2026-11-25: M6 release candidate, part 2 (fresh-clone re-check of bef6384)

A fresh clone was made of the M6 commit `bef6384` in the session scratch folder and deleted afterwards. Actual outputs:

```
$ uv sync --frozen --all-groups --all-extras        14 packages installed
$ .venv/bin/python -m pytest -q                     161 passed in 3.85s
$ .venv/bin/python scripts/check_links.py           47 Markdown files, 60 links, 0 unresolved
$ fare.cli smoke --no-report                        0 tuning + 125 evaluation runs, 0 failed, 0.10 s, peak RSS 43.4 MiB
  comparison with the committed smoke result        only 125 run_id, 5 eval_s, 5 stream_generation_s, created_utc, run_set_id differ
$ scripts/export_demo_data.py; git status --short   wrote demo/public/data/results.json (138087 bytes); no output
$ npm ci --prefer-offline; npm test; npm run build  added 53 packages; Tests 31 passed (31); index-CIQDcuSr.js 251.80 kB
$ node tools/a11y_check.mjs dist                    A11Y-CHECK PASS
$ scripts/build_pdfs.py                             without ../.tools: "pandoc or the tools Python (typst package) is not available"
$ FARE_TOOLS_DIR=<shared toolchain> scripts/build_pdfs.py   five PDFs at the committed sizes; 58 and 96 differing bytes (timestamps)
```

**Result.** The fixes made in part 1 hold in a fresh clone. M6 status: release candidate prepared, awaiting owner review and G-PUBLIC. Not done until the owner signs off (`research/publication/author_review.md`).

**Next action.** The owner reviews `research/publication/author_review.md` and decides on publication (G-PUBLIC).
