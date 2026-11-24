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
