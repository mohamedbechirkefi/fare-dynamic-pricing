# SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0
"""Number trace used by the M4 evidence audit (fare.audit)."""

from fare.audit import traceable_strings, untraced


def test_decimal_percent_and_grouped_numbers_trace():
    known = traceable_strings([407.04456676154973, 0.03474391547778375, 4000, 415727616])
    text = "OCC +407.04 (+3.47%), 407.0, n = 4,000, peak 396.5 MiB"
    assert untraced(text, known) == []


def test_untraced_numbers_are_reported_with_line():
    known = traceable_strings([407.04456676154973])
    text = "first line 407.04\nsecond line 7.5 and 12,345"
    assert untraced(text, known) == [(2, "7.5"), (2, "12,345")]


def test_rounding_must_match_displayed_precision():
    known = traceable_strings([1.2345])
    assert untraced("1.23", known) == []
    assert untraced("1.24", known) == [(1, "1.24")]


def test_plain_small_integers_and_identifiers_are_not_checked():
    known = traceable_strings([])
    assert untraced("EXP-001 cell 3 of 9 on 2026-11-25", known) == []
