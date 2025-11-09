from __future__ import annotations

import calendar

from typing import Callable, Protocol, cast

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ...styles import constants
from ...styles.theme import CalendarStyleConfig, LayoutConfig


class CalendarMonthView(QWidget):
    """Month selection grid."""

    month_selected = pyqtSignal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        style: CalendarStyleConfig | None = None,
        layout: LayoutConfig | None = None,
    ) -> None:
        super().__init__(parent)
        self._style = style or CalendarStyleConfig(
            background="#1f1f1f",
            header_text_color="#f5f5f5",
            day_text_color="#f5f5f5",
            muted_day_text_color="#8c8c8c",
            today_background="#f5f5f5",
            today_text_color="#1f1f1f",
            today_underline_color="#1f1f1f",
            day_hover_background="#343434",
            day_hover_text_color="#f5f5f5",
            nav_icon_color="#dbdbdb",
            day_label_background="#2e2e2e",
            mode_label_background="#2e2e2e",
            header_hover_background="#2e2e2e",
            header_hover_text_color="#ffffff",
        )
        self._layout_config = layout or LayoutConfig()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(262, 236)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(self._layout_config.calendar_grid_spacing)
        grid_layout.setVerticalSpacing(self._layout_config.calendar_month_vertical_spacing)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._buttons: list[QPushButton] = []
        for index in range(1, 13):
            month_name = calendar.month_abbr[index]
            button = QPushButton(month_name, self)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFont(constants.create_calendar_day_font())
            button.setFixedWidth(86)
            button.setFixedHeight(self._layout_config.calendar_day_cell_size)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            cast(_VoidSignal, button.clicked).connect(self._make_handler(index))
            row = (index - 1) // 3
            column = (index - 1) % 3
            grid_layout.addWidget(button, row, column)
            grid_layout.setColumnStretch(column, 1)
            grid_layout.setRowStretch(row, 1)
            self._buttons.append(button)

        self._selected_month = 1
        self.apply_style(self._style)

    def apply_style(self, style: CalendarStyleConfig) -> None:
        self._style = style
        self.setStyleSheet(f"background-color: {style.background};")
        self._refresh_button_styles()

    def set_selected_month(self, month: int) -> None:
        if month < 1 or month > 12:
            return
        if self._selected_month == month:
            return
        self._selected_month = month
        self._refresh_button_styles()

    def _refresh_button_styles(self) -> None:
        for index, button in enumerate(self._buttons, start=1):
            if index == self._selected_month:
                self._apply_selected_style(button)
            else:
                self._apply_default_style(button)

    def _apply_selected_style(self, button: QPushButton) -> None:
        radius = self._layout_config.calendar_day_cell_radius
        button.setStyleSheet(
            "QPushButton {"
            f"background-color: {self._style.today_background};"
            f"color: {self._style.today_text_color};"
            "border: none;"
            f"border-radius: {radius}px;"
            "padding: 0;"
            "outline: none;"
            "}"
        )

    def _apply_default_style(self, button: QPushButton) -> None:
        radius = self._layout_config.calendar_day_cell_radius
        button.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            f"color: {self._style.day_text_color};"
            "border: none;"
            f"border-radius: {radius}px;"
            "padding: 0;"
            "outline: none;"
            "}"
            "QPushButton:hover {"
            f"background-color: {self._style.day_hover_background};"
            f"color: {self._style.day_hover_text_color};"
            "outline: none;"
            "}"
        )

    def _make_handler(self, month: int):
        def handler() -> None:
            self._selected_month = month
            self._refresh_button_styles()
            self.month_selected.emit(month)

        return handler


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


__all__ = ["CalendarMonthView"]


