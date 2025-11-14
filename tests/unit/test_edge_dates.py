"""Edge-case coverage for date and time handling."""

from __future__ import annotations

import pytest
from date_range_popover.components.inputs.time_completer import generate_time_options
from date_range_popover.exceptions import InvalidDateError
from date_range_popover.managers.state_manager import DatePickerStateManager
from PyQt6.QtCore import QDate

pytestmark = pytest.mark.usefixtures("qapp")


def test_select_date_rejects_values_outside_min_and_max_bounds() -> None:
    """State manager should refuse selections outside the configured window."""
    min_date = QDate(2024, 1, 10)
    max_date = QDate(2024, 1, 20)
    manager = DatePickerStateManager(min_date=min_date, max_date=max_date)

    with pytest.raises(InvalidDateError):
        manager.select_date(min_date.addDays(-1))

    with pytest.raises(InvalidDateError):
        manager.select_date(max_date.addDays(1))


def test_select_date_accepts_leap_day_in_leap_year() -> None:
    """Feb 29 on a leap year should be treated as a perfectly valid selection."""
    manager = DatePickerStateManager()
    leap_day = QDate(2024, 2, 29)

    manager.select_date(leap_day)

    start, end = manager.state.selected_dates
    assert start == leap_day
    assert end is None


def test_select_date_rejects_nonexistent_leap_day() -> None:
    """Invalid leap-day candidates should raise InvalidDateError."""
    manager = DatePickerStateManager()
    nonexistent = QDate(2023, 2, 29)  # Non-leap year

    with pytest.raises(InvalidDateError):
        manager.select_date(nonexistent)


def test_select_range_normalizes_year_boundary() -> None:
    """Ranges that cross over a year boundary should stay normalized."""
    manager = DatePickerStateManager()
    start = QDate(2024, 12, 31)
    end = QDate(2025, 1, 2)

    manager.select_range(end, start)  # intentionally reversed

    normalized_start, normalized_end = manager.state.selected_dates
    assert normalized_start == start
    assert normalized_end == end


def test_time_options_cover_daylight_savings_gap() -> None:
    """
    The generated time list should include the 2 AM hour even though many regions
    skip or repeat it during DST transitions. This keeps the UI consistent across
    locales.
    """

    options = generate_time_options(30)

    assert "01:30" in options
    assert "02:00" in options
    assert "02:30" in options
