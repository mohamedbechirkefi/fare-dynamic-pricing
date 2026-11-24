# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Scenario parameters with explicit units and validation.

Units: periods are abstract simulation periods; prices, valuations and revenue
are abstract currency units; stock is in units of capacity.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, fields, replace
from typing import Any, Mapping

ARRIVAL_PROFILES = ("linear", "linear_reversed", "flat")


class ParameterError(ValueError):
    """Raised when a scenario parameter is outside its valid domain."""


@dataclass(frozen=True)
class ScenarioParams:
    """One scenario cell. Defaults are the draft base cell (protocol section 3)."""

    T: int = 60                      # number of booking periods
    C: int = 100                     # initial stock (units)
    kappa: float = 2.0               # expected arrivals / capacity (dimensionless)
    demand_scale: float = 1.0        # extra multiplier on expected arrivals (EXP-003 shifts)
    w_L: float = 0.7                 # share of low-valuation (early) segment
    m_L: float = 100.0               # median valuation, segment L (currency)
    m_H: float = 200.0               # median valuation, segment H (currency)
    sigma_v: float = 0.5             # log-sd of valuations
    sigma_M: float = 0.25            # log-sd of the stream-level demand multiplier
    surge_prob: float = 0.05         # probability that a period starts a surge
    surge_len: int = 3               # surge length (periods)
    surge_factor: float = 1.8        # arrival-intensity multiplier during a surge
    arrival_profile: str = "linear"  # L decreasing / H increasing ("linear"), reversed, or flat
    p_min: float = 30.0              # lower price bound (currency)
    p_max: float = 600.0             # upper price bound (currency)

    def __post_init__(self) -> None:
        def check(cond: bool, msg: str) -> None:
            if not cond:
                raise ParameterError(msg)

        for f in fields(self):
            v = getattr(self, f.name)
            if isinstance(v, float):
                check(math.isfinite(v), f"{f.name} must be finite, got {v!r}")
        check(isinstance(self.T, int) and self.T >= 1, f"T must be an integer >= 1, got {self.T!r}")
        check(isinstance(self.C, int) and self.C >= 0, f"C must be an integer >= 0, got {self.C!r}")
        check(self.kappa >= 0, "kappa must be >= 0")
        check(self.demand_scale >= 0, "demand_scale must be >= 0")
        check(0.0 <= self.w_L <= 1.0, "w_L must lie in [0, 1]")
        check(self.m_L > 0 and self.m_H > 0, "segment medians must be > 0")
        check(self.sigma_v >= 0 and self.sigma_M >= 0, "sigma_v and sigma_M must be >= 0")
        check(0.0 <= self.surge_prob <= 1.0, "surge_prob must lie in [0, 1]")
        check(isinstance(self.surge_len, int) and self.surge_len >= 1, "surge_len must be an integer >= 1")
        check(self.surge_factor > 0, "surge_factor must be > 0")
        check(self.arrival_profile in ARRIVAL_PROFILES, f"arrival_profile must be one of {ARRIVAL_PROFILES}")
        check(0 < self.p_min <= self.p_max, "price bounds must satisfy 0 < p_min <= p_max")

    @property
    def expected_arrivals(self) -> float:
        """A = kappa * demand_scale * C (expected arrivals before shocks)."""
        return self.kappa * self.demand_scale * self.C

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_(self, **changes: Any) -> "ScenarioParams":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "ScenarioParams":
        known = {f.name for f in fields(cls)}
        unknown = set(d) - known
        if unknown:
            raise ParameterError(f"unknown scenario parameters: {sorted(unknown)}")
        return cls(**dict(d))
