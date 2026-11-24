# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Experiment runner: config -> streams -> tuning -> evaluation -> contrasts.

The runner never writes files; `cli` serialises its output. Guards:
- a confirmatory config is refused unless the experiment's protocol is frozen
  (registry hash equals the on-disk protocol hash);
- an exploratory config may not touch evaluation streams (role 1): held-out
  streams are reserved for the frozen confirmatory analysis;
- tuning and evaluation stream sets may not overlap.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass
from typing import Any

import numpy as np

from .metrics import compute_metrics
from .params import ScenarioParams
from .policies import Policy, policy_from_dict, policy_to_dict
from .simulate import simulate
from .stats import classify, summarise
from .streams import ROLE_EVAL, DemandStream, SeedKey, generate_stream
from .tuning import grid, revenue_matrix, select

GRID_KEYS = ("lo", "hi", "fix_n", "p0_n", "occ_k", "drp_eta")

PRIMARY_ARMS = ("OCC", "DRP")
SECONDARY_METRICS = ("sell_through", "availability", "consumer_surplus", "total_surplus")
ROLE_NAMES = {0: "tune", 1: "eval"}


class ConfigError(ValueError):
    """The experiment configuration is invalid or not permitted."""


class ProtocolNotFrozen(PermissionError):
    """A confirmatory run was requested while the protocol is not frozen."""


@dataclass(frozen=True)
class StreamSet:
    role: int
    start: int
    count: int

    @classmethod
    def from_dict(cls, d: dict) -> "StreamSet":
        s = cls(int(d["role"]), int(d.get("start", 0)), int(d["count"]))
        if s.role not in (0, 1) or s.start < 0 or s.count < 0:
            raise ConfigError(f"invalid stream set {d}")
        return s

    def indices(self) -> range:
        return range(self.start, self.start + self.count)

    def overlaps(self, other: "StreamSet") -> bool:
        return self.role == other.role and max(self.start, other.start) < min(
            self.start + self.count, other.start + other.count)


def validate_config(cfg: dict, protocol: dict) -> None:
    for key in ("experiment_id", "experiment_number", "label", "mode", "cells"):
        if key not in cfg:
            raise ConfigError(f"config is missing '{key}'")
    if cfg["label"] not in ("exploratory", "confirmatory"):
        raise ConfigError("label must be 'exploratory' or 'confirmatory'")
    if cfg["mode"] not in ("tuned", "fixed"):
        raise ConfigError("mode must be 'tuned' or 'fixed'")
    if cfg["label"] == "confirmatory" and not protocol.get("frozen"):
        raise ProtocolNotFrozen(
            f"{cfg['experiment_id']}: protocol {protocol.get('path')!r} is not frozen (G-FREEZE): "
            f"{protocol.get('reason') or 'not frozen'}. Confirmatory runs are refused unless the registry "
            "and research/freeze.json record the protocol, the main protocol and this exact config.")
    ev = StreamSet.from_dict(cfg["eval_streams"])
    if cfg["label"] != "confirmatory" and ev.role == ROLE_EVAL:
        raise ConfigError("exploratory configs may not use evaluation streams (role 1)")
    if cfg["mode"] == "tuned":
        tu = StreamSet.from_dict(cfg["tune_streams"])
        if tu.overlaps(ev):
            raise ConfigError("tuning and evaluation stream sets overlap")
        if tu.count < 1:
            raise ConfigError("tuning needs at least one stream")
    else:
        if not cfg.get("fixed_policies"):
            raise ConfigError("mode 'fixed' needs fixed_policies")
    unknown = set(cfg.get("grid", {})) - set(GRID_KEYS)
    if unknown:
        raise ConfigError(f"unknown grid keys {sorted(unknown)}")
    ids = [c["id"] for c in cfg["cells"]]
    if len(set(ids)) != len(ids):
        raise ConfigError("cell ids must be unique")


def _streams(sp: ScenarioParams, exp: int, cell: int, ss: StreamSet) -> list[DemandStream]:
    """Streams with spawn keys (exp, cell, role, index)."""
    return [generate_stream(sp, SeedKey(exp, cell, ss.role, i)) for i in ss.indices()]


