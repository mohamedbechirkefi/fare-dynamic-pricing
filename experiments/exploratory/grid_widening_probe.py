# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""EXPLORATORY, pre-freeze: how far would the OCC and DRP grids need to widen
for the EXP-002 pilot optima to be interior?

Tuning only, on the pilot tuning streams (role 0, indices 0-49) of the nine
EXP-002 cells, with 6 geometric p0 values in [40, 400] and a deliberately wide
sensitivity axis: OCC k in {0.25, 0.5, ..., 32} and DRP eta in {0, 0.1 * 2^-8,
..., 0.1, 0.25, 0.5, 1}. eta = 0 is DRP reduced to a fixed price. Nothing is
evaluated and no contrast is computed. Not a candidate grid; a diagnostic.

    PYTHONPATH=src uv run python experiments/exploratory/grid_widening_probe.py > results/exploratory/grid_widening_probe.json
"""

from __future__ import annotations

import json
import sys

from fare.cli import _load
from fare.manifest import REPO_ROOT, git_revision
from fare.params import ScenarioParams
from fare.runner import StreamSet, _streams
from fare.tuning import grid, revenue_matrix, select

OCC_K_WIDE = [0.25 * 2 ** i for i in range(8)]
DRP_ETA_WIDE = [0.0] + [0.1 * 2.0 ** -i for i in range(8, 0, -1)] + [0.1, 0.25, 0.5, 1.0]


def main() -> int:
    cfg = _load(REPO_ROOT / "experiments" / "exploratory" / "pilot-exp002.json")
    base = ScenarioParams.from_dict(cfg.get("base_scenario", {}))
    rows = []
    for c in cfg["cells"]:
        sp = base.with_(**c.get("scenario", {}))
        streams = _streams(sp, int(cfg["experiment_number"]), int(c["index"]), StreamSet(0, 0, 50))
        for fam, kw, name, vals in (("OCC", {"occ_k": OCC_K_WIDE}, "k", OCC_K_WIDE),
                                    ("DRP", {"drp_eta": DRP_ETA_WIDE}, "eta", DRP_ETA_WIDE)):
            configs = grid(fam, lo=40.0, hi=400.0, p0_n=6, **kw)
            tr = select(fam, configs, revenue_matrix(configs, streams, sp))
            v = getattr(tr.best, name)
            rows.append({"cell_id": c["id"], "family": fam, "selected_p0": tr.best.p0, "sensitivity_name": name,
                         "selected_sensitivity": v, "sensitivity_at_edge": v in (min(vals), max(vals))})
    json.dump({"label": "EXPLORATORY (pre-freeze; tuning streams 0-49 only; no evaluation, no contrast; not evidence)",
               "git": git_revision(), "occ_k": OCC_K_WIDE, "drp_eta": DRP_ETA_WIDE, "rows": rows}, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
