# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Check that every relative link in the tracked Markdown files resolves (M6).

A link is `[text](target)` or `![alt](target)` outside fenced code blocks and inline
code. External targets (http, https, mailto) are skipped. A relative target must name
an existing file or folder, resolved from the linking file's folder; a `#fragment` must
match a heading of the target Markdown file, using GitHub's anchor rule (lower case,
punctuation other than hyphens and underscores removed, spaces turned into hyphens,
duplicates numbered -1, -2, ...).

Usage: python scripts/check_links.py [files ...]   (default: every tracked *.md file)
Exit status 0 when every link resolves, 1 otherwise.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=REPO, check=True, capture_output=True, text=True).stdout
    return [REPO / line for line in out.splitlines() if line and "node_modules/" not in line]


def _prose_lines(text: str):
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield n, re.sub(r"`[^`]*`", "", line)


def slug(heading: str) -> str:
    h = re.sub(r"<[^>]+>", "", heading)              # inline HTML
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)     # links keep their text
    h = h.replace("*", "").replace("`", "").strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    seen: dict[str, int] = {}
    found = set()
    for _, line in _prose_lines(md.read_text(encoding="utf-8")):
        m = HEADING.match(line)
        if not m:
            continue
        s = slug(m.group(2))
        k = seen.get(s, 0)
        found.add(s if k == 0 else f"{s}-{k}")
        seen[s] = k + 1
    return found


def check_file(md: Path) -> list[str]:
    problems = []
    for n, line in _prose_lines(md.read_text(encoding="utf-8")):
        for m in LINK.finditer(line):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            path_part, _, frag = target.partition("#")
            dest = md if not path_part else (md.parent / unquote(path_part)).resolve()
            where = f"{md.relative_to(REPO)}:{n}: {target}"
            if not dest.exists():
                problems.append(f"{where} (missing file)")
            elif frag and dest.suffix == ".md" and unquote(frag).lower() not in anchors(dest):
                problems.append(f"{where} (missing anchor)")
            elif REPO not in dest.parents and dest != REPO:
                problems.append(f"{where} (outside the repository)")
    return problems


def main(argv: list[str]) -> int:
    files = [Path(a).resolve() for a in argv] or tracked_markdown()
    problems, links = [], 0
    for f in files:
        problems += check_file(f)
        links += sum(len(LINK.findall(line)) for _, line in _prose_lines(f.read_text(encoding="utf-8")))
    for p in problems:
        print(p)
    print(f"{len(files)} Markdown files, {links} links, {len(problems)} unresolved")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
