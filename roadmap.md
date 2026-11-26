<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE roadmap

Updated 2026-11-25 (M6: release candidate prepared, awaiting owner review and G-PUBLIC; M5 done). Effort is a planning estimate in focused days (five-day target). Section 11.6 additions of the master prompt are included and mandatory.

| ID | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 d | done pending owner review (see acceptance) | none |
| M1 | Research and preregistration | M0 | P0 | 0.5 d | done: protocols frozen v1.0 (owner-approved 2026-11-24, D-009; `research/freeze.json`); **M1 gate passed** | none |
| M2 | Core implementation | M1 drafts (implementation may start before the freeze) | P0 | 1 d | implemented; acceptance met for the draft protocol (133 tests pass); exploratory smoke and pilot run | none (frozen configs in place) |
| M3 | Experiments | M2 gate; M1 freeze for confirmatory runs | P0 | 0.75 d | matrix complete: EXP-001 73,000, EXP-002 594,000, EXP-003 258,000 runs, 0 failed (J-0009 to J-0011); summaries, figures, claims and records done; 11.3 reports written by the coordinator (D-012); **done** | none |
| M4 | Interpretation | M3 | P0 | 1 d | **done** 2026-11-25 (D-013, J-0012): confounder and sensitivity review, expected versus observed, claims register with result ids, evidence audit (11 findings fixed), manuscript and supplementary, second review pass; gate holds | owner review of the manuscript, title, funding and competing-interests statements (not a gate blocker) |
| M5 | Interactive experience | M2 schemas; M4 verified results for published numbers | P1 (cut first if time is short) | 0.75 d | **done** 2026-11-25 (D-015, J-0013): `demo/` built, checker A11Y-CHECK PASS, 151 Python and 31 vitest tests pass; gate holds | owner placeholders filled 2026-11-26 (D-017) |
| M6 | Release candidate | M4, M5 | P0 | 0.5 d | release candidate prepared, awaiting owner review and G-PUBLIC (2026-11-25, D-016, J-0014): clean clone reproduced, 5 PDFs compiled and inspected, links, references, manifests and scans checked, owner checklist prepared; not done until the owner signs off | owner review (`research/publication/author_review.md`); owner approval for the release (B18; the repository is public since 2026-11-25); owner-only facts answered 2026-11-26 (D-017) |

## M0: Bootstrap and feasibility

- Deliverables: control files (section 2), feasibility audit (`research/feasibility.md`), source audit (`research/literature_review.md`, `data/manifest.json`), budget (zero cost), explicit scope and fallback, publication tree skeleton (11.1), zero-cost toolchain confirmed (11.6), lockfile.
- Acceptance: the owner can understand the question, cost and exclusions from README.md and `research/protocol.md`; every tool version confirmed by command; no unverified source cited as read.
- Status: all deliverables created on 2026-11-24; owner review outstanding.

## M1: Research and preregistration

- Deliverables: evidence review, formal model, baselines, study protocol and per-experiment protocols (11.2), experiment registry with planned entries, manuscript skeleton, fixture manifest.
- 11.6 additions: initialise registry, manuscript skeleton and experiment-specific protocols (done as drafts); confirm the zero-cost toolchain (done, exploratory check); **the owner freezes confirmatory protocols before execution**.
- Acceptance: protocols frozen by the owner with SHA-256 recorded in the registry and decision log; exploratory results (if any) visibly separated; fixture manifest lists the synthetic fixtures.
- Open items: optional pilot on tuning streams to estimate the paired-difference SD; owner decisions listed in `progress.md`.
- Status (2026-11-24, freeze session): owner-approved amendments applied (D-008): 500 tuning and 4,000 evaluation streams, scope cut (no DP reference, no scale experiment), D-006 choices and DRP target reading pinned, EXP-002 interaction method named and implemented, commands fixed, authorship set. The grid amendment could not be applied as written (7 of 20 pilot optima stay on an edge with the proposed grid; J-0006), so the protocols were not frozen. The freeze guard (`research/freeze.json` plus registry hashes plus config hashes) is implemented and tested.
- Status (2026-11-24, second round): the owner approved the widened grids within the equal budget and the grid-edge reporting rule ("Approve all"); protocols and configs frozen as v1.0 (D-009), hashes in `research/freeze.json` and the registry. **M1 gate passed.**

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
    - the tuning-grid ruling (D-008), which changes the confirmatory configs before the freeze.
  - Freeze session additions: configurable grids, EXP-002 interaction-contrast bootstrap, freeze record and config-hash freeze guard; 138 tests pass.

