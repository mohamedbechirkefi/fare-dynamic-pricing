# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Export the published results for the static demo (M5).

Writes demo/public/data/results.json in the shared demo schema
("lab-demo-results", 1.0.0) plus FARE-specific top-level keys:

- exploratory_checks: the M4 exploratory checks (J-0012), labelled as such;
- price_paths: posted price by period on evaluation stream 0 for every
  evaluated cell, the data behind the committed F-EXP-NNN-price figures;
- cells: scenario parameters and tuned policies per cell (sandbox presets);
- display_exceptions: display strings that are deliberately not printed in
  the manuscript, each with a reason.

Inputs are committed files only: the experiment summaries, metrics and arm
summaries, the frozen configs, the exploratory audit file, the claims
register, the artifact manifest, the limitations list and the manuscript. No
raw result file is read. The price paths are re-simulated from the committed
seed keys and tuned policies, exactly as src/fare/report.py builds the
committed price figures, and the export fails unless the regenerated SVG is
byte-identical to the committed figure. No metric is computed from them.

Every display and interval_display string must occur verbatim in
research/paper/manuscript.md unless it is listed in display_exceptions; the
export fails closed otherwise. Output is deterministic (no timestamps).

Usage: PYTHONPATH=src .venv/bin/python scripts/export_demo_data.py [--check]
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fare.params import ScenarioParams  # noqa: E402
from fare.policies import policy_from_dict  # noqa: E402
from fare.report import price_path_svg  # noqa: E402
from fare.simulate import simulate  # noqa: E402
from fare.streams import ROLE_EVAL, SeedKey, generate_stream  # noqa: E402

OUT = ROOT / "demo" / "public" / "data" / "results.json"
MANUSCRIPT = ROOT / "research" / "paper" / "manuscript.md"
EXPS = ("EXP-001", "EXP-002", "EXP-003")
RESULT_FILES = [f"research/experiments/{e}/{n}" for e in EXPS
                for n in ("summary.json", "metrics.csv", "arm_summary.csv", "config.json")]
RESULT_FILES.append("results/exploratory/m4_audit_sensitivity.json")
RECORD_FILES = ["research/claims_register.csv", "research/publication/artifact_manifest.json",
                "research/experiment_registry.csv", "research/limitations.md", "research/paper/manuscript.md"]

CLASS_TEXT = {
    "detectable_practically_relevant": "detectable, practically relevant",
    "detectable_below_sesoi": "detectable, below the SESOI",
    "practically_equivalent": "practically equivalent",
    "inconclusive": "inconclusive",
}


class ExportError(RuntimeError):
    pass


def _load(rel: str):
    return json.loads((ROOT / rel).read_text())


def _csv(rel: str) -> list[dict]:
    with open(ROOT / rel, newline="") as f:
        return list(csv.DictReader(f))


def _sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def results_revision() -> str:
    out = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%H", "--", *RESULT_FILES],
                         capture_output=True, text=True, check=True).stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", out):
        raise ExportError("could not determine the commit of the committed results")
    return out


# Display formats (match the manuscript's printed precision).
def sgn(x: float, nd: int) -> str:
    return f"{x:+,.{nd}f}"


def ivl(lo: float, hi: float, nd: int) -> str:
    return f"[{lo:,.{nd}f}, {hi:,.{nd}f}]"


def pct(x: float, nd: int = 2) -> str:
    return f"{x * 100:+.{nd}f}%"


def est(label, value, lo, hi, level, unit, nd, *, group="", relative=None, cls=None, display=None, interval=None,
        kind="measured") -> dict:
    return {
        "label": label, "estimate": float(value),
        "ci_low": None if lo is None else float(lo), "ci_high": None if hi is None else float(hi),
        "ci_level": level if lo is not None else None, "unit": unit,
        "display": display if display is not None else sgn(value, nd),
        "interval_display": interval if interval is not None else (None if lo is None else ivl(lo, hi, nd)),
        "group": group,
        "relative_display": None if relative is None else pct(relative),
        "class_display": None if cls is None else CLASS_TEXT[cls],
        "kind": kind,
    }


