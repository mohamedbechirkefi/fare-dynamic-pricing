# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Frozen-analysis summaries (fare.summary) on tiny exploratory runs."""

import copy
import json

from fare import cli
from fare.summary import summarise_result, verdict_exp001, verdict_exp003

TINY = {
    "experiment_id": "EXP-001", "experiment_number": 1, "label": "exploratory", "mode": "tuned",
    "base_scenario": {"T": 20, "C": 20},
    "grid": {"p0_n": 6, "occ_k": [0.25, 0.5, 1.0, 2.0, 4.0, 8.0], "drp_eta": [0.025, 0.05, 0.1, 0.25, 0.5, 1.0]},
    "cells": [{"id": "base", "index": 0, "scenario": {}}],
    "tune_streams": {"role": 0, "start": 0, "count": 2},
    "eval_streams": {"role": 0, "start": 2, "count": 6},
    "fix_coarse_sensitivity": True,
    "bootstrap": {"resamples": 200, "seed": 1, "primary_level": 0.975, "secondary_level": 0.95},
}


def _run(tmp_path, cfg):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(cfg))
    return cli.execute(p, tmp_path / "out", ["test"])


def test_summary_exp001_counts_files_and_verdict(tmp_path):
    res = _run(tmp_path, copy.deepcopy(TINY))
    s = summarise_result(res, tmp_path / "sum")
    assert s["counts"]["eval_runs"] == 4 * 6 and s["counts"]["failed_runs"] == 0
    assert {r["arm"] for r in s["arm_summary"]} == {"FIX", "OCC", "DRP", "FIX6"}
    assert all(r["n_ok"] == 6 for r in s["arm_summary"])
    v = s["verdict"]
    for j in ("OCC", "DRP"):
        lo, hi = v[j]["boot_ci_97_5"]
        assert v[j]["reject_h0"] == (lo > 0 or hi < 0)
        assert v[j]["grid_sensitivity"] is not None
    paths = {f["path"] for f in s["raw_manifest"]["files"]}
    assert {"result.json", "run_manifest.json", "config.json"} <= paths
    assert (tmp_path / "sum" / "metrics.csv").read_text().count("\n") == 1 + len(s["contrasts"])
    assert (tmp_path / "sum" / "figures" / "fig-EXP-001-forest-revenue.svg").exists()
    json.loads((tmp_path / "sum" / "summary.json").read_text())


def _k(cell, arm, comp, m, lo, hi, cls="x"):
    return {"cell_id": cell, "arm": arm, "comparator": comp, "metric": "revenue", "mean_diff": m, "boot_lo": lo,
            "boot_hi": hi, "t_lo": lo, "t_hi": hi, "relative_effect": m / 1000, "n": 10, "classification": cls}


def test_verdict_rules_on_constructed_contrasts():
    c = [_k("base", "OCC", "FIX", 50, 10, 90, "a"), _k("base", "OCC", "FIX6", -5, -20, 10, "b"),
         _k("base", "DRP", "FIX", 5, -10, 20, "c"), _k("base", "DRP", "FIX6", 5, -10, 20, "c")]
    v = verdict_exp001(c)
    assert v["OCC"]["reject_h0"] and v["OCC"]["grid_sensitivity"]["attributed_to_grid_resolution"]
    assert not v["DRP"]["reject_h0"] and not v["DRP"]["grid_sensitivity"]["attributed_to_grid_resolution"]
    c3 = [_k("demand-x0.8", "OCC", "FIX", -30, -50, -10), _k("demand-x1.25", "OCC", "FIX", 10, -5, 25),
          _k("demand-x0.8", "DRP", "FIX", -30, -50, -10), _k("demand-x1.25", "DRP", "FIX", 10, -5, 25)]
    v3 = verdict_exp003(c3, v)
    assert v3["OCC"]["specific_to_correct_specification"] is True
    assert v3["DRP"]["status"] == "descriptive only"
