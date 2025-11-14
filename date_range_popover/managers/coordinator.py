from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtCore import QDate, QObject

from ..components.buttons.button_strip import ButtonStrip
from ..components.calendar.calendar_widget import CalendarWidget
from ..components.inputs.date_time_selector import CUSTOM_DATE_RANGE, GO_TO_DATE, DateTimeSelector
from ..components.layout.sliding_track import SlidingTrackIndicator
from ..utils import connect_signal, get_logger
from .state_manager import DatePickerStateManager, PickerMode
from .style_manager import StyleManager

LOGGER = get_logger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from ..components.buttons.basic_button import BasicButton


class DatePickerCoordinator(QObject):
    """
    Internal hub that wires the state manager, style manager, and widgets.

    This class is not part of the public API surface, but documenting it helps
    advanced users understand how signals flow between components when they
    embed custom widgets.
    """

    def __init__(
        self,
        state_manager: DatePickerStateManager,
        style_manager: StyleManager,
    ) -> None:
        super().__init__()
        self._state_manager = state_manager
        self._style_manager = style_manager

        self._button_strip: ButtonStrip | None = None
        self._calendar: CalendarWidget | None = None
        self._date_time_selector: DateTimeSelector | None = None
        self._sliding_track: SlidingTrackIndicator | None = None

        self._pending_range_start: QDate | None = None
        self._sliding_track_animator: Callable[[PickerMode], None] | None = None

        connect_signal(self._state_manager.mode_changed, self._on_mode_changed)
        connect_signal(self._state_manager.selected_date_changed, self._on_selected_date_changed)
        connect_signal(self._state_manager.selected_range_changed, self._on_selected_range_changed)
        connect_signal(self._state_manager.visible_month_changed, self._on_visible_month_changed)

    # Registration helpers ----------------------------------------------------------

    def register_button_strip(self, button_strip: ButtonStrip) -> None:
        """Attach the button strip and wire up palette + mode switching."""
        self._button_strip = button_strip
        self._style_manager.apply_button_strip(button_strip)
        connect_signal(button_strip.date_selected, lambda: self.switch_mode(PickerMode.DATE))
        connect_signal(
            button_strip.custom_range_selected, lambda: self.switch_mode(PickerMode.CUSTOM_RANGE)
        )
        self._apply_mode_to_button_strip(self._state_manager.state.mode)

    def register_calendar(self, calendar: CalendarWidget) -> None:
        """Attach the calendar widget and synchronize initial selection."""
        self._calendar = calendar
        self._style_manager.apply_calendar(calendar)
        connect_signal(calendar.date_selected, self.handle_calendar_selection)
        calendar.set_selected_date(
            self._state_manager.state.selected_dates[0] or QDate.currentDate()
        )

    def register_date_time_selector(self, selector: DateTimeSelector) -> None:
        """Attach the date-time selector and connect validation callbacks."""
        self._date_time_selector = selector
        selector.apply_palette(self._style_manager.theme.palette)
        connect_signal(selector.date_input_valid, self._on_date_input_valid)
        self._apply_mode_to_date_time_selector(self._state_manager.state.mode)

    def register_sliding_track(self, sliding_track: SlidingTrackIndicator) -> None:
        """Attach the sliding track indicator and style it."""
        self._sliding_track = sliding_track
        self._style_manager.apply_sliding_track(sliding_track)
        self._update_sliding_track(self._state_manager.state.mode)

    def set_sliding_track_animator(self, callback: Callable[[PickerMode], None]) -> None:
        """Provide a callback for animating the sliding track."""
        self._sliding_track_animator = callback

    def apply_basic_button_style(self, button: BasicButton) -> None:
        """Apply the default theme styling to an action button."""
        self._style_manager.apply_basic_button(button)

    # Coordination methods ----------------------------------------------------------

    def select_date(self, date: QDate) -> None:
        """Proxy to the state manager's ``select_date`` method."""
        LOGGER.debug("Coordinator selecting date %s", date.toString("yyyy-MM-dd"))
        self._state_manager.select_date(date)

    def switch_mode(self, mode: PickerMode) -> None:
        """Switch the picker mode via the state manager."""
        LOGGER.debug("Coordinator switching mode to %s", mode.name)
        self._state_manager.set_mode(mode)

    def handle_calendar_selection(self, date: QDate) -> None:
        """Handle a date emitted by the calendar widget."""
        LOGGER.debug("Calendar emitted selection %s", date.toString("yyyy-MM-dd"))
        current_mode = self._state_manager.state.mode
        if current_mode is PickerMode.DATE:
            self._pending_range_start = None
            self._state_manager.select_date(date)
            return

        if current_mode is not PickerMode.CUSTOM_RANGE:
            return

        self._pending_range_start = None
        if self._date_time_selector is not None:
            self._date_time_selector.apply_calendar_selection(date)

    # State change handlers ---------------------------------------------------------

    def _on_mode_changed(self, mode: PickerMode) -> None:
        """React to mode switches by updating widgets and clearing pending ranges."""
        self._apply_mode_to_button_strip(mode)
        self._apply_mode_to_date_time_selector(mode)
        self._update_sliding_track(mode)
        self._pending_range_start = None
        if self._calendar is not None:
            if mode is PickerMode.DATE:
                self._calendar.clear_selected_range()
            else:
                start, end = self._state_manager.state.selected_dates
                if start is not None and end is not None and start.isValid() and end.isValid():
                    self._calendar.set_selected_range(start, end)
                else:
                    self._calendar.clear_selected_range()

    def _on_selected_date_changed(self, date: QDate) -> None:
        """Propagate single-date selection changes to child widgets."""
        if self._calendar is not None:
            self._calendar.set_selected_date(date)
        if self._date_time_selector is not None:
            self._date_time_selector.update_go_to_date(date)

    def _on_selected_range_changed(self, start: QDate, end: QDate) -> None:
        """Propagate range selection changes to both inputs and calendar."""
        if self._date_time_selector is not None:
            self._date_time_selector.set_range(start, end)
        if self._calendar is not None and self._state_manager.state.mode is PickerMode.CUSTOM_RANGE:
            self._calendar.set_selected_range(start, end)

    def _on_visible_month_changed(self, month: QDate) -> None:
        """Keep the calendar widget aligned with state-manager month changes."""
        if self._calendar is not None:
            self._calendar.set_visible_month(month)

    def _on_date_input_valid(self, date: QDate) -> None:
        """Handle validated input from the date-time selector."""
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
        """Reflect the current mode in the button strip selection."""
        if self._button_strip is None:
            return
        if mode is PickerMode.DATE:
            self._button_strip.set_selected_button("date")
        else:
            self._button_strip.set_selected_button("custom_range")

    def _apply_mode_to_date_time_selector(self, mode: PickerMode) -> None:
        """Ensure the date-time selector renders the correct UI for ``mode``."""
        if self._date_time_selector is None:
            return
        if mode is PickerMode.DATE:
            self._date_time_selector.set_mode(GO_TO_DATE)
        else:
            self._date_time_selector.set_mode(CUSTOM_DATE_RANGE)

    def _update_sliding_track(self, mode: PickerMode) -> None:
        """Update the sliding indicator position or delegate to an animator."""
        if self._sliding_track is None:
            return
        if self._sliding_track_animator is not None:
            self._sliding_track_animator(mode)
            return
        layout_cfg = self._style_manager.theme.layout
        if mode is PickerMode.DATE:
            self._sliding_track.set_state(
                position=0,
                width=layout_cfg.date_indicator_width,
            )
        else:
            position = layout_cfg.date_indicator_width + layout_cfg.button_gap
            self._sliding_track.set_state(
                position=position,
                width=layout_cfg.custom_range_indicator_width,
            )


__all__ = ["DatePickerCoordinator"]