def claims_for(prefix_ids: list[str]) -> list[str]:
    ids = {r["claim_id"] for r in _csv("research/claims_register.csv")}
    missing = [c for c in prefix_ids if c not in ids]
    if missing:
        raise ExportError(f"claim ids not in the claims register: {missing}")
    return prefix_ids


def contrast(rows: list[dict], cell: str, arm: str, comp: str, metric: str) -> dict:
    hit = [r for r in rows if r["cell_id"] == cell and r["arm"] == arm and r["comparator"] == comp
           and r["metric"] == metric]
    if len(hit) != 1:
        raise ExportError(f"expected one contrast for {cell} {arm}-{comp} {metric}, found {len(hit)}")
    r = hit[0]
    return {k: (float(r[k]) if k in ("mean_diff", "boot_lo", "boot_hi", "relative_effect", "level") else r[k])
            for k in r}


def exp001() -> dict:
    s = _load("research/experiments/EXP-001/summary.json")
    rows = _csv("research/experiments/EXP-001/metrics.csv")
    ests = []
    for arm, comp in (("OCC", "FIX"), ("DRP", "FIX"), ("OCC", "FIX6"), ("DRP", "FIX6")):
        c = contrast(rows, "base", arm, comp, "revenue")
        ests.append(est(f"{arm} - {comp}", c["mean_diff"], c["boot_lo"], c["boot_hi"], c["level"],
                        "currency units per season", 2, group="Revenue (primary, 97.5% paired bootstrap)",
                        relative=c["relative_effect"], cls=c["classification"]))
    for metric, nd, name in (("sell_through", 3, "Sell-through"), ("availability", 3, "Availability"),
                             ("consumer_surplus", 1, "Consumer surplus proxy")):
        for arm in ("OCC", "DRP"):
            c = contrast(rows, "base", arm, "FIX", metric)
            unit = "currency units per season" if metric == "consumer_surplus" else "share (0 to 1)"
            ests.append(est(f"{name}, {arm} - FIX", c["mean_diff"], c["boot_lo"], c["boot_hi"], c["level"], unit,
                            nd, group="Secondary metrics (descriptive, 95%, unadjusted)"))
    v = s["verdict"]
    if not (v["OCC"]["reject_h0"] and v["DRP"]["reject_h0"]):
        raise ExportError("EXP-001 verdict differs from the manuscript")
    gs = [v[a]["grid_sensitivity"]["attributed_to_grid_resolution"] for a in ("OCC", "DRP")]
    verdict = ("H0 rejected for OCC and for DRP: both Bonferroni-adjusted 97.5% paired bootstrap intervals exclude 0, "
               "and both effects are detectable and practically relevant (SESOI 1% of FIX* revenue). "
               + ("The FIX6 sensitivity changes neither sign nor class, so the result is not attributed to grid "
                  "resolution (a one-sided check)." if not any(gs) else "The FIX6 sensitivity attributes the "
                  "result to grid resolution."))
    pols = {t["arm"]: t["selected"] for t in s["tuning"]}
    return {
        "id": "EXP-001", "title": "Tuned occupancy and demand-responsive rules versus the best fixed price, base scenario",
        "status": "confirmatory, complete (frozen v1.0; 73,000 runs, 0 failed)", "verdict": verdict,
        "estimates": ests, "claim_ids": claims_for(["C-001", "C-002", "C-003", "C-014"]),
        "report_path": "research/experiments/EXP-001/report.md",
        "notes": [
            f"Selected policies: FIX(p = {pols['FIX']['params']['p']:.2f}), OCC(p0 = {pols['OCC']['params']['p0']:.2f}, "
            f"k = {pols['OCC']['params']['k']:g}), DRP(p0 = {pols['DRP']['params']['p0']:.2f}, "
            f"eta = {pols['DRP']['params']['eta']:g}); no tuned configuration lies on a grid edge.",
            "n = 4,000 paired evaluation streams per contrast. Paired t intervals agree with the bootstrap intervals "
            "(manuscript Table 2).",
            "FIX6 is FIX re-tuned on the 6 starting prices available to the rules. It is a weaker comparator by "
            "construction, so this check can only fail in one direction.",
        ],
    }


