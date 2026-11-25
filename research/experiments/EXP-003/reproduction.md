<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-003 reproduction

All commands run from the repository root. The environment is as in `research/experiments/EXP-001/reproduction.md`, at revision `4204eac0776f4a04e512ef5ce92a10eefa5c5252`.

## Inputs

| File | SHA-256 |
|---|---|
| `research/protocol.md` | `d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1` |
| `research/experiments/EXP-003/protocol.md` | `b1e2a2f8931bada91fd5f4589f0fa8bd50004db6c05d568c9354f43f14a510fd` |
| `research/experiments/EXP-003/config.json` | file `b49710e31d943ed1fba05388a5f6ea95e3e793b6bf76033824c3020a858b2c1c`, canonical `3c25c10c1cfcacf1103e6613b195c58c5ce0afd675556efa290f8b380ca039fd` |
| `data/manifest.json` | `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee` |

## Commands

```
PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-003/config.json
PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-003/config.json --out results/raw/confirmatory
PYTHONPATH=src .venv/bin/python -m fare.cli report --result results/raw/confirmatory/<run_set_id>/result.json
PYTHONPATH=src .venv/bin/python -m fare.summary --result results/raw/confirmatory/<run_set_id>/result.json --out research/experiments/EXP-003 --exp001-summary research/experiments/EXP-001/summary.json
```

- The plan prints `total_runs` 258000.
- The invalidation rule needs the EXP-001 summary.

## Raw results (git-ignored, regenerable)

Directory `results/raw/confirmatory/EXP-003-con-config-20261124T233547Z/`, 132,230,945 bytes in total:

| File | Bytes | SHA-256 |
|---|---|---|
| `result.json` | 94,624,773 | `66e50974d7036ddd8e3e7e38f43e508cc021cf523cb995cad0ccf05d53f125a2` |
| `run_manifest.json` | 1,581 | `fc24c6e09803ea5bfe78b5ba175d322db4da1366b3878b9dc0e854b00bba1746` |
| `config.json` | 2,238 | `b49710e31d943ed1fba05388a5f6ea95e3e793b6bf76033824c3020a858b2c1c` |
| `report/metrics.csv` | 32,160,824 | `6616e9ab90f90e7e7297d4fc24c82a7ed95836208998e8a5ba5e38982a2604c8` |
| `report/report.md` | 23,221 | `fd9e6c392550bf576451c9bd3bf9b4f95f005011dd5b70919e31793d8fec31ee` |

The complete list is in `summary.json` (`raw_manifest`).

## Committed outputs

`summary.json`, `metrics.csv`, `arm_summary.csv`, `run_manifest.json` and `figures/` (the forest plot and 6 price-path figures). Run log: `results/confirmatory/logs/`.

## Note on the raw report

The generic raw `report.md` also prints a Holm table across the six cells. Holm is not part of the EXP-003 frozen analysis, and that table is not used (D-010).

## Tolerance

The run is deterministic given the seeds, so every number reproduces exactly at revision 4204eac. Timing varies.
