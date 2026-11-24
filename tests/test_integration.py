# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Config-to-results integration, schema, manifest, freeze guard and report."""

import copy
import json
from pathlib import Path

import pytest

from fare import cli
from fare.manifest import REPO_ROOT, protocol_status, sha256_file
from fare.report import ReportError, build_report
from fare.runner import ConfigError, ProtocolNotFrozen, planned_run_counts, run_experiment, validate_config
from fare.schema import ResultValidationError, read_result, validate_result

TINY = {
    "experiment_id": "EXP-001", "experiment_number": 1, "label": "exploratory", "mode": "tuned",
    "base_scenario": {"T": 20, "C": 20},
    "cells": [{"id": "base", "index": 0, "scenario": {}}],
    "tune_streams": {"role": 0, "start": 0, "count": 2},
    "eval_streams": {"role": 0, "start": 2, "count": 4},
    "fix_coarse_sensitivity": True,
    "bootstrap": {"resamples": 200, "seed": 1},
}
UNFROZEN = {"path": "x", "sha256": None, "frozen": False}


def _cfg(**kw):
    c = copy.deepcopy(TINY)
    c.update(kw)
    return c


def test_tiny_tuned_run_is_deterministic_and_complete():
    a = run_experiment(_cfg(), UNFROZEN, "rs")
    b = run_experiment(_cfg(), UNFROZEN, "rs")
    strip = lambda body: [[{k: v for k, v in r.items()} for r in c["runs"]] for c in body["cells"]]
    assert strip(a) == strip(b)
    cell = a["cells"][0]
    assert {t["arm"] for t in cell["tuning"]} == {"FIX", "OCC", "DRP", "FIX9"}
    assert len(cell["runs"]) == 4 * 4 and a["failures"] == 0
    assert cell["timing"]["tuning_runs"] == 3 * 36 * 2 + 9 * 2
    arms = {(k["arm"], k["comparator"], k["metric"]) for k in cell["contrasts"]}
    assert ("OCC", "FIX", "revenue") in arms and ("DRP", "FIX9", "revenue") in arms
    assert planned_run_counts(_cfg())["total_runs"] == cell["timing"]["tuning_runs"] + len(cell["runs"])


def test_misspecified_cells_reuse_tuning():
    cfg = _cfg(fix_coarse_sensitivity=False, cells=[
        {"id": "base", "index": 0, "scenario": {}, "evaluate": False},
        {"id": "low", "index": 1, "scenario": {"demand_scale": 0.6}, "tune_in": "base", "retuned_fix_reference": True},
    ])
    body = run_experiment(cfg, UNFROZEN, "rs")
    base, low = body["cells"]
    assert base["runs"] == []
    sel = {t["arm"]: t["selected"] for t in base["tuning"]}
    used = {r["arm"]: r["policy"] for r in low["runs"]}
    for fam in ("FIX", "OCC", "DRP"):
        assert used[fam] == sel[fam]
    assert "FIX_retuned" in used
    assert planned_run_counts(cfg)["total_runs"] == sum(c["timing"]["tuning_runs"] + len(c["runs"]) for c in body["cells"])


@pytest.mark.parametrize("mutate,exc", [
    (lambda c: c.update(label="confirmatory"), ProtocolNotFrozen),
    (lambda c: c.update(eval_streams={"role": 1, "start": 0, "count": 3}), ConfigError),
    (lambda c: c.update(eval_streams={"role": 0, "start": 1, "count": 3}), ConfigError),
    (lambda c: c.pop("cells"), ConfigError),
    (lambda c: c.update(mode="optimal"), ConfigError),
    (lambda c: c.update(cells=[{"id": "a", "index": 0}, {"id": "a", "index": 1}]), ConfigError),
])
def test_config_guards(mutate, exc):
    c = _cfg()
    mutate(c)
    with pytest.raises(exc):
        validate_config(c, UNFROZEN)


