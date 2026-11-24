<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE roadmap

Updated 2026-11-24 (M2 session). Effort is a planning estimate in focused days (five-day target). Section 11.6 additions of the master prompt are included and mandatory.

| ID | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 d | done pending owner review (see acceptance) | none |
| M1 | Research and preregistration | M0 | P0 | 0.5 d | in progress: drafts written; freeze pending | owner freeze (G-FREEZE) of research/protocol.md and EXP-001..003 |
| M2 | Core implementation | M1 drafts (implementation may start before the freeze) | P0 | 1 d | implemented; acceptance met for the draft protocol (133 tests pass); exploratory smoke and pilot run | owner decisions D-007 may require config and grid changes before M3 |
| M3 | Experiments | M2 gate; M1 freeze for confirmatory runs | P0 | 0.75 d | not started (exploratory pilot only) | owner freeze; D-007 decisions |
| M4 | Interpretation | M3 | P0 | 1 d | not started | M3 |
| M5 | Interactive experience | M2 schemas; M4 verified results for published numbers | P1 (cut first if time is short) | 0.75 d | not started | M4 |
| M6 | Release candidate | M4, M5 | P0 | 0.5 d | not started | owner approval for any publication (G-PUBLIC) |

## M0: Bootstrap and feasibility

- Deliverables: control files (section 2), feasibility audit (`research/feasibility.md`), source audit (`research/literature_review.md`, `data/manifest.json`), budget (zero cost), explicit scope and fallback, publication tree skeleton (11.1), zero-cost toolchain confirmed (11.6), lockfile.
- Acceptance: the owner can understand the question, cost and exclusions from README.md and `research/protocol.md`; every tool version confirmed by command; no unverified source cited as read.
- Status: all deliverables created on 2026-11-24; owner review outstanding.

## M1: Research and preregistration

- Deliverables: evidence review, formal model, baselines, study protocol and per-experiment protocols (11.2), experiment registry with planned entries, manuscript skeleton, fixture manifest.
- 11.6 additions: initialise registry, manuscript skeleton and experiment-specific protocols (done as drafts); confirm the zero-cost toolchain (done, exploratory check); **the owner freezes confirmatory protocols before execution**.
- Acceptance: protocols frozen by the owner with SHA-256 recorded in the registry and decision log; exploratory results (if any) visibly separated; fixture manifest lists the synthetic fixtures.
- Open items: optional pilot on tuning streams to estimate the paired-difference SD; owner decisions listed in `progress.md`.

## M2: Core implementation

- Deliverables: demand-stream generator, simulator, FIX baseline first, then OCC and DRP; metrics; runner with CLI (`smoke`, `run`, `report`, `test`); run manifests (runtime, peak memory, OS, CPU, package versions, git revision, config).
- 11.6 additions: versioned JSON output schemas, reproducibility manifests and report generators built alongside the core.
- Acceptance: unit, invariant and property tests pass and their actual counts are recorded: stock conservation, price bounds, no-demand state, sold-out state, policy nesting (k = 0, eta = 0 equal FIX exactly), hand-computed examples, golden fixtures, config-to-results integration test, extreme parameters. Correctness before any UI work.
- Status (2026-11-24, M2 session):
  - Done:
    - core package `src/fare`, with the FIX baseline first, then OCC and DRP;
    - result schema 1.0.0, validated at export and import;
    - run manifests;
    - CLI with `smoke`, `run` (refuses confirmatory configs while the protocol is unfrozen), `report` and `test`;
    - report generator (Markdown, CSV, SVG, pandoc to Typst PDF).
  - Tests: 133 passed, 0 failed. Every acceptance item above has a test, including Hypothesis property tests and a differential test against a naive reference simulator.
  - Exploratory smoke and pilots on tuning streams only: J-0002 to J-0005 and `results/exploratory/`.
  - Open:
    - the EXP-002 interaction-contrast interval (D-007, item 7);
    - the owner's decisions on the D-007 amendments (n, tuning streams, grids), which change the planned configs before M3.

## M3: Experiments

- Deliverables: smoke run, metric validation, frozen matrix EXP-001 to EXP-003, raw machine-readable results, figures with uncertainty.
- 11.6 additions: generate each individual report (11.3) as its experiment finishes; record unsuccessful runs and deviations at once; capture provenance during execution.
- Acceptance: complete planned matrix or documented failure; no silently dropped runs; each report has the twelve sections.

## M4: Interpretation

- Deliverables: confounder inspection, sensitivity analyses (tuning grid, EXP-002, EXP-003), expected versus observed, claims register, limitations.
- 11.6 additions: finish experiment reports and evidence audit; synthesise the manuscript; include contradictory results and sensitivity; second review pass challenging the preferred hypothesis.
- Acceptance: each numerical claim maps to result ID, config and figure; each external claim maps to an opened source; unsupported claims removed or qualified.

## M5: Interactive experience

- Deliverables: static booking-market simulator with price timeline and policy comparisons, published results separated from visitor sandbox runs, methodology and limitations panels.
- 11.6 additions: demo, paper, reports and articles use identical verified results, labels and scope.
- Acceptance: offline after initial load, responsive, keyboard usable, reduced-motion option, fails closed on malformed results, no runtime service, no fabricated data.

## M6: Release candidate

- Deliverables: clean clone in a separate directory, locked install, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan, README, report.md, articles drafts.
- 11.6 additions: compile and visually inspect manuscript and report PDFs (Typst path); verify references, cross-links, equations, figure readability and metadata; complete the owner review checklist.
- Acceptance: actual command outputs recorded in `research/publication/reproducibility_report.md`; owner approves any publication; nothing pushed without approval.

## Optional (only if the budget allows, owner decision)

- Scale sensitivity (C in {10, 30, 100, 300, 1000} with proportional demand) to relate results to the asymptotic optimality of fixed prices (Gallego and van Ryzin, 1994). Would need its own EXP ID and protocol.
- Known-model dynamic-programming reference arm (upper reference, not a primary contrast).
