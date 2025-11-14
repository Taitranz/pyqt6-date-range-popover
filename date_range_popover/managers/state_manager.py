from __future__ import annotations

from dataclasses import replace
from typing import cast

from PyQt6.QtCore import QDate, QObject, pyqtSignal

from ..core.state_logic import (
    DatePickerState,
    PickerMode,
    apply_range_selection,
    apply_single_date,
    build_initial_state,
    clamp_visible_month,
    ensure_within_bounds,
    switch_mode,
)
from ..exceptions import InvalidDateError
from ..utils import get_logger
from ..validation import validate_date_range, validate_qdate

LOGGER = get_logger(__name__)


class DatePickerStateManager(QObject):
    """
    Centralized store for picker state.

    The manager owns the authoritative selection, mode, and visible month. It
    enforces ``min_date``/``max_date`` bounds, emits granular signals for UI
    components, and exposes a small mutator surface (`select_date`,
    `select_range`, `set_mode`, `set_visible_month`, `reset`). This class is an
    internal detail—public consumers interact with :class:`DateRangePicker`
    instead—but documenting it clarifies extension points for advanced users.
    """

    mode_changed = pyqtSignal(PickerMode)
    selected_date_changed = pyqtSignal(QDate)
    selected_range_changed = pyqtSignal(QDate, QDate)
    visible_month_changed = pyqtSignal(QDate)
    state_changed = pyqtSignal(DatePickerState)

    def __init__(self, *, min_date: QDate | None = None, max_date: QDate | None = None) -> None:
        """
        Build a new state manager with optional selection bounds.

        :param min_date: Lower bound; ``None`` means unbounded.
        :param max_date: Upper bound; ``None`` means unbounded.
        :raises InvalidDateError: If ``min_date`` is after ``max_date``.
        """
        super().__init__()
        self._min_date = QDate(min_date) if isinstance(min_date, QDate) else None
        self._max_date = QDate(max_date) if isinstance(max_date, QDate) else None
        if (
            self._min_date is not None
            and self._max_date is not None
            and self._min_date > self._max_date
        ):
            raise InvalidDateError("min_date must be on or before max_date")
        self._state = build_initial_state(self._min_date, self._max_date)

    @property
    def state(self) -> DatePickerState:
        """Latest immutable snapshot used by coordinators and widgets."""
        return self._state

    @property
    def min_date(self) -> QDate | None:
        """Configured lower bound for selection/navigation (defensive copy)."""
        return self._min_date

    @property
    def max_date(self) -> QDate | None:
        """Configured upper bound for selection/navigation (defensive copy)."""
        return self._max_date

    def set_mode(self, mode: PickerMode) -> None:
        """
        Update the active picker mode and notify listeners.

        :param mode: Desired :class:`PickerMode`.
        :raises InvalidDateError: Propagated from downstream logic when the
            switch would violate invariants.

        Thread Safety:
            Must be invoked on the Qt GUI thread because it emits Qt signals.
        """
        if mode is self._state.mode:
            return
        LOGGER.debug("Picker mode change: %s -> %s", self._state.mode.name, mode.name)
        self._state = switch_mode(self._state, mode)
        self.mode_changed.emit(mode)
        self.state_changed.emit(self._state)

    def select_date(self, date: QDate) -> None:
        """
        Select a single date and clear any existing range selection.

        :param date: Candidate ``QDate`` (must be valid and within bounds).
        :raises InvalidDateError: If ``date`` falls outside ``min_date`` /
            ``max_date``.

        Thread Safety:
            Invoke from the Qt GUI thread; the method emits signals and touches
            widgets indirectly via coordinators.
        """
        validated = cast(QDate, validate_qdate(date, field_name="selected_date"))
        validated = ensure_within_bounds(
            validated,
            self._min_date,
            self._max_date,
            field_name="selected_date",
        )
        LOGGER.debug("Selecting date: %s", validated.toString("yyyy-MM-dd"))
        current_start, current_end = self._state.selected_dates
        if current_start == validated and current_end is None:
            return
        self._state = apply_single_date(self._state, validated)
        self.selected_date_changed.emit(validated)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def select_range(self, start: QDate, end: QDate) -> None:
        """
        Select a date range (inclusive) and emit corresponding signals.

        :param start: Range start (inclusive).
        :param end: Range end (inclusive).
        :raises InvalidDateError: If either endpoint violates configured bounds.

        Thread Safety:
            Invoke from the Qt GUI thread to keep signal delivery consistent.
        """
        start_candidate, end_candidate = validate_date_range(
            start,
            end,
            field_name="selected_range",
            allow_partial=False,
        )
        validated_start = cast(QDate, start_candidate)
        validated_end = cast(QDate, end_candidate)
        validated_start = ensure_within_bounds(
            validated_start,
            self._min_date,
            self._max_date,
            field_name="selected_range.start",
        )
        validated_end = ensure_within_bounds(
            validated_end,
            self._min_date,
            self._max_date,
            field_name="selected_range.end",
        )
        LOGGER.debug(
            "Selecting range: %s -> %s",
            validated_start.toString("yyyy-MM-dd"),
            validated_end.toString("yyyy-MM-dd"),
        )
        self._state = apply_range_selection(self._state, validated_start, validated_end)
        self.selected_range_changed.emit(validated_start, validated_end)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)

    def set_visible_month(self, month: QDate) -> None:
        """
        Change the month displayed in the calendar UI.

        :param month: Any ``QDate`` within the desired month/year.
        :raises InvalidDateError: If ``month`` is invalid.

        Thread Safety:
            Invoke from the Qt GUI thread; downstream widgets assume single-threaded access.
        """
        validated_month = cast(QDate, validate_qdate(month, field_name="visible_month"))
        target = clamp_visible_month(validated_month, self._min_date, self._max_date)
        LOGGER.debug("Updating visible month to %s", target.toString("yyyy-MM"))
        if target == self._state.visible_month:
            return
        self._state = replace(self._state, visible_month=target)
        self.visible_month_changed.emit(target)
        self.state_changed.emit(self._state)

    def reset(self) -> None:
        """
        Reset the internal state to today's date in ``DATE`` mode.

        Thread Safety:
            Call from the Qt GUI thread so emitted signals remain ordered.
        """
        previous_mode = self._state.mode
        self._state = build_initial_state(self._min_date, self._max_date)
        start_date, _ = self._state.selected_dates
        LOGGER.debug(
            "Resetting picker state to %s",
            start_date.toString("yyyy-MM-dd") if start_date is not None else "N/A",
        )
        if self._state.mode is not previous_mode:
            self.mode_changed.emit(self._state.mode)
        if start_date is not None:
            self.selected_date_changed.emit(start_date)
        self.visible_month_changed.emit(self._state.visible_month)
        self.state_changed.emit(self._state)


__all__ = ["DatePickerStateManager", "DatePickerState", "PickerMode"]
