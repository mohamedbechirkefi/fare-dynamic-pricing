# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""EXPLORATORY: summarise the pre-freeze smoke and pilot result files.

Reports what the owner needs before the freeze: runtime per run, projected
full-matrix runtime, the spread of paired differences between streams and the
implied sample size for the draft SESOI, grid-edge optima and degenerate cells.
Not evidence; never reported as a finding.

    PYTHONPATH=src uv run python experiments/exploratory/pilot_summary.py <result.json>... > summary.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from fare.cli import _load
from fare.manifest import REPO_ROOT
from fare.runner import planned_run_counts
from fare.schema import read_result
from fare.stats import required_n

ALPHA, POWERS = 0.025, (0.8, 0.89)


def summarise(path: Path) -> dict:
    doc = read_result(path)
    out = {"run_set_id": doc["run_set_id"], "label": doc["label"], "experiment_id": doc["experiment_id"],
           "failures": doc["failures"], "cells": []}
    tune_s = sum(c["timing"]["tuning_s"] for c in doc["cells"])
    tune_n = sum(c["timing"]["tuning_runs"] for c in doc["cells"])
    eval_s = sum(c["timing"]["eval_s"] for c in doc["cells"])
    eval_n = sum(c["timing"]["eval_runs"] for c in doc["cells"])
    gen_s = sum(c["timing"]["stream_generation_s"] for c in doc["cells"])
    man = json.loads((path.parent / doc["manifest_path"]).read_text())
    out["timing"] = {"wall_s": man["runtime_s"], "peak_rss_mib": man["peak_rss_bytes"] / 2**20,
                     "tuning_ms_per_run": 1e3 * tune_s / tune_n if tune_n else None,
                     "eval_ms_per_run_incl_metrics": 1e3 * eval_s / eval_n if eval_n else None,
                     "stream_generation_s": gen_s, "tuning_runs": tune_n, "eval_runs": eval_n}
    for c in doc["cells"]:
        cell = {"cell_id": c["cell_id"], "grid_edge_optima": [
            {"arm": t["arm"], "selected": t["selected"]} for t in c["tuning"] if t["at_grid_edge"]]}
        fix = {r["stream_index"]: r["metrics"] for r in c["runs"] if r["arm"] == "FIX" and r["status"] == "ok"}
        if fix:
            rev = np.array([m["revenue"] for m in fix.values()])
            cell["FIX_revenue_mean"] = float(rev.mean())
            cell["FIX_revenue_sd_between_streams"] = float(rev.std(ddof=1)) if len(rev) > 1 else None
            cell["FIX_sell_through_mean"] = float(np.mean([m["sell_through"] for m in fix.values()]))
            cell["FIX_share_streams_sold_out"] = float(np.mean([m["units_sold"] == round(m["sell_through"] * c["scenario"]["C"]) and m["sell_through"] == 1.0 for m in fix.values()]))
        arms = {}
        for r in c["runs"]:
            if r["status"] == "ok":
                arms.setdefault(r["arm"], []).append(r["metrics"])
        cell["arm_spread"] = {a: {"n": len(ms), "revenue_mean": float(np.mean([m["revenue"] for m in ms])),
                                  "revenue_sd": float(np.std([m["revenue"] for m in ms], ddof=1)) if len(ms) > 1 else None,
                                  "sell_through_mean": float(np.mean([m["sell_through"] for m in ms])),
                                  "price_volatility_mean": float(np.mean([m["price_volatility"] for m in ms]))}
                              for a, ms in arms.items()}
        cell["paired_revenue"] = []
        for k in c["contrasts"]:
            if k["metric"] != "revenue" or k["comparator"] != "FIX":
                continue
            entry = {"arm": k["arm"], "n": k["n"], "sd_diff": k["sd_diff"], "abs_d_z": abs(k["d_z"]) if k["d_z"] is not None else None,
                     "degenerate_all_zero": k["sd_diff"] == 0.0 and k["mean_diff"] == 0.0}
            if fix and k["sd_diff"] > 0:
                ses = 0.01 * cell["FIX_revenue_mean"]
                entry["sesoi_abs"] = ses
                entry["required_n_for_sesoi"] = {str(p): required_n(k["sd_diff"], ses, ALPHA, p) for p in POWERS}
            cell["paired_revenue"].append(entry)
        out["cells"].append(cell)
    return out


def projection(per_run_ms: float) -> dict:
    res = {}
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        cfg = _load(REPO_ROOT / "research" / "experiments" / exp / "config.json")
        n = planned_run_counts(cfg)
        res[exp] = {**n, "projected_simulation_s": n["total_runs"] * per_run_ms / 1e3}
    res["all"] = {"total_runs": sum(v["total_runs"] for v in res.values()),
                  "projected_simulation_s": sum(v["projected_simulation_s"] for v in res.values())}
    return res


def main(paths: list[str]) -> None:
    sums = [summarise(Path(p)) for p in paths]
    rates = [(s["timing"]["tuning_ms_per_run"], s["timing"]["tuning_runs"]) for s in sums if s["timing"]["tuning_ms_per_run"]]
    per_run = sum(r * n for r, n in rates) / sum(n for _, n in rates) if rates else None
    total_wall = sum(s["timing"]["wall_s"] for s in sums)
    total_runs = sum(s["timing"]["tuning_runs"] + s["timing"]["eval_runs"] for s in sums)
    print(json.dumps({"label": "EXPLORATORY (pre-freeze; not evidence)", "results": sums,
                      "pooled_tuning_ms_per_run": per_run,
                      "pooled_wall_ms_per_run_all_inclusive": 1e3 * total_wall / total_runs,
                      "projection_from_tuning_rate": projection(per_run) if per_run else None,
                      "projection_all_inclusive": projection(1e3 * total_wall / total_runs)}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
