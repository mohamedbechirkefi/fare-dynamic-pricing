# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Versioned result schema; validation at export and import (fail closed)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_PATH = Path(__file__).with_name("schemas") / "result.schema.json"
SCHEMA_VERSION = "1.0.0"


class ResultValidationError(ValueError):
    """A result document does not conform to the result schema."""


@lru_cache(maxsize=1)
def _validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def validate_result(doc: Any) -> None:
    errors = sorted(_validator().iter_errors(doc), key=lambda e: list(e.path))
    if errors:
        e = errors[0]
        where = "/".join(str(p) for p in e.path) or "<root>"
        raise ResultValidationError(f"{len(errors)} schema error(s); first at {where}: {e.message}")
    # semantic checks beyond JSON Schema
    n_failed = sum(1 for c in doc["cells"] for r in c["runs"] if r["status"] == "failed")
    if n_failed != doc["failures"]:
        raise ResultValidationError(f"failures={doc['failures']} but {n_failed} failed runs recorded")
    seen = set()
    for c in doc["cells"]:
        for r in c["runs"]:
            if r["run_id"] in seen:
                raise ResultValidationError(f"duplicate run_id {r['run_id']}")
            seen.add(r["run_id"])
            if (r["status"] == "ok") != (r["metrics"] is not None):
                raise ResultValidationError(f"run {r['run_id']}: metrics must be present iff status is ok")
    if doc["label"] == "confirmatory" and not doc["protocol"]["frozen"]:
        raise ResultValidationError("a confirmatory result requires a frozen protocol")


def write_result(doc: dict, path: Path) -> None:
    validate_result(doc)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=False, allow_nan=False) + "\n")


def read_result(path: Path) -> dict:
    try:
        doc = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ResultValidationError(f"cannot read result {path}: {exc}") from exc
    validate_result(doc)
    return doc
