from __future__ import annotations

from typing import Callable, Protocol, cast

from PyQt6.QtCore import QDate, Qt, pyqtSignal
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
    ) -> None:
        self._date = date

        if self._style is None:
            return

        if not in_current_month:
            self._button.setVisible(False)
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

        if is_selected:
            background = self._style.today_background
            hover_background = self._style.today_background
            hover_text = self._style.today_text_color
            text_color = self._style.today_text_color
        else:
            background = "transparent"
            hover_background = self._style.day_hover_background
            hover_text = self._style.day_hover_text_color

        self._update_stylesheet(
            background=background,
            text_color=text_color,
            hover_background=hover_background,
            hover_text=hover_text,
        )

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
            "}"
            "QPushButton:hover {"
            f"background-color: {hover_background};"
            f"color: {hover_text};"
            "}"
        )


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


__all__ = ["CalendarDayCell"]


