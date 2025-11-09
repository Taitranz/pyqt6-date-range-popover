from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Protocol, cast

from PyQt6.QtCore import QDate, QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..animation.slide_animator import SlideAnimator
from ..components.buttons import BasicButton, ButtonStrip
from ..components.calendar import CalendarWidget
from ..components.inputs import CUSTOM_DATE_RANGE, GO_TO_DATE, DateTimeSelector
from ..components.layout import DraggableHeaderStrip, SlidingTrackIndicator
from ..managers.coordinator import DatePickerCoordinator
from ..managers.state_manager import DatePickerStateManager, PickerMode
from ..managers.style_manager import StyleManager
from ..styles import constants
from ..styles.style_registry import StyleRegistry
from ..utils.svg_loader import load_colored_svg_icon
from .config import DatePickerConfig, DateRange

CLOSE_ICON_PATH = Path(__file__).resolve().parents[1] / "assets" / "cross.svg"


class DateRangePicker(QWidget):
    """High-level facade for constructing and interacting with the picker."""

    date_selected = pyqtSignal(QDate)
    range_selected = pyqtSignal(DateRange)
    cancelled = pyqtSignal()

    def __init__(
        self,
        config: Optional[DatePickerConfig] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._config = config or DatePickerConfig()

        registry = StyleRegistry(self._config.theme)
        self._style_manager = StyleManager(registry)
        self._state_manager = DatePickerStateManager()
        self._coordinator = DatePickerCoordinator(self._state_manager, self._style_manager)
        self._animator = SlideAnimator(parent=self)
        self._current_track_position = 0
        self._current_track_width = constants.DATE_INDICATOR_WIDTH

        self._header_strip = DraggableHeaderStrip(self, palette=self._style_manager.theme.palette)
        self._button_strip = ButtonStrip(self)
        self._sliding_track = SlidingTrackIndicator(self, palette=self._style_manager.theme.palette)
        self._date_time_selector = DateTimeSelector(self, mode=GO_TO_DATE, palette=self._style_manager.theme.palette)
        self._calendar = CalendarWidget(self, style=registry.calendar_config())
        self._cancel_button = BasicButton(self, label="Cancel", width=72, height=34)
        self._go_to_button = BasicButton(self, label="Go to", width=64, height=34)

        self._build_ui()
        self._connect_signals()
        self._initialize_state()

    # Public API --------------------------------------------------------------------

    def get_selected_date(self) -> QDate:
        start, _ = self._state_manager.state.selected_dates
        return start or QDate()

    def get_selected_range(self) -> DateRange:
        start, end = self._state_manager.state.selected_dates
        return DateRange(start_date=start, end_date=end)

    def set_mode(self, mode: PickerMode) -> None:
        self._coordinator.switch_mode(mode)

    # Internal setup ----------------------------------------------------------------

    def _build_ui(self) -> None:
        self._setup_window()
        self._build_header(self._header_strip)

        palette = self._style_manager.theme.palette

        button_container = QWidget(self)
        button_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        button_container.setStyleSheet(
            f"background-color: {palette.button_container_background};"
            "border: none;"
        )
        button_container_layout = QVBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(0)
        button_container_layout.addWidget(self._button_strip)
        button_container_layout.addWidget(self._sliding_track)
        button_container_layout.addSpacing(16)
        button_container_layout.addWidget(self._date_time_selector)
        button_container_layout.addWidget(self._calendar, alignment=Qt.AlignmentFlag.AlignCenter)

        content_container = QWidget(self)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(
            self._config.theme.layout.main_padding,
            0,
            self._config.theme.layout.main_padding,
            0,
        )
        content_layout.setSpacing(0)
        content_layout.addWidget(self._header_strip)
        content_layout.addWidget(button_container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, self._config.theme.layout.main_padding)
        main_layout.setSpacing(0)
        main_layout.addWidget(content_container)
        main_layout.addStretch(1)
        main_layout.addSpacing(16)

        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.NoFrame)
        divider.setFixedHeight(1)
        divider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        divider.setStyleSheet(f"background-color: {palette.track_background};")
        main_layout.addWidget(divider)
        main_layout.addSpacing(16)

        actions_wrapper = QWidget(self)
        actions_layout = QHBoxLayout(actions_wrapper)
        actions_layout.setContentsMargins(
            self._config.theme.layout.main_padding,
            0,
            self._config.theme.layout.main_padding,
            0,
        )
        actions_layout.setSpacing(12)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self._cancel_button)
        actions_layout.addWidget(self._go_to_button)
        actions_wrapper.setStyleSheet(
            f"background-color: {palette.window_background};"
            "border: none;"
        )
        main_layout.addWidget(actions_wrapper)

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

    def _setup_window(self) -> None:
        layout_config = self._config.theme.layout
        self.setFixedWidth(layout_config.window_min_width)
        self._apply_window_height(layout_config.window_min_height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"background-color: {self._style_manager.theme.palette.window_background}; "
            f"border-radius: {layout_config.window_radius}px;"
        )
        self.setWindowFlags(Qt.WindowType.Window)

    def _build_header(self, header_strip: DraggableHeaderStrip) -> None:
        layout = QHBoxLayout(header_strip)
        layout.setContentsMargins(
            0,
            self._config.theme.layout.main_padding,
            0,
            self._config.theme.layout.header_bottom_margin,
        )
        layout.setSpacing(0)

        title = QLabel("Go to", header_strip)
        title_font = constants.create_header_font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        close_button = QPushButton(header_strip)
        icon_size = QSize(18, 18)
        close_button.setIcon(load_colored_svg_icon(CLOSE_ICON_PATH, 18, self._style_manager.theme.palette.button_selected_color))
        close_button.setIconSize(icon_size)
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("border: none; background: transparent;")
        close_button.setToolTip("Close")
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        self._close_button = close_button

    def _connect_signals(self) -> None:
        close_signal = cast(_VoidSignal, self._close_button.clicked)
        close_signal.connect(self.cancelled.emit)
        cancel_signal = cast(_VoidSignal, self._cancel_button.clicked)
        cancel_signal.connect(self.cancelled.emit)

        date_signal = cast(_DateSignal, self._state_manager.selected_date_changed)
        date_signal.connect(self.date_selected.emit)
        range_signal = cast(_RangeSignal, self._state_manager.selected_range_changed)
        range_signal.connect(self._emit_range_selected)

        go_to_signal = cast(_VoidSignal, self._go_to_button.clicked)
        go_to_signal.connect(self._emit_current_selection)
        mode_signal = cast(_ModeSignal, self._state_manager.mode_changed)
        mode_signal.connect(self._on_mode_changed)

    def _initialize_state(self) -> None:
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
        self._sliding_track.set_state(position=0, width=constants.DATE_INDICATOR_WIDTH)
        self._on_mode_changed(self._state_manager.state.mode)

    # Event helpers -----------------------------------------------------------------

    def _animate_sliding_track(self, mode: PickerMode) -> None:
        if mode is PickerMode.DATE:
            target_position = 0
            target_width = constants.DATE_INDICATOR_WIDTH
        else:
            target_position = constants.DATE_INDICATOR_WIDTH + constants.BUTTON_GAP
            target_width = constants.CUSTOM_RANGE_INDICATOR_WIDTH

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

    def _emit_range_selected(self, start: QDate, end: QDate) -> None:
        self.range_selected.emit(DateRange(start_date=start, end_date=end))

    def _emit_current_selection(self) -> None:
        start, end = self._state_manager.state.selected_dates
        if end is not None:
            self.range_selected.emit(DateRange(start_date=start, end_date=end))
        elif start is not None:
            self.date_selected.emit(start)

    def _on_mode_changed(self, mode: PickerMode) -> None:
        layout_config = self._config.theme.layout
        if mode is PickerMode.CUSTOM_RANGE:
            target_height = layout_config.window_min_height_custom_range
        else:
            target_height = layout_config.window_min_height
        self._apply_window_height(target_height)

    def _apply_window_height(self, height: int) -> None:
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.resize(self.width(), height)


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


class _RangeSignal(Protocol):
    def connect(self, slot: Callable[[QDate, QDate], None]) -> object: ...


class _ModeSignal(Protocol):
    def connect(self, slot: Callable[[PickerMode], None]) -> object: ...


__all__ = ["DateRangePicker"]


