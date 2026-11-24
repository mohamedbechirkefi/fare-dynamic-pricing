<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# results/confirmatory/

Confirmatory runs of the frozen v1.0 protocols (M3, 2026-11-25). The raw run directories are larger than 20 MB each and live in the git-ignored `results/raw/confirmatory/` (decision D-010). They are regenerable exactly from the frozen configs at revision 4204eac.

- `logs/EXP-NNN.log`: console output of each `fare.cli run`.
- `logs/exit_status.jsonl`: start, end, exit status and revision of each run, written by the run wrapper.
- Summaries, aggregate tables, figures and the SHA-256 of every raw file: `research/experiments/EXP-NNN/summary.json`.
