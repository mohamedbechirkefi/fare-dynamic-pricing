# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Shared fixtures and Hypothesis strategies."""

from __future__ import annotations

from hypothesis import strategies as st

from fare.params import ScenarioParams
from fare.policies import DRP, FIX, OCC
from fare.streams import make_stream

PRICE = st.floats(min_value=1.0, max_value=1000.0, allow_nan=False)


@st.composite
def market(draw):
    """A small random scenario, hand-built stream and policy."""
    T = draw(st.integers(1, 8))
    C = draw(st.integers(0, 6))
    p_min = draw(st.floats(1.0, 100.0))
    p_max = draw(st.floats(p_min, 500.0))
    sp = ScenarioParams(T=T, C=C, p_min=p_min, p_max=p_max)
    n = draw(st.integers(0, 25))
    periods = sorted(draw(st.lists(st.integers(1, T), min_size=n, max_size=n)))
    arr = [(t, draw(st.integers(0, 1)), draw(st.floats(0.0, 800.0))) for t in periods]
    stream = make_stream(T, arr)
    fam = draw(st.sampled_from(["FIX", "OCC", "DRP"]))
    if fam == "FIX":
        pol = FIX(draw(PRICE))
    elif fam == "OCC":
        pol = OCC(draw(PRICE), draw(st.floats(0.0, 8.0)))
    else:
        pol = DRP(draw(PRICE), draw(st.floats(0.0, 2.0)))
    return sp, stream, pol
