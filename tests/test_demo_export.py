# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo shows the manuscript's numbers.

1. Re-running the export in memory reproduces the committed
   demo/public/data/results.json byte for byte.
2. Every display, interval_display and relative_display string appears
   verbatim in research/paper/manuscript.md, or is a documented exception
   (display_exceptions, each with a note).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "demo" / "public" / "data" / "results.json"


@pytest.fixture(scope="module")
def export():
    spec = importlib.util.spec_from_file_location("export_demo_data", ROOT / "scripts" / "export_demo_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fresh(export):
    return export.build()


def test_committed_results_json_equals_a_fresh_export(export, fresh):
    assert RESULTS.read_text() == export.render(fresh)


def test_every_display_string_is_printed_in_the_manuscript_or_documented(fresh):
    text = (ROOT / "research" / "paper" / "manuscript.md").read_text()
    exceptions = {(e["label"], e["field"], e["value"]): e for e in fresh["display_exceptions"]}
    for e in exceptions.values():
        assert e["note"].strip(), f"exception without a note: {e}"
    checked = 0
    for block in ("experiments", "exploratory_checks"):
        for exp in fresh[block]:
            for x in exp["estimates"]:
                for field in ("display", "interval_display", "relative_display"):
                    v = x.get(field)
                    if v is None:
                        continue
                    checked += 1
                    if (x["label"], field, v) in exceptions:
                        continue
                    assert v in text, f"{exp['id']} {x['label']} {field}={v!r} is not printed in the manuscript"
    assert checked > 150


def test_every_registered_experiment_is_exported_with_status_verdict_and_claims(fresh):
    import csv

    with open(ROOT / "research" / "experiment_registry.csv", newline="") as f:
        registry = [r["exp_id"] for r in csv.DictReader(f)]
    with open(ROOT / "research" / "claims_register.csv", newline="") as f:
        claims = {r["claim_id"] for r in csv.DictReader(f)}
    assert [e["id"] for e in fresh["experiments"]] == registry
    for e in fresh["experiments"] + fresh["exploratory_checks"]:
        assert e["status"] and e["verdict"]
        assert set(e["claim_ids"]) <= claims
    # negative results are exported with the same structure as positive ones
    signs = [x["estimate"] < 0 for x in fresh["experiments"][1]["estimates"] if x["group"].startswith("sv")]
    assert sum(signs) == 8 and len(signs) == 18


def test_no_timestamp_and_hashes_match_sources(fresh):
    import hashlib

    for s in fresh["sources"]:
        assert hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest() == s["sha256"]
    text = json.dumps(fresh)
    assert "created_utc" not in text and "T00:" not in text
