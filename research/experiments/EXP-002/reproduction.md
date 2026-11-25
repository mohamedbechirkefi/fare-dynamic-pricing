<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-002 reproduction

All commands run from the repository root. The environment is as in `research/experiments/EXP-001/reproduction.md`: `uv sync --frozen --all-groups --all-extras`, with 143 tests passing at revision `4204eac0776f4a04e512ef5ce92a10eefa5c5252`.

## Inputs

| File | SHA-256 |
|---|---|
| `research/protocol.md` | `d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1` |
| `research/experiments/EXP-002/protocol.md` | `7ffbc666ffd6465791d09e10ee3a3014002a513c90a876bf65c6e8ea4d2f6ab9` |
| `research/experiments/EXP-002/config.json` | file `5f279b83f972b83df3c5d7629f3152c7c2a8328757ce10e950dfe48777499e44`, canonical `df7da4d68172d469301e6b46d70628dede3cfa255ee660898ceedf6d30d62856` |
| `data/manifest.json` | `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee` |

## Commands

```
PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-002/config.json
PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-002/config.json --out results/raw/confirmatory
PYTHONPATH=src .venv/bin/python -m fare.cli report --result results/raw/confirmatory/<run_set_id>/result.json
PYTHONPATH=src .venv/bin/python -m fare.summary --result results/raw/confirmatory/<run_set_id>/result.json --out research/experiments/EXP-002
```

- The plan prints `total_runs` 594000.
- The Holm and interaction results are in `summary.json` (`verdict`) and in the raw `report/report.md`.

## Raw results (git-ignored, regenerable)

Directory `results/raw/confirmatory/EXP-002-con-config-20261124T233503Z/`, 147,753,410 bytes in total:

| File | Bytes | SHA-256 |
|---|---|---|
| `result.json` | 106,456,005 | `ef1584366c3c2b55c92946ec30aed2b2621b1a5564c2668e6eff4ad7b624a6a9` |
| `run_manifest.json` | 1,582 | `19d2bfa9fccb4021973daef78e461fa47b832140d5e95f81942af2815bc4daac` |
| `config.json` | 1,999 | `5f279b83f972b83df3c5d7629f3152c7c2a8328757ce10e950dfe48777499e44` |
| `report/metrics.csv` | 35,846,152 | `973d9d22879090e6b5edcc17a1accdedbf38b6c1602fbfe9925d5570106aa238` |
| `report/report.md` (includes the per-cell purchase elasticities) | 30,433 | `9548aee6799102b0a414486414e5aaec039791a881146343f48b46267910e082` |

The complete list is in `summary.json` (`raw_manifest`).

## Committed outputs

`summary.json`, `metrics.csv`, `arm_summary.csv`, `run_manifest.json` and `figures/` (the forest plot and 9 price-path figures). Run log: `results/confirmatory/logs/`.

## Tolerance

The run is deterministic given the seeds; the permutation and bootstrap seeds are 20261124. Every number reproduces exactly at revision 4204eac. Timing varies.
