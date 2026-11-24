<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# src/

Core Python package `fare` (M2). The layers are kept separate:

- `params.py`: scenario parameters with units and validation.
- `streams.py`: ingestion, that is, seeded synthetic demand streams.
- `policies.py`: FIX (the baseline), OCC and DRP.
- `simulate.py`: the fast simulator, the naive reference oracle and the invariant checker.
- `metrics.py`: per-season metrics and purchase elasticity.
- `tuning.py`: equal-budget grids and selection.
- `stats.py`: paired uncertainty methods.
- `runner.py`: the experiment runner.
- `schema.py` with `schemas/result.schema.json`: the versioned result schema.
- `manifest.py`: run manifests and the freeze check.
- `report.py`: tables and figures from result files.
- `cli.py`: `smoke`, `run`, `report` and `test`.

Import with `PYTHONPATH=src`.