def test_real_registry_protocols_are_unfrozen():
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        st = protocol_status(exp)
        assert st["frozen"] is False and st["sha256"] is not None


def test_freeze_detection(tmp_path):
    proto = tmp_path / "p.md"
    proto.write_text("protocol v1\n")
    reg = tmp_path / "reg.csv"
    reg.write_text("exp_id,protocol_path,protocol_hash\nEXP-009,p.md," + sha256_file(proto) + "\n")
    assert protocol_status("EXP-009", reg, tmp_path)["frozen"] is True
    proto.write_text("protocol v1, edited after the freeze\n")
    assert protocol_status("EXP-009", reg, tmp_path)["frozen"] is False


def test_cli_refuses_confirmatory_configs(capsys):
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        code = cli.main(["run", "--config", str(REPO_ROOT / "research" / "experiments" / exp / "config.json")])
        assert code == 3
        assert "REFUSED" in capsys.readouterr().err


def test_cli_plan_counts_match_protocol(capsys):
    expected = {"EXP-001": 12_900, "EXP-002": 105_300}
    for exp, n in expected.items():
        cli.main(["run", "--plan", "--config", str(REPO_ROOT / "research" / "experiments" / exp / "config.json")])
        out = capsys.readouterr().out
        plan = json.loads(out[: out.rindex("}") + 1])
        assert plan["planned"]["total_runs"] == n


def test_end_to_end_cli_and_report(tmp_path):
    cfg_path = tmp_path / "tiny.json"
    cfg_path.write_text(json.dumps(_cfg()))
    res = cli.execute(cfg_path, tmp_path / "out", ["test"])
    doc = read_result(res)
    assert doc["label"] == "exploratory" and doc["protocol"]["frozen"] is False
    man = json.loads((res.parent / "run_manifest.json").read_text())
    for key in ("config_sha256", "seeds", "git", "environment", "runtime_s", "peak_rss_bytes", "start_utc"):
        assert key in man
    assert man["config_sha256"] == doc["config_sha256"]
    produced = build_report(res)
    assert Path(produced["report_md"]).read_text().count("EXPLORATORY") >= 1
    assert all((res.parent / "report" / f).exists() for f in produced["figures"])
    assert "Holm" in Path(produced["report_md"]).read_text()
    assert Path(produced["metrics_csv"]).read_text().count("\n") == 1 + 16
    # tampering with a recorded stream hash makes the report fail closed
    doc["cells"][0]["runs"][0]["stream_sha256"] = "0" * 64
    res.write_text(json.dumps(doc))
    with pytest.raises(ReportError):
        build_report(res)


def test_schema_rejects_malformed(tmp_path):
    body = run_experiment(_cfg(fix_coarse_sensitivity=False), UNFROZEN, "rs")
    doc = {"schema": "fare-result", "schema_version": "1.0.0", "label": "exploratory", "simulated": True,
           "experiment_id": "EXP-001", "run_set_id": "rs", "created_utc": "now", "config": {},
           "config_sha256": "a" * 64, "protocol": UNFROZEN | {"path": "p"}, "cells": body["cells"],
           "failures": 0, "manifest_path": "m.json"}
    validate_result(doc)
    for mutate in (
        lambda d: d.update(simulated=False),
        lambda d: d.update(failures=1),
        lambda d: d.update(label="confirmatory"),
        lambda d: d["cells"][0]["runs"][0]["metrics"].update(sell_through=1.5),
        lambda d: d["cells"][0]["runs"][0].update(status="failed"),
        lambda d: d["cells"][0]["runs"][1].update(run_id=d["cells"][0]["runs"][0]["run_id"]),
        lambda d: d.pop("cells"),
        lambda d: d.update(extra=1),
    ):
        bad = copy.deepcopy(doc)
        mutate(bad)
        with pytest.raises(ResultValidationError):
            validate_result(bad)
    p = tmp_path / "broken.json"
    p.write_text("{not json")
    with pytest.raises(ResultValidationError):
        read_result(p)
