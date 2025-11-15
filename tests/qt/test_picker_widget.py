"""Integration tests for the DateRangePicker widget."""

from __future__ import annotations

from typing import Any, cast

from date_range_popover.api.config import DatePickerConfig, DateRange
from date_range_popover.api.picker import DateRangePicker
from date_range_popover.managers.state_manager import PickerMode
from PyQt6.QtCore import QDate
from pytestqt.qtbot import QtBot


def test_picker_emits_date_selected_signal(qtbot: QtBot) -> None:
    """Wiring between the state manager and widget signals should stay intact."""
    picker = DateRangePicker()
    qtbot.addWidget(picker)
    target = QDate.currentDate().addDays(-2)

    with qtbot.waitSignal(picker.date_selected, timeout=1000):
        cast(Any, picker)._state_manager.select_date(target)

    assert picker.selected_date == target


def test_picker_applies_initial_range_and_mode(qtbot: QtBot) -> None:
    """Initial configuration should sync to the widget state."""
    start = QDate(2024, 6, 1)
    end = QDate(2024, 6, 10)
    config = DatePickerConfig(
        initial_range=DateRange(start_date=start, end_date=end),
        mode=PickerMode.CUSTOM_RANGE,
    )
    picker = DateRangePicker(config=config)
    qtbot.addWidget(picker)

    selected = picker.selected_range
    assert selected.start_date == start
    assert selected.end_date == end
    assert cast(Any, picker)._state_manager.state.mode is PickerMode.CUSTOM_RANGE


def test_set_mode_updates_sliding_track(qtbot: QtBot) -> None:
    """Calling set_mode should update both state and the track indicator."""
    picker = DateRangePicker()
    qtbot.addWidget(picker)

    picker.set_mode(PickerMode.CUSTOM_RANGE)

    layout = cast(Any, picker)._layout_config
    target_position = layout.date_indicator_width + layout.button_gap
    target_width = layout.custom_range_indicator_width

    def track_reached() -> bool:
        internal_picker = cast(Any, picker)
        return bool(
            internal_picker._sliding_track.current_position == target_position
            and internal_picker._sliding_track.current_width == target_width
        )

    qtbot.waitUntil(track_reached, timeout=1500)
    assert cast(Any, picker)._state_manager.state.mode is PickerMode.CUSTOM_RANGE


def test_cancel_button_emits_cancelled_signal(qtbot: QtBot) -> None:
    """User-facing buttons should emit the widget's cancelled signal."""
    picker = DateRangePicker()
    qtbot.addWidget(picker)

    with qtbot.waitSignal(picker.cancelled, timeout=1000):
        cast(Any, picker)._cancel_button.click()
