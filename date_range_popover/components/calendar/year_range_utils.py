"""
Utility helpers for computing the year ranges used by
:class:`CalendarWidget`.

These helpers keep the arithmetic separate from the widget itself so the
logic can be unit-tested in isolation and reused by other calendar
surfaces if needed.
"""

from __future__ import annotations

from PyQt6.QtCore import QDate


def compute_year_range_start(year: int, range_size: int, *, max_year: int) -> int:
    """
    Compute the first year for the range that should contain ``year``.

    The return value is clamped to the valid
    ``[1, max_year - range_size + 1]`` interval so the range never
    overflows the supported year span.
    """

    span = max(1, range_size)
    upper_bound = max(1, max_year - span + 1)
    if year < 1:
        return 1
    bucket = ((year - 1) // span) * span + 1
    return min(bucket, upper_bound)


def year_range_limits(
    min_date: QDate | None,
    max_date: QDate | None,
    range_size: int,
    *,
    max_year: int,
) -> tuple[int, int]:
    """
    Return the minimum/maximum allowed starting year for the calendar
    grid.

    The minimum bound is derived from ``min_date`` if provided;
    otherwise it falls back to ``1``. The maximum bound always
    respects ``max_year`` and is additionally constrained by
    ``max_date`` when supplied.
    """

    span = max(1, range_size)
    min_start = 1
    if min_date is not None and min_date.isValid():
        min_start = compute_year_range_start(min_date.year(), span, max_year=max_year)

    max_start = max(1, max_year - span + 1)
    if max_date is not None and max_date.isValid():
        max_start = min(
            max_start,
            compute_year_range_start(max_date.year(), span, max_year=max_year),
        )

    min_start = min(min_start, max_start)
    return min_start, max_start


def clamp_year_range_start(
    proposed_start: int,
    min_date: QDate | None,
    max_date: QDate | None,
    range_size: int,
    *,
    max_year: int,
) -> int:
    """
    Clamp ``proposed_start`` to the permitted year-range start interval.
    """

    min_start, max_start = year_range_limits(
        min_date,
        max_date,
        range_size,
        max_year=max_year,
    )
    return max(min_start, min(proposed_start, max_start))


__all__ = [
    "clamp_year_range_start",
    "compute_year_range_start",
    "year_range_limits",
]