def exp002() -> dict:
    s = _load("research/experiments/EXP-002/summary.json")
    rows = _csv("research/experiments/EXP-002/metrics.csv")
    audit = {r["cell_id"]: r for r in
             _load("results/exploratory/m4_audit_sensitivity.json")["audit"]["EXP-002_elasticity"]["rows"]}
    arms = {(a["cell_id"], a["arm"]): a for a in s["arm_summary"]}
    edges = {(t["cell_id"], t["arm"]): t["at_grid_edge"] for t in s["tuning"]}
    cells = list(dict.fromkeys(a["cell_id"] for a in s["arm_summary"]))
    ests = []
    for cid in cells:
        for arm in ("OCC", "DRP"):
            c = contrast(rows, cid, arm, "FIX", "revenue")
            e = est(f"{cid}: {arm} - FIX", c["mean_diff"], c["boot_lo"], c["boot_hi"], c["level"],
                    "currency units per season", 1, group=cid, relative=c["relative_effect"], cls=c["classification"])
            if edges[(cid, arm)]:
                e["class_display"] += " (tuned optimum on a grid edge)"
            ests.append(e)
    for cid in cells:
        el = audit[cid]["elasticity_printed_raw_report"]
        ests.append(est(f"{cid}: purchase elasticity at the tuned FIX price", el, None, None, None, "dimensionless",
                        3, group="Elasticity at the tuned fixed price", display=f"{el:.3f}"))
        fr = arms[(cid, "FIX")]["revenue_mean"]
        ests.append(est(f"{cid}: FIX* mean revenue", fr, None, None, None, "currency units per season", 1,
                        group="FIX* mean revenue", display=f"{fr:,.1f}"))
    for it in s["verdict"]["interactions"]:
        ests.append(est(f"sigma_v = {it['sigma_v']:g}: {it['arm']} interaction", it["estimate"], it["lo"], it["hi"],
                        it["level"], "currency units per season", 1,
                        group="Interaction Delta(kappa = 4.0) - Delta(kappa = 1.0) (descriptive, 95%)"))
    vc = s["verdict"]["contrasts"]
    neg = sum(1 for c in vc if c["mean_diff"] < 0)
    rej = sum(1 for c in vc if c["reject_h0_at_0.05"])
    verdict = (f"{rej} of {len(vc)} contrasts reject H0 after Holm adjustment (family-wise alpha 0.05); "
               f"the directions are mixed: {neg} negative and {len(vc) - neg} positive. The sign is cell-specific: "
               "the rules lose in every loose-capacity cell (kappa = 1.0) and in sv1.0-k2.0.")
    return {
        "id": "EXP-002", "title": "Sensitivity to price elasticity and demand-to-capacity tightness",
        "status": "confirmatory, complete (frozen v1.0; 594,000 runs, 0 failed)", "verdict": verdict,
        "estimates": ests, "claim_ids": claims_for(["C-004", "C-005", "C-006", "C-012", "C-015"]),
        "report_path": "research/experiments/EXP-002/report.md",
        "notes": [
            "Cells: sv = valuation dispersion sigma_v, k = expected arrivals to capacity kappa; FIX re-tuned in every "
            "cell; n = 4,000 paired streams per cell; paired bootstrap 95% intervals.",
            "Every raw sign-flip p-value is at the permutation floor 1/10001, so every Holm value (0.0018) is a bound.",
            "8 of the 18 rule selections lie on a grid edge; under the frozen reading an upper edge may understate the "
            "rule, and the DRP lower edge does not keep prices near p0 (claim C-012).",
            "Interaction contrasts use an independent stratified bootstrap and are descriptive.",
        ],
    }


