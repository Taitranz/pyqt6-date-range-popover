from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Tuple, cast

from PyQt6.QtCore import QDate, QObject, pyqtSignal

from ..validation import validate_date_range, validate_qdate
from ..utils import first_of_month, get_logger

LOGGER = get_logger(__name__)


class PickerMode(Enum):
    """Supported picker modes."""

    DATE = auto()
    CUSTOM_RANGE = auto()


@dataclass(frozen=True, slots=True)
class DatePickerState:
    """Immutable state snapshot for the picker."""

    mode: PickerMode
    selected_dates: Tuple[QDate | None, QDate | None]
    visible_month: QDate


class DatePickerStateManager(QObject):
    """Centralized store for picker state."""

    mode_changed = pyqtSignal(PickerMode)
    selected_date_changed = pyqtSignal(QDate)
    selected_range_changed = pyqtSignal(QDate, QDate)
    visible_month_changed = pyqtSignal(QDate)
    state_changed = pyqtSignal(DatePickerState)

    def __init__(self) -> None:
        super().__init__()
        today = QDate.currentDate()
        self._state = DatePickerState(
            mode=PickerMode.DATE,
            selected_dates=(today, None),
            visible_month=QDate(today.year(), today.month(), 1),
        )

    @property
    def state(self) -> DatePickerState:
        return self._state

    def set_mode(self, mode: PickerMode) -> None:
        """Update the active picker mode and notify listeners."""
        if mode is self._state.mode:
            return
        LOGGER.debug("Picker mode change: %s -> %s", self._state.mode.name, mode.name)
        self._update_state(mode=mode)
        self.mode_changed.emit(mode)
        self.state_changed.emit(self._state)

    def select_date(self, date: QDate) -> None:
        """Select a single date and clear any existing range selection."""
        validated = cast(QDate, validate_qdate(date, field_name="selected_date"))
        LOGGER.debug("Selecting date: %s", validated.toString("yyyy-MM-dd"))
        current_start, current_end = self._state.selected_dates
        if current_start == validated and current_end is None:
            return
        self._update_state(
            selected_dates=(validated, None),
            visible_month=first_of_month(validated),
        )
        self.selected_date_changed.emit(validated)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def select_range(self, start: QDate, end: QDate) -> None:
        """Select a date range (inclusive) and emit corresponding signals."""
        start_candidate, end_candidate = validate_date_range(
            start,
            end,
            field_name="selected_range",
            allow_partial=False,
        )
        validated_start = cast(QDate, start_candidate)
        validated_end = cast(QDate, end_candidate)
        LOGGER.debug(
            "Selecting range: %s -> %s",
            validated_start.toString("yyyy-MM-dd"),
            validated_end.toString("yyyy-MM-dd"),
        )
        self._update_state(
            selected_dates=(validated_start, validated_end),
            visible_month=first_of_month(validated_start),
        )
        self.selected_range_changed.emit(validated_start, validated_end)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def set_visible_month(self, month: QDate) -> None:
        """Change the month displayed in the calendar UI."""
        validated_month = cast(QDate, validate_qdate(month, field_name="visible_month"))
        target = first_of_month(validated_month)
        LOGGER.debug("Updating visible month to %s", target.toString("yyyy-MM"))
        if target == self._state.visible_month:
            return
        self._update_state(visible_month=target)
        self.visible_month_changed.emit(target)
        self.state_changed.emit(self._state)

    def reset(self) -> None:
        """Reset the internal state to today's date in ``DATE`` mode."""
        today = QDate.currentDate()
        LOGGER.debug("Resetting picker state to %s", today.toString("yyyy-MM-dd"))
        self._update_state(
            mode=PickerMode.DATE,
            selected_dates=(today, None),
            visible_month=first_of_month(today),
        )
        self.mode_changed.emit(self._state.mode)
        self.selected_date_changed.emit(today)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def _update_state(
        self,
        *,
        mode: PickerMode | None = None,
        selected_dates: Tuple[QDate | None, QDate | None] | None = None,
        visible_month: QDate | None = None,
    ) -> None:
        new_state = replace(
            self._state,
            mode=mode if mode is not None else self._state.mode,
            selected_dates=selected_dates if selected_dates is not None else self._state.selected_dates,
            visible_month=visible_month if visible_month is not None else self._state.visible_month,
        )
        self._state = new_state

__all__ = ["DatePickerStateManager", "DatePickerState", "PickerMode"]