## M3: Experiments

- Deliverables: smoke run, metric validation, frozen matrix EXP-001 to EXP-003, raw machine-readable results, figures with uncertainty.
- 11.6 additions: generate each individual report (11.3) as its experiment finishes; record unsuccessful runs and deviations at once; capture provenance during execution.
- Acceptance: complete planned matrix or documented failure; no silently dropped runs; each report has the twelve sections.
- Status (2026-11-25): the planned matrix is complete, no run failed or was dropped, provenance captured at run time (D-010). The three 11.3 reports were written by the coordinator from committed results (D-011, D-012). M3 is done.

## M4: Interpretation

- Deliverables: confounder inspection, sensitivity analyses (tuning grid, EXP-002, EXP-003), expected versus observed, claims register, limitations.
- 11.6 additions: finish experiment reports and evidence audit; synthesise the manuscript; include contradictory results and sensitivity; second review pass challenging the preferred hypothesis.
- Acceptance: each numerical claim maps to result ID, config and figure; each external claim maps to an opened source; unsupported claims removed or qualified.
- Status (2026-11-25): done. Every row of `research/claims_register.csv` carries a result id, config hash, figure or table and manuscript section; every number in the manuscript, supplementary file, reports and review pass traces to a committed result file (`python -m fare.audit`, 0 untraced); external claims map to sources marked full text or abstract only. Exploratory checks are J-0012; records are D-013, `research/publication/evidence_audit.md` and `review_pass_2.md`.

## M5: Interactive experience

- Deliverables: static booking-market simulator with price timeline and policy comparisons, published results separated from visitor sandbox runs, methodology and limitations panels.
- 11.6 additions: demo, paper, reports and articles use identical verified results, labels and scope.
- Acceptance: offline after initial load, responsive, keyboard usable, reduced-motion option, fails closed on malformed results, no runtime service, no fabricated data.
- Status (2026-11-25): done. Owner "Next" (D-015). Static page from the shared template; `scripts/export_demo_data.py` exports committed results only, and `tests/test_demo_export.py` checks that every displayed string is printed in the manuscript (or is a documented exception) and that the committed file equals a fresh export. Price timelines reproduce the committed price figures byte for byte. Sandbox: simulator and rules ported exactly (1e-9 against Python); demand streams use a different generator (checked in distribution). README, CITATION, demo README and article drafts use the manuscript's numbers. Checker output and test counts are in `progress.md`.

## M6: Release candidate

- Deliverables: clean clone in a separate directory, locked install, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan, README, report.md, articles drafts.
- 11.6 additions: compile and visually inspect manuscript and report PDFs (Typst path); verify references, cross-links, equations, figure readability and metadata; complete the owner review checklist.
- Acceptance: actual command outputs recorded in `research/publication/reproducibility_report.md`; owner approves any publication; nothing pushed without approval.
- Status (2026-11-25): release candidate prepared, awaiting owner review and G-PUBLIC (D-016). Clean clone of ecbbca3: 151 tests passed, smoke result identical apart from ids and timings, demo `A11Y-CHECK PASS`, export deterministic. PDFs: manuscript 17 pages, supplementary 8, reports 7, 7 and 6, every manuscript page inspected. Links 0 unresolved; manifests resolve; 0 e-mail addresses, tokens or keys; dependency licences all permissive. Open: the owner review checklist, the publication decision, and absolute local paths left in frozen and append-only files.

## Out of scope (owner decision, 2026-11-24, D-008)

- Scale sensitivity (C in {10, 30, 100, 300, 1000} with proportional demand) to relate results to the asymptotic optimality of fixed prices (Gallego and van Ryzin, 1994). Not run.
- Known-model dynamic-programming reference arm (upper reference, not a primary contrast). Not computed.