def exp003() -> dict:
    s = _load("research/experiments/EXP-003/summary.json")
    rows = _csv("research/experiments/EXP-003/metrics.csv")
    cells = [c for c in dict.fromkeys(a["cell_id"] for a in s["arm_summary"])]
    ests = []
    for cid in cells:
        for comp, name in (("FIX", "base-tuned FIX"), ("FIX_retuned", "FIX re-tuned in the cell")):
            for arm in ("OCC", "DRP"):
                c = contrast(rows, cid, arm, comp, "revenue")
                ests.append(est(f"{cid}: {arm} - {name}", c["mean_diff"], c["boot_lo"], c["boot_hi"], c["level"],
                                "currency units per season", 1, group=cid, relative=c["relative_effect"],
                                cls=c["classification"]))
    v = s["verdict"]
    trig = [a for a in ("OCC", "DRP") if v[a]["specific_to_correct_specification"]]
    verdict = ("The pre-specified invalidation rule is not triggered for OCC or DRP: at demand x0.8 and x1.25 every "
               "95% interval of the contrast against the base-tuned FIX lies above 0, the same side as EXP-001."
               if not trig else f"The invalidation rule is triggered for {', '.join(trig)}.")
    return {
        "id": "EXP-003", "title": "Robustness of the base comparison to demand misspecification",
        "status": "confirmatory, complete (frozen v1.0; 258,000 runs, 0 failed)", "verdict": verdict,
        "estimates": ests, "claim_ids": claims_for(["C-007", "C-008", "C-013"]),
        "report_path": "research/experiments/EXP-003/report.md",
        "notes": [
            "The policies tuned at the base cell are evaluated without re-tuning; a FIX re-tuned on each cell's own "
            "tuning streams separates the cost of misspecification from policy structure. Paired bootstrap 95% "
            "intervals, n = 4,000 per cell, descriptive.",
            "In the reversed-arrivals cell the re-tuned fixed price is the base price, so the two comparisons coincide.",
            "The invalidation rule compares the rules with an equally misspecified fixed price; it is weaker than a "
            "test of structural advantage.",
        ],
    }


def exploratory(exceptions: list[dict]) -> list[dict]:
    ex = _load("results/exploratory/m4_audit_sensitivity.json")["exploratory"]
    b1 = next(r for r in ex["B1_tuning_decomposition"]["rows"] if r["experiment"] == "EXP-001")
    b1e = []
    for part, name in (("price_resolution_part", "price-resolution part"), ("responsiveness_part", "responsiveness part")):
        for arm in ("OCC", "DRP"):
            b1e.append(est(f"{arm} {name}", b1[arm][part], None, None, None, "currency units per season", 1,
                           group="Base cell, tuning streams (in-sample)", kind="exploratory"))
    b2 = ex["B2_internal_replication"]["arms"]
    b2e = [est(f"{arm}: EXP-002 sv0.5-k2.0 minus EXP-001", b2[arm]["difference"], *b2[arm]["normal_95"], 0.95,
               "currency units per season", 1, group="Difference of mean paired differences (normal 95%)",
               kind="exploratory") for arm in ("OCC", "DRP")]
    b3e = []
    for r in ex["B3_distribution"]["rows"]:
        if r["experiment"] != "EXP-001":
            continue
        share = r["share_rule_loses"] * 100
        txt = f"{share:.3f}".rstrip("0").rstrip(".") + "%"
        b3e.append(est(f"{r['arm']}: share of streams where the rule loses", share, None, None, None, "% of streams", 3,
                       group="Base cell, 4,000 evaluation streams", display=txt, kind="exploratory"))
        for i, t in enumerate(r["arrivals_terciles"], 1):
            lab = f"{r['arm']}: tercile {i} of realised arrivals, mean paired difference"
            e = est(lab, t["mean_diff"], t["t95"][0], t["t95"][1], 0.95, "currency units per season", 1,
                    group="Base cell, by tercile of realised arrivals (paired t 95%)", kind="exploratory")
            exceptions.append({"experiment": "J-0012", "label": lab, "field": "interval_display",
                               "value": e["interval_display"],
                               "note": "The manuscript prints the tercile means without intervals; this interval is "
                                       "the t95 value of results/exploratory/m4_audit_sensitivity.json (B3), rounded "
                                       "to 1 decimal."})
            b3e.append(e)
    b4 = [r for r in ex["B4_tuning_optimism"]["rows"] if r["experiment"] == "EXP-001" and r["arm"] in ("FIX", "OCC", "DRP")]
    b4e = [est(f"{r['arm']}: evaluation minus tuning mean revenue", r["eval_minus_tuning"], None, None, None,
               "currency units per season", 1, group="Base cell, selected configuration", kind="exploratory")
           for r in b4]
    common = "Exploratory and post hoc (journal J-0012); no simulation was run; not evidence for any preregistered hypothesis."
    return [
        {"id": "B1", "title": "Tuning-stream decomposition (in-sample)", "status": "exploratory check",
         "verdict": "Qualifies the EXP-001 gain: the rules gain despite a coarser starting-price grid.",
         "estimates": b1e, "claim_ids": claims_for(["C-011"]),
         "report_path": "results/exploratory/m4_audit_sensitivity.json", "notes": [common, "In-sample on the 500 tuning streams; no interval is defined."]},
        {"id": "B2", "title": "Internal replication of EXP-001 by EXP-002 sv0.5-k2.0", "status": "exploratory check",
         "verdict": "Both intervals include 0: the base cell replicates on independent streams.",
         "estimates": b2e, "claim_ids": claims_for(["C-009"]),
         "report_path": "results/exploratory/m4_audit_sensitivity.json", "notes": [common]},
        {"id": "B3", "title": "Distribution of the base-cell gain", "status": "exploratory check",
         "verdict": "The rules lose on about a third of streams; most of the mean gain arises in high-demand streams.",
         "estimates": b3e, "claim_ids": claims_for(["C-010"]),
         "report_path": "results/exploratory/m4_audit_sensitivity.json", "notes": [common]},
        {"id": "B4", "title": "Tuning optimism", "status": "exploratory check",
         "verdict": "Small relative to the effects; evaluation streams are held out.",
         "estimates": b4e, "claim_ids": [],
         "report_path": "results/exploratory/m4_audit_sensitivity.json", "notes": [common, "Differences of two means; no interval is defined."]},
    ]


