<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Decision log (append-only)

Each entry: ID, date, decision, decided by, context, alternatives, consequences.

## D-001 (2026-11-24): Licence is the owner's protective source-available licence

- **Decided by:** the owner.
- **Decision:** All original material is licensed under the FARE Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-FARE-NC-Research-1.0`), with a Contributor License Agreement, from the first commit.
- **Context:** The master prompt (section 2) asks for an "owner-approved permissive code license". On 2026-11-24 the owner instead chose this protective licence for their own protection. The licence package (LICENSE, NOTICE.md, LICENSE_HISTORY.md, CLA.md, CONTRIBUTING.md, .github/CODEOWNERS, .github/workflows/cla.yml) was committed before this session.
- **Alternatives:** a permissive licence such as MIT or Apache-2.0, as the prompt suggests.
- **Consequences:** The repository is source-available, not OSI open source. Sessions do not modify the licence files. Third-party data and dependencies keep their own licences (`data/manifest.json`, `uv.lock`).

## D-002 (2026-11-24): Synthetic-only data for the primary study

- **Decided by:** AI assistant, proposed; pending owner confirmation.
- **Decision:** The draft protocol uses only synthetic demand streams. No dataset is downloaded.
- **Context:** The question concerns a simulated market; the claims boundary forbids scraping and actual fare predictions; the one candidate public dataset found (hotel booking demand) has an unconfirmed data licence.
- **Alternatives:** calibrate parameters to the hotel booking data.
- **Consequences:** Results hold only within the model's assumptions; parameter plausibility is argued, not calibrated.

## D-003 (2026-11-24): Zero-cost publication toolchain without TeX

- **Decided by:** AI assistant under the M0 brief; recorded for owner review.
- **Decision:** Markdown is canonical. PDFs are built with pandoc 3.6.3 to Typst and compiled with the `typst` Python package 0.15.0. `manuscript.tex` is generated from Markdown with pandoc and not compiled locally.
- **Context:** No TeX distribution is installed (tex, pdflatex, xelatex, tectonic not found). Installing one is unnecessary; paid tools are prohibited.
- **Consequences:** LaTeX output is unverified by compilation; this is listed in `research/limitations.md`.

## D-004 (2026-11-24): Dependency resolution capped at 2026-11-10

- **Decided by:** AI assistant under the M0 brief.
- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` so that every locked version was released at least two weeks before 2026-11-24. Runtime dependencies: numpy, jsonschema; development: pytest, hypothesis.
- **Consequences:** Upgrades require changing the cap and recording a new decision.

## D-005 (2026-11-24): Draft protocol design choices (pending owner freeze)

- **Decided by:** AI assistant, proposed; the owner decides at the freeze (G-FREEZE).
- **Decision:** Primary metric revenue per selling season; baseline the tuned fixed price; nondirectional H1; Bonferroni over two primary contrasts; SESOI 1% of baseline revenue; 300 evaluation streams per cell; equal 36-configuration tuning budget per policy family; three registered experiments (EXP-001 base comparison, EXP-002 elasticity and capacity grid, EXP-003 misspecification robustness).
- **Rationale:** See `research/protocol.md` sections 2, 5 and 7.
- **Consequences:** None of these is binding until the owner freezes the protocol.

## D-006 (2026-11-24): M2 implementation choices where the draft protocol is silent

- **Decided by:** AI assistant during M2; recorded for owner review. Each item can be changed before the freeze.
- **Decisions:**
  1. Project entropy for `SeedSequence` is 20261124 (`src/fare/streams.py`, `PROJECT_ENTROPY`). The protocol says only "fixed project entropy".
  2. Segment arrival profiles are linear: a_L(t) proportional to T + 1 - t, a_H(t) proportional to t. The protocol says only "L decreasing, H increasing". The EXP-003 reversed cell swaps them.
  3. Within a period, the arrival order of L and H buyers is a uniform random permutation. Overlapping surges do not compound.
  4. DRP follows the protocol text literally: after period t, r*_t = x_t / (T - t + 1) with x_t the stock at the start of period t. A reading with the post-period stock, x_{t+1} / (T - t), is also plausible (see D-007, item 4).
  5. The production simulator uses bisection on per-period sorted valuations and scans arrival order only in the period where the last unit sells. A naive buyer-by-buyer simulator is kept as the differential-test oracle; Hypothesis checks their agreement.
  6. Figures are plain SVG written by the report generator, so no plotting dependency is added (D-004 unchanged). PDFs use the M0 pandoc to Typst path with `mainfont="Libertinus Serif"`.
  7. The package lives in `src/fare` and is imported with `PYTHONPATH=src`; `[tool.uv] package = false` is kept, so the lock has no build backend. The project version is 0.2.0 (lock updated offline; no dependency changed).
  8. The EXP-003 config re-derives the base tuning from the EXP-001 tuning-stream keys instead of reading an EXP-001 result file. The result is identical by construction, but it adds 10,800 runs (39,600 rather than 28,800).
  9. An exploratory config may not use evaluation streams (role 1). The runner refuses it, so held-out streams stay unseen until the freeze.
