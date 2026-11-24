# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""EXPLORATORY, pre-freeze: are the tuned OCC and DRP optima interior on the
widened v1.0 grids (owner-approved amendment 2026-11-24, D-008)?

Tuning only. For every pilot cell (EXP-001 base, which EXP-003 also uses for
its base tuning, and the nine EXP-002 cells) the script tunes OCC and DRP on
the pilot tuning streams (role 0, indices 0-49), once on the draft v0.1 grid
and once on the v1.0 grid, and prints the selected configurations and whether
they lie on a grid edge. Nothing is evaluated: no evaluation stream is
generated and no contrast between policies is computed.

    PYTHONPATH=src uv run python experiments/exploratory/grid_interior_check.py > results/exploratory/grid_interior_check.json
"""

from __future__ import annotations

import json
import sys

from fare.cli import _load
from fare.manifest import REPO_ROOT, git_revision
from fare.params import ScenarioParams
from fare.runner import StreamSet, _streams
from fare.tuning import DRP_ETA, DRP_ETA_V1, OCC_K, OCC_K_V1, grid, revenue_matrix, select

GRIDS = {
    "draft-v0.1": {"lo": 40.0, "hi": 400.0, "p0_n": 9, "occ_k": OCC_K, "drp_eta": DRP_ETA},
    "v1.0": {"lo": 40.0, "hi": 400.0, "p0_n": 6, "occ_k": OCC_K_V1, "drp_eta": DRP_ETA_V1},
}
PILOT_TUNE = StreamSet(role=0, start=0, count=50)


def _cells():
    for name in ("pilot-exp001", "pilot-exp002"):
        cfg = _load(REPO_ROOT / "experiments" / "exploratory" / f"{name}.json")
        base = ScenarioParams.from_dict(cfg.get("base_scenario", {}))
        for c in cfg["cells"]:
            yield cfg["experiment_id"], int(cfg["experiment_number"]), c["id"], int(c["index"]), base.with_(**c.get("scenario", {}))


def main() -> int:
    rows = []
    for exp_id, exp, cid, cidx, sp in _cells():
        streams = _streams(sp, exp, cidx, PILOT_TUNE)
        for gname, g in GRIDS.items():
            for fam in ("OCC", "DRP"):
                configs = grid(fam, **{k: v for k, v in g.items()})
                tr = select(fam, configs, revenue_matrix(configs, streams, sp))
                sens_name = "k" if fam == "OCC" else "eta"
                sens = getattr(tr.best, sens_name)
                values = g["occ_k"] if fam == "OCC" else g["drp_eta"]
                rows.append({"experiment_id": exp_id, "cell_id": cid, "grid": gname, "family": fam,
                             "n_configs": len(configs), "selected_p0": tr.best.p0, f"selected_sensitivity": sens,
                             "sensitivity_name": sens_name,
                             "sensitivity_at_edge": sens in (min(values), max(values)),
                             "at_grid_edge": tr.at_grid_edge})
    out = {"label": "EXPLORATORY (pre-freeze; tuning streams 0-49 only; no evaluation, no contrast; not evidence)",
           "git": git_revision(), "grids": {k: {kk: list(vv) if isinstance(vv, tuple) else vv for kk, vv in v.items()}
                                            for k, v in GRIDS.items()},
           "rows": rows,
           "summary": {g: {"n": sum(1 for r in rows if r["grid"] == g),
                           "at_grid_edge": sum(1 for r in rows if r["grid"] == g and r["at_grid_edge"])}
                       for g in GRIDS}}
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
