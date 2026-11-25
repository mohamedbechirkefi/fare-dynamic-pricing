# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""M6 consistency: README, article drafts and CITATION.cff quote the manuscript's numbers.

Every decimal number, comma-grouped integer and percentage in these texts must appear
verbatim (sign aside) in research/paper/manuscript.md, unless it is a documented exception.
The demo data is covered by tests/test_demo_export.py.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MS = (ROOT / "research" / "paper" / "manuscript.md").read_text()
NUM = re.compile(r"(?<![\w.])[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|(?<![\w.])[+-]?\d+\.\d+%?")
# Numbers that are not results, each with its reason.
EXCEPTIONS = {
    ("demo/README.md", "1,000"): "size of the sandbox test fixture, not a result",
}
TEXTS = ["README.md", "articles/README.md", "articles/medium.md", "articles/linkedin.md", "demo/README.md"]


def _cff_abstract() -> str:
    text = (ROOT / "CITATION.cff").read_text()
    m = re.search(r"^abstract:\s*(.*?)(?=^\S)", text, re.M | re.S)
    assert m, "CITATION.cff has no abstract"
    return m.group(1)


@pytest.mark.parametrize("name", TEXTS + ["CITATION.cff"])
def test_numbers_match_manuscript(name):
    text = _cff_abstract() if name == "CITATION.cff" else (ROOT / name).read_text()
    missing = [n for n in NUM.findall(text)
               if n not in MS and n.lstrip("+-") not in MS and (name, n) not in EXCEPTIONS]
    assert missing == []
