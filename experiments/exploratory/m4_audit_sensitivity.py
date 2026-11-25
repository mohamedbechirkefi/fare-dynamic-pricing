# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""M4 evidence audit and exploratory sensitivity checks (EXPLORATORY, journal J-0012).

    PYTHONPATH=src .venv/bin/python experiments/exploratory/m4_audit_sensitivity.py \
        > results/exploratory/m4_audit_sensitivity.json

No simulation is run and no stream is generated. Everything is read from the
committed summaries (research/experiments/EXP-NNN/) and from the git-ignored
raw confirmatory outputs (results/raw/confirmatory/<run_set_id>/result.json),
whose SHA-256 is first checked against the raw manifest in each summary.json.

Part A (audit) recomputes, independently of fare.summary, the per-arm means
and SDs and every committed contrast from the per-run metrics, and replays
the revenue bootstrap intervals with the frozen seed; it reports the largest
absolute discrepancy against the committed CSV files.

Part B (exploratory, never a verdict) computes:
  B1 a tuning-stream decomposition of each tuned dynamic rule's advantage into
     a price-resolution part (best of 36 fixed prices versus the fixed price at
     the rule's own p0) and a responsiveness part (rule versus that fixed
     price), from the per-configuration mean tuning revenues already recorded;
  B2 the internal replication of EXP-001 by the EXP-002 base-parameter cell
     (independent tuning and evaluation streams);
  B3 the per-stream distribution of paired revenue differences (share of
     streams where the rule loses, quantiles) and, at the EXP-001 base cell,
     the mean difference by tercile of realised arrivals (policy-independent);
  B4 tuning optimism: mean tuning revenue of the selected configuration versus
     its mean evaluation revenue.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

import re

from fare.metrics import purchase_elasticity
from fare.params import ScenarioParams
from fare.stats import bootstrap_ci, paired_t_ci

ROOT = Path(__file__).resolve().parents[2]
EXPS = ("EXP-001", "EXP-002", "EXP-003")
SEED = 20261124
SESOI = 0.01


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_csv(p: Path) -> list[dict]:
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def classify(lo: float, hi: float, est: float, sesoi: float) -> str:
    if lo > 0 or hi < 0:
        return "detectable_practically_relevant" if abs(est) > sesoi else "detectable_below_sesoi"
    if -sesoi < lo and hi < sesoi:
        return "practically_equivalent"
    return "inconclusive"


def vec(cell: dict, arm: str, metric: str) -> dict[int, float]:
    return {r["stream_index"]: r["metrics"][metric] for r in cell["runs"]
            if r["arm"] == arm and r["status"] == "ok" and r["metrics"][metric] is not None}


