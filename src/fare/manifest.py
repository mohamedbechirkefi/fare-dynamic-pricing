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


def protocol_status(exp_id: str, registry: Path = REGISTRY, root: Path = REPO_ROOT) -> dict[str, Any]:
    """Frozen iff the registry row carries a 64-hex protocol hash equal to the
    SHA-256 of the protocol file now on disk. Anything else is unfrozen."""
    path = None
    recorded = None
    if registry.exists():
        with registry.open(newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("exp_id") == exp_id:
                    path = row.get("protocol_path")
                    recorded = (row.get("protocol_hash") or "").strip()
    if path is None:
        return {"path": "", "sha256": None, "frozen": False}
    p = root / path
    actual = sha256_file(p) if p.exists() else None
    frozen = bool(recorded) and len(recorded) == 64 and recorded == actual
    return {"path": path, "sha256": actual, "frozen": frozen}


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
        "environment": environment(),
        "command": command,
        "start_utc": start_utc,
        "end_utc": end_utc,
        "runtime_s": runtime_s,
        "peak_rss_bytes": peak_rss_bytes(),
        "counts": counts,
    }
