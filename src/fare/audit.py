# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Number trace for the evidence audit (master prompt 11.5, M4).

    PYTHONPATH=src python -m fare.audit research/paper/manuscript.md research/experiments/EXP-001/report.md ...

Every decimal number written in a document (a token with a decimal point,
such as 407.04, -1.72% or 1,094.1) and every comma-grouped integer (such as
73,000 or 21,532,968) must equal, at the precision shown, a value
stored in a committed machine-readable result file. Values are collected from
the committed JSON and CSV evidence files listed in SOURCES; a value v also
yields 100 v (percentages) and v / 2**20 (bytes to MiB). The command prints
every number it cannot trace, with its line, for manual review; it exits 1 if
any is untraced. It checks traceability, not meaning: a matched number can
still be quoted for the wrong quantity, which the audit checks by reading.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Iterable

from .manifest import REPO_ROOT

SOURCES = (
    "research/experiments/*/summary.json",
    "research/experiments/*/metrics.csv",
    "research/experiments/*/arm_summary.csv",
    "research/experiments/*/run_manifest.json",
    "research/experiments/*/config.json",
    "results/exploratory/m4_audit_sensitivity.json",
    "results/exploratory/metric_validation.json",
    "results/exploratory/pilot_summary.json",
    "research/freeze.json",
)

NUMBER = re.compile(r"(?<![\w.])[-+]?\d{1,3}(?:,\d{3})*\.\d+|(?<![\w.])[-+]?\d+\.\d+")
# Comma-grouped integers (1,000 and above), such as run counts and byte sizes.
GROUPED = re.compile(r"(?<![\w.,])[-+]?\d{1,3}(?:,\d{3})+(?![\d.,]*\d)")


def _leaves(x) -> Iterable[float]:
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        yield float(x)
    elif isinstance(x, dict):
        for v in x.values():
            yield from _leaves(v)
    elif isinstance(x, list):
        for v in x:
            yield from _leaves(v)
    elif isinstance(x, str):
        try:
            yield float(x)
        except ValueError:
            return


def source_values(root: Path = REPO_ROOT, patterns: Iterable[str] = SOURCES) -> list[float]:
    vals: list[float] = []
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if p.suffix == ".json":
                vals.extend(_leaves(json.loads(p.read_text())))
            elif p.suffix == ".csv":
                with open(p, newline="") as f:
                    for row in csv.reader(f):
                        vals.extend(_leaves(row))
    return vals


def traceable_strings(values: Iterable[float], max_decimals: int = 4) -> set[str]:
    out: set[str] = set()
    for v in values:
        for w in (v, 100.0 * v, v / 2**20):
            a = abs(w)
            for d in range(1, max_decimals + 1):
                out.add(f"{a:.{d}f}")
        if float(v).is_integer():
            out.add(f"{abs(v):.0f}")
    return out


def untraced(text: str, known: set[str]) -> list[tuple[int, str]]:
    missing = []
    for ln, line in enumerate(text.splitlines(), 1):
        for m in list(NUMBER.finditer(line)) + list(GROUPED.finditer(line)):
            tok = m.group(0).lstrip("+-").replace(",", "")
            if line[m.end():m.end() + 1] == "/":
                continue  # DOI prefix such as 10.1287/..., not a result
            if tok not in known:
                missing.append((ln, m.group(0)))
    return missing


def main(argv: list[str] | None = None) -> int:
    paths = [Path(a) for a in (argv if argv is not None else sys.argv[1:])]
    known = traceable_strings(source_values())
    bad = 0
    for p in paths:
        miss = untraced(p.read_text(), known)
        total = sum(len(NUMBER.findall(line)) + len(GROUPED.findall(line)) for line in p.read_text().splitlines())
        print(f"{p}: {total} numbers checked, {len(miss)} untraced")
        for ln, tok in miss:
            print(f"  line {ln}: {tok}")
        bad += len(miss)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
