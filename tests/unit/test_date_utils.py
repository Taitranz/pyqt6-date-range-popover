"""Tests for date_range_popover.utils.date_utils."""

from __future__ import annotations

import pytest
from date_range_popover.exceptions import InvalidDateError
from date_range_popover.utils.date_utils import (
    copy_qdate,
    first_of_month,
    iter_month_days,
    normalize_range,
)
from PyQt6.QtCore import QDate


def test_copy_qdate_returns_new_instance() -> None:
    """copy_qdate should return a distinct but equal QDate."""
    original = QDate(2024, 6, 15)
    cloned = copy_qdate(original)
    assert cloned == original
    assert cloned is not original


def test_copy_qdate_rejects_invalid_dates() -> None:
    """Invalid dates should raise an InvalidDateError when copied."""
    with pytest.raises(InvalidDateError):
        copy_qdate(QDate())


def test_first_of_month_rejects_invalid_dates() -> None:
    """first_of_month should guard against invalid inputs."""
    with pytest.raises(InvalidDateError):
        first_of_month(QDate())


def test_normalize_range_swaps_and_copies_inputs() -> None:
    """normalize_range should order inputs and return defensive copies."""
    later = QDate(2024, 7, 20)
    earlier = QDate(2024, 7, 10)
    start, end = normalize_range(later, earlier)
    assert start == earlier
    assert end == later
    assert start is not earlier
    assert end is not later


def test_normalize_range_rejects_invalid_dates() -> None:
    """Invalid endpoints should raise InvalidDateError."""
    with pytest.raises(InvalidDateError):
        normalize_range(QDate(), QDate(2024, 8, 1))


def test_iter_month_days_emits_full_grid() -> None:
    """iter_month_days should always produce a 6x7 grid of dates."""
    month = QDate(2024, 2, 1)
    days = list(iter_month_days(month))
    assert len(days) == 42
    assert days[0].dayOfWeek() == 1  # The grid should start on Monday
    assert days[-1].dayOfWeek() == 7
