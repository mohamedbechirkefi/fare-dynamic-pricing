<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Feasibility audit (M0, 2026-11-24)

All values below were confirmed by commands run in this session; the outputs are recorded verbatim in `progress.md` (entry 2026-11-24).

## 1. Hardware

| Item | Confirmed value | Command |
|---|---|---|
| CPU | Apple M1 Pro | `sysctl -n machdep.cpu.brand_string` |
| Cores | 10 | `sysctl -n hw.ncpu` |
| RAM | 17179869184 bytes (16 GiB) | `sysctl -n hw.memsize` |
| OS | macOS 15.3.1 (build 24D70) | `sw_vers` |
| Free disk | 127 GiB available of 460 GiB on the data volume | `df -h` |

## 2. Tools

| Tool | Confirmed version | Location | Use |
|---|---|---|---|
| Python | 3.12.1 | `/usr/local/bin/python3` | runtime for the core and experiments |
| uv | 0.9.5 | `../.tools/py/bin/uv` | lockfile and environment |
| typst (Python package) | 0.15.0 | `../.tools/py/` | PDF compilation |
| pypdf | 6.20.0 | same | PDF inspection |
| pillow | 11.3.0 | same | figure checks |
| pandoc | 3.6.3 | `../.tools/pandoc` | Markdown to Typst and LaTeX |
| Node | v22.23.3 | a shared read-only Node folder outside the repository | static demo build (M5) |
| git | 2.42.1 | system | version control |
| TeX (tex, pdflatex, xelatex, tectonic) | not found | n/a | not available |

Note: the brief locates a `typst` executable in `.tools/py/bin/`; there is none. Typst is available only as the Python package (`import typst`), which is what the toolchain uses.

## 3. Zero-cost publication toolchain (decision D-003)

There is no TeX distribution. PDFs are produced as: Markdown (canonical) -> `pandoc -t typst` -> `typst.compile()` from the Python package. `research/paper/manuscript.tex` is generated from `manuscript.md` with `pandoc -s -t latex` and kept as a source artifact; it is not compiled locally. An exploratory toolchain check in this session compiled the manuscript skeleton to a PDF in a scratch location (not committed; see `progress.md`). No paid typesetting or service is involved.

## 4. Time budget

Five focused development days (planning estimate): day 1 M0 and M1 drafts; day 2 M2 core, tests, schemas; day 3 M3 runs and per-experiment reports; day 4 M4 interpretation and manuscript; day 5 M5 demo and M6 release checks. If the target is threatened, the order of cuts is: optional EXP-003 cells beyond the two moderate shifts, then demo polish, never controls, reports or truthfulness.

## 5. Compute budget

The simulation is a small discrete-time model (60 periods, a few hundred buyers per stream). The full planned matrix is about 0.2 million policy runs. Estimated well under one CPU-hour on this laptop (estimate, to be replaced by the measured smoke runtime). No GPU, cloud or paid compute is needed.

## 6. Data

The primary study uses synthetic data only (generator, parameters and seeds recorded per run). No dataset is needed or downloaded. Candidate public datasets and their licence status are recorded in `data/manifest.json` and `research/literature_review.md`; none is used in the draft protocol.

## 7. Risks

- R1: The tuned fixed price may already be near optimal (as theory suggests), producing small or null effects. Mitigation: the protocol defines a SESOI and an equivalence criterion so a null result is still informative.
- R2: Parameter choices are arbitrary and may drive results. Mitigation: EXP-002 grid and EXP-003 misspecification analysis; the claims boundary restricts statements to the model.
- R3: Unequal tuning resolution across families (36 FIX prices versus 9 starting prices). Mitigation: tuning-grid sensitivity inside EXP-001.
- R4: Myopic buyers omit strategic waiting. Mitigation: stated as a limitation; no extrapolation.
- R5: No TeX; LaTeX output is generated but not compiled. Mitigation: Typst PDF path; recorded in limitations.
- R6: Node lives in another project's folder and is used read-only; if it changes, the demo build may break. Mitigation: record the Node version in each demo build manifest.