- **Consequences:** The choices are visible in code, tests and this log. If the owner prefers another option, it changes before the freeze, and every exploratory output is regenerated.

## D-007 (2026-11-24): Proposed protocol amendments from the exploratory pilot (owner decision, G-FREEZE)

- **Decided by:** not decided. The AI assistant proposes; the owner decides at the freeze. The draft protocols were not edited.
- **Evidence:** journal entries J-0002 to J-0005 and `results/exploratory/pilot_summary.json`. Exploratory, tuning streams only, not evidence about the hypotheses.
- **Proposals:**
  1. **Sample size.** The pilot SD of the paired revenue differences implies that n = 300 is too small for the 1% SESOI. At the base cell, the normal-approximation n at two-sided alpha 0.025 and power 0.89 is 384 (OCC) and 680 (DRP). Across the EXP-002 and EXP-003 cells it reaches 2,735 and 3,435. Compute is not a constraint. The full draft matrix (157,800 runs) is projected at 9 to 13 s in the committed summary, and at up to 41 s in a repeat made while the shared machine was loaded. The proposal is n = 4,000 evaluation streams per cell. Storage then needs a decision: the EXP-002 result file would grow from about 1.4 MB per 50 streams to roughly 100 MB, so per-run records would go to the git-ignored `results/raw/`, with a compact committed summary. An alternative is to keep n = 300 and raise the SESOI to about 3% to 4%, stating this as a power limit.
  2. **Tuning streams.** Raise the number of tuning streams from 100 to 500. Selection noise with 36 configurations then falls, and the extra cost is a few minutes at most.
  3. **Tuning grids.** The tuned DRP sensitivity is at the lowest grid value (eta = 0.1) in every pilot cell. The tuned OCC k is at a grid edge (0.5 or 4) in every pilot cell. The comparison is therefore limited by the grids, which is anticipated failure mode 17 of EXP-001. The proposal keeps the 36-configuration budget with 6 p0 values times 6 sensitivity values: OCC k in {0.25, 0.5, 1, 2, 4, 8} and DRP eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1}. FIX keeps 36 prices. The tuning-grid sensitivity arm then uses the 6 shared p0 values.
  4. **DRP target rate.** Confirm which stock enters r*_t (D-006, item 4).
  5. **Pin the D-006 choices in the protocol text:** entropy, arrival-profile shape, within-period order and the EXP-003 run count.
  6. **Commands.** Protocol section 19 names `fare.cli smoke --exp EXP-001`. The implemented commands are `smoke` (no `--exp`), `run --config` and `report --result`, with `PYTHONPATH=src`.
  7. **EXP-002 interaction contrasts.** Cells use different streams, so the difference of differences is an independent-samples contrast. The protocol should name its interval method; the proposal is an independent stratified bootstrap. It is not implemented yet (M3).
- **Consequences:** Accepting any item changes the protocol text and therefore its hash before the freeze. The planned configs in `research/experiments/EXP-00N/config.json` must then be updated to match.

## D-008 (2026-11-24): Owner-approved amendments applied; the tuning-grid item cannot be applied as written; freeze not performed

