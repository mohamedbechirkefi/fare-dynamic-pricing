<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# EXP-001 reproduction

All commands run from the repository root. `UV` is `/Users/bechir/research/labs/.tools/py/bin/uv` on the owner's machine.

## Environment

```
$UV sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q            # 143 passed at revision 4204eac
```

- Python 3.12.1.
- Locked packages (`uv.lock`): numpy 2.5.4, jsonschema 4.26.0, pytest 9.2.0 and hypothesis 6.170.15.
- Code revision for the confirmatory run: `4204eac0776f4a04e512ef5ce92a10eefa5c5252`.

## Inputs

| File | SHA-256 |
|---|---|
| `research/protocol.md` | `d4b7c1e04c1152853769f1a1de851a5fc1950a91b37cba693543b88ffebe03b1` |
| `research/experiments/EXP-001/protocol.md` | `06f939d8fd59389a3438cd539f862a36ed4d47275137b50aeb3ffdc233df2ec2` |
| `research/experiments/EXP-001/config.json` | file `b8f3f87283c791e6da1fa845c0e6e7559a460ee9d9488e86ca42465f9c003178`, canonical `592a197632390bb9ab8fdcf7e95555e3bb590c921faba573175c4dcaa9cffc76` |
| `data/manifest.json` (synthetic data only) | `a1a99feb3579f3abefdc314495a2eb3c99deea5c7caec4948c38fe08405195ee` |

## Commands

```
PYTHONPATH=src .venv/bin/python -m fare.cli run --plan --config research/experiments/EXP-001/config.json
PYTHONPATH=src nice -n 10 .venv/bin/python -m fare.cli run --config research/experiments/EXP-001/config.json --out results/raw/confirmatory
PYTHONPATH=src .venv/bin/python -m fare.cli report --result results/raw/confirmatory/<run_set_id>/result.json
PYTHONPATH=src .venv/bin/python -m fare.summary --result results/raw/confirmatory/<run_set_id>/result.json --out research/experiments/EXP-001
```

- The plan prints `total_runs` 73000 and `frozen` true.
- `run` refuses any config or protocol that differs from the freeze record (exit 3).

## Raw results (git-ignored, regenerable)

Directory `results/raw/confirmatory/EXP-001-con-config-20261124T233503Z/`, 21,532,968 bytes in total:

| File | Bytes | SHA-256 |
|---|---|---|
| `result.json` (schema 1.0.0) | 15,579,281 | `d957c9fe8533841dc60d42b03e85e164d525d265d3d77c5806968e1f2a438a39` |
| `run_manifest.json` | 1,579 | `67db5eec4e9ed74b381445888e9186620c0a989d3fa3c5e5070189e82be12765` |
| `config.json` | 950 | `b8f3f87283c791e6da1fa845c0e6e7559a460ee9d9488e86ca42465f9c003178` |
| `report/metrics.csv` (per run) | 5,043,822 | `26b3b48c1e207974fbbaf52f9b4226b5879ebf578d0060be99c93b3a1e7d0fd8` |
| `report/report.md` | 4,457 | `23b59fb8c362d14803da0ab6ffc43aaa11ecbe8080a1aee7820015dd7876ce26` |

The complete file list, including the figures, is in `summary.json` under `raw_manifest`.

## Committed outputs

In this folder:
- `summary.json`
- `metrics.csv` (one row per contrast)
- `arm_summary.csv`
- `run_manifest.json`
- `figures/fig-EXP-001-forest-revenue.svg`, `fig-EXP-001-base-diff.svg` and `fig-EXP-001-base-price.svg`

Run log and exit status: `results/confirmatory/logs/`.

## Expected schema and tolerance

- The simulation is deterministic given the seed keys. A rerun at revision 4204eac reproduces every metric, contrast and interval exactly, and gives the same `result.json` content apart from timestamps, run set ID and timing fields.
- Wall-clock time and peak memory vary with machine load.

## Figure regeneration

- The forest plot comes from `fare.summary`.
- The dot and price-path figures come from `fare.cli report`.
- The price-path generator fails closed if a regenerated stream hash differs from the recorded one.