def _eval_runs(run_set_id: str, cell_id: str, arm: str, pol: Policy, streams: list[DemandStream],
               sp: ScenarioParams, role_name: str) -> list[dict]:
    runs = []
    for s in streams:
        idx = s.seed_key[3]
        rid = f"{run_set_id}/{cell_id}/{arm}/{role_name}{idx:04d}"
        rec = {"run_id": rid, "arm": arm, "role": role_name, "stream_index": int(idx),
               "seed_key": list(s.seed_key), "stream_sha256": s.sha256(), "policy": policy_to_dict(pol),
               "status": "ok", "error": None, "metrics": None}
        try:
            rec["metrics"] = compute_metrics(simulate(s, sp, pol), sp)
        except Exception:  # recorded, never silently dropped
            rec["status"] = "failed"
            rec["error"] = traceback.format_exc(limit=5)
        runs.append(rec)
    return runs


def _metric_vec(runs: list[dict], arm: str, metric: str) -> dict[int, float]:
    return {r["stream_index"]: r["metrics"][metric] for r in runs
            if r["arm"] == arm and r["status"] == "ok" and r["metrics"][metric] is not None}


def _contrast(runs, arm, comp, metric, level, boot, sesoi) -> dict | None:
    a, b = _metric_vec(runs, arm, metric), _metric_vec(runs, comp, metric)
    common = sorted(set(a) & set(b))
    if len(common) < 2:
        return None
    d = np.array([a[i] - b[i] for i in common])
    s = summarise(d, level, boot["resamples"], boot["seed"])
    base_mean = float(np.mean([b[i] for i in common]))
    rel = s.mean_diff / base_mean if base_mean != 0 else None
    cls = None
    if sesoi is not None and base_mean > 0:
        cls = classify(s.boot_ci, s.mean_diff, sesoi * base_mean)
    return {"arm": arm, "comparator": comp, "metric": metric, "n": s.n, "mean_diff": s.mean_diff,
            "sd_diff": s.sd_diff, "d_z": s.d_z, "level": level, "boot_ci": list(s.boot_ci),
            "t_ci": list(s.t_ci), "relative_effect": rel, "classification": cls}


