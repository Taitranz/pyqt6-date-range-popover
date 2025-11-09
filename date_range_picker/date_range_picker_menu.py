from __future__ import annotations

from pathlib import Path
from typing import Callable, Final, Protocol, cast

from PyQt6.QtCore import QByteArray, QDate, QSize, Qt
from PyQt6.QtGui import QIcon, QMouseEvent, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .animation.slide_animator import SlideAnimator
from .components.basic_button import BasicButton
from .components.button_strip import ButtonStrip
from .components.calendar_widget import CalendarWidget
from .components.date_time_range_selector import (
    CUSTOM_DATE_RANGE,
    GO_TO_DATE,
    DateTimeRangeSelector,
)
from .components.draggable_header import DraggableHeaderStrip
from .components.sliding_track import SlidingTrackIndicator
from .styles import constants


class _ZeroArgSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


CLOSE_ICON_PATH: Final[Path] = Path(__file__).resolve().parent / "assets" / "cross.svg"


def _clear_current_focus(widget: QWidget) -> None:
    focus_widget = QApplication.focusWidget()
    if focus_widget is not None and focus_widget is not widget:
        focus_widget.clearFocus()


def _create_close_icon(size: QSize) -> QIcon:
    try:
        svg_text = CLOSE_ICON_PATH.read_text(encoding="utf-8")
    except OSError:
        return QIcon()
    colored_svg = svg_text.replace("currentColor", "#dbdbdb")
    renderer = QSvgRenderer(QByteArray(colored_svg.encode("utf-8")))
    if not renderer.isValid():
        return QIcon()
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    icon = QIcon(pixmap)
    return icon


