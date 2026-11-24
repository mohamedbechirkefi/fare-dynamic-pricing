# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Command-line interface: smoke, run, report, test.

    PYTHONPATH=src uv run python -m fare.cli smoke
    PYTHONPATH=src uv run python -m fare.cli run --config <config.json> [--plan]
    PYTHONPATH=src uv run python -m fare.cli report --result <result.json> [--pdf]
    PYTHONPATH=src uv run python -m fare.cli test

`run` refuses a confirmatory config while the experiment's protocol is not
frozen (G-FREEZE). Exploratory outputs go to results/exploratory/.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .manifest import REPO_ROOT, build_manifest, config_hash, protocol_status, utc_now
from .report import build_report
from .runner import ConfigError, ProtocolNotFrozen, planned_run_counts, run_experiment, validate_config
from .schema import SCHEMA_VERSION, write_result

SMOKE_CONFIG = REPO_ROOT / "experiments" / "smoke.json"


def _load(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from exc


def _rel(path: Path) -> str:
    """Repository-relative path when possible, so manifests carry no local paths."""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return Path(path).name


def execute(cfg_path: Path, out_root: Path | None = None, argv: list[str] | None = None) -> Path:
    cfg = _load(cfg_path)
    protocol = protocol_status(cfg.get("experiment_id", ""), cfg=cfg)
    validate_config(cfg, protocol)
    label = cfg["label"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_set_id = f"{cfg['experiment_id']}-{label[:3]}-{Path(cfg_path).stem}-{stamp}"
    root = out_root or (REPO_ROOT / "results" / label)
    out = root / run_set_id
    out.mkdir(parents=True, exist_ok=False)
    start = utc_now()
    t0 = time.perf_counter()
    body = run_experiment(cfg, protocol, run_set_id)
    runtime = time.perf_counter() - t0
    end = utc_now()
    cfg_sha = config_hash(cfg)
    counts = {"cells": len(body["cells"]),
              "tuning_runs": sum(c["timing"]["tuning_runs"] for c in body["cells"]),
              "eval_runs": sum(c["timing"]["eval_runs"] for c in body["cells"]),
              "failed_runs": body["failures"]}
    seed_keys = {"spawn_key_layout": "(experiment, cell, role, index)",
                 "experiment_number": cfg["experiment_number"],
                 "tune_streams": cfg.get("tune_streams"), "eval_streams": cfg["eval_streams"],
                 "bootstrap_seed": cfg.get("bootstrap", {}).get("seed", 20261124)}
    manifest = build_manifest(run_set_id=run_set_id, label=label, experiment_id=cfg["experiment_id"], cfg=cfg,
                              cfg_sha=cfg_sha, protocol=protocol, start_utc=start, end_utc=end,
                              runtime_s=runtime, seed_keys=seed_keys, counts=counts,
                              command=argv or sys.argv)
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    (out / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    doc = {"schema": "fare-result", "schema_version": SCHEMA_VERSION, "label": label, "simulated": True,
           "experiment_id": cfg["experiment_id"], "run_set_id": run_set_id, "created_utc": end,
           "config": cfg, "config_sha256": cfg_sha,
           "protocol": {k: protocol[k] for k in ("path", "sha256", "frozen")}, "cells": body["cells"],
           "failures": body["failures"], "manifest_path": "run_manifest.json"}
    if cfg.get("note"):
        doc["note"] = cfg["note"]
    write_result(doc, out / "result.json")
    print(f"{label.upper()} run set {run_set_id}: {counts['tuning_runs']} tuning + {counts['eval_runs']} "
          f"evaluation runs, {counts['failed_runs']} failed, {runtime:.2f} s, peak RSS "
          f"{manifest['peak_rss_bytes'] / 2**20:.1f} MiB")
    print(f"wrote {out / 'result.json'}")
    return out / "result.json"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="fare", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="exploratory smoke run (tuning streams and edge cases only)")
    s.add_argument("--config", type=Path, default=SMOKE_CONFIG)
    s.add_argument("--out", type=Path, default=None)
    s.add_argument("--no-report", action="store_true")
    r = sub.add_parser("run", help="run an experiment config")
    r.add_argument("--config", type=Path, required=True)
    r.add_argument("--out", type=Path, default=None)
    r.add_argument("--plan", action="store_true", help="print planned run counts and the freeze check, run nothing")
    p = sub.add_parser("report", help="build tables and figures from a result file")
    p.add_argument("--result", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--pdf", action="store_true")
    t = sub.add_parser("test", help="run the test suite")
    t.add_argument("pytest_args", nargs="*")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "smoke":
            res = execute(a.config, a.out, ["fare", "smoke", "--config", _rel(a.config)])
            if not a.no_report:
                print(json.dumps(build_report(res), indent=1))
            return 0
        if a.cmd == "run":
            cfg = _load(a.config)
            prot = protocol_status(cfg.get("experiment_id", ""), cfg=cfg)
            if a.plan:
                print(json.dumps({"experiment_id": cfg.get("experiment_id"), "label": cfg.get("label"),
                                  "protocol": prot, "planned": planned_run_counts(cfg)}, indent=1))
                validate_config(cfg, prot)
                return 0
            execute(a.config, a.out, ["fare", "run", "--config", _rel(a.config)])
            return 0
        if a.cmd == "report":
            print(json.dumps(build_report(a.result, a.out, a.pdf), indent=1))
            return 0
        if a.cmd == "test":
            return subprocess.call([sys.executable, "-m", "pytest", "-q", str(REPO_ROOT / "tests"), *a.pytest_args])
    except ProtocolNotFrozen as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    except ConfigError as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