def run_experiment(cfg: dict, protocol: dict, run_set_id: str) -> dict:
    """Execute a config; return the result document body (without manifest path)."""
    validate_config(cfg, protocol)
    exp = int(cfg["experiment_number"])
    base = ScenarioParams.from_dict(cfg.get("base_scenario", {}))
    families = cfg.get("families", ["FIX", "OCC", "DRP"])
    g = cfg.get("grid", {})
    boot = {"resamples": 10_000, "seed": 20261124, "primary_level": 0.975, "secondary_level": 0.95,
            **cfg.get("bootstrap", {})}
    sesoi = cfg.get("sesoi_fraction", 0.01)
    ev_set = StreamSet.from_dict(cfg["eval_streams"])
    tuned_cache: dict[str, dict[str, Policy]] = {}
    cells_out = []
    for cell in cfg["cells"]:
        cid, cidx = cell["id"], int(cell["index"])
        sp = base.with_(**cell.get("scenario", {}))
        timing = {"stream_generation_s": 0.0, "tuning_s": 0.0, "tuning_runs": 0, "eval_s": 0.0, "eval_runs": 0}
        evaluate = bool(cell.get("evaluate", True))
        t0 = time.perf_counter()
        ev_streams = _streams(sp, exp, cidx, ev_set) if evaluate else []
        timing["stream_generation_s"] += time.perf_counter() - t0
        # tuning streams may borrow another experiment's keys (EXP-003 reuses EXP-001 tuning)
        tk = cell.get("tune_key", {})
        tu_exp, tu_cell = int(tk.get("experiment", exp)), int(tk.get("cell", cidx))
        arms: dict[str, Policy] = {}
        tuning_out = []

        def do_tune(arm: str, family: str, streams, **gkw):
            t1 = time.perf_counter()
            configs = grid(family, **{**g, **gkw})
            R = revenue_matrix(configs, streams, sp)
            tr = select(family, configs, R)
            timing["tuning_s"] += time.perf_counter() - t1
            timing["tuning_runs"] += R.size
            tuning_out.append({"arm": arm, "family": family, "n_configs": len(configs), "n_streams": len(streams),
                               "tuned_in_cell": cid, "selected_index": tr.best_index,
                               "selected": policy_to_dict(tr.best), "at_grid_edge": tr.at_grid_edge,
                               "mean_revenue": [float(x) for x in tr.mean_revenue]})
            return tr.best

        if cfg["mode"] == "fixed":
            for fp in cfg["fixed_policies"]:
                arms[fp["arm"]] = policy_from_dict(fp)
        else:
            src = cell.get("tune_in")
            need_tune_here = src is None or cell.get("retuned_fix_reference") or cfg.get("fix_coarse_sensitivity")
            tu_streams = []
            if need_tune_here:
                t0 = time.perf_counter()
                tu_streams = _streams(sp, tu_exp, tu_cell, StreamSet.from_dict(cfg["tune_streams"]))
                timing["stream_generation_s"] += time.perf_counter() - t0
            if src is None:
                for fam in families:
                    arms[fam] = do_tune(fam, fam, tu_streams)
                tuned_cache[cid] = {f: arms[f] for f in families}
            else:
                if src not in tuned_cache:
                    raise ConfigError(f"cell {cid}: tune_in {src!r} must name an earlier tuned cell")
                arms.update(tuned_cache[src])
                for fam in families:
                    tuning_out.append(next(t for c in cells_out if c["cell_id"] == src for t in c["tuning"]
                                           if t["arm"] == fam))
                if cell.get("retuned_fix_reference"):
                    arms["FIX_retuned"] = do_tune("FIX_retuned", "FIX", tu_streams)
            if cfg.get("fix_coarse_sensitivity") and "FIX" in families:
                # FIX re-tuned on the p0 values shared by OCC and DRP: "FIX9" in
                # draft v0.1 (9 p0 values), "FIX6" in frozen v1.0 (6 p0 values).
                coarse = f"FIX{int(g.get('p0_n', 9))}"
                arms[coarse] = do_tune(coarse, "FIX", tu_streams, fix_n=int(g.get("p0_n", 9)))
        t0 = time.perf_counter()
        runs = []
        for arm, pol in arms.items():
            runs += _eval_runs(run_set_id, cid, arm, pol, ev_streams, sp, ROLE_NAMES[ev_set.role])
        timing["eval_s"] = time.perf_counter() - t0
        timing["eval_runs"] = len(runs)
        contrasts = []
        if "FIX" in arms:
            comps = [("FIX", sesoi)] + [(c, sesoi) for c in arms if c.startswith("FIX") and c != "FIX"]
            for comp, ses in comps:
                for arm in arms:
                    if arm.startswith("FIX"):
                        continue
                    c = _contrast(runs, arm, comp, "revenue", boot["primary_level"], boot, ses)
                    if c:
                        contrasts.append(c)
            for arm in arms:
                if arm.startswith("FIX"):
                    continue
                for m in SECONDARY_METRICS:
                    c = _contrast(runs, arm, "FIX", m, boot["secondary_level"], boot, None)
                    if c:
                        contrasts.append(c)
        cells_out.append({"cell_id": cid, "cell_index": cidx, "scenario": sp.to_dict(), "tuning": tuning_out,
                          "runs": runs, "contrasts": contrasts, "timing": timing})
    failures = sum(1 for c in cells_out for r in c["runs"] if r["status"] == "failed")
    return {"cells": cells_out, "failures": failures}


def planned_run_counts(cfg: dict) -> dict[str, int]:
    """Number of simulation runs a config implies (for runtime projection)."""
    families = cfg.get("families", ["FIX", "OCC", "DRP"])
    n_fam = len(families)
    g = cfg.get("grid", {})
    n_cfg_all = sum(len(grid(f, **g)) for f in families)
    n_fix = len(grid("FIX", **g))
    p0 = int(g.get("p0_n", 9))
    tu = int(cfg.get("tune_streams", {}).get("count", 0))
    ev = int(cfg["eval_streams"]["count"])
    tuning = evals = 0
    for cell in cfg["cells"]:
        arms = n_fam
        if cfg["mode"] == "fixed":
            arms = len(cfg["fixed_policies"])
        elif cell.get("tune_in") is None:
            tuning += n_cfg_all * tu
        if cell.get("retuned_fix_reference"):
            tuning += n_fix * tu
            arms += 1
        if cfg.get("fix_coarse_sensitivity"):
            tuning += p0 * tu
            arms += 1
        if cell.get("evaluate", True):
            evals += arms * ev
    return {"tuning_runs": tuning, "eval_runs": evals, "total_runs": tuning + evals}


__all__ = ["run_experiment", "planned_run_counts", "validate_config", "ConfigError", "ProtocolNotFrozen"]
