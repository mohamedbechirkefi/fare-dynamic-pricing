# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Frozen-analysis summaries of a result file (M3 evidence layer).

    PYTHONPATH=src python -m fare.summary --result <run_dir>/result.json --out research/experiments/EXP-NNN \
        [--exp001-summary research/experiments/EXP-001/summary.json]

Reads a validated result file and writes, into --out:
- summary.json: run counts, tuned configurations and grid-edge findings, arm
  summaries, every recorded contrast, the frozen decision rule applied to the
  experiment, and the SHA-256 manifest of the raw run directory;
- metrics.csv: one row per contrast (aggregate, small enough to commit);
- arm_summary.csv: per cell and arm, mean and SD of every metric;
- figures/fig-<EXP>-forest-revenue.svg: paired revenue differences with
  their intervals and the SESOI band, one row per cell and arm.

Only computations fixed in the frozen protocols are applied here, with the
seeds of the frozen configs; the same statistics functions as `fare.report`
are reused. Nothing in this module tunes, filters or excludes runs.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .manifest import REPO_ROOT, sha256_file
from .metrics import METRIC_NAMES
from .report import _paired_revenue, _policy_str, grid_edge_findings
from .schema import read_result
from .stats import holm, interaction_bootstrap_ci, sign_flip_pvalue

SUMMARY_VERSION = "1.0.0"
FROZEN_SEED = 20261124
N_PERM = 10_000
N_BOOT = 10_000
MODERATE_SHIFT_CELLS = ("demand-x0.8", "demand-x1.25")


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def raw_manifest(run_dir: Path) -> dict[str, Any]:
    """SHA-256 and size of every file in the raw run directory."""
    run_dir = Path(run_dir)
    files = []
    for f in sorted(p for p in run_dir.rglob("*") if p.is_file()):
        files.append({"path": str(f.relative_to(run_dir)), "bytes": f.stat().st_size, "sha256": sha256_file(f)})
    return {"run_dir": _rel(run_dir), "files": files, "total_bytes": sum(f["bytes"] for f in files)}


def arm_summary(doc: dict) -> list[dict]:
    rows = []
    for c in doc["cells"]:
        arms = list(dict.fromkeys(r["arm"] for r in c["runs"]))
        for a in arms:
            rs = [r for r in c["runs"] if r["arm"] == a]
            ok = [r for r in rs if r["status"] == "ok"]
            row = {"cell_id": c["cell_id"], "arm": a, "policy": _policy_str(rs[0]["policy"]),
                   "n_runs": len(rs), "n_ok": len(ok), "n_failed": len(rs) - len(ok)}
            for m in METRIC_NAMES:
                v = np.array([r["metrics"][m] for r in ok if r["metrics"][m] is not None], float)
                row[f"{m}_n"] = int(len(v))
                row[f"{m}_mean"] = float(v.mean()) if len(v) else None
                row[f"{m}_sd"] = float(v.std(ddof=1)) if len(v) > 1 else None
            rows.append(row)
    return rows


def contrast_rows(doc: dict) -> list[dict]:
    rows = []
    for c in doc["cells"]:
        for k in c["contrasts"]:
            rows.append({"cell_id": c["cell_id"], "arm": k["arm"], "comparator": k["comparator"],
                         "metric": k["metric"], "n": k["n"], "mean_diff": k["mean_diff"], "sd_diff": k["sd_diff"],
                         "d_z": k["d_z"], "level": k["level"], "boot_lo": k["boot_ci"][0], "boot_hi": k["boot_ci"][1],
                         "t_lo": k["t_ci"][0], "t_hi": k["t_ci"][1], "relative_effect": k["relative_effect"],
                         "classification": k["classification"]})
    return rows


def holm_rows(doc: dict, n_perm: int = N_PERM, seed: int = FROZEN_SEED) -> list[dict]:
    """Sign-flip p-values (revenue, arm minus FIX) per evaluated cell, Holm over
    all of them: the EXP-002 frozen test (same computation as
    `fare.report.multiplicity_table`)."""
    rows = []
    for c in doc["cells"]:
        if not c["runs"]:
            continue
        for arm in ("OCC", "DRP"):
            d = _paired_revenue(c, arm)
            if len(d) >= 2:
                rows.append({"cell_id": c["cell_id"], "arm": arm, "n": len(d), "mean_diff": float(np.mean(d)),
                             "p_sign_flip": sign_flip_pvalue(d, n_perm, seed)})
    adj = holm([r["p_sign_flip"] for r in rows]) if rows else []
    for r, a in zip(rows, adj):
        r["p_holm"] = a
        r["reject_h0_at_0.05"] = bool(a < 0.05)
    return rows