def main() -> None:
    out: dict = {"label": "exploratory", "journal": "J-0012", "simulated": True,
                 "note": "M4 audit and exploratory checks; reads committed summaries and raw confirmatory outputs; "
                         "no simulation, no stream generated; never changes a frozen verdict.",
                 "audit": {}, "exploratory": {}}
    docs = {}
    for e in EXPS:
        s = json.loads((ROOT / "research/experiments" / e / "summary.json").read_text())
        run_dir = ROOT / s["raw_manifest"]["run_dir"]
        files = []
        for f in s["raw_manifest"]["files"]:
            got = sha256(run_dir / f["path"])
            files.append({"path": f["path"], "match": got == f["sha256"]})
        doc = json.loads((run_dir / "result.json").read_text())
        docs[e] = (s, doc)

        # A1 arm summaries
        arm_rows = read_csv(ROOT / "research/experiments" / e / "arm_summary.csv")
        max_arm = 0.0
        n_checked = 0
        counts = {"runs": 0, "ok": 0, "failed": 0}
        for row in arm_rows:
            cell = next(c for c in doc["cells"] if c["cell_id"] == row["cell_id"])
            rs = [r for r in cell["runs"] if r["arm"] == row["arm"]]
            counts["runs"] += len(rs)
            counts["ok"] += sum(r["status"] == "ok" for r in rs)
            counts["failed"] += sum(r["status"] != "ok" for r in rs)
            assert int(row["n_runs"]) == len(rs)
            for m in ("revenue", "sell_through", "availability", "price_volatility", "consumer_surplus",
                      "total_surplus", "stockout_period", "mean_price_paid"):
                v = np.array([r["metrics"][m] for r in rs if r["status"] == "ok" and r["metrics"][m] is not None])
                for stat, val in (("mean", v.mean()), ("sd", v.std(ddof=1))):
                    ref = float(row[f"{m}_{stat}"])
                    max_arm = max(max_arm, abs(val - ref) / max(1.0, abs(ref)))
                    n_checked += 1
        # A2 contrasts
        met_rows = read_csv(ROOT / "research/experiments" / e / "metrics.csv")
        max_rel = 0.0
        boot_max = 0.0
        class_mismatch = []
        n_neg = n_pos = 0
        for row in met_rows:
            cell = next(c for c in doc["cells"] if c["cell_id"] == row["cell_id"])
            a, b = vec(cell, row["arm"], row["metric"]), vec(cell, row["comparator"], row["metric"])
            common = sorted(set(a) & set(b))
            d = np.array([a[i] - b[i] for i in common])
            base = float(np.mean([b[i] for i in common]))
            level = float(row["level"])
            tl, th = paired_t_ci(d, level)
            checks = {"n": (len(d), float(row["n"])), "mean_diff": (d.mean(), float(row["mean_diff"])),
                      "sd_diff": (d.std(ddof=1), float(row["sd_diff"])), "t_lo": (tl, float(row["t_lo"])),
                      "t_hi": (th, float(row["t_hi"]))}
            if row["relative_effect"]:
                checks["relative_effect"] = (d.mean() / base, float(row["relative_effect"]))
            for got, ref in checks.values():
                max_rel = max(max_rel, abs(got - ref) / max(1.0, abs(ref)))
            if row["metric"] == "revenue":
                lo, hi = bootstrap_ci(d, level, 10_000, SEED)
                boot_max = max(boot_max, abs(lo - float(row["boot_lo"])), abs(hi - float(row["boot_hi"])))
                cls = classify(float(row["boot_lo"]), float(row["boot_hi"]), float(row["mean_diff"]), SESOI * base)
                if cls != row["classification"]:
                    class_mismatch.append([row["cell_id"], row["arm"], row["comparator"], cls, row["classification"]])
                if row["comparator"] == "FIX":
                    if float(row["boot_hi"]) < 0:
                        n_neg += 1
                    elif float(row["boot_lo"]) > 0:
                        n_pos += 1
        out["audit"][e] = {
            "raw_files_hash_match": all(f["match"] for f in files), "raw_files_checked": len(files),
            "total_runs_tuning_plus_eval": s["counts"]["tuning_runs"] + s["counts"]["eval_runs"],
            "raw_total_bytes": s["raw_manifest"]["total_bytes"],
            "raw_total_megabytes_decimal": s["raw_manifest"]["total_bytes"] / 1e6,
            "runs": counts, "arm_summary_values_checked": n_checked,
            "arm_summary_max_rel_discrepancy": max_arm,
            "contrast_rows_checked": len(met_rows), "contrast_max_rel_discrepancy": max_rel,
            "revenue_bootstrap_max_abs_discrepancy": boot_max,
            "classification_mismatches": class_mismatch,
            "revenue_vs_FIX_intervals_below_0": n_neg, "revenue_vs_FIX_intervals_above_0": n_pos,
        }

    out["audit"]["all_experiments_total_runs"] = sum(out["audit"][e]["total_runs_tuning_plus_eval"] for e in EXPS)

    # A3 EXP-002 purchase elasticity at the tuned FIX price: the value printed by the confirmatory
    # run's raw report (git-ignored) and its deterministic re-derivation from the scenario parameters
    s2, doc2 = docs["EXP-002"]
    rep = ROOT / s2["raw_manifest"]["run_dir"] / "report" / "report.md"
    printed = {}
    for line in rep.read_text().splitlines():
        m = re.match(r"\| FIX \| (sv[0-9.]+-k[0-9.]+) \| .* \| (-?[0-9.]+) \|$", line)
        if m:
            printed[m.group(1)] = float(m.group(2))
    el = []
    for cell in doc2["cells"]:
        t = next(x for x in cell["tuning"] if x["arm"] == "FIX")
        p = t["selected"]["params"]["p"]
        val = purchase_elasticity(ScenarioParams.from_dict(cell["scenario"]), p)
        el.append({"cell_id": cell["cell_id"], "sigma_v": cell["scenario"]["sigma_v"], "kappa": cell["scenario"]["kappa"],
                   "fix_price": p, "elasticity_printed_raw_report": printed.get(cell["cell_id"]),
                   "elasticity_rederived": val})
    out["audit"]["EXP-002_elasticity"] = {
        "definition": "point elasticity d ln P(v >= p) / d ln p of the segment-share-weighted purchase probability at "
                      "the tuned FIX price (EXP-002 protocol section 7; fare.metrics.purchase_elasticity)",
        "source": str(rep.relative_to(ROOT)), "source_sha256": sha256(rep), "rows": el}

    # B1 tuning-stream decomposition (in-sample on the 500 tuning streams)
    b1 = []
    for e in ("EXP-001", "EXP-002"):
        _, doc = docs[e]
        for cell in doc["cells"]:
            t = {x["arm"]: x for x in cell["tuning"]}
            fix_means = np.array(t["FIX"]["mean_revenue"])
            fix_prices = np.geomspace(40.0, 400.0, 36)
            p0s = np.geomspace(40.0, 400.0, 6)
            # the 6 p0 values are FIX grid indices 0, 7, 14, 21, 28, 35
            idx6 = [int(np.argmin(abs(fix_prices - p))) for p in p0s]
            assert np.allclose(fix_prices[idx6], p0s)
            fix_best = float(fix_means.max())
            row = {"experiment": e, "cell_id": cell["cell_id"], "FIX36_best": fix_best,
                   "FIX6_best": float(fix_means[idx6].max())}
            for fam in ("OCC", "DRP"):
                sel = t[fam]["selected"]["params"]
                p0 = sel["p0"]
                fix_at_p0 = float(fix_means[int(np.argmin(abs(fix_prices - p0)))])
                rule = float(t[fam]["mean_revenue"][t[fam]["selected_index"]])
                row[fam] = {"selected": sel, "tuning_mean": rule, "FIX_at_p0": fix_at_p0,
                            "advantage_vs_FIX36": rule - fix_best,
                            "price_resolution_part": fix_at_p0 - fix_best,
                            "responsiveness_part": rule - fix_at_p0}
            b1.append(row)
    out["exploratory"]["B1_tuning_decomposition"] = {
        "definition": "advantage_vs_FIX36 = price_resolution_part + responsiveness_part, where price_resolution_part "
                      "= mean tuning revenue of FIX at the rule's selected p0 minus the best of 36 FIX prices (<= 0), "
                      "and responsiveness_part = the rule minus FIX at its own p0. Tuning streams 0-499 (in-sample, "
                      "selection-biased upward for every family); exploratory.",
        "rows": b1}

    # B2 replication of EXP-001 by the EXP-002 base-parameter cell
    m1 = {(r["arm"]): r for r in read_csv(ROOT / "research/experiments/EXP-001/metrics.csv")
          if r["metric"] == "revenue" and r["comparator"] == "FIX"}
    m2 = {(r["arm"]): r for r in read_csv(ROOT / "research/experiments/EXP-002/metrics.csv")
          if r["metric"] == "revenue" and r["comparator"] == "FIX" and r["cell_id"] == "sv0.5-k2.0"}
    b2 = {}
    for arm in ("OCC", "DRP"):
        a, b = m1[arm], m2[arm]
        diff = float(b["mean_diff"]) - float(a["mean_diff"])
        se = math.sqrt(float(a["sd_diff"]) ** 2 / float(a["n"]) + float(b["sd_diff"]) ** 2 / float(b["n"]))
        b2[arm] = {"EXP-001": float(a["mean_diff"]), "EXP-002 sv0.5-k2.0": float(b["mean_diff"]),
                   "difference": diff, "normal_95": [diff - 1.959964 * se, diff + 1.959964 * se]}
    out["exploratory"]["B2_internal_replication"] = {
        "definition": "EXP-002 cell sv0.5-k2.0 has the base parameters and selects the same configurations as EXP-001 "
                      "on independent tuning and evaluation streams; difference of the two mean paired differences "
                      "with a normal 95% interval from the committed SDs (independent samples).",
        "arms": b2}

    # B3 distributions and arrivals terciles
    b3 = []
    for e in EXPS:
        _, doc = docs[e]
        for cell in doc["cells"]:
            fix = vec(cell, "FIX", "revenue")
            arr = vec(cell, "FIX", "arrivals")
            for arm in ("OCC", "DRP"):
                a = vec(cell, arm, "revenue")
                common = sorted(set(a) & set(fix))
                d = np.array([a[i] - fix[i] for i in common])
                if len(d) == 0:
                    continue  # EXP-003 base cell: tuning only, no evaluation runs
                row = {"experiment": e, "cell_id": cell["cell_id"], "arm": arm, "n": len(d),
                       "share_rule_loses": float((d < 0).mean()), "share_equal": float((d == 0).mean()),
                       "quantiles_5_25_50_75_95": [float(x) for x in np.quantile(d, [0.05, 0.25, 0.5, 0.75, 0.95])]}
                if e == "EXP-001":
                    ar = np.array([arr[i] for i in common])
                    so = vec(cell, "FIX", "stockout_period")
                    fix_sold_out = np.array([so[i] <= cell["scenario"]["T"] for i in common])
                    st_fix = vec(cell, "FIX", "sell_through")
                    st_arm = vec(cell, arm, "sell_through")
                    dst = np.array([st_arm[i] - st_fix[i] for i in common])
                    q1, q2 = np.quantile(ar, [1 / 3, 2 / 3])
                    groups = [ar <= q1, (ar > q1) & (ar <= q2), ar > q2]
                    row["arrivals_terciles"] = [
                        {"arrivals_range": [float(ar[g].min()), float(ar[g].max())], "n": int(g.sum()),
                         "mean_diff": float(d[g].mean()),
                         "share_FIX_sold_out": float(fix_sold_out[g].mean()),
                         "mean_sell_through_diff": float(dst[g].mean()),
                         "t95": list(paired_t_ci(d[g], 0.95))} for g in groups]
                b3.append(row)
    out["exploratory"]["B3_distribution"] = {
        "definition": "per-stream paired revenue difference rule minus FIX (base-tuned FIX in EXP-003); arrivals are "
                      "policy-independent (common random numbers); tercile intervals are paired t 95%, unadjusted; share_FIX_sold_out "
                      "is the share of streams in which FIX sold its last unit before the end of period T.",
        "rows": b3}

    # B4 tuning optimism
    b4 = []
    for e in EXPS:
        s, _ = docs[e]
        ev = {(r["cell_id"], r["arm"]): r["revenue_mean"] for r in s["arm_summary"]}
        for t in s["tuning"]:
            key = (t["cell_id"], t["arm"])
            if key in ev:
                b4.append({"experiment": e, "cell_id": t["cell_id"], "arm": t["arm"],
                           "tuning_mean": t["selected_mean_tuning_revenue"], "eval_mean": ev[key],
                           "eval_minus_tuning": ev[key] - t["selected_mean_tuning_revenue"]})
    out["exploratory"]["B4_tuning_optimism"] = {
        "definition": "mean evaluation revenue minus mean tuning revenue of the selected configuration, same cell "
                      "(EXP-003 base-tuned arms are tuned in the base cell, so only re-tuned FIX rows are like-for-like).",
        "rows": b4}
    json.dump(out, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
