<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Every runtime and build dependency, with its declared licence. Python entries are read from the installed `.venv` metadata (`uv sync --frozen --all-groups --all-extras`, `uv.lock`); npm entries from `demo/node_modules/*/package.json` after `npm ci` (`demo/package-lock.json`). Accepted without a flag: MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0, 0BSD, Zlib, CC0-1.0 and similarly permissive licences. The licence of FARE itself is the owner's decision (D-001) and is not assessed here.

## Flags

No installed Python or npm dependency carries a licence outside the accepted list. Two items of the external toolchain are noted for the owner, neither of which is distributed with the repository:

1. **pandoc 3.6.3** (GPL-2.0-or-later) converts Markdown to Typst and LaTeX. It runs as a separate program on the owner's machine; it is not linked, bundled or redistributed. Its output (the PDFs and `manuscript.tex`) is not covered by the GPL.
2. **Libertinus Serif** (SIL Open Font License 1.1, shipped with the `typst` package) is embedded as a font subset in the committed PDFs. The OFL permits embedding in documents.

MPL-2.0 (hypothesis, lightningcss) is file-level copyleft and applies only to those packages' own files; they are test and build tools and none of their files is shipped in `demo/dist`.

## Python (`.venv`, 14 packages)

| Package | Version | Licence | Use |
|---|---|---|---|
| attrs | 26.1.0 | MIT | runtime |
| hypothesis | 6.170.15 | MPL-2.0 | test (dev group) |
| iniconfig | 2.3.1 | MIT | test (dev group) |
| jsonschema | 4.26.0 | MIT | runtime |
| jsonschema-specifications | 2025.9.1 | MIT | runtime |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | test (dev group) |
| pluggy | 1.7.0 | MIT | test (dev group) |
| Pygments | 2.21.0 | BSD-2-Clause | test (dev group) |
| pytest | 9.2.0 | MIT | test (dev group) |
| referencing | 0.37.0 | MIT | runtime |
| rpds-py | 2026.9.1 | MIT | runtime |
| sortedcontainers | 2.4.0 | Apache-2.0 (License field "Apache 2.0"; classifier Apache Software License) | test (dev group) |
| typing_extensions | 4.16.0 | PSF-2.0 | runtime |

## External build tools (shared toolchain, not in the repository)

| Tool | Version | Licence | Use |
|---|---|---|---|
| typst (Python package) | 0.15.0 | Apache-2.0 | PDF compilation |
| pypdf | 6.20.0 | BSD-3-Clause | PDF metadata check |
| pandoc | 3.6.3 | GPL-2.0-or-later (flag 1) | Markdown to Typst and LaTeX |
| Node.js | v22.23.3 | MIT | demo build and tests |
| uv | 0.9.5 | MIT OR Apache-2.0 | lockfile and environment |

## npm (`demo/`, 53 installed packages)

Runtime packages are bundled into `demo/dist`; dev packages are used only to build and test.

| Package | Version | Licence | Use |
|---|---|---|---|
| @jridgewell/sourcemap-codec | 1.6.0 | MIT | dev |
| @oxc-project/types | 0.156.0 | MIT | dev |
| @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | dev (optional) |
| @rolldown/pluginutils | 1.1.1 | MIT | dev |
| @standard-schema/spec | 1.1.0 | MIT | dev |
| @types/chai | 5.2.3 | MIT | dev |
| @types/deep-eql | 4.0.2 | MIT | dev |
| @types/estree | 1.0.11 | MIT | dev |
| @types/react | 19.3.0 | MIT | dev |
| @types/react-dom | 19.3.0 | MIT | dev |
| @vitejs/plugin-react | 6.1.2 | MIT | dev |
| @vitest/expect | 4.1.12 | MIT | dev |
| @vitest/mocker | 4.1.12 | MIT | dev |
| @vitest/pretty-format | 4.1.12 | MIT | dev |
| @vitest/runner | 4.1.12 | MIT | dev |
| @vitest/snapshot | 4.1.12 | MIT | dev |
| @vitest/spy | 4.1.12 | MIT | dev |
| @vitest/utils | 4.1.12 | MIT | dev |
| assertion-error | 2.0.1 | MIT | dev |
| chai | 6.3.0 | MIT | dev |
| convert-source-map | 2.0.0 | MIT | dev |
| csstype | 3.2.4 | MIT | dev |
| detect-libc | 2.1.2 | Apache-2.0 | dev |
| es-module-lexer | 2.3.2 | MIT | dev |
| estree-walker | 3.0.3 | MIT | dev |
| expect-type | 1.4.0 | Apache-2.0 | dev |
| fdir | 6.5.0 | MIT | dev |
| fsevents | 2.3.3 | MIT | dev (optional) |
| lightningcss | 1.33.0 | MPL-2.0 | dev |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | dev (optional) |
| magic-string | 0.30.21 | MIT | dev |
| nanoid | 3.3.20 | MIT | dev |
| obug | 2.2.1 | MIT | dev |
| pathe | 2.0.3 | MIT | dev |
| picocolors | 1.1.1 | ISC | dev |
| picomatch | 4.0.7 | MIT | dev |
| postcss | 8.5.33 | MIT | dev |
| react | 19.3.1 | MIT | runtime |
| react-dom | 19.3.1 | MIT | runtime |
| rolldown | 1.2.19 | MIT | dev |
| scheduler | 0.28.0 | MIT | runtime |
| siginfo | 2.0.0 | ISC | dev |
| source-map-js | 1.2.4 | BSD-3-Clause | dev |
| stackback | 0.0.2 | MIT | dev |
| std-env | 4.3.0 | MIT | dev |
| tinybench | 2.9.0 | MIT | dev |
| tinyexec | 1.4.0 | MIT | dev |
| tinyglobby | 0.2.17 | MIT | dev |
| tinyrainbow | 3.2.0 | MIT | dev |
| typescript | 5.9.3 | Apache-2.0 | dev |
| vite | 8.3.5 | MIT | dev |
| vitest | 4.1.12 | MIT | dev |
| why-is-node-running | 2.3.0 | MIT | dev |

The lockfile also lists 31 optional platform-specific binaries that are not installed on this machine (rolldown, lightningcss and WebAssembly bindings for other platforms, and tslib); their lockfile licences are MIT, MPL-2.0 or 0BSD.
