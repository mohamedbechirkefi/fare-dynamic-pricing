<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# results/

Versioned, machine-readable experiment outputs.

- `exploratory/`: pre-freeze smoke and pilot runs on tuning streams only. They are labelled exploratory, are never evidence and are never reported as findings. Each `<run_set_id>/` holds `result.json` (schema 1.0.0), `run_manifest.json`, `config.json` and `report/`. `pilot_summary.json` summarises them for the owner's freeze decisions.
- `confirmatory/`: written by `fare.cli run` only after the owner freezes a protocol. Empty.
- `raw/`: large regenerable outputs (git-ignored).