- **Decided by:** the owner approved the amendments and the freeze on 2026-11-24 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24.md`, quoted answer "yes for all others"; FARE section). The AI assistant applied them and stopped at the item below, as the freeze brief requires.
- **Applied (draft v0.2 of `research/protocol.md` and the three EXP protocols, each with a dated "Amendments before freeze (owner-approved 2026-11-24)" section):**
  1. 4,000 evaluation and 500 tuning streams per cell (protocols and `research/experiments/EXP-00N/config.json`). Planned runs: EXP-001 74,500; EXP-002 594,000; EXP-003 258,000.
  2. No dynamic-programming reference policy; the optional scale experiment is out of scope.
  3. The D-006 choices and the DRP target reading (stock at the start of period t) are pinned in the protocol text.
  4. EXP-002 interaction contrasts: independent stratified percentile bootstrap, implemented in `fare.stats.interaction_bootstrap_ci` and the report.
  5. Reproduction commands name the implemented CLI.
  6. Authorship (C3): "Mohamed Bechir Kefi", no affiliation, in CITATION.cff and the manuscript; the AI assistant is disclosed, not an author.
- **Not applied: "Widen the OCC and DRP tuning grids so the pilot optima are interior."** The D-007 proposal (6 p0 values times OCC k in {0.25, 0.5, 1, 2, 4, 8} and DRP eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1}) was checked by tuning only on the pilot tuning streams 0 to 49 (J-0006). It makes the base-cell optima interior, but 7 of 20 pilot optima stay on an edge, all in EXP-002 cells: OCC k = 8 (sv0.25-k2.0, sv0.5-k4.0), OCC k = 0.25 (sv0.5-k1.0), DRP eta = 0.025 (sv0.25-k1.0, sv0.5-k1.0, sv1.0-k1.0, sv1.0-k2.0). A wider tuning-only probe selected DRP eta = 0, that is DRP reduced to a fixed price, in sv0.5-k1.0 and sv1.0-k1.0, and OCC k = 0.25 (the probe's lowest value) in sv0.5-k1.0. No positive eta grid can make those optima interior, and widening OCC to cover them needs more than 6 sensitivity values, which breaks the 6 x 6 = 36 equal budget. Choosing among these is a design decision, so it is left to the owner. The draft grid stays in the protocol text, and the code supports either grid (`grid.occ_k`, `grid.drp_eta`, `grid.p0_n` config keys; v1.0 candidates `OCC_K_V1`, `DRP_ETA_V1` in `src/fare/tuning.py`).
- **Options for the owner:** (a) adopt the D-007 grid and report the 7 EXP-002 edge optima as a limitation (the DRP lower edges sit at the boundary where DRP nests FIX); (b) widen further with a different budget split (for example 4 p0 x 9 sensitivity values), keeping 36 configurations; (c) add the nesting value (k = 0, eta = 0) as the lower end and define "interior" as away from the upper edge and the non-nesting lower edge.
- **Freeze:** not performed. Freezing would fix a grid the owner asked to change, and a frozen artifact cannot be touched without a new study. The freeze guard is ready: `run` accepts a confirmatory config only if the registry hash, `research/freeze.json` (protocol, main protocol and canonical config hashes) and the files on disk all agree (tested on a temporary fixture).
- **C4 disclosure (for the freeze record):** exploratory values of the primary contrast were seen before the freeze, on tuning streams only (n = 50 per cell, draft grid). Base cell (J-0003, `results/exploratory/EXP-001-exp-pilot-exp001-20261124T161050Z/result.json`): OCC minus FIX +536.4 (97.5% bootstrap [332.8, 741.1]); DRP minus FIX +515.5 ([243.5, 793.6]). Smoke (J-0002, 5 streams): OCC +62.8, DRP +525.8. EXP-002 and EXP-003 pilot cell values are in `results/exploratory/EXP-002-exp-pilot-exp002-20261124T161051Z/result.json` and `results/exploratory/EXP-003-exp-pilot-exp003-20261124T161055Z/result.json` and summarised in `results/exploratory/pilot_summary.json`. The J-0006 grid check computed no contrast.

## D-009 (2026-11-24): Tuning-grid ruling and grid-edge reporting rule applied; protocols frozen as v1.0

- **Decided by:** the owner. Quoted answer "Approve all", 2026-11-24, to the coordinator's recommendations (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-24b.md`, section 2): "Keep the widened grids within the equal tuning budget. Report optima on a grid edge as a finding (a DRP responsiveness of 0 means the dynamic rule reduces to a fixed price). Freeze." This is option (a) of D-008. The AI assistant applied it.
- **Applied (before any confirmatory data; no evaluation stream has been generated):**
  1. Grids: 6 geometric p0 in [40, 400] times OCC k in {0.25, 0.5, 1, 2, 4, 8} and DRP eta in {0.025, 0.05, 0.1, 0.25, 0.5, 1.0}; 36 configurations per family, FIX unchanged at 36 prices, so the tuning budget stays equal. The tuning-grid sensitivity arm becomes FIX6. Planned runs: EXP-001 73,000 (was 74,500), EXP-002 594,000 and EXP-003 258,000 (unchanged), from `fare.cli run --plan`.
  2. Grid-edge reporting rule written into `research/protocol.md` section 4 (and referenced in each EXP protocol): optima on an edge are findings, never exclusions; the grid is not extended after the freeze; a DRP optimum at eta = 0.025 is read as a rule close to eta = 0, which is the fixed price; an upper or price edge means the contrast measures the family as gridded. Implemented in `fare.tuning.edge_labels` and `fare.report.grid_edge_findings` (a "Grid-edge findings" section in every tuned report), with tests.
  3. Freeze: `research/protocol.md`, the three EXP protocols and the three confirmatory configs frozen as v1.0. Freeze record `research/freeze.json` (owner quotes of both rounds, C1 to C4, C4 disclosure from D-008, amendment list A1 to A8, superseded draft v0.2 hashes, git revision 1d0fcfc). Registry rows carry the v1.0 hashes and the status "frozen (owner-approved 2026-11-24), not yet run".