def interaction_rows(doc: dict, level: float = 0.95, n_resamples: int = N_BOOT, seed: int = FROZEN_SEED) -> list[dict]:
    """EXP-002 interaction contrasts (same computation as
    `fare.report.interaction_table`), with a descriptive reading."""
    by_sv: dict[float, dict[float, dict]] = {}
    for c in doc["cells"]:
        sc = c.get("scenario", {})
        if c["runs"]:
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
                est, (lo, hi) = interaction_bootstrap_ci(dh, dl, level, n_resamples, seed)
                reading = ("larger at the high kappa" if lo > 0 else "smaller at the high kappa" if hi < 0
                           else "not distinguishable (interval includes 0)")
                rows.append({"sigma_v": sv, "arm": arm, "kappa_hi": ks[-1], "kappa_lo": ks[0], "n_hi": len(dh),
                             "n_lo": len(dl), "estimate": est, "lo": lo, "hi": hi, "level": level,
                             "reading": reading})
    return rows


def _find(rows: list[dict], **kw) -> dict | None:
    for r in rows:
        if all(r.get(k) == v for k, v in kw.items()):
            return r
    return None


def verdict_exp001(contrasts: list[dict]) -> dict:
    out: dict[str, Any] = {"rule": "research/protocol.md section 5: reject H0_j when the Bonferroni-adjusted 97.5% "
                                   "paired bootstrap interval for Delta_j excludes 0; classify against SESOI = 1% of "
                                   "mean FIX* revenue; tuning-grid sensitivity (section 10.2): a change of sign or "
                                   "class against FIX6 attributes the result to grid resolution."}
    for j in ("OCC", "DRP"):
        k = _find(contrasts, cell_id="base", arm=j, comparator="FIX", metric="revenue")
        s = _find(contrasts, cell_id="base", arm=j, comparator="FIX6", metric="revenue")
        if k is None:
            out[j] = {"status": "missing"}
            continue
        reject = k["boot_lo"] > 0 or k["boot_hi"] < 0
        sens = None
        if s is not None:
            same_sign = math.copysign(1, k["mean_diff"]) == math.copysign(1, s["mean_diff"])
            same_class = k["classification"] == s["classification"]
            sens = {"mean_diff_vs_FIX6": s["mean_diff"], "boot_ci_vs_FIX6": [s["boot_lo"], s["boot_hi"]],
                    "classification_vs_FIX6": s["classification"], "sign_changed": not same_sign,
                    "class_changed": not same_class,
                    "attributed_to_grid_resolution": (not same_sign) or (not same_class)}
        rel = k["relative_effect"]
        out[j] = {"mean_diff": k["mean_diff"], "boot_ci_97_5": [k["boot_lo"], k["boot_hi"]],
                  "t_ci_97_5": [k["t_lo"], k["t_hi"]], "relative_effect": rel, "n": k["n"],
                  "reject_h0": bool(reject), "classification": k["classification"],
                  "gain_above_5pct_contradicts_planning_expectation": bool(rel is not None and rel > 0.05),
                  "grid_sensitivity": sens}
    return out


def verdict_exp002(holm_table: list[dict], contrasts: list[dict], interactions: list[dict]) -> dict:
    cells = []
    for r in holm_table:
        k = _find(contrasts, cell_id=r["cell_id"], arm=r["arm"], comparator="FIX", metric="revenue") or {}
        cells.append({**r, "boot_ci_95": [k.get("boot_lo"), k.get("boot_hi")], "relative_effect": k.get("relative_effect"),
                      "classification": k.get("classification")})
    return {"rule": "EXP-002 protocol section 5: paired sign-flip permutation p-value per contrast (10,000 "
                    "permutations, seed 20261124), Holm over the 18 contrasts at family-wise alpha 0.05; paired "
                    "bootstrap 95% intervals alongside; interaction contrasts descriptive (independent stratified "
                    "bootstrap, 95%, no multiplicity adjustment).",
            "n_contrasts": len(cells), "n_rejected": sum(1 for c in cells if c["reject_h0_at_0.05"]),
            "contrasts": cells, "interactions": interactions}


