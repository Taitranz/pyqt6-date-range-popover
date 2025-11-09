from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Tuple

from PyQt6.QtCore import QDate, QObject, pyqtSignal


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
        if mode is self._state.mode:
            return
        self._update_state(mode=mode)
        self.mode_changed.emit(mode)
        self.state_changed.emit(self._state)

    def select_date(self, date: QDate) -> None:
        if not date.isValid():
            return
        current_start, current_end = self._state.selected_dates
        if current_start == date and current_end is None:
            return
        self._update_state(selected_dates=(date, None), visible_month=self._first_of_month(date))
        self.selected_date_changed.emit(date)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def select_range(self, start: QDate, end: QDate) -> None:
        if not start.isValid() or not end.isValid():
            return
        if start > end:
            start, end = end, start
        self._update_state(selected_dates=(start, end), visible_month=self._first_of_month(start))
        self.selected_range_changed.emit(start, end)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def set_visible_month(self, month: QDate) -> None:
        if not month.isValid():
            return
        target = self._first_of_month(month)
        if target == self._state.visible_month:
            return
        self._update_state(visible_month=target)
        self.visible_month_changed.emit(target)
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

    @staticmethod
    def _first_of_month(date: QDate) -> QDate:
        return QDate(date.year(), date.month(), 1)


__all__ = ["DatePickerStateManager", "DatePickerState", "PickerMode"]


