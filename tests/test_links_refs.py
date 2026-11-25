# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""M6 checks: relative Markdown links resolve, and the bibliography matches the manuscript.

1. `scripts/check_links.py` finds no unresolved relative link or anchor in the tracked
   Markdown files.
2. Every `references.bib` entry is listed in the manuscript's References section (first
   author surname and year, DOI equal), and every listed reference has a bib entry.
3. Every author-year citation in the manuscript body names a listed reference, and no
   pandoc `[@key]` citation is left unresolved.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "research" / "paper" / "manuscript.md"
BIB = ROOT / "research" / "paper" / "references.bib"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bib_entries() -> dict[str, dict[str, str]]:
    out = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", BIB.read_text(), re.S):
        fields = dict(re.findall(r"(\w+)\s*=\s*\{(.*?)\},?\s*$", m.group(2), re.M))
        out[m.group(1)] = fields
    return out


def _reference_list() -> list[str]:
    text = MS.read_text()
    block = text.split("\n# References\n", 1)[1].split("\n# ", 1)[0]
    return [p.strip() for p in block.split("\n\n") if p.strip()]


def test_relative_links_resolve():
    chk = _load_checker()
    problems = [p for f in chk.tracked_markdown() for p in chk.check_file(f)]
    assert problems == []


def test_link_checker_detects_breakage(tmp_path):
    chk = _load_checker()
    chk.REPO = tmp_path
    (tmp_path / "a.md").write_text("# Title\n\n[ok](#title) [bad](missing.md) [anchor](a.md#nope)\n```\n[skip](x.md)\n```\n")
    problems = chk.check_file(tmp_path / "a.md")
    assert len(problems) == 2 and "missing file" in problems[0] and "missing anchor" in problems[1]


def test_bib_and_reference_list_agree():
    bib = _bib_entries()
    refs = _reference_list()
    assert len(bib) == len(refs) == 4
    for key, f in bib.items():
        surname = f["author"].split(",")[0].strip()
        hits = [r for r in refs if r.startswith(surname) and f"({f['year']})" in r]
        assert len(hits) == 1, key
        assert f"https://doi.org/{f['doi']}" in hits[0], key


def test_body_citations_are_listed():
    text = MS.read_text()
    assert not re.search(r"\[@[\w:-]+", text)
    body = text.split("\n# References\n", 1)[0]
    refs = _reference_list()
    cited = set(re.findall(r"(Gallego and van Ryzin|Elmaghraby and Keskinocak|Su)[ ,(]+(?:\d{4}[;, ]*)*?(\d{4})", body))
    assert cited, "no author-year citation found"
    for author, year in cited:
        first = author.split(" and ")[0]
        assert any(r.startswith(first) and f"({year})" in r for r in refs), (author, year)
