from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Protocol, cast

from PyQt6.QtCore import QDate, QObject

from ..components.buttons.button_strip import ButtonStrip
from ..components.calendar.calendar_widget import CalendarWidget
from ..components.inputs.date_time_selector import CUSTOM_DATE_RANGE, DateTimeSelector, GO_TO_DATE
from ..components.layout.sliding_track import SlidingTrackIndicator
from ..styles import constants
from .state_manager import DatePickerStateManager, PickerMode
from .style_manager import StyleManager

if TYPE_CHECKING:  # pragma: no cover
    from ..components.buttons.basic_button import BasicButton

class DatePickerCoordinator(QObject):
    """Coordinates interactions between components and managers."""

    def __init__(
        self,
        state_manager: DatePickerStateManager,
        style_manager: StyleManager,
    ) -> None:
        super().__init__()
        self._state_manager = state_manager
        self._style_manager = style_manager

        self._button_strip: Optional[ButtonStrip] = None
        self._calendar: Optional[CalendarWidget] = None
        self._date_time_selector: Optional[DateTimeSelector] = None
        self._sliding_track: Optional[SlidingTrackIndicator] = None

        self._pending_range_start: QDate | None = None
        self._sliding_track_animator: Optional[Callable[[PickerMode], None]] = None

        cast(_ModeSignal, self._state_manager.mode_changed).connect(self._on_mode_changed)
        cast(_DateSignal, self._state_manager.selected_date_changed).connect(self._on_selected_date_changed)
        cast(_RangeSignal, self._state_manager.selected_range_changed).connect(self._on_selected_range_changed)
        cast(_DateSignal, self._state_manager.visible_month_changed).connect(self._on_visible_month_changed)

    # Registration helpers ----------------------------------------------------------

    def register_button_strip(self, button_strip: ButtonStrip) -> None:
        self._button_strip = button_strip
        self._style_manager.apply_button_strip(button_strip)
        cast(_VoidSignal, button_strip.date_selected).connect(
            lambda: self.switch_mode(PickerMode.DATE)
        )
        cast(_VoidSignal, button_strip.custom_range_selected).connect(
            lambda: self.switch_mode(PickerMode.CUSTOM_RANGE)
        )
        self._apply_mode_to_button_strip(self._state_manager.state.mode)

    def register_calendar(self, calendar: CalendarWidget) -> None:
        self._calendar = calendar
        self._style_manager.apply_calendar(calendar)
        cast(_DateSignal, calendar.date_selected).connect(self.handle_calendar_selection)
        calendar.set_selected_date(self._state_manager.state.selected_dates[0] or QDate.currentDate())

    def register_date_time_selector(self, selector: DateTimeSelector) -> None:
        self._date_time_selector = selector
        selector.apply_palette(self._style_manager.theme.palette)
        cast(_DateSignal, selector.date_input_valid).connect(self._on_date_input_valid)
        self._apply_mode_to_date_time_selector(self._state_manager.state.mode)

    def register_sliding_track(self, sliding_track: SlidingTrackIndicator) -> None:
        self._sliding_track = sliding_track
        self._style_manager.apply_sliding_track(sliding_track)
        self._update_sliding_track(self._state_manager.state.mode)

    def set_sliding_track_animator(self, callback: Callable[[PickerMode], None]) -> None:
        self._sliding_track_animator = callback

    def apply_basic_button_style(self, button: "BasicButton") -> None:
        self._style_manager.apply_basic_button(button)

    # Coordination methods ----------------------------------------------------------

    def select_date(self, date: QDate) -> None:
        self._state_manager.select_date(date)

    def switch_mode(self, mode: PickerMode) -> None:
        self._state_manager.set_mode(mode)

    def handle_calendar_selection(self, date: QDate) -> None:
        current_mode = self._state_manager.state.mode
        if current_mode is PickerMode.DATE:
            self._pending_range_start = None
            self._state_manager.select_date(date)
        else:
            if self._date_time_selector is not None:
                self._date_time_selector.apply_calendar_selection(date)
            if self._pending_range_start is None:
                self._pending_range_start = date
            else:
                self._state_manager.select_range(self._pending_range_start, date)
                self._pending_range_start = None

    # State change handlers ---------------------------------------------------------

    def _on_mode_changed(self, mode: PickerMode) -> None:
        self._apply_mode_to_button_strip(mode)
        self._apply_mode_to_date_time_selector(mode)
        self._update_sliding_track(mode)
        self._pending_range_start = None

    def _on_selected_date_changed(self, date: QDate) -> None:
        if self._calendar is not None:
            self._calendar.set_selected_date(date)
        if self._date_time_selector is not None:
            self._date_time_selector.update_go_to_date(date)

    def _on_selected_range_changed(self, start: QDate, end: QDate) -> None:
        if self._date_time_selector is not None:
            self._date_time_selector.set_range(start, end)

    def _on_visible_month_changed(self, month: QDate) -> None:
        if self._calendar is not None:
            self._calendar.set_visible_month(month)

    def _on_date_input_valid(self, date: QDate) -> None:
        if self._state_manager.state.mode is PickerMode.DATE:
            self._state_manager.select_date(date)
        else:
            if self._date_time_selector is not None:
                index = self._date_time_selector.last_focused_date_index()
            else:
                index = None
            if index == 0:
                _, current_end = self._state_manager.state.selected_dates
                end_date = current_end if current_end is not None else date
                self._state_manager.select_range(date, end_date)
                self._pending_range_start = None
                return
            if index == 1:
                current_start, _ = self._state_manager.state.selected_dates
                start_date = current_start if current_start is not None else date
                self._state_manager.select_range(start_date, date)
                self._pending_range_start = None
                return
            if self._pending_range_start is None:
                self._pending_range_start = date
            else:
                self._state_manager.select_range(self._pending_range_start, date)
                self._pending_range_start = None

    # Helpers -----------------------------------------------------------------------

    def _apply_mode_to_button_strip(self, mode: PickerMode) -> None:
        if self._button_strip is None:
            return
        if mode is PickerMode.DATE:
            self._button_strip.set_selected_button("date")
        else:
            self._button_strip.set_selected_button("custom_range")

    def _apply_mode_to_date_time_selector(self, mode: PickerMode) -> None:
        if self._date_time_selector is None:
            return
        if mode is PickerMode.DATE:
            self._date_time_selector.set_mode(GO_TO_DATE)
        else:
            self._date_time_selector.set_mode(CUSTOM_DATE_RANGE)

    def _update_sliding_track(self, mode: PickerMode) -> None:
        if self._sliding_track is None:
            return
        if self._sliding_track_animator is not None:
            self._sliding_track_animator(mode)
            return
        if mode is PickerMode.DATE:
            self._sliding_track.set_state(
                position=0,
                width=constants.DATE_INDICATOR_WIDTH,
            )
        else:
            position = constants.DATE_INDICATOR_WIDTH + constants.BUTTON_GAP
            self._sliding_track.set_state(
                position=position,
                width=constants.CUSTOM_RANGE_INDICATOR_WIDTH,
            )


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


class _RangeSignal(Protocol):
    def connect(self, slot: Callable[[QDate, QDate], None]) -> object: ...


class _ModeSignal(Protocol):
    def connect(self, slot: Callable[[PickerMode], None]) -> object: ...


__all__ = ["DatePickerCoordinator"]