- **Hashes (SHA-256):** research/protocol.md d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1; EXP-001 protocol 06f939d8fd59389a3438cd539f862a36ed4d47275137b50aeb3ffdc233df2ec2; EXP-002 protocol 7ffbc666ffd6465791d09e10ee3a3014002a513c90a876bf65c6e8ea4d2f6ab9; EXP-003 protocol b1e2a2f8931bada91fd5f4589f0fa8bd50004db6c05d568c9354f43f14a510fd. Config canonical hashes are in the freeze record.
- **Superseded:** the draft v0.2 hashes recorded in `progress.md` (freeze session) were never frozen; they are listed in the freeze record as superseded by the v1.0 text.
- **Consequences:** `fare.cli run` now accepts the three frozen configs and refuses any changed config or protocol (tested). No confirmatory run was made; M3 is scheduled by the coordinator. Any later change to a frozen file is a new study or a dated, labelled deviation.

## D-010 (2026-11-25): M3 execution choices and deviations (records and storage only; no analysis change)

- **Decided by:** the AI assistant, under the shared M3 brief scheduled by the coordinator after the owner's "Start next" (2026-11-25). No protocol, config, seed, exclusion rule or analysis rule was changed.
- **Before any confirmatory output (commit 4204eac):**
  1. `fare.summary` added: applies only the frozen decision rules (EXP-001 Bonferroni 97.5% bootstrap and FIX6 sensitivity; EXP-002 sign-flip permutation with Holm over 18 contrasts and the interaction contrasts; EXP-003 invalidation rule on the x0.8 and x1.25 cells), reusing the statistics functions and seeds of `fare.report`; it also writes a SHA-256 manifest of each raw run directory and an interval (forest) figure. Tested (`tests/test_summary.py`).
  2. Run manifests now record the path and SHA-256 of `data/manifest.json` (`data_manifest`), as the M3 brief requires per run set.
- **Deviation 1 (location).** The protocols say `run` writes `results/confirmatory/<run_set_id>/`. The raw outputs total 21.5 MB (EXP-001), 147.8 MB (EXP-002) and 132.2 MB (EXP-003), above the 20 MB commit limit, so they were written with `--out results/raw/confirmatory` (git-ignored, regenerable). Committed instead: `research/experiments/EXP-NNN/{summary.json, metrics.csv, arm_summary.csv, run_manifest.json, figures/}` and `results/confirmatory/logs/` (run logs and exit statuses). Every raw file's SHA-256 is in `summary.json` (`raw_manifest`).
- **Deviation 2 (execution conditions).** EXP-002 ran as a second worker beside EXP-001 and then EXP-003, under `nice -n 10`, on a machine shared with other sessions (load average up to about 50). Wall-clock: EXP-001 34.5 s, EXP-002 268.8 s, EXP-003 161.1 s, all within the frozen caps (15, 40, 15 minutes). Runtime is not a result.
- **Not used as evidence.** The generic `fare.cli report` also prints a Holm table for EXP-001 and EXP-003; Holm across cells is frozen only for EXP-002. Those tables are not part of the frozen analysis and are not reported.
- **Open (owner):** the 11.3 experiment reports (`research/experiments/EXP-NNN/report.md`, `reproduction.md`) were not written in this session: the file tool refused to write an experiment report, and the coordinator instructed that this not be worked around.

## D-011 (2026-11-25): Owner approves writing the missing experiment reports; the file tool still refuses

- **Decided by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25.md`, item 4, "Experiment reports"). The decision reads: "The owner approves writing the missing 11.3/11.6 experiment reports (`report.md`, and `reproduction.md` where the repo uses it). They are written from the committed results, tables and figures only." It adds: "Nothing is recomputed and no numbers change." No other item of that file concerns FARE.
- **Applied:** not yet. In the M3 close session, the Write tool was called for `research/experiments/EXP-001/report.md` with a report drawn only from the committed summaries. The tool refused it again. As the close brief requires, report writing stopped there: no shell or other workaround was used, and no report or `reproduction.md` exists for EXP-001, EXP-002 or EXP-003.
- **Consequences:**
  - M3 stays open. The run matrix is complete (D-010), but the 11.6 report requirement is not met.
  - No result, claim, limitation or freeze-record entry changes, because the decision adds no deviation to the frozen protocol.
  - The reports must be written in a session whose file tool permits it, from `research/experiments/EXP-NNN/{summary.json, metrics.csv, arm_summary.csv}`.
