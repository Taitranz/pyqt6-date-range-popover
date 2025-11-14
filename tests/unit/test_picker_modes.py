"""Picker mode transition regression tests."""

from __future__ import annotations

import pytest
from date_range_popover.managers.state_manager import DatePickerStateManager, PickerMode
from PyQt6.QtCore import QDate
from PyQt6.QtTest import QSignalSpy

pytestmark = pytest.mark.usefixtures("qapp")


def test_mode_transitions_emit_signals_once_per_change() -> None:
    """Switching modes should emit mode/state signals exactly once per transition."""
    manager = DatePickerStateManager()
    mode_spy = QSignalSpy(manager.mode_changed)
    state_spy = QSignalSpy(manager.state_changed)

    manager.set_mode(PickerMode.CUSTOM_RANGE)
    manager.set_mode(PickerMode.DATE)

    assert len(mode_spy) == 2
    assert mode_spy[0][0] is PickerMode.CUSTOM_RANGE
    assert mode_spy[1][0] is PickerMode.DATE
    # state_changed fires for each transition as well
    assert len(state_spy) >= 2


def test_redundant_mode_assignment_is_ignored() -> None:
    """Setting the same mode repeatedly should not emit additional signals."""
    manager = DatePickerStateManager()
    spy = QSignalSpy(manager.mode_changed)

    manager.set_mode(PickerMode.DATE)
    manager.set_mode(PickerMode.DATE)

    assert len(spy) == 0


def test_range_selection_survives_mode_switches() -> None:
    """Selections should remain intact while switching between range/single modes."""
    manager = DatePickerStateManager()
    start = QDate(2024, 5, 10)
    end = QDate(2024, 5, 14)

    manager.select_range(start, end)
    manager.set_mode(PickerMode.CUSTOM_RANGE)
    manager.set_mode(PickerMode.DATE)

    assert manager.state.selected_dates == (start, end)


def test_single_date_selection_survives_full_cycle() -> None:
    """DATE -> CUSTOM_RANGE -> DATE should keep an existing single-date selection."""
    manager = DatePickerStateManager()
    selection = QDate(2024, 7, 4)
    mode_spy = QSignalSpy(manager.mode_changed)
    date_spy = QSignalSpy(manager.selected_date_changed)

    manager.select_date(selection)
    manager.set_mode(PickerMode.CUSTOM_RANGE)
    manager.set_mode(PickerMode.DATE)

    assert manager.state.mode is PickerMode.DATE
    assert manager.state.selected_dates == (selection, None)
    assert [entry[0] for entry in mode_spy] == [
        PickerMode.CUSTOM_RANGE,
        PickerMode.DATE,
    ]
    # Only the explicit select_date call should emit the date signal.
    assert len(date_spy) == 1


def test_range_selection_restored_after_multi_switch() -> None:
    """Range selections stay normalized even after multiple mode hops."""
    manager = DatePickerStateManager()
    start = QDate(2024, 9, 1)
    end = QDate(2024, 9, 12)
    manager.set_mode(PickerMode.CUSTOM_RANGE)
    manager.select_range(start, end)
    manager.set_mode(PickerMode.DATE)
    manager.set_mode(PickerMode.CUSTOM_RANGE)

    captured_start, captured_end = manager.state.selected_dates
    assert captured_start == start
    assert captured_end == end
