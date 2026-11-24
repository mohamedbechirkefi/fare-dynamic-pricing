# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Pricing policies (research/protocol.md section 4).

A policy is an immutable parameter record. `controller(params)` returns a fresh
stateful controller for one season. The controller observes only the period t,
the current stock x_t and its own past prices and sales (never valuations or
arrivals of non-buyers).

- FIX(p):        p_t = p.
- OCC(p0, k):    p_t = clip(p0 * exp(k * (f_t - e_t))), f_t = (C - x_t) / C,
                 e_t = (t - 1) / T.
- DRP(p0, eta):  p_1 = p0; after period t, r_hat <- w * s_t + (1 - w) * r_hat
                 (w = 0.3, r_hat initialised at C / T), r*_t = x_t / (T - t + 1)
                 with x_t the stock at the start of period t, and
                 p_{t+1} = clip(p_t * ((r_hat + 0.5) / (r*_t + 0.5)) ** eta).

k = 0 and eta = 0 reproduce FIX(p0) exactly (nesting, tested).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol

from .params import ScenarioParams


class PolicyError(ValueError):
    """Raised for invalid policy parameters."""


def clip(p: float, lo: float, hi: float) -> float:
    return lo if p < lo else hi if p > hi else p


class Controller(Protocol):
    def price(self, t: int, x: int) -> float: ...
    def observe(self, t: int, x_start: int, sold: int) -> None: ...


def _check_positive(name: str, v: float) -> None:
    if not (isinstance(v, (int, float)) and math.isfinite(v) and v > 0):
        raise PolicyError(f"{name} must be a finite positive number, got {v!r}")


def _check_nonneg(name: str, v: float) -> None:
    if not (isinstance(v, (int, float)) and math.isfinite(v) and v >= 0):
        raise PolicyError(f"{name} must be a finite non-negative number, got {v!r}")


@dataclass(frozen=True)
class FIX:
    p: float
    family = "FIX"

    def __post_init__(self) -> None:
        _check_positive("p", self.p)

    def params_dict(self) -> dict[str, Any]:
        return {"p": float(self.p)}

    def controller(self, sp: ScenarioParams) -> Controller:
        return _FixCtl(clip(float(self.p), sp.p_min, sp.p_max))


class _FixCtl:
    __slots__ = ("p",)

    def __init__(self, p: float) -> None:
        self.p = p

    def price(self, t: int, x: int) -> float:
        return self.p

    def observe(self, t: int, x_start: int, sold: int) -> None:
        return None


@dataclass(frozen=True)
class OCC:
    p0: float
    k: float
    family = "OCC"

    def __post_init__(self) -> None:
        _check_positive("p0", self.p0)
        _check_nonneg("k", self.k)

    def params_dict(self) -> dict[str, Any]:
        return {"p0": float(self.p0), "k": float(self.k)}

    def controller(self, sp: ScenarioParams) -> Controller:
        return _OccCtl(float(self.p0), float(self.k), sp)


class _OccCtl:
    __slots__ = ("p0", "k", "C", "T", "lo", "hi")

    def __init__(self, p0: float, k: float, sp: ScenarioParams) -> None:
        self.p0, self.k, self.C, self.T = p0, k, sp.C, sp.T
        self.lo, self.hi = sp.p_min, sp.p_max

    def price(self, t: int, x: int) -> float:
        f = (self.C - x) / self.C if self.C > 0 else 1.0
        e = (t - 1) / self.T
        return clip(self.p0 * math.exp(self.k * (f - e)), self.lo, self.hi)

    def observe(self, t: int, x_start: int, sold: int) -> None:
        return None


@dataclass(frozen=True)
class DRP:
    p0: float
    eta: float
    weight: float = 0.3
    family = "DRP"

    def __post_init__(self) -> None:
        _check_positive("p0", self.p0)
        _check_nonneg("eta", self.eta)
        if not (0.0 < self.weight <= 1.0):
            raise PolicyError(f"weight must lie in (0, 1], got {self.weight!r}")

    def params_dict(self) -> dict[str, Any]:
        return {"p0": float(self.p0), "eta": float(self.eta), "weight": float(self.weight)}

    def controller(self, sp: ScenarioParams) -> Controller:
        return _DrpCtl(float(self.p0), float(self.eta), float(self.weight), sp)


class _DrpCtl:
    __slots__ = ("p", "eta", "w", "r_hat", "T", "lo", "hi")

    def __init__(self, p0: float, eta: float, w: float, sp: ScenarioParams) -> None:
        self.p = clip(p0, sp.p_min, sp.p_max)
        self.eta, self.w, self.T = eta, w, sp.T
        self.r_hat = sp.C / sp.T
        self.lo, self.hi = sp.p_min, sp.p_max

    def price(self, t: int, x: int) -> float:
        return self.p

    def observe(self, t: int, x_start: int, sold: int) -> None:
        self.r_hat = self.w * sold + (1.0 - self.w) * self.r_hat
        r_star = x_start / (self.T - t + 1)
        ratio = (self.r_hat + 0.5) / (r_star + 0.5)
        self.p = clip(self.p * ratio ** self.eta, self.lo, self.hi)


Policy = FIX | OCC | DRP


def policy_from_dict(d: dict[str, Any]) -> Policy:
    fam = d.get("family")
    params = d.get("params", {})
    try:
        if fam == "FIX":
            return FIX(**params)
        if fam == "OCC":
            return OCC(**params)
        if fam == "DRP":
            return DRP(**params)
    except TypeError as exc:
        raise PolicyError(f"bad parameters for {fam}: {exc}") from exc
    raise PolicyError(f"unknown policy family {fam!r}")


def policy_to_dict(p: Policy) -> dict[str, Any]:
    return {"family": p.family, "params": p.params_dict()}
