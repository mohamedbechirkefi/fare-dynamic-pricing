# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Run manifests and protocol-freeze status (records layer)."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import resource
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

from . import GENERATOR_VERSION, __version__
from .streams import PROJECT_ENTROPY

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "research" / "experiment_registry.csv"
FREEZE_RECORD = REPO_ROOT / "research" / "freeze.json"
MAIN_PROTOCOL = "research/protocol.md"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def config_hash(cfg: dict) -> str:
    return sha256_bytes(canonical_json(cfg))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_revision(root: Path = REPO_ROOT) -> dict[str, Any]:
    try:
        rev = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], capture_output=True,
                               text=True, check=True).stdout.strip() != ""
        return {"revision": rev, "dirty_tracked_files": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"revision": None, "dirty_tracked_files": None}


def cpu_name() -> str:
    if sys.platform == "darwin":
        try:
            return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True,
                                  text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.processor() or platform.machine()


def peak_rss_bytes() -> int:
    """Peak resident set size of this process (macOS reports bytes, Linux KiB)."""
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r if sys.platform == "darwin" else r * 1024)


def package_versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {"python": platform.python_version(), "fare": __version__}
    for pkg in ("numpy", "jsonschema"):
        try:
            out[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            out[pkg] = None
    return out


def environment() -> dict[str, Any]:
    return {
        "os": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "cpu": cpu_name(),
        "machine": platform.machine(),
        "versions": package_versions(),
    }


def _registry_row(exp_id: str, registry: Path) -> tuple[str | None, str | None]:
    if registry.exists():
        with registry.open(newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("exp_id") == exp_id:
                    return row.get("protocol_path"), (row.get("protocol_hash") or "").strip()
    return None, None


def _hex64(x) -> bool:
    return isinstance(x, str) and len(x) == 64 and all(ch in "0123456789abcdef" for ch in x)


def protocol_status(exp_id: str, registry: Path = REGISTRY, root: Path = REPO_ROOT, cfg: dict | None = None,
                    freeze_record: Path | None = None) -> dict[str, Any]:
    """Freeze check (G-FREEZE). An experiment is frozen only if all hold:

    1. its registry row carries a 64-hex protocol hash equal to the SHA-256 of
       the protocol file now on disk;
    2. the freeze record (`research/freeze.json`) exists, has status "frozen",
       and lists the same protocol hash for this experiment;
    3. the main protocol (`research/protocol.md`) on disk matches the hash in
       the freeze record;
    4. when a config is given, its canonical-JSON SHA-256 equals the config
       hash recorded for this experiment in the freeze record.

    Anything else is unfrozen; `reason` names the first failed condition.
    """
    freeze_record = freeze_record or root / "research" / "freeze.json"
    path, recorded = _registry_row(exp_id, registry)
    if path is None:
        return {"path": "", "sha256": None, "frozen": False, "reason": "experiment not in registry"}
    p = root / path
    actual = sha256_file(p) if p.exists() else None
    out = {"path": path, "sha256": actual, "frozen": False}
    if not (_hex64(recorded) and recorded == actual):
        return out | {"reason": "registry protocol hash missing or different from the protocol on disk"}
    try:
        rec = json.loads(Path(freeze_record).read_text())
    except (OSError, json.JSONDecodeError):
        return out | {"reason": "no readable freeze record"}
    entry = (rec.get("experiments") or {}).get(exp_id) or {}
    if rec.get("status") != "frozen" or (entry.get("protocol") or {}).get("sha256") != actual:
        return out | {"reason": "freeze record does not freeze this protocol version"}
    main = rec.get("main_protocol") or {}
    mp = root / main.get("path", MAIN_PROTOCOL)
    if not mp.exists() or sha256_file(mp) != main.get("sha256"):
        return out | {"reason": "main protocol changed since the freeze"}
    if cfg is not None and config_hash(cfg) != (entry.get("config") or {}).get("canonical_sha256"):
        return out | {"reason": "config differs from the frozen confirmatory config"}
    return out | {"frozen": True, "reason": None}


def build_freeze_record(*, approval: dict, common_decisions: dict, disclosure: dict, experiments: dict[str, dict],
                        root: Path = REPO_ROOT, revision: str | None = None) -> dict[str, Any]:
    """Freeze record in the format `protocol_status` reads.

    `experiments` maps EXP-ID -> {"protocol": path, "config": path}; paths are
    repository-relative. Hashes are computed here from the files on disk.
    """
    exps = {}
    for exp_id, e in experiments.items():
        cfg_path = root / e["config"]
        exps[exp_id] = {
            "protocol": {"path": e["protocol"], "sha256": sha256_file(root / e["protocol"])},
            "config": {"path": e["config"], "file_sha256": sha256_file(cfg_path),
                       "canonical_sha256": config_hash(json.loads(cfg_path.read_text()))},
        }
    return {
        "freeze_record_version": "1.0.0",
        "status": "frozen",
        "approval": approval,
        "common_decisions": common_decisions,
        "c4_disclosure": disclosure,
        "main_protocol": {"path": MAIN_PROTOCOL, "sha256": sha256_file(root / MAIN_PROTOCOL)},
        "experiments": exps,
        "git_revision": revision if revision is not None else git_revision(root)["revision"],
    }


def data_manifest_record(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Path and SHA-256 of the data manifest in force when a run set executes.

    FARE uses synthetic streams only (decision D-002); the manifest documents
    the generator and seed scheme, so its hash pins the data provenance."""
    path = root / "data" / "manifest.json"
    return {"path": "data/manifest.json", "sha256": sha256_file(path) if path.exists() else None}


def build_manifest(*, run_set_id: str, label: str, experiment_id: str, cfg: dict, cfg_sha: str,
                   protocol: dict, start_utc: str, end_utc: str, runtime_s: float, seed_keys: dict,
                   counts: dict, command: list[str]) -> dict[str, Any]:
    return {
        "manifest_version": "1.0.0",
        "run_set_id": run_set_id,
        "label": label,
        "simulated": True,
        "experiment_id": experiment_id,
        "config_sha256": cfg_sha,
        "protocol": protocol,
        "seeds": {"project_entropy": PROJECT_ENTROPY, "generator_version": GENERATOR_VERSION, **seed_keys},
        "git": git_revision(),
        "data_manifest": data_manifest_record(),
        "environment": environment(),
        "command": command,
        "start_utc": start_utc,
        "end_utc": end_utc,
        "runtime_s": runtime_s,
        "peak_rss_bytes": peak_rss_bytes(),
        "counts": counts,
    }
