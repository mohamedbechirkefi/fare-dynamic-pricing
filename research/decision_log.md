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