def _figure_path(exp: str, cid: str) -> str:
    return f"research/experiments/{exp}/figures/fig-{exp}-{cid}-price.svg"


def price_paths_and_cells() -> tuple[list[dict], list[dict]]:
    paths, cells = [], []
    for exp in EXPS:
        cfg = _load(f"research/experiments/{exp}/config.json")
        s = _load(f"research/experiments/{exp}/summary.json")
        base = ScenarioParams.from_dict(cfg.get("base_scenario", {}))
        tuned: dict[str, dict[str, dict]] = {}
        for t in s["tuning"]:
            tuned.setdefault(t["cell_id"], {})[t["arm"]] = t["selected"]
        arm_order: dict[str, list[str]] = {}
        for a in s["arm_summary"]:
            arm_order.setdefault(a["cell_id"], []).append(a["arm"])
        for cell in cfg["cells"]:
            cid = cell["id"]
            sp = base.with_(**cell.get("scenario", {}))
            pols = dict(tuned.get(cell.get("tune_in", cid), {}))
            pols.update({k: v for k, v in tuned.get(cid, {}).items() if k not in pols or k.startswith("FIX_")})
            if cid not in arm_order:  # tuning-only cell (EXP-003 base-tuning): no evaluation, no figure
                continue
            cells.append({"experiment": exp, "cell_id": cid, "scenario": cell.get("scenario", {}),
                          "policies": {a: pols[a] for a in arm_order[cid]}})
            key = SeedKey(int(cfg["experiment_number"]), int(cell["index"]), ROLE_EVAL, int(cfg["eval_streams"]["start"]))
            stream = generate_stream(sp, key)
            runs, arms = [], []
            for arm in arm_order[cid]:
                pol = pols[arm]
                o = simulate(stream, sp, policy_from_dict(pol))
                runs.append({"status": "ok", "stream_index": key.index, "arm": arm, "seed_key": list(key.as_tuple()),
                             "stream_sha256": stream.sha256(), "policy": pol, "metrics": {"revenue": o.revenue},
                             "run_id": f"{exp}/{cid}/{arm}/eval{key.index:04d}"})
                arms.append({"arm": arm, "policy": pol, "prices": [round(float(p), 4) for p in o.prices]})
            svg = price_path_svg({"runs": runs, "scenario": sp.to_dict()}, f"{exp} {cid}")
            fig = _figure_path(exp, cid)
            if svg != (ROOT / fig).read_text():
                raise ExportError(f"re-simulated price paths do not reproduce the committed figure {fig}")
            paths.append({"experiment": exp, "cell_id": cid, "stream": f"evaluation stream {key.index}",
                          "figure_path": fig, "figure_sha256": _sha(fig), "T": sp.T, "p_min": sp.p_min,
                          "p_max": sp.p_max, "arms": arms})
    return paths, cells


