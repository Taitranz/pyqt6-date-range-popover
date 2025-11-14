from __future__ import annotations

import calendar
from collections.abc import Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ...exceptions import InvalidDateError
from ...styles import constants
from ...styles.style_templates import (
    CircularButtonHoverStyle,
    CircularButtonStyle,
    circular_button_default_qss,
    circular_button_selected_qss,
)
from ...styles.theme import CalendarStyleConfig, LayoutConfig
from ...utils import connect_signal


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
        if style is None:
            style = CalendarStyleConfig(
                background="#1f1f1f",
                header_text_color="#f5f5f5",
                day_text_color="#f5f5f5",
                muted_day_text_color="#8c8c8c",
                today_background="#f5f5f5",
                today_text_color="#1f1f1f",
                today_underline_color="#1f1f1f",
                day_hover_background="#2e2e2e",
                day_hover_text_color="#f5f5f5",
                nav_icon_color="#dbdbdb",
                day_label_background="#2e2e2e",
                mode_label_background="#2e2e2e",
                header_hover_background="#2e2e2e",
                header_hover_text_color="#ffffff",
                range_edge_background="#f2f2f2",
                range_edge_text_color="#1f1f1f",
                range_between_background="#2e2e2e",
                range_between_text_color="#ffffff",
            )
        self._style = style
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
            connect_signal(button.clicked, self._make_handler(index))
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
            raise InvalidDateError("month must be between 1 and 12")
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
            circular_button_selected_qss(
                CircularButtonStyle(
                    background=self._style.today_background,
                    text_color=self._style.today_text_color,
                    radius=radius,
                )
            )
        )

    def _apply_default_style(self, button: QPushButton) -> None:
        radius = self._layout_config.calendar_day_cell_radius
        button.setStyleSheet(
            circular_button_default_qss(
                CircularButtonHoverStyle(
                    text_color=self._style.day_text_color,
                    hover_background=self._style.day_hover_background,
                    hover_text_color=self._style.day_hover_text_color,
                    radius=radius,
                )
            )
        )

    def _make_handler(self, month: int) -> Callable[[], None]:
        def handler() -> None:
            self._selected_month = month
            self._refresh_button_styles()
            self.month_selected.emit(month)

        return handler


__all__ = ["CalendarMonthView"]
