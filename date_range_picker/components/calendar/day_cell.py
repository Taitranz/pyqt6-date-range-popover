from __future__ import annotations

from typing import Callable, Protocol, cast

from PyQt6.QtCore import QDate, Qt, pyqtSignal, QEvent, QObject
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QWidget

from ...styles import constants
from ...styles.theme import CalendarStyleConfig, LayoutConfig


class CalendarDayCell(QWidget):
    """Visual representation of a day cell in the calendar grid."""

    clicked = pyqtSignal(QDate)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        style: CalendarStyleConfig | None = None,
        layout: LayoutConfig | None = None,
    ) -> None:
        super().__init__(parent)
        self._date = QDate()
        self._style = style
        self._layout = layout or LayoutConfig()

        self._button = QPushButton(self)
        self._button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.setFont(constants.create_calendar_day_font())
        self._button.installEventFilter(self)

        self._underline = QWidget(self._button)
        self._underline.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._underline.hide()
        self._underline.raise_()

        self._is_today = False
        self._is_hovered = False
        self._underline_color = ""
        self._hover_underline_color = ""

        self.setFixedSize(
            self._layout.calendar_day_cell_size,
            self._layout.calendar_day_cell_size,
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._position_elements()
        cast(_VoidSignal, self._button.clicked).connect(self._on_clicked)

        if self._style is not None:
            self.apply_style(self._style)

    def apply_style(self, style: CalendarStyleConfig) -> None:
        self._style = style
        self._update_stylesheet(
            background="transparent",
            text_color=style.day_text_color,
            hover_background=style.day_hover_background,
            hover_text=style.day_hover_text_color,
        )

    def set_day(
        self,
        date: QDate,
        *,
        in_current_month: bool,
        is_selected: bool,
        is_future: bool = False,
        is_range_start: bool = False,
        is_range_end: bool = False,
        is_in_range: bool = False,
        is_today: bool = False,
    ) -> None:
        self._date = date

        if self._style is None:
            self._is_today = False
            self._update_underline()
            return

        if not in_current_month:
            self._button.setVisible(False)
            self._is_today = False
            self._update_underline()
            return

        self._button.setVisible(True)
        self._button.setText(str(date.day()))
        self._button.setEnabled(not is_future)

        if is_future:
            text_color = self._style.muted_day_text_color
            self._button.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            text_color = self._style.day_text_color
            self._button.setCursor(Qt.CursorShape.PointingHandCursor)

        background = "transparent"
        hover_background = self._style.day_hover_background
        hover_text = self._style.day_hover_text_color

        is_range_edge = is_range_start or is_range_end
        if is_range_edge:
            background = self._style.range_edge_background
            hover_background = self._style.range_edge_background
            text_color = self._style.range_edge_text_color
            hover_text = self._style.range_edge_text_color
        elif is_in_range:
            background = self._style.range_between_background
            hover_background = self._style.range_between_background
            text_color = self._style.range_between_text_color
            hover_text = self._style.range_between_text_color
        elif is_selected:
            background = self._style.today_background
            hover_background = self._style.today_background
            hover_text = self._style.today_text_color
            text_color = self._style.today_text_color

        underline_color = text_color if is_today else None
        hover_underline_color = hover_text if is_today else None

        self._update_stylesheet(
            background=background,
            text_color=text_color,
            hover_background=hover_background,
            hover_text=hover_text,
        )

        self._is_today = is_today
        self._underline_color = underline_color or ""
        self._hover_underline_color = hover_underline_color or underline_color or ""
        self._update_underline()

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        self._position_elements()

    def _on_clicked(self) -> None:
        if self._date.isValid():
            self.clicked.emit(self._date)

    def _position_elements(self) -> None:
        size = self._layout.calendar_day_cell_size
        self._button.move(0, 0)
        self._button.resize(size, size)
        underline_height = self._layout.calendar_day_underline_height
        underline_offset = self._layout.calendar_day_underline_offset
        underline_width_config = self._layout.calendar_day_underline_width

        if underline_offset < 0:
            underline_offset = 0
        if underline_height < 0:
            underline_height = 0
        if underline_width_config < 0:
            underline_width_config = 0

        usable_height = max(0, min(underline_height, size))
        usable_width = max(0, min(underline_width_config, size))
        max_offset = max(0, min(underline_offset, size - usable_height))
        underline_x = (size - usable_width) // 2 if usable_width > 0 else 0

        self._underline.resize(usable_width, usable_height)
        self._underline.move(underline_x, size - usable_height - max_offset)
        self._underline.raise_()
        self._update_underline()

    def _update_stylesheet(
        self,
        *,
        background: str,
        text_color: str,
        hover_background: str,
        hover_text: str,
    ) -> None:
        radius = self._layout.calendar_day_cell_radius
        self._button.setStyleSheet(
            "QPushButton {"
            f"background-color: {background};"
            f"color: {text_color};"
            "border: none;"
            f"border-radius: {radius}px;"
            "padding: 0;"
            "outline: none;"
            "}"
            "QPushButton:hover {"
            f"background-color: {hover_background};"
            f"color: {hover_text};"
            "outline: none;"
            "}"
        )

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        if a0 is self._button and a1 is not None:
            if a1.type() == QEvent.Type.Enter:
                self._is_hovered = True
                self._update_underline()
            elif a1.type() == QEvent.Type.Leave:
                self._is_hovered = False
                self._update_underline()
        return super().eventFilter(a0, a1)

    def _update_underline(self) -> None:
        if not self._is_today:
            self._underline.hide()
            return

        color = self._hover_underline_color if self._is_hovered else self._underline_color
        if not color:
            self._underline.hide()
            return

        height = self._layout.calendar_day_underline_height
        radius = max(0, height // 2)
        self._underline.setStyleSheet(
            f"background-color: {color};"
            "border: none;"
            f"border-radius: {radius}px;"
        )
        self._underline.show()


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


__all__ = ["CalendarDayCell"]


