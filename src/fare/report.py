# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Report generator: tables and figures built only from validated result files.

Figures are plain SVG written without plotting dependencies. Price-path figures
are re-simulated from the recorded scenario, seed key and policy, and the
regenerated stream's SHA-256 must equal the recorded one (fail closed).
"""

from __future__ import annotations

import csv
import html
import io
import math
import subprocess
from pathlib import Path

import numpy as np

from .metrics import METRIC_NAMES, purchase_elasticity
from .params import ScenarioParams
from .policies import policy_from_dict
from .schema import read_result
from .simulate import simulate
from .stats import holm, interaction_bootstrap_ci, sign_flip_pvalue
from .streams import SeedKey, generate_stream

PANDOC = Path("/Users/bechir/research/labs/.tools/pandoc")
TOOLS_PY = Path("/Users/bechir/research/labs/.tools/py/bin/python")
PALETTE = {"FIX": "#4a4a4a", "OCC": "#1f6f8b", "DRP": "#b5562b", "FIX9": "#8a8a8a", "FIX6": "#8a8a8a", "FIX_retuned": "#6b8e23"}


class ReportError(RuntimeError):
    pass


def _fmt(x, nd=2) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f"{x:,.{nd}f}"


def _policy_str(p: dict) -> str:
    return p["family"] + "(" + ", ".join(f"{k}={v:.4g}" for k, v in p["params"].items()) + ")"


def metrics_csv(doc: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["run_id", "cell_id", "arm", "role", "stream_index", "stream_sha256", "policy", "status", *METRIC_NAMES])
    for c in doc["cells"]:
        for r in c["runs"]:
            m = r["metrics"] or {}
            w.writerow([r["run_id"], c["cell_id"], r["arm"], r["role"], r["stream_index"], r["stream_sha256"],
                        _policy_str(r["policy"]), r["status"], *[m.get(k, "") if m.get(k) is not None else "" for k in METRIC_NAMES]])
    return buf.getvalue()


def arm_table(cell: dict) -> str:
    cols = ["revenue", "sell_through", "availability", "price_volatility", "consumer_surplus", "stockout_period"]
    lines = ["| Arm | Policy | n | " + " | ".join(f"{c} mean (sd)" for c in cols) + " |",
             "|" + "---|" * (3 + len(cols))]
    arms = []
    for r in cell["runs"]:
        if r["arm"] not in arms:
            arms.append(r["arm"])
    for a in arms:
        rs = [r for r in cell["runs"] if r["arm"] == a and r["status"] == "ok"]
        if not rs:
            lines.append(f"| {a} | n/a | 0 |" + " n/a |" * len(cols))
            continue
        cells = []
        for c in cols:
            v = np.array([r["metrics"][c] for r in rs], float)
            sd = v.std(ddof=1) if len(v) > 1 else float("nan")
            cells.append(f"{_fmt(float(v.mean()))} ({_fmt(float(sd)) if math.isfinite(sd) else 'n/a'})")
        lines.append(f"| {a} | {_policy_str(rs[0]['policy'])} | {len(rs)} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def tuning_table(cell: dict) -> str:
    if not cell["tuning"]:
        return "_No tuning in this cell (fixed hand-set policies)._"
    sp = ScenarioParams.from_dict(cell["scenario"])
    lines = ["| Arm | Tuned in cell | Configs x streams | Selected | Mean tuning revenue | At grid edge | Purchase elasticity at selected FIX price |",
             "|---|---|---|---|---|---|---|"]
    for t in cell["tuning"]:
        el = "n/a"
        if t["family"] == "FIX":
            e = purchase_elasticity(sp, t["selected"]["params"]["p"])
            el = _fmt(e, 3) if e is not None else "undefined"
        lines.append(f"| {t['arm']} | {t.get('tuned_in_cell', '')} | {t['n_configs']} x {t['n_streams']} | "
                     f"{_policy_str(t['selected'])} | {_fmt(t['mean_revenue'][t['selected_index']])} | "
                     f"{'yes' if t['at_grid_edge'] else 'no'} | {el} |")
    return "\n".join(lines)


def contrast_table(cell: dict) -> str:
    if not cell["contrasts"]:
        return "_No contrasts (no FIX arm)._"
    lines = ["| Arm | vs | Metric | n | Mean paired diff | SD diff | d_z | Level | Bootstrap CI | t CI | Relative | Class |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in cell["contrasts"]:
        rel = f"{100 * k['relative_effect']:.2f}%" if k["relative_effect"] is not None else "n/a"
        lines.append(f"| {k['arm']} | {k['comparator']} | {k['metric']} | {k['n']} | {_fmt(k['mean_diff'], 3)} | "
                     f"{_fmt(k['sd_diff'], 3)} | {_fmt(k['d_z'], 3)} | {k['level']} | "
                     f"[{_fmt(k['boot_ci'][0], 3)}, {_fmt(k['boot_ci'][1], 3)}] | "
                     f"[{_fmt(k['t_ci'][0], 3)}, {_fmt(k['t_ci'][1], 3)}] | {rel} | {k['classification'] or 'n/a'} |")
    return "\n".join(lines)


def multiplicity_table(doc: dict, n_perm: int = 10_000, seed: int = 20261124) -> str | None:
    """Paired sign-flip p-values for revenue (arm minus FIX) in every evaluated
    cell, Holm-adjusted over all such contrasts (EXP-002 analysis plan)."""
    rows = []
    for c in doc["cells"]:
        fix = {r["stream_index"]: r["metrics"]["revenue"] for r in c["runs"] if r["arm"] == "FIX" and r["status"] == "ok"}
        for arm in ("OCC", "DRP"):
            d = [r["metrics"]["revenue"] - fix[r["stream_index"]] for r in c["runs"]
                 if r["arm"] == arm and r["status"] == "ok" and r["stream_index"] in fix]
            if len(d) >= 2:
                rows.append((c["cell_id"], arm, len(d), float(np.mean(d)), sign_flip_pvalue(d, n_perm, seed)))
    if len(rows) < 2:
        return None
    adj = holm([r[4] for r in rows])
    lines = ["| Cell | Arm | n | Mean paired revenue diff | Sign-flip p | Holm-adjusted p |", "|---|---|---|---|---|---|"]
    for r, a in zip(rows, adj):
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {_fmt(r[3], 3)} | {r[4]:.4f} | {a:.4f} |")
    return "\n".join(lines)


def interaction_table(doc: dict, level: float = 0.95, n_resamples: int = 10_000,
                      seed: int = 20261124) -> str | None:
    """EXP-002 interaction contrasts: for each sigma_v, Delta at the largest
    kappa minus Delta at the smallest kappa, per arm, with the independent
    stratified bootstrap interval (stats.interaction_bootstrap_ci)."""
    by_sv: dict[float, dict[float, dict]] = {}
    for c in doc["cells"]:
        sc = c.get("scenario", {})
        if c["runs"] and "sigma_v" in sc and "kappa" in sc:
            by_sv.setdefault(float(sc["sigma_v"]), {})[float(sc["kappa"])] = c
    rows = []
    for sv in sorted(by_sv):
        ks = sorted(by_sv[sv])
        if len(ks) < 2:
            continue
        hi_c, lo_c = by_sv[sv][ks[-1]], by_sv[sv][ks[0]]
        for arm in ("OCC", "DRP"):
            dh, dl = _paired_revenue(hi_c, arm), _paired_revenue(lo_c, arm)
            if len(dh) >= 2 and len(dl) >= 2:
                est, ci = interaction_bootstrap_ci(dh, dl, level, n_resamples, seed)
                rows.append((sv, ks[-1], ks[0], arm, len(dh), len(dl), est, ci))
    if not rows:
        return None
    lines = ["| sigma_v | Arm | Contrast | n (hi, lo) | Difference of differences | Bootstrap interval |",
             "|---|---|---|---|---|---|"]
    for sv, kh, kl, arm, nh, nl, est, ci in rows:
        lines.append(f"| {sv:g} | {arm} | Delta(kappa={kh:g}) - Delta(kappa={kl:g}) | {nh}, {nl} | {_fmt(est, 3)} | "
                     f"[{_fmt(ci[0], 3)}, {_fmt(ci[1], 3)}] |")
    return "\n".join(lines)


def _paired_revenue(cell: dict, arm: str) -> list[float]:
    fix = {r["stream_index"]: r["metrics"]["revenue"] for r in cell["runs"] if r["arm"] == "FIX" and r["status"] == "ok"}
    return [r["metrics"]["revenue"] - fix[r["stream_index"]] for r in cell["runs"]
            if r["arm"] == arm and r["status"] == "ok" and r["stream_index"] in fix]


def _svg(width: int, height: int, body: list[str], title: str, desc: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-labelledby="t d" font-family="Helvetica, Arial, sans-serif" font-size="12">\n'
            f'<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->\n'
            f'<title id="t">{html.escape(title)}</title><desc id="d">{html.escape(desc)}</desc>\n'
            f'<rect width="100%" height="100%" fill="#ffffff"/>\n' + "\n".join(body) + "\n</svg>\n")


def diff_strip_svg(cell: dict, label: str) -> str | None:
    """Per-stream paired revenue differences (arm minus FIX), one row per arm."""
    fix = {r["stream_index"]: r["metrics"]["revenue"] for r in cell["runs"] if r["arm"] == "FIX" and r["status"] == "ok"}
    arms = [a for a in dict.fromkeys(r["arm"] for r in cell["runs"]) if a != "FIX"]
    if not fix or not arms:
        return None
    data = {}
    for a in arms:
        d = [r["metrics"]["revenue"] - fix[r["stream_index"]] for r in cell["runs"]
             if r["arm"] == a and r["status"] == "ok" and r["stream_index"] in fix]
        if d:
            data[a] = np.array(d)
    if not data:
        return None
    lo = min(0.0, min(float(v.min()) for v in data.values()))
    hi = max(0.0, max(float(v.max()) for v in data.values()))
    if hi == lo:
        hi = lo + 1.0
    W, rowh, L, R, top = 760, 60, 110, 30, 40
    H = top + rowh * len(data) + 50
    sx = lambda x: L + (x - lo) / (hi - lo) * (W - L - R)
    body = [f'<text x="{L}" y="22" font-size="13" font-weight="bold">{html.escape(label)}: paired revenue difference vs FIX (currency per season)</text>',
            f'<line x1="{sx(0):.1f}" y1="{top - 5}" x2="{sx(0):.1f}" y2="{top + rowh * len(data)}" stroke="#999" stroke-dasharray="4 3"/>']
    rng = np.random.default_rng(0)
    for i, (a, v) in enumerate(data.items()):
        cy = top + rowh * i + rowh / 2
        body.append(f'<text x="{L - 10}" y="{cy + 4:.1f}" text-anchor="end">{html.escape(a)} (n={len(v)})</text>')
        jit = rng.uniform(-12, 12, len(v))
        col = PALETTE.get(a, "#333")
        for x, j in zip(v, jit):
            body.append(f'<circle cx="{sx(x):.1f}" cy="{cy + j:.1f}" r="2.2" fill="{col}" fill-opacity="0.45"/>')
        m = float(v.mean())
        body.append(f'<line x1="{sx(m):.1f}" y1="{cy - 18:.1f}" x2="{sx(m):.1f}" y2="{cy + 18:.1f}" stroke="#000" stroke-width="2"/>')
    yb = top + rowh * len(data) + 10
    body.append(f'<line x1="{L}" y1="{yb}" x2="{W - R}" y2="{yb}" stroke="#333"/>')
    for k in range(6):
        x = lo + (hi - lo) * k / 5
        body.append(f'<line x1="{sx(x):.1f}" y1="{yb}" x2="{sx(x):.1f}" y2="{yb + 5}" stroke="#333"/>')
        body.append(f'<text x="{sx(x):.1f}" y="{yb + 18}" text-anchor="middle">{x:,.0f}</text>')
    desc = ("Dot plot, one dot per stream, of revenue under each arm minus revenue under FIX on the same stream; "
            "the black bar is the mean; the dashed line is zero. " + "; ".join(
                f"{a}: n={len(v)}, mean {v.mean():.2f}, min {v.min():.2f}, max {v.max():.2f}" for a, v in data.items()))
    return _svg(W, H, body, f"{label} paired revenue differences", desc)


def price_path_svg(cell: dict, label: str) -> str | None:
    """Posted price over the season for each arm on the first evaluated stream,
    re-simulated from the recorded keys and checked against the stream hash."""
    runs = [r for r in cell["runs"] if r["status"] == "ok"]
    if not runs:
        return None
    first = min(r["stream_index"] for r in runs)
    sp = ScenarioParams.from_dict(cell["scenario"])
    paths = {}
    for r in runs:
        if r["stream_index"] != first or r["arm"] in paths:
            continue
        s = generate_stream(sp, SeedKey(*r["seed_key"]))
        if s.sha256() != r["stream_sha256"]:
            raise ReportError(f"stream hash mismatch for {r['run_id']}: result file and code disagree")
        o = simulate(s, sp, policy_from_dict(r["policy"]))
        if abs(o.revenue - r["metrics"]["revenue"]) > 1e-6 * max(1.0, o.revenue):
            raise ReportError(f"re-simulated revenue differs for {r['run_id']}")
        paths[r["arm"]] = o.prices
    T = sp.T
    lo, hi = sp.p_min, max(float(max(p.max() for p in paths.values())) * 1.05, 1.0)
    W, H, L, R, top, bot = 760, 360, 70, 120, 40, 50
    sx = lambda t: L + (t - 1) / max(T - 1, 1) * (W - L - R)
    sy = lambda p: top + (1 - (p - lo) / (hi - lo)) * (H - top - bot)
    body = [f'<text x="{L}" y="22" font-size="13" font-weight="bold">{html.escape(label)}: posted price by period, stream {first}</text>',
            f'<line x1="{L}" y1="{H - bot}" x2="{W - R}" y2="{H - bot}" stroke="#333"/>',
            f'<line x1="{L}" y1="{top}" x2="{L}" y2="{H - bot}" stroke="#333"/>',
            f'<text x="{(L + W - R) / 2}" y="{H - 12}" text-anchor="middle">period t (simulation periods)</text>',
            f'<text x="16" y="{(top + H - bot) / 2}" transform="rotate(-90 16 {(top + H - bot) / 2})" text-anchor="middle">price (currency)</text>']
    for k in range(5):
        p = lo + (hi - lo) * k / 4
        body.append(f'<text x="{L - 6}" y="{sy(p) + 4:.1f}" text-anchor="end">{p:,.0f}</text>')
    for t in sorted({1, T // 4 or 1, T // 2 or 1, 3 * T // 4 or 1, T}):
        body.append(f'<text x="{sx(t):.1f}" y="{H - bot + 16}" text-anchor="middle">{t}</text>')
    for i, (a, p) in enumerate(paths.items()):
        pts = " ".join(f"{sx(t + 1):.1f},{sy(v):.1f}" for t, v in enumerate(p))
        col = PALETTE.get(a, "#333")
        body.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2"/>')
        body.append(f'<text x="{W - R + 10}" y="{top + 16 * i + 10}" fill="{col}">{html.escape(a)}</text>')
    desc = "Line chart of the posted price in each period for each arm on one stream. " + "; ".join(
        f"{a}: start {p[0]:.1f}, end {p[-1]:.1f}, min {p.min():.1f}, max {p.max():.1f}" for a, p in paths.items())
    return _svg(W, H, body, f"{label} price paths", desc)


def build_report(result_path: Path, out_dir: Path | None = None, pdf: bool = False) -> dict:
    doc = read_result(result_path)
    out = Path(out_dir) if out_dir else Path(result_path).parent / "report"
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.csv").write_text(metrics_csv(doc))
    banner = ("**EXPLORATORY. Not evidence.** Produced before the owner froze the protocol; exploratory runs are "
              "never reported as findings." if doc["label"] == "exploratory" else
              "**Confirmatory** run under a frozen protocol.")
    md = ["<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->",
          f"# {doc['experiment_id']} run set {doc['run_set_id']}", "", banner, "",
          "All numbers are simulated and hold only within the model of `research/protocol.md`.", "",
          f"- Created (UTC): {doc['created_utc']}",
          f"- Config SHA-256: `{doc['config_sha256']}`",
          f"- Protocol: `{doc['protocol']['path']}` SHA-256 `{doc['protocol']['sha256']}`, frozen: {doc['protocol']['frozen']}",
          f"- Failed runs: {doc['failures']}",
          f"- Manifest: `{doc['manifest_path']}`"]
    if doc.get("note"):
        md += ["", doc["note"]]
    figs = []
    for c in doc["cells"]:
        tm = c["timing"]
        md += ["", f"## Cell {c['cell_id']} (index {c['cell_index']})", "",
               f"Timing: stream generation {tm['stream_generation_s']:.2f} s; tuning {tm['tuning_runs']} runs in "
               f"{tm['tuning_s']:.2f} s; evaluation {tm['eval_runs']} runs in {tm['eval_s']:.2f} s.", "",
               "### Tuning", "", tuning_table(c), "", "### Arms (per-stream metrics)", "", arm_table(c), "",
               "### Paired contrasts", "", contrast_table(c)]
        for kind, fn in (("diff", diff_strip_svg), ("price", price_path_svg)):
            svg = fn(c, f"{doc['experiment_id']} {c['cell_id']}")
            if svg:
                name = f"fig-{c['cell_id']}-{kind}.svg"
                (out / name).write_text(svg)
                figs.append(name)
                md += ["", f"![{doc['experiment_id']} {c['cell_id']} {kind} figure]({name})"]
    mt = multiplicity_table(doc)
    if mt:
        md += ["", "## Multiplicity across cells (revenue vs FIX, Holm over all listed contrasts)", "", mt]
    it = interaction_table(doc)
    if it:
        md += ["", "## Interaction contrasts (independent stratified bootstrap, 95%)", "", it]
    (out / "report.md").write_text("\n".join(md) + "\n")
    produced = {"report_md": str(out / "report.md"), "metrics_csv": str(out / "metrics.csv"), "figures": figs, "pdf": None}
    if pdf:
        produced["pdf"] = str(render_pdf(out / "report.md"))
    return produced


def render_pdf(md_path: Path) -> Path:
    """pandoc -> Typst -> PDF (the M0 workaround: mainfont must be set)."""
    if not PANDOC.exists() or not TOOLS_PY.exists():
        raise ReportError("pandoc or the tools Python (typst package) is not available")
    md_path = Path(md_path).resolve()
    typ = md_path.with_suffix(".typ")
    pdf = md_path.with_suffix(".pdf")
    subprocess.run([str(PANDOC), str(md_path), "-s", "-t", "typst", "-V", 'mainfont=Libertinus Serif',
                    "-o", str(typ)], check=True, cwd=md_path.parent)
    subprocess.run([str(TOOLS_PY), "-c", f"import typst; typst.compile({str(typ)!r}, output={str(pdf)!r}, root={str(md_path.parent)!r})"],
                   check=True, cwd=md_path.parent)
    return pdf