def assumptions() -> list[dict]:
    sp = ScenarioParams()
    src = "research/protocol.md section 3 (frozen v1.0); manuscript Table 1"
    rows = [
        ("Selling horizon", f"T = {sp.T} periods"),
        ("Initial stock", f"C = {sp.C} units; unsold units perish with zero salvage"),
        ("Expected arrivals to capacity (base)", f"kappa = {sp.kappa:g}"),
        ("Buyer segments", f"L (share {sp.w_L:g}, median valuation {sp.m_L:g}, arrives early) and H (share "
                           f"{1 - sp.w_L:g}, median valuation {sp.m_H:g}, arrives late)"),
        ("Valuation dispersion (base)", f"sigma_v = {sp.sigma_v:g} (log-normal valuations)"),
        ("Stream shock dispersion", f"sigma_M = {sp.sigma_M:g} (log-normal multiplier with mean 1)"),
        ("Demand surges", f"start probability {sp.surge_prob:g} per period, length {sp.surge_len} periods, "
                          f"factor {sp.surge_factor:g}, non-compounding"),
        ("Price bounds", f"[{sp.p_min:g}, {sp.p_max:g}] currency units"),
        ("Buyer behaviour", "myopic, unit demand: a buyer buys if valuation >= price and stock remains, otherwise "
                            "leaves for good"),
        ("Tuning budget", "36 configurations per family on the same 500 tuning streams; 4,000 disjoint evaluation "
                          "streams per cell"),
        ("Currency", "abstract currency units; no real prices, fares or markets"),
    ]
    return [{"name": n, "value": v, "source": src} for n, v in rows]


def limitations() -> list[str]:
    items = []
    for line in (ROOT / "research/limitations.md").read_text().splitlines():
        m = re.match(r"^\d+\.\s+(.*)$", line)
        if m:
            items.append(m.group(1).replace("**", "").replace("`", ""))
    if len(items) < 10:
        raise ExportError("limitations list unexpectedly short")
    return items


def check_displays(doc: dict) -> None:
    text = MANUSCRIPT.read_text()
    exc = {(e["label"], e["field"], e["value"]) for e in doc["display_exceptions"]}
    missing = []
    for group in ("experiments", "exploratory_checks"):
        for e in doc[group]:
            for x in e["estimates"]:
                for field in ("display", "interval_display", "relative_display"):
                    v = x.get(field)
                    if v is None or (x["label"], field, v) in exc:
                        continue
                    if v not in text:
                        missing.append(f"{e['id']} {x['label']} {field}={v!r}")
    if missing:
        raise ExportError("display strings not printed in the manuscript:\n  " + "\n  ".join(missing))


def build() -> dict:
    exceptions: list[dict] = []
    experiments = [exp001(), exp002(), exp003()]
    registry = [r["exp_id"] for r in _csv("research/experiment_registry.csv")]
    if [e["id"] for e in experiments] != registry:
        raise ExportError(f"exported experiments {[e['id'] for e in experiments]} differ from the registry {registry}")
    expl = exploratory(exceptions)
    paths, cells = price_paths_and_cells()
    sources = sorted(set(RESULT_FILES + RECORD_FILES + [p["figure_path"] for p in paths]))
    doc = {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "FARE",
        "question": "How do demand and inventory policies affect prices and availability in a simulated market?",
        "status_label": ("Simulation study. Preprint draft, not peer-reviewed. The frozen confirmatory matrix ran in "
                         "full (925,000 simulated seasons, 0 failed). The owner's full-text review of the manuscript "
                         "is pending (M6). Nothing here describes any real seller, fare or pricing system."),
        "code_revision": results_revision(),
        "sources": [{"path": p, "sha256": _sha(p)} for p in sources],
        "experiments": experiments,
        "assumptions": assumptions(),
        "limitations": limitations(),
        "exploratory_checks": expl,
        "price_paths": paths,
        "cells": cells,
        "display_exceptions": exceptions,
    }
    check_displays(doc)
    return doc


def render(doc: dict) -> str:
    return json.dumps(doc, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text() == text
        print("results.json is up to date" if same else "results.json differs from a fresh export")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