class _ClickableContainer(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        _clear_current_focus(self)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(a0)


class DateRangePickerMenu(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._current_position = 0
        self._current_width = constants.DATE_INDICATOR_WIDTH

        self._setup_window()

        self._animator = SlideAnimator(parent=self)

        self._header_strip = DraggableHeaderStrip(self)
        self._build_header(self._header_strip)

        self._button_strip = ButtonStrip(self)
        self._sliding_track = SlidingTrackIndicator(self)
        self._button_strip.set_selected_button("date")

        button_container = _ClickableContainer(self)
        button_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        button_container.setStyleSheet(
            f"background-color: {constants.BUTTON_CONTAINER_BACKGROUND}; border-radius: 0px;"
        )
        button_container_layout = QVBoxLayout(button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(0)
        button_container_layout.addWidget(self._button_strip)
        button_container_layout.addWidget(self._sliding_track)

        spacer = QWidget(self)
        spacer.setFixedHeight(16)
        button_container_layout.addWidget(spacer)

        self._date_time_selector = DateTimeRangeSelector(self, mode=GO_TO_DATE)
        button_container_layout.addWidget(self._date_time_selector)

        self._calendar_widget = CalendarWidget(self)
        button_container_layout.addWidget(
            self._calendar_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, constants.MAIN_PADDING)
        main_layout.setSpacing(0)

        content_container = QWidget(self)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(constants.MAIN_PADDING, 0, constants.MAIN_PADDING, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._header_strip)
        content_layout.addWidget(button_container)

        main_layout.addWidget(content_container)

        main_layout.addStretch(1)
        main_layout.addSpacing(16)

        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.NoFrame)
        divider.setFixedHeight(1)
        divider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        divider.setStyleSheet(f"background-color: {constants.TRACK_BACKGROUND};")
        main_layout.addWidget(divider)

        main_layout.addSpacing(16)

        action_container = QWidget(self)
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(0)

        action_layout.addStretch(1)

        self._cancel_button = BasicButton(
            self,
            label="Cancel",
            width=72,
            height=34,
            background_color=constants.WINDOW_BACKGROUND,
            border_color=constants.BUTTON_SELECTED_COLOR,
            hover_background_color="#f2f2f2",
            pressed_background_color="#f2f2f2",
            hover_font_color=constants.WINDOW_BACKGROUND,
        )
        action_layout.addWidget(self._cancel_button)

        action_layout.addSpacing(12)

        self._go_to_button = BasicButton(
            self,
            label="Go to",
            width=64,
            height=34,
            background_color="#ffffff",
            border_color="#ffffff",
            hover_background_color="#f2f2f2",
            pressed_background_color="#f2f2f2",
            font_color=constants.WINDOW_BACKGROUND,
        )
        action_layout.addWidget(self._go_to_button)

        actions_wrapper = QWidget(self)
        actions_wrapper_layout = QVBoxLayout(actions_wrapper)
        actions_wrapper_layout.setContentsMargins(
            constants.MAIN_PADDING, 0, constants.MAIN_PADDING, 0
        )
        actions_wrapper_layout.setSpacing(0)
        actions_wrapper_layout.addWidget(action_container)

        main_layout.addWidget(actions_wrapper)

        self._sliding_track.set_state(position=self._current_position, width=self._current_width)

        self._connect_signals()
        self._on_date_selected()

    def sizeHint(self) -> QSize:  # noqa: D401
        return QSize(320, constants.WINDOW_MIN_HEIGHT)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        _clear_current_focus(self)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(a0)

    def _setup_window(self) -> None:
        self.setMinimumSize(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
        self.setMaximumSize(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"background-color: {constants.WINDOW_BACKGROUND}; border-radius: {constants.WINDOW_RADIUS}px;"
        )
        self.setWindowFlags(Qt.WindowType.Window)

    def _build_header(self, header_strip: DraggableHeaderStrip) -> None:
        layout = QHBoxLayout(header_strip)
        layout.setContentsMargins(0, constants.MAIN_PADDING, 0, constants.HEADER_BOTTOM_MARGIN)
        layout.setSpacing(0)

        title = QLabel("Go to", header_strip)
        title_font = constants.create_header_font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        close_button = QPushButton(header_strip)
        icon_size = QSize(18, 18)
        close_button.setIcon(_create_close_icon(icon_size))
        close_button.setIconSize(icon_size)
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("border: none; background: transparent; color: #dbdbdb;")
        close_button.setToolTip("Close")
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        self._close_button = close_button

    def _connect_signals(self) -> None:
        date_signal = cast(_ZeroArgSignal, self._button_strip.date_selected)
        custom_signal = cast(_ZeroArgSignal, self._button_strip.custom_range_selected)
        date_signal.connect(self._on_date_selected)
        custom_signal.connect(self._on_custom_range_selected)
        
        # Connect calendar date selection to update the input in go_to_date mode
        calendar_date_signal = cast(_DateSignal, self._calendar_widget.date_selected)
        calendar_date_signal.connect(self._on_calendar_date_selected)

    def _on_date_selected(self) -> None:
        self._button_strip.set_selected_button("date")
        self._date_time_selector.set_mode(GO_TO_DATE)
        self._animate_to(position=0, width=constants.DATE_INDICATOR_WIDTH)

    def _on_custom_range_selected(self) -> None:
        self._button_strip.set_selected_button("custom_range")
        self._date_time_selector.set_mode(CUSTOM_DATE_RANGE)
        target_position = constants.DATE_BUTTON_WIDTH + constants.BUTTON_GAP
        self._animate_to(position=target_position, width=constants.CUSTOM_RANGE_INDICATOR_WIDTH)

    def _on_calendar_date_selected(self, date: QDate) -> None:
        """Update the go_to_date input when a date is selected from the calendar."""
        self._date_time_selector.apply_calendar_selection(date)

    def _animate_to(self, *, position: int, width: int) -> None:
        current_position = self._sliding_track.current_position
        current_width = self._sliding_track.current_width or self._current_width
        self._current_position = current_position
        self._current_width = current_width

        self._animator.animate(
            current_position=current_position,
            current_width=current_width,
            target_position=position,
            target_width=width,
            on_step=self._on_animation_step,
            on_complete=self._on_animation_complete,
        )

    def _on_animation_step(self, position: int, width: int) -> None:
        self._sliding_track.set_state(position=position, width=width)

    def _on_animation_complete(self, position: int, width: int) -> None:
        self._current_position = position
        self._current_width = width
        self._sliding_track.set_state(position=position, width=width)