def verdict_exp003(contrasts: list[dict], exp001: dict | None) -> dict:
    out: dict[str, Any] = {"rule": "EXP-003 protocol section 5: if EXP-001 rejected H0_j, the EXP-001 result for j is "
                                   "reported as specific to correct specification when, in demand-x0.8 or "
                                   "demand-x1.25, the 95% interval of Delta_{j,c} (vs base-tuned FIX) lies entirely "
                                   "on the opposite side of zero from the EXP-001 point estimate; if EXP-001 did not "
                                   "reject H0_j, this experiment is descriptive only for j."}
    for j in ("OCC", "DRP"):
        e1 = (exp001 or {}).get(j)
        cells = {}
        for cid in MODERATE_SHIFT_CELLS:
            k = _find(contrasts, cell_id=cid, arm=j, comparator="FIX", metric="revenue")
            cells[cid] = None if k is None else {"mean_diff": k["mean_diff"], "boot_ci_95": [k["boot_lo"], k["boot_hi"]]}
        if not e1 or "reject_h0" not in e1:
            out[j] = {"status": "EXP-001 verdict unavailable; rule not applied", "cells": cells}
            continue
        if not e1["reject_h0"]:
            out[j] = {"exp001_rejected": False, "applies": False, "status": "descriptive only", "cells": cells}
            continue
        sign = math.copysign(1, e1["mean_diff"])
        opposite = {cid: (v is not None and ((sign > 0 and v["boot_ci_95"][1] < 0) or (sign < 0 and v["boot_ci_95"][0] > 0)))
                    for cid, v in cells.items()}
        out[j] = {"exp001_rejected": True, "exp001_mean_diff": e1["mean_diff"], "applies": True, "cells": cells,
                  "interval_opposite_side": opposite,
                  "specific_to_correct_specification": any(opposite.values())}
    return out


def forest_svg(rows: list[dict], title: str, sesoi: dict[str, float]) -> str:
    """Horizontal interval plot of paired revenue differences."""
    W, rowh, L, R, top = 820, 26, 250, 40, 50
    H = top + rowh * len(rows) + 60
    vals = [v for r in rows for v in (r["boot_lo"], r["boot_hi"], r["mean_diff"])]
    vals += [s for r in rows for s in (-sesoi.get(r["cell_id"], 0), sesoi.get(r["cell_id"], 0))] + [0.0]
    lo, hi = min(vals), max(vals)
    pad = 0.05 * (hi - lo or 1.0)
    lo, hi = lo - pad, hi + pad
    sx = lambda x: L + (x - lo) / (hi - lo) * (W - L - R)
    body = [f'<text x="10" y="22" font-size="13" font-weight="bold">{html.escape(title)}</text>',
            f'<line x1="{sx(0):.1f}" y1="{top - 8}" x2="{sx(0):.1f}" y2="{top + rowh * len(rows)}" stroke="#999" stroke-dasharray="4 3"/>']
    col = {"OCC": "#1f6f8b", "DRP": "#b5562b"}
    for i, r in enumerate(rows):
        cy = top + rowh * i + rowh / 2
        s = sesoi.get(r["cell_id"])
        if s:
            body.append(f'<rect x="{sx(-s):.1f}" y="{cy - 9:.1f}" width="{sx(s) - sx(-s):.1f}" height="18" fill="#dddddd" fill-opacity="0.6"/>')
        c = col.get(r["arm"], "#333")
        lab = f'{r["cell_id"]}: {r["arm"]} vs {r["comparator"]} (n={r["n"]}, {100 * r["level"]:g}%)'
        body.append(f'<text x="{L - 8}" y="{cy + 4:.1f}" text-anchor="end">{html.escape(lab)}</text>')
        body.append(f'<line x1="{sx(r["boot_lo"]):.1f}" y1="{cy:.1f}" x2="{sx(r["boot_hi"]):.1f}" y2="{cy:.1f}" stroke="{c}" stroke-width="2.5"/>')
        body.append(f'<circle cx="{sx(r["mean_diff"]):.1f}" cy="{cy:.1f}" r="4" fill="{c}"/>')
    yb = top + rowh * len(rows) + 8
    body.append(f'<line x1="{L}" y1="{yb}" x2="{W - R}" y2="{yb}" stroke="#333"/>')
    for k in range(6):
        x = lo + (hi - lo) * k / 5
        body.append(f'<line x1="{sx(x):.1f}" y1="{yb}" x2="{sx(x):.1f}" y2="{yb + 5}" stroke="#333"/>')
        body.append(f'<text x="{sx(x):.1f}" y="{yb + 18}" text-anchor="middle">{x:,.0f}</text>')
    body.append(f'<text x="{(L + W - R) / 2}" y="{yb + 38}" text-anchor="middle">mean paired revenue difference (currency per season); '
                f'bar = paired percentile bootstrap interval; grey band = +/- SESOI (1% of mean FIX revenue in the cell)</text>')
    desc = "Interval plot. " + "; ".join(
        f'{r["cell_id"]} {r["arm"]} vs {r["comparator"]}: mean {r["mean_diff"]:.2f}, interval [{r["boot_lo"]:.2f}, {r["boot_hi"]:.2f}], n {r["n"]}'
        for r in rows)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t d" font-family="Helvetica, Arial, sans-serif" font-size="11">\n'
            f'<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->\n'
            f'<title id="t">{html.escape(title)}</title><desc id="d">{html.escape(desc)}</desc>\n'
            f'<rect width="100%" height="100%" fill="#ffffff"/>\n' + "\n".join(body) + "\n</svg>\n")


