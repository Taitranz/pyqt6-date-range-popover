"""Unit tests for year range utility helpers."""

from __future__ import annotations

from PyQt6.QtCore import QDate

from date_range_popover.components.calendar.year_range_utils import (
    clamp_year_range_start,
    compute_year_range_start,
    year_range_limits,
)


def test_compute_year_range_start_aligns_to_span() -> None:
    """The helper should snap arbitrary years to the configured span."""

    assert compute_year_range_start(2024, 20, max_year=9999) == 2021
    assert compute_year_range_start(2001, 20, max_year=9999) == 2001
    assert compute_year_range_start(1999, 20, max_year=9999) == 1981


def test_compute_year_range_start_clamps_to_max_year() -> None:
    """Ranges should never exceed the configured max year."""

    assert compute_year_range_start(9999, 20, max_year=9999) == 9980
    assert compute_year_range_start(12000, 20, max_year=9999) == 9980


def test_year_range_limits_respect_min_max_dates() -> None:
    """Min/max dates should shrink the allowed range interval."""

    min_date = QDate(1950, 1, 1)
    max_date = QDate(2055, 1, 1)
    min_start, max_start = year_range_limits(
        min_date,
        max_date,
        20,
        max_year=9999,
    )
    assert min_start == 1941
    assert max_start == 2041


def test_clamp_year_range_start_obeys_limits() -> None:
    """Values outside the allowed bounds should be clamped."""

    min_date = QDate(2000, 1, 1)
    max_date = QDate(2100, 1, 1)
    assert clamp_year_range_start(
        1901,
        min_date,
        max_date,
        20,
        max_year=9999,
    ) == 1981
    assert clamp_year_range_start(
        2201,
        min_date,
        max_date,
        20,
        max_year=9999,
    ) == 2081

