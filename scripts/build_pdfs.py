# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Build the manuscript, supplementary and experiment-report PDFs (M6).

Markdown is canonical (decision D-003). Each document goes through pandoc to Typst
(`-V mainfont="Libertinus Serif"`, the M0 workaround) and is compiled with the
`typst` Python package of the shared toolchain. Documents without YAML front matter
take their first level-1 heading as the title (passed as metadata, the heading removed
and the others shifted up one level), so the PDF metadata carries a title. The Typst root is `research/`, so the manuscript can
reference the experiment figures in place. The intermediate `.typ` files are removed
unless `--keep-typ` is given; `--png-dir` also renders every page to PNG for visual
inspection (outside the repository).

Usage: PYTHONPATH=src .venv/bin/python scripts/build_pdfs.py [--png-dir DIR] [--ppi 60] [--keep-typ]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from fare.report import PANDOC, TOOLS_PY  # noqa: E402

ROOT = REPO / "research"
DOCS = [
    ("manuscript", ROOT / "paper" / "manuscript.md", False),
    ("supplementary", ROOT / "paper" / "supplementary.md", True),
    ("EXP-001", ROOT / "experiments" / "EXP-001" / "report.md", True),
    ("EXP-002", ROOT / "experiments" / "EXP-002" / "report.md", True),
    ("EXP-003", ROOT / "experiments" / "EXP-003" / "report.md", True),
]


# Typst rules added to every document (M6 visual inspection):
# - image captions already start with "Figure N." in the Markdown, so the automatic "Figure N:" prefix is dropped;
# - table cells are left-aligned and not justified (prose cells were stretched), in a slightly smaller size;
# - tables may break across pages instead of leaving a page half empty.
HEADER = "\n".join([
    "#show figure.caption: it => it.body",
    "#show figure: set block(breakable: true)",
    "#show table: set text(size: 0.9em)",
    "#show table.cell: set align(left)",
    "#show table.cell: set par(justify: false)",
    # long inline code (hashes, paths) may break at any character instead of running off the page
    "#show raw.where(block: false): r => if r.text.len() > 24 "
    "{ text(font: \"DejaVu Sans Mono\", size: 0.9em, r.text.clusters().join(sym.zws)) } else { r }",
])


def build(name: str, md: Path, shift: bool, png_dir: Path | None, ppi: int, keep_typ: bool) -> Path:
    typ, pdf = md.with_suffix(".typ"), md.with_suffix(".pdf")
    text = md.read_text(encoding="utf-8")
    cmd = [str(PANDOC), "-f", "markdown", "-s", "-t", "typst", "-V", "mainfont=Libertinus Serif",
           "-V", "papersize=a4", "-V", f"header-includes={HEADER}", "-o", typ.name]
    if shift:
        # the first level-1 heading becomes the document title (and the PDF metadata title);
        # the remaining headings move up one level
        m = re.search(r"^# (.+)$", text, re.M)
        text = text[:m.start()] + text[m.end():]
        cmd += ["-M", f"title={m.group(1).strip()}", "--shift-heading-level-by=-1"]
    subprocess.run(cmd, check=True, cwd=md.parent, input=text, text=True)
    code = ("import sys, typst\n"
            "typ, pdf, root = sys.argv[1:4]\n"
            "typst.compile(typ, output=pdf, root=root)\n"
            "if len(sys.argv) > 4:\n"
            "    typst.compile(typ, output=sys.argv[4], format='png', ppi=int(sys.argv[5]), root=root)\n")
    args = [str(TOOLS_PY), "-c", code, str(typ), str(pdf), str(ROOT)]
    if png_dir is not None:
        png_dir.mkdir(parents=True, exist_ok=True)
        args += [str(png_dir / f"{name}-{{p}}.png"), str(ppi)]
    subprocess.run(args, check=True)
    if not keep_typ:
        typ.unlink()
    return pdf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png-dir", type=Path)
    ap.add_argument("--ppi", type=int, default=60)
    ap.add_argument("--keep-typ", action="store_true")
    a = ap.parse_args()
    if not PANDOC.exists() or not TOOLS_PY.exists():
        print("pandoc or the tools Python (typst package) is not available", file=sys.stderr)
        return 2
    for name, md, shift in DOCS:
        pdf = build(name, md, shift, a.png_dir, a.ppi, a.keep_typ)
        print(f"wrote {pdf.relative_to(REPO)} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
