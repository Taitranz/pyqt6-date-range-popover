from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto

from PyQt6.QtCore import QDate

from ..exceptions import InvalidDateError
from ..utils import first_of_month


class PickerMode(Enum):
    """Supported picker modes exposed via the public API."""

    DATE = auto()
    CUSTOM_RANGE = auto()


@dataclass(frozen=True, slots=True)
class DatePickerState:
    """
    Immutable snapshot of the picker state.

    Splitting the snapshot into a pure dataclass makes it easier to test state
    transitions independently from Qt.
    """

    mode: PickerMode
    selected_dates: tuple[QDate | None, QDate | None]
    visible_month: QDate


def build_initial_state(min_date: QDate | None, max_date: QDate | None) -> DatePickerState:
    """Return the default state used when the picker first loads or resets."""
    initial_date = clamp_date(QDate.currentDate(), min_date, max_date)
    return DatePickerState(
        mode=PickerMode.DATE,
        selected_dates=(initial_date, None),
        visible_month=first_of_month(initial_date),
    )


def clamp_date(date: QDate, min_date: QDate | None, max_date: QDate | None) -> QDate:
    """Clamp ``date`` to the provided bounds without raising."""
    result = QDate(date)
    if min_date is not None and result < min_date:
        result = QDate(min_date)
    if max_date is not None and result > max_date:
        result = QDate(max_date)
    return result


def ensure_within_bounds(
    date: QDate,
    min_date: QDate | None,
    max_date: QDate | None,
    *,
    field_name: str,
) -> QDate:
    """Validate that ``date`` stays inside the configured bounds."""
    if min_date is not None and date < min_date:
        raise InvalidDateError(f"{field_name} must be on or after the configured min_date")
    if max_date is not None and date > max_date:
        raise InvalidDateError(f"{field_name} must be on or before the configured max_date")
    return date


def clamp_visible_month(month: QDate, min_date: QDate | None, max_date: QDate | None) -> QDate:
    """Clamp a month to the allowed range (first-of-month resolution)."""
    target = first_of_month(month)
    if min_date is not None:
        min_month = first_of_month(min_date)
        if target < min_month:
            target = min_month
    if max_date is not None:
        max_month = first_of_month(max_date)
        if target > max_month:
            target = max_month
    return target


def apply_single_date(state: DatePickerState, date: QDate) -> DatePickerState:
    """Return a new state snapshot representing a single-date selection."""
    return replace(
        state,
        selected_dates=(date, None),
        visible_month=first_of_month(date),
    )


def apply_range_selection(
    state: DatePickerState,
    start: QDate,
    end: QDate,
) -> DatePickerState:
    """Return a new state snapshot representing a range selection."""
    return replace(
        state,
        selected_dates=(start, end),
        visible_month=first_of_month(start),
    )


def switch_mode(state: DatePickerState, mode: PickerMode) -> DatePickerState:
    """Return a new snapshot with the provided picker mode."""
    return replace(state, mode=mode)


__all__ = [
    "DatePickerState",
    "PickerMode",
    "apply_range_selection",
    "apply_single_date",
    "build_initial_state",
    "clamp_date",
    "clamp_visible_month",
    "ensure_within_bounds",
    "switch_mode",
]
