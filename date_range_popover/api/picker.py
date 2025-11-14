from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QDate, Qt, QTime, pyqtSignal
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ..animation import AnimationStrategy, SlideAnimator
from ..components.buttons import BasicButton, ButtonStrip
from ..components.calendar import CalendarWidget
from ..components.inputs import CUSTOM_DATE_RANGE, GO_TO_DATE, DateTimeSelector
from ..components.layout import DraggableHeaderStrip, SlidingTrackIndicator
from ..managers.coordinator import DatePickerCoordinator
from ..managers.state_manager import DatePickerStateManager, PickerMode
from ..managers.style_manager import StyleManager
from ..styles.style_registry import StyleRegistry
from ..types.selection import SelectionCallback, SelectionSnapshot
from ..utils import connect_signal, get_logger
from .config import DatePickerConfig, DateRange
from .picker_layouts import (
    build_actions_section,
    build_button_section,
    build_content_container,
    build_divider,
    build_header_layout,
)

LOGGER = get_logger(__name__)

CLOSE_ICON_PATH = Path(__file__).resolve().parents[1] / "assets" / "cross.svg"


class DateRangePicker(QWidget):
    """
    High-level facade for constructing and embedding the popover.

    The widget exposes a small surface area focused on things host applications
    care about: reacting to user selections (via Qt signals), reading the
    current selection, switching between picker modes, and resetting/cleaning up
    resources. Everything else—layout, component wiring, state transitions—is
    encapsulated so the embedding code stays simple.

    Example:
        >>> picker = DateRangePicker(DatePickerConfig(mode=PickerMode.DATE))
        >>> picker.date_selected.connect(lambda d: print(d.toString("yyyy-MM-dd")))
        >>> picker.show()

    Signals
    -------
    date_selected(QDate)
        Emitted when a single date is confirmed. An invalid ``QDate`` indicates
        that no date is currently selected.
    range_selected(DateRange)
        Emitted when both ends of the range are locked in.
    cancelled()
        Emitted when the user dismisses or cancels the popover.
    """

    date_selected = pyqtSignal(QDate)
    range_selected = pyqtSignal(DateRange)
    cancelled = pyqtSignal()

    def __init__(
        self,
        config: DatePickerConfig | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build a picker instance using the provided configuration.

        The constructor clones all configuration values and initialises the
        internal managers immediately, so callers should treat the config object
        as immutable after passing it in.

        Args:
            config: Optional :class:`DatePickerConfig`. Defaults to a new
                instance when omitted.
            parent: Optional widget parent for lifetime management.

        Raises:
            InvalidConfigurationError: Propagated when ``config`` contains
                invalid values (for example, ``min_date > max_date``).
        """
        super().__init__(parent)

        self._config = config or DatePickerConfig()

        registry = StyleRegistry(self._config.theme)
        self._style_manager = StyleManager(registry)
        self._layout_config = self._config.theme.layout
        self._state_manager = DatePickerStateManager(
            min_date=self._config.min_date,
            max_date=self._config.max_date,
        )
        self._coordinator = DatePickerCoordinator(self._state_manager, self._style_manager)
        self._animator: AnimationStrategy = SlideAnimator(parent=self)
        self._current_track_position = 0
        self._current_track_width = self._layout_config.date_indicator_width
        self._selection_callbacks: list[SelectionCallback] = []

        self._header_strip = DraggableHeaderStrip(self, palette=self._style_manager.theme.palette)
        self._button_strip = ButtonStrip(self, layout_config=self._layout_config)
        self._sliding_track = SlidingTrackIndicator(
            self,
            palette=self._style_manager.theme.palette,
            layout=self._layout_config,
        )
        (
            default_start_date,
            default_end_date,
            default_start_time,
            default_end_time,
        ) = self._resolve_initial_input_values()
        self._date_time_selector = DateTimeSelector(
            self,
            mode=GO_TO_DATE,
            palette=self._style_manager.theme.palette,
            primary_date=default_start_date,
            secondary_date=default_end_date,
            primary_time=default_start_time,
            secondary_time=default_end_time,
            time_step_minutes=self._config.time_step_minutes,
        )
        self._calendar = CalendarWidget(self, style=registry.calendar_config())
        self._calendar.set_constraints(
            min_date=self._config.min_date, max_date=self._config.max_date
        )
        self._cancel_button = BasicButton(
            self, label="Cancel", width=72, layout=self._layout_config
        )
        self._go_to_button = BasicButton(self, label="Go to", width=64, layout=self._layout_config)

        self._build_ui()
        self._connect_signals()
        self._initialize_state()

    # Public API --------------------------------------------------------------------

    @property
    def selected_date(self) -> QDate:
        """
        Currently selected single date.

        Returns:
            A defensive ``QDate`` copy representing the active single-date
            selection. The value is invalid (``QDate()``) when no single date is
            locked in.

        Guarantees:
            * When valid, the date always respects ``config.min_date`` /
              ``config.max_date``.
            * The returned object is never shared with internal state.
        """
        start, _ = self._state_manager.state.selected_dates
        return start or QDate()

    @property
    def selected_range(self) -> DateRange:
        """
        Currently selected range (may be partial).

        Returns:
            :class:`DateRange`: a defensive copy with the best-known endpoints.
            Missing endpoints remain ``None`` so callers can differentiate
            between partial and complete selections.

        Guarantees:
            * When present, endpoints always satisfy ``start <= end``.
            * Every endpoint is clamped to ``[min_date, max_date]``.
        """
        start, end = self._state_manager.state.selected_dates
        return DateRange(start_date=start, end_date=end)

    def set_mode(self, mode: PickerMode) -> None:
        """
        Switch the picker to the provided :class:`PickerMode`.

        Args:
            mode: ``PickerMode.DATE`` or ``PickerMode.CUSTOM_RANGE``.

        Notes:
            Must be invoked from the Qt GUI thread because it drives widget
            mutations and animations.
        """
        LOGGER.debug("Switching picker mode via API: %s", mode.name)
        self._coordinator.switch_mode(mode)

    def reset(self) -> None:
        """
        Reset the picker state to match the initial configuration.

        This method clears animations, re-applies selection defaults, and
        ensures the coordinator redraws UI components.

        Notes:
            Safe to call any time the host wants to discard in-progress user
            input. Must run on the Qt GUI thread.
        """
        LOGGER.info("Resetting DateRangePicker to configuration defaults")
        self._animator.stop()
        self._state_manager.reset()
        self._initialize_state()

    def cleanup(self) -> None:
        """
        Release long-lived objects and stop active animations.

        Call this during application teardown or when removing the widget from a
        complex embedding scenario to make sure timers/animations are cleaned up.

        Notes:
            The widget becomes unusable after ``cleanup``; create a new instance
            if you need to re-mount the UI.
        """
        LOGGER.info("Cleaning up DateRangePicker resources")
        self._animator.stop()
        self._date_time_selector.cleanup()
        self._coordinator.deleteLater()
        self._state_manager.deleteLater()

    def register_selection_callback(self, callback: SelectionCallback) -> None:
        """
        Register a Python callback that mirrors the Qt selection signals.

        Args:
            callback: Callable that receives a :class:`SelectionSnapshot`.

        Notes:
            Callbacks are invoked synchronously on the Qt GUI thread. They are
            in addition to (not instead of) the Qt signals, which remain the
            canonical integration surface for Qt consumers.
        """
        if callback not in self._selection_callbacks:
            self._selection_callbacks.append(callback)

    def deregister_selection_callback(self, callback: SelectionCallback) -> None:
        """
        Remove a previously registered callback.

        Calling this method with an unknown callback is a no-op.
        """
        try:
            self._selection_callbacks.remove(callback)
        except ValueError:
            pass

    # Internal setup ----------------------------------------------------------------

    def _build_ui(self) -> None:
        """Assemble the widget tree and persist references to core components."""
        self._setup_window()
        self._close_button = build_header_layout(
            header_strip=self._header_strip,
            layout_config=self._layout_config,
            palette=self._style_manager.theme.palette,
            close_icon_path=CLOSE_ICON_PATH,
        )

        button_section = build_button_section(
            parent=self,
            palette=self._style_manager.theme.palette,
            layout_config=self._layout_config,
            button_strip=self._button_strip,
            sliding_track=self._sliding_track,
            date_time_selector=self._date_time_selector,
            calendar=self._calendar,
        )
        content_container = build_content_container(
            parent=self,
            layout_config=self._layout_config,
            header_strip=self._header_strip,
            button_section=button_section,
        )
        actions_wrapper = build_actions_section(
            parent=self,
            palette=self._style_manager.theme.palette,
            layout_config=self._layout_config,
            cancel_button=self._cancel_button,
            go_to_button=self._go_to_button,
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, self._layout_config.main_padding)
        main_layout.setSpacing(0)
        main_layout.addWidget(content_container)
        main_layout.addStretch(1)
        main_layout.addSpacing(16)

        divider = build_divider(
            parent=self,
            palette=self._style_manager.theme.palette,
        )
        main_layout.addWidget(divider)
        main_layout.addSpacing(16)
        main_layout.addWidget(actions_wrapper)

        self._configure_components()

    def _setup_window(self) -> None:
        """Apply static window geometry, palette, and QWidget flags."""
        layout_config = self._layout_config
        self.setFixedWidth(layout_config.window_min_width)
        self._apply_window_height(layout_config.window_min_height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"background-color: {self._style_manager.theme.palette.window_background}; "
            f"border-radius: {layout_config.window_radius}px;"
        )
        self.setWindowFlags(Qt.WindowType.Window)

    def _configure_components(self) -> None:
        """Register child widgets with their coordinators and apply styles."""
        self._coordinator.register_button_strip(self._button_strip)
        self._coordinator.register_sliding_track(self._sliding_track)
        self._coordinator.register_date_time_selector(self._date_time_selector)
        self._coordinator.register_calendar(self._calendar)
        self._coordinator.set_sliding_track_animator(self._animate_sliding_track)

        self._style_manager.apply_basic_button(
            self._cancel_button,
            variant=self._style_manager.registry.BUTTON_GHOST,
        )
        self._style_manager.apply_basic_button(
            self._go_to_button,
            variant=self._style_manager.registry.BUTTON_ACCENT,
        )

    def _connect_signals(self) -> None:
        """Wire child widget signals to both Qt signals and internal handlers."""
        connect_signal(self._close_button.clicked, self.cancelled.emit)
        connect_signal(self._cancel_button.clicked, self.cancelled.emit)

        connect_signal(self._state_manager.selected_date_changed, self._handle_selected_date)
        connect_signal(self._state_manager.selected_range_changed, self._emit_range_selected)

        connect_signal(self._go_to_button.clicked, self._emit_current_selection)
        connect_signal(self._state_manager.mode_changed, self._on_mode_changed)

    def _initialize_state(self) -> None:
        """Sync UI state with the validated configuration and state manager."""
        state = self._state_manager.state
        desired_mode = self._config.mode
        if desired_mode is not state.mode:
            self._coordinator.switch_mode(desired_mode)

        if self._config.initial_range is not None:
            initial = self._config.initial_range
            start = initial.start_date or QDate.currentDate()
            end = initial.end_date or start
            self._state_manager.select_range(start, end)
        elif self._config.initial_date is not None:
            self._state_manager.select_date(self._config.initial_date)

        # Ensure coordinator applies current state
        if self._state_manager.state.mode is PickerMode.DATE:
            self._date_time_selector.set_mode(GO_TO_DATE)
        else:
            self._date_time_selector.set_mode(CUSTOM_DATE_RANGE)
        self._sliding_track.set_state(position=0, width=self._layout_config.date_indicator_width)
        self._on_mode_changed(self._state_manager.state.mode)

    # Event helpers -----------------------------------------------------------------

    def _animate_sliding_track(self, mode: PickerMode) -> None:
        """Animate the sliding indicator whenever the picker mode changes."""
        indicator_width = self._layout_config.date_indicator_width
        custom_width = self._layout_config.custom_range_indicator_width
        button_gap = self._layout_config.button_gap

        if mode is PickerMode.DATE:
            target_position = 0
            target_width = indicator_width
        else:
            target_position = indicator_width + button_gap
            target_width = custom_width

        current_position = self._sliding_track.current_position
        current_width = self._sliding_track.current_width or self._current_track_width

        self._current_track_position = current_position
        self._current_track_width = current_width

        self._animator.animate(
            current_position=current_position,
            current_width=current_width,
            target_position=target_position,
            target_width=target_width,
            on_step=lambda pos, width: self._sliding_track.set_state(position=pos, width=width),
            on_complete=lambda pos, width: self._sliding_track.set_state(position=pos, width=width),
        )

    def _handle_selected_date(self, date: QDate) -> None:
        """Emit ``date_selected`` and notify Python callbacks."""
        self.date_selected.emit(date)
        self._notify_selection_callbacks(self._build_snapshot())

    def _emit_range_selected(self, start: QDate, end: QDate) -> None:
        """Emit ``range_selected`` with a defensive :class:`DateRange` copy."""
        payload = DateRange(start_date=start, end_date=end)
        self.range_selected.emit(payload)
        self._notify_selection_callbacks(self._build_snapshot(range_override=payload))

    def _emit_current_selection(self) -> None:
        """Emit the most specific signal for the current selection."""
        start, end = self._state_manager.state.selected_dates
        if end is not None:
            self.range_selected.emit(DateRange(start_date=start, end_date=end))
        elif start is not None:
            self.date_selected.emit(start)

    def _on_mode_changed(self, mode: PickerMode) -> None:
        """Adjust window height whenever the picker switches modes."""
        layout_config = self._layout_config
        if mode is PickerMode.CUSTOM_RANGE:
            target_height = layout_config.window_min_height_custom_range
        else:
            target_height = layout_config.window_min_height
        self._apply_window_height(target_height)

    def _apply_window_height(self, height: int) -> None:
        """Apply a fixed window height while keeping existing width."""
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.resize(self.width(), height)

    def _resolve_initial_input_values(self) -> tuple[QDate, QDate, QTime | None, QTime | None]:
        """Derive initial dates/times from the configuration for widget seeding."""
        today = QDate.currentDate()
        start_date = today
        end_date = today
        start_time: QTime | None = None
        end_time: QTime | None = None

        if self._config.initial_range is not None:
            initial = self._config.initial_range
            if initial.start_date is not None:
                start_date = initial.start_date
            if initial.end_date is not None:
                end_date = initial.end_date
            else:
                end_date = start_date
            start_time = initial.start_time
            end_time = initial.end_time
        elif self._config.initial_date is not None:
            start_date = self._config.initial_date
            end_date = self._config.initial_date
        if end_time is None:
            end_time = start_time

        return start_date, end_date, start_time, end_time

    def _build_snapshot(self, *, range_override: DateRange | None = None) -> SelectionSnapshot:
        """Construct a snapshot describing the current selection state."""
        state = self._state_manager.state
        start, end = state.selected_dates
        current_range = range_override
        if current_range is None and (start is not None or end is not None):
            current_range = DateRange(start_date=start, end_date=end)
        return SelectionSnapshot(
            mode=state.mode,
            selected_date=start,
            selected_range=current_range,
        )

    def _notify_selection_callbacks(self, snapshot: SelectionSnapshot) -> None:
        """Invoke registered Python callbacks."""
        if not self._selection_callbacks:
            return
        for callback in list(self._selection_callbacks):
            callback(snapshot)


__all__ = ["DateRangePicker"]
