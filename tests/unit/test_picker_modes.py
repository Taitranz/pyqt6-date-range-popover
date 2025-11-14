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
