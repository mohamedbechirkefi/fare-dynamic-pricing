<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# FARE: how every session works in this repository

FARE studies how demand and inventory policies affect prices and availability in a simulated market of perishable capacity. `master_prompt.md` is the authority for this project. It is saved unchanged and must never be edited. If this file and `master_prompt.md` disagree, `master_prompt.md` wins; record the conflict in `progress.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md`
2. `roadmap.md`
3. `progress.md`
4. `research/protocol.md`
5. `research/claims_register.csv`

Then inspect `git status` and the existing files. Never overwrite changes made by the owner. State the current milestone and the next bounded task before starting work.

## 2. Mandatory requirements (master prompt section 11, made binding by 11.6)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex generated, references.bib, figures/, supplementary.md, manuscript.pdf generated locally only after validation), `research/experiments/EXP-NNN/` (protocol.md, report.md, report.pdf, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** Experiment IDs (EXP-NNN), run IDs, figure IDs and claim IDs never change once assigned. A seed is a run inside an experiment, not a new experiment. A new question or a materially different protocol gets a new EXP ID.
- **Before each experiment (11.2).** Write `research/experiments/EXP-NNN/protocol.md` with every item listed in 11.2, including what result would contradict the hypothesis. The owner freezes the confirmatory protocol (version and hash) before held-out results are evaluated. Post-hoc changes are exploratory, dated and justified.
- **Every registered experiment gets a standalone report (11.3)** with the twelve mandatory sections, including failed, null, abandoned and exploratory experiments, each visibly labelled.
- **One integrated manuscript (11.4)**, built from the experiment reports, 3,000 to 6,000 words where the evidence justifies it, preprint-draft status, owner-approved authorship only, accurate AI-assistance disclosure.
- **Evidence-to-publication pipeline (11.5).** Tables and figures are generated once from versioned results and reused everywhere. A manifest maps every number, figure and claim to experiment ID, run IDs, metric definition, result path, generator script, config or protocol hash and code revision. A second review pass challenges the preferred hypothesis.
- **Milestone additions (11.6).** M0/M1: registry, manuscript skeleton, experiment protocols, zero-cost toolchain confirmed, protocols frozen by the owner before execution. M2: versioned output schemas, reproducibility manifests and report generators built alongside the core. M3: reports written as experiments finish; failures and deviations recorded at once. M4: reports and evidence audit finished; manuscript synthesised, contradictions and sensitivity included. M5: demo, paper, reports and articles use identical verified results, labels and scope. M6: compile and inspect PDFs; verify references, links, equations, figures and metadata; reproduce smoke results in a clean clone; complete the owner review checklist.
- **Publication gate.** Satisfied only when every registered experiment has a truthful report, the manuscript is complete, every artifact is traceable and remaining blockers are disclosed.

## 3. Rules for all sessions

- **Gates.**
  - Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC).
  - No paid service of any kind. The coding subscription is never an inference backend.
  - Never freeze a protocol: freezing belongs to the owner (G-FREEZE). Until the owner freezes a protocol, every run is exploratory and labelled as such.
  - A tiny exploratory smoke check of the toolchain is allowed; label it exploratory.
- **Scope.**
  - Work only inside this repository, except read-only use of the shared tools in `../.tools/` (the shared labs toolchain) and Node in `../../helix/.tools/node/bin` (the research root's Helix toolchain; never modify that folder).
  - Do not touch any other folder under the research root (the folder that contains `labs/`).
  - Never kill processes you did not start. Never delete anything you did not create in the current session.
- **Truthfulness.**
  - Never fabricate results, citations, test counts or PDFs.
  - Record the commands you run and their actual outputs in `progress.md`.
  - A source you could not open is labelled unverified and is not cited as read.
- **Files and style.**
  - New text and code files start with `SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0` as a comment where the format allows. JSON and CSV are covered by `NOTICE.md`.
  - English. No em dashes. Plain, formal register.
  - No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
  - Refer to the owner as "the owner" (they/them).
- **Licence.** The licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`) are the owner's decision (decision D-001). Do not change them. Development commands may be appended to `CONTRIBUTING.md`.
- **Claims boundary (master prompt section 10).** No airline personalisation claims, no live scraping, no actual fare predictions. All results are simulated and labelled as such.
- **Commits.** Local only, as `git -c user.name=mohamedbechirkefi -c user.email=<owner address> commit`, message ending with a blank line and the `Co-Authored-By` trailer. Run `git status` before and after.

## 4. Toolchain (decision D-003)

- Python 3.12.1 (`/usr/local/bin/python3`), environment and lockfile via `../.tools/py/bin/uv`.
- Documents: Markdown is canonical. PDFs are produced by pandoc (`../.tools/pandoc`) to Typst, compiled with the `typst` Python package in `../.tools/py/`. `manuscript.tex` is generated from Markdown by pandoc. There is no TeX distribution on this machine.
- Commands are listed in `CONTRIBUTING.md` (section "Development commands").

## 5. Session end

Update `progress.md` (dated entry: decisions, commands, actual outputs, failures, changed files, risks, next action) and `roadmap.md` (status and blockers). Never mark incomplete work done.