def _csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    return buf.getvalue()


def summarise_result(result_path: Path, out_dir: Path, exp001_summary: Path | None = None) -> dict:
    result_path = Path(result_path)
    doc = read_result(result_path)
    run_dir = result_path.parent
    man = json.loads((run_dir / "run_manifest.json").read_text())
    exp = doc["experiment_id"]
    contrasts = contrast_rows(doc)
    arms = arm_summary(doc)
    summary: dict[str, Any] = {
        "summary_version": SUMMARY_VERSION, "experiment_id": exp, "label": doc["label"], "simulated": True,
        "run_set_id": doc["run_set_id"], "result_path": _rel(result_path), "config_sha256": doc["config_sha256"],
        "protocol": doc["protocol"], "git": man.get("git"), "data_manifest": man.get("data_manifest"),
        "environment": man.get("environment"), "start_utc": man.get("start_utc"), "end_utc": man.get("end_utc"),
        "runtime_s": man.get("runtime_s"), "peak_rss_bytes": man.get("peak_rss_bytes"), "counts": man.get("counts"),
        "tuning": [{"cell_id": c["cell_id"], **{k: t[k] for k in ("arm", "family", "n_configs", "n_streams",
                    "tuned_in_cell", "selected_index", "selected", "at_grid_edge")},
                    "selected_mean_tuning_revenue": t["mean_revenue"][t["selected_index"]]}
                   for c in doc["cells"] for t in c["tuning"]],
        "grid_edge_findings": grid_edge_findings(doc),
        "arm_summary": arms, "contrasts": contrasts,
    }
    if exp == "EXP-001":
        summary["verdict"] = verdict_exp001(contrasts)
    elif exp == "EXP-002":
        summary["verdict"] = verdict_exp002(holm_rows(doc), contrasts, interaction_rows(doc))
    elif exp == "EXP-003":
        e1 = json.loads(Path(exp001_summary).read_text())["verdict"] if exp001_summary else None
        summary["verdict"] = verdict_exp003(contrasts, e1)
    out = Path(out_dir)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    rev = [r for r in contrasts if r["metric"] == "revenue"]
    fix_mean = {a["cell_id"]: a["revenue_mean"] for a in arms if a["arm"] == "FIX"}
    sesoi = {cid: 0.01 * m for cid, m in fix_mean.items() if m}
    fig = out / "figures" / f"fig-{exp}-forest-revenue.svg"
    if rev:
        fig.write_text(forest_svg(rev, f"{exp}: paired revenue differences with intervals ({doc['label']})", sesoi))
        summary["figures"] = [_rel(fig)]
    (out / "metrics.csv").write_text(_csv(contrasts))
    (out / "arm_summary.csv").write_text(_csv(arms))
    summary["raw_manifest"] = raw_manifest(run_dir)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, allow_nan=False) + "\n")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="fare.summary", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--exp001-summary", type=Path, default=None)
    a = ap.parse_args(argv)
    s = summarise_result(a.result, a.out, a.exp001_summary)
    print(json.dumps({"experiment_id": s["experiment_id"], "label": s["label"], "verdict": s.get("verdict")},
                     indent=1, default=str)[:20000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
