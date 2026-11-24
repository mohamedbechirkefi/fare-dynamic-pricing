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
