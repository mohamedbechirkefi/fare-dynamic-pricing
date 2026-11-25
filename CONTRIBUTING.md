<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# Contributing to FARE

FARE is an independent, source-available research project maintained by Mohamed Bechir Kefi: dynamic pricing.

Technical suggestions, bug reports, reproducibility results, corrections and Pull Requests are welcome. The project is available for non-commercial research under the FARE Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE)); it is not OSI-approved open-source software.

## 1. Before you start

For major changes, open an Issue first. Read `master_prompt.md`, `research/protocol.md` and `research/claims_register.csv`: frozen protocols are never changed silently, and every reported number must trace to a result file.

## 2. Pull Request requirements

- Your contribution is original or appropriately licensed, and you have the right to submit it.
- No credentials, secrets, confidential information or personal data.
- Relevant tests are included and pass; you report what you actually ran.
- Third-party dependencies and data sources are identified with their licenses.
- New files carry the header `SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0` where the format allows.
- You accept the Contributor License Agreement before your contribution is merged.

## 3. Contributor License Agreement

A recorded acceptance of [CLA.md](CLA.md) is required before merging copyrightable contributions. When you open a Pull Request, the "CLA Assistant" check comments on it; read the CLA, then post this exact comment:

    I have read the FARE CLA v1.0 and I hereby sign it

The check records your public GitHub username and account ID, the date and the PR. You sign once. If the check does not update, comment `recheck`. Checking a box is not a signature; the comment is.

The CLA lets the maintainer use, modify, distribute, relicense and commercially exploit accepted contributions. You keep the copyright in your original contributions.

## 4. Governance

Mohamed Bechir Kefi is the project owner and lead maintainer, and the only person who can change the protected `main` branch. The maintainer decides the research direction, protocol freezes, claims, releases and licensing.

## 5. Privacy and disclosure

Never commit an e-mail address, a name or any other personal identifier in code, logs, fixtures or results. Report security issues privately through GitHub's private vulnerability reporting.

## 6. Development commands

Paths below are those of the owner's machine; adapt them to your installation of uv and pandoc.

```
# environment (locked; resolution capped at 2026-11-10)
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen --python /usr/local/bin/python3

# regenerate the lockfile after a recorded dependency decision
/Users/bechir/research/labs/.tools/py/bin/uv lock --python /usr/local/bin/python3

# manuscript: Markdown -> LaTeX source (not compiled locally; no TeX distribution)
{ echo '% SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0'; echo '% Generated from research/paper/manuscript.md by pandoc 3.6.3; do not edit by hand.'; /Users/bechir/research/labs/.tools/pandoc research/paper/manuscript.md -s -t latex; } > research/paper/manuscript.tex

# manuscript: Markdown -> Typst -> PDF (mainfont must be set: the default template's empty font list fails to compile)
/Users/bechir/research/labs/.tools/pandoc research/paper/manuscript.md -s -t typst -V mainfont="Libertinus Serif" -o research/paper/manuscript.typ
/Users/bechir/research/labs/.tools/py/bin/python -c "import typst; typst.compile('research/paper/manuscript.typ', output='research/paper/manuscript.pdf')"
```

Simulation, test and report commands (M2). The package is imported from `src/` with `PYTHONPATH=src`.

```
export PYTHONPATH=src
UV=/Users/bechir/research/labs/.tools/py/bin/uv

# tests (unit, property, golden, differential, integration)
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli test

# exploratory smoke run (tuning streams and edge cases only) -> results/exploratory/<run_set_id>/
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli smoke

# exploratory pilots (tuning streams only) and their summary
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --config experiments/exploratory/pilot-exp001.json
$UV run --frozen --python /usr/local/bin/python3 python experiments/exploratory/pilot_summary.py results/exploratory/*/result.json > results/exploratory/pilot_summary.json

# planned run counts and freeze status; the frozen confirmatory configs are accepted, any changed config is refused
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli run --plan --config research/experiments/EXP-001/config.json

# tables, figures and (optionally) a PDF from a result file
$UV run --frozen --python /usr/local/bin/python3 python -m fare.cli report --result results/exploratory/<run_set_id>/result.json [--pdf]
```

Demo commands (M5). Node from `/Users/bechir/research/helix/.tools/node/bin` on the owner's machine.

```
# published data for the demo (committed results only; fails closed if a display string is not in the manuscript)
PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py
# fixture that checks the browser sandbox against the Python engine (about 4 s, one core)
PYTHONPATH=src .venv/bin/python scripts/make_sandbox_fixture.py

cd demo && npm ci && npm test && npm run build && npm run preview
node tools/a11y_check.mjs dist --screenshots <dir>      # must print A11Y-CHECK PASS
```
