"""Behavioural tests for DatePickerStateManager."""

from __future__ import annotations

import pytest
from PyQt6.QtCore import QDate
from PyQt6.QtTest import QSignalSpy

from date_range_popover.managers.state_manager import DatePickerStateManager, PickerMode
from date_range_popover.utils import first_of_month

pytestmark = pytest.mark.usefixtures("qapp")


def test_select_date_updates_state_and_emits_signal() -> None:
    """select_date should emit the signal and update the snapshot."""
    manager = DatePickerStateManager()
    target = QDate.currentDate().addDays(3)
    spy = QSignalSpy(manager.selected_date_changed)

    manager.select_date(target)

    assert len(spy) == 1
    assert spy[-1][0] == target
    assert manager.state.selected_dates == (target, None)
    assert manager.state.visible_month == first_of_month(target)


def test_select_range_emits_correct_bounds() -> None:
    """select_range should normalize ranges and notify observers."""
    manager = DatePickerStateManager()
    start = QDate(2024, 2, 10)
    end = QDate(2024, 2, 20)
    spy = QSignalSpy(manager.selected_range_changed)

    manager.select_range(end, start)  # intentionally reversed

    assert len(spy) == 1
    normalized_start, normalized_end = spy[-1]
    assert normalized_start == start
    assert normalized_end == end
    assert manager.state.selected_dates == (start, end)
    assert manager.state.visible_month == first_of_month(start)


def test_set_mode_emits_only_on_change() -> None:
    """The manager should emit mode_changed only when the value changes."""
    manager = DatePickerStateManager()
    spy = QSignalSpy(manager.mode_changed)

    manager.set_mode(PickerMode.CUSTOM_RANGE)

    assert len(spy) == 1
    assert spy[-1][0] is PickerMode.CUSTOM_RANGE

    # Re-sending the same mode should be a no-op.
    manager.set_mode(PickerMode.CUSTOM_RANGE)
    assert len(spy) == 1
    assert manager.state.mode is PickerMode.CUSTOM_RANGE


def test_reset_clamps_to_bounds_and_emits_signals() -> None:
    """reset should clamp to configured bounds and broadcast the new state."""
    today = QDate.currentDate()
    min_date = today.addDays(-5)
    max_date = today.addDays(-1)
    manager = DatePickerStateManager(min_date=min_date, max_date=max_date)
    spy = QSignalSpy(manager.state_changed)

    # Move the state away from the defaults.
    manager.select_date(max_date)

    manager.reset()

    assert len(spy) == 1
    selected_start, selected_end = manager.state.selected_dates
    assert selected_start == max_date  # default date is clamped to max bound
    assert selected_end is None
    assert manager.state.mode is PickerMode.DATE

