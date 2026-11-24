# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Config-to-results integration, schema, manifest, freeze guard and report."""

import copy
import json
from pathlib import Path

import pytest

from fare import cli
from fare.manifest import REPO_ROOT, build_freeze_record, protocol_status, sha256_file
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


def _frozen_fixture(tmp_path, cfg):
    """A temporary repository with one frozen experiment (EXP-009)."""
    (tmp_path / "research").mkdir()
    (tmp_path / "research" / "protocol.md").write_text("main protocol v1\n")
    proto = tmp_path / "p.md"
    proto.write_text("protocol v1\n")
    (tmp_path / "c.json").write_text(json.dumps(cfg))
    reg = tmp_path / "reg.csv"
    reg.write_text("exp_id,protocol_path,protocol_hash\nEXP-009,p.md," + sha256_file(proto) + "\n")
    rec = build_freeze_record(approval={"quote": "q", "date": "2026-11-24"}, common_decisions={}, disclosure={},
                              experiments={"EXP-009": {"protocol": "p.md", "config": "c.json"}},
                              root=tmp_path, revision="0" * 40)
    (tmp_path / "research" / "freeze.json").write_text(json.dumps(rec))
    return reg, proto


def test_freeze_detection(tmp_path):
    cfg = _cfg(experiment_id="EXP-009", label="confirmatory")
    reg, proto = _frozen_fixture(tmp_path, cfg)
    st = protocol_status("EXP-009", reg, tmp_path, cfg=cfg)
    assert st["frozen"] is True and st["reason"] is None
    validate_config(cfg, st)  # accepted
    # a changed config is refused
    changed = _cfg(experiment_id="EXP-009", label="confirmatory", sesoi_fraction=0.02)
    st = protocol_status("EXP-009", reg, tmp_path, cfg=changed)
    assert st["frozen"] is False and "config" in st["reason"]
    with pytest.raises(ProtocolNotFrozen):
        validate_config(changed, st)
    # an edited main protocol unfreezes everything
    main = tmp_path / "research" / "protocol.md"
    main.write_text("main protocol v1, edited\n")
    assert protocol_status("EXP-009", reg, tmp_path, cfg=cfg)["frozen"] is False
    main.write_text("main protocol v1\n")
    assert protocol_status("EXP-009", reg, tmp_path, cfg=cfg)["frozen"] is True
    # an edited experiment protocol unfreezes it
    proto.write_text("protocol v1, edited after the freeze\n")
    assert protocol_status("EXP-009", reg, tmp_path, cfg=cfg)["frozen"] is False
    proto.write_text("protocol v1\n")
    # no freeze record: not frozen even though the registry hash matches
    (tmp_path / "research" / "freeze.json").unlink()
    st = protocol_status("EXP-009", reg, tmp_path, cfg=cfg)
    assert st["frozen"] is False and "freeze record" in st["reason"]


def test_cli_accepts_frozen_and_refuses_changed_config(tmp_path, monkeypatch, capsys):
    import functools
    cfg = _cfg(experiment_id="EXP-009", label="confirmatory")
    reg, _ = _frozen_fixture(tmp_path, cfg)
    monkeypatch.setattr(cli, "protocol_status", functools.partial(protocol_status, registry=reg, root=tmp_path))
    out = tmp_path / "out"
    assert cli.main(["run", "--config", str(tmp_path / "c.json"), "--out", str(out)]) == 0
    doc = read_result(next(out.glob("*/result.json")))
    assert doc["label"] == "confirmatory" and doc["protocol"]["frozen"] is True
    capsys.readouterr()
    (tmp_path / "c2.json").write_text(json.dumps(_cfg(experiment_id="EXP-009", label="confirmatory",
                                                      bootstrap={"resamples": 201, "seed": 1})))
    assert cli.main(["run", "--config", str(tmp_path / "c2.json"), "--out", str(out)]) == 3
    assert "REFUSED" in capsys.readouterr().err


def test_cli_refuses_confirmatory_configs(capsys):
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        code = cli.main(["run", "--config", str(REPO_ROOT / "research" / "experiments" / exp / "config.json")])
        assert code == 3
        assert "REFUSED" in capsys.readouterr().err


def test_cli_plan_counts_match_protocol(capsys):
    expected = {"EXP-001": 74_500, "EXP-002": 594_000, "EXP-003": 258_000}  # 500 tuning, 4,000 evaluation streams
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


def test_v1_grid_config_runs_with_fix6_sensitivity_arm():
    from fare.tuning import DRP_ETA_V1, OCC_K_V1
    cfg = _cfg(grid={"lo": 40.0, "hi": 400.0, "fix_n": 36, "p0_n": 6,
                     "occ_k": list(OCC_K_V1), "drp_eta": list(DRP_ETA_V1)})
    body = run_experiment(cfg, UNFROZEN, "rs")
    cell = body["cells"][0]
    assert {t["arm"] for t in cell["tuning"]} == {"FIX", "OCC", "DRP", "FIX6"}
    assert all(t["n_configs"] == 36 for t in cell["tuning"] if t["arm"] != "FIX6")
    assert cell["timing"]["tuning_runs"] == 3 * 36 * 2 + 6 * 2
    assert ("DRP", "FIX6", "revenue") in {(k["arm"], k["comparator"], k["metric"]) for k in cell["contrasts"]}
    assert planned_run_counts(cfg)["total_runs"] == cell["timing"]["tuning_runs"] + len(cell["runs"])
    with pytest.raises(ConfigError):
        validate_config(_cfg(grid={"p0_n": 6, "occ_K": [1.0]}), UNFROZEN)


def test_interaction_table_in_report():
    from fare.report import interaction_table
    cells = [{"id": f"sv{sv}-k{k}", "index": i, "scenario": {"sigma_v": sv, "kappa": k}}
             for i, (sv, k) in enumerate([(0.5, 1.0), (0.5, 4.0)])]
    body = run_experiment(_cfg(cells=cells, fix_coarse_sensitivity=False), UNFROZEN, "rs")
    tab = interaction_table({"cells": body["cells"]}, n_resamples=200, seed=1)
    assert tab is not None and tab.count("Delta(kappa=4) - Delta(kappa=1)") == 2
    assert interaction_table({"cells": body["cells"][:1]}) is None
