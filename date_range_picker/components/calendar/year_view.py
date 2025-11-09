from __future__ import annotations

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


class CalendarYearView(QWidget):
    """Year range selection grid."""

    year_selected = pyqtSignal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        style: CalendarStyleConfig | None = None,
        layout: LayoutConfig | None = None,
        range_size: int = 20,
        grid_columns: int = 4,
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
        self._range_size = range_size
        self._grid_columns = grid_columns

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(self._layout_config.calendar_grid_spacing)
        grid_layout.setVerticalSpacing(14)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._buttons: list[QPushButton] = []
        for index in range(self._range_size):
            button = QPushButton("", self)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFont(constants.create_calendar_day_font())
            button.setFixedWidth(64)
            button.setFixedHeight(self._layout_config.calendar_day_cell_size)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            cast(_VoidSignal, button.clicked).connect(self._make_handler(button))
            row = index // self._grid_columns
            column = index % self._grid_columns
            grid_layout.addWidget(button, row, column)
            self._buttons.append(button)

        self._current_year = 1
        self._range_start = 1
        self.apply_style(self._style)

    def apply_style(self, style: CalendarStyleConfig) -> None:
        self._style = style
        self.setStyleSheet(f"background-color: {style.background};")
        self._refresh_button_styles()

    def set_year_range(self, start_year: int, *, current_year: int) -> None:
        self._range_start = start_year
        self._current_year = current_year
        for offset, button in enumerate(self._buttons):
            year = start_year + offset
            button.setText(str(year))
            button.setProperty("year", year)
        self._refresh_button_styles()

    def _refresh_button_styles(self) -> None:
        for button in self._buttons:
            year_value = button.property("year")
            if isinstance(year_value, int) and year_value == self._current_year:
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
            "}"
            "QPushButton:hover {"
            f"background-color: {self._style.day_hover_background};"
            f"color: {self._style.day_hover_text_color};"
            "}"
        )

    def _make_handler(self, button: QPushButton):
        def handler() -> None:
            year_value = button.property("year")
            if not isinstance(year_value, int):
                return
            self._current_year = year_value
            self._refresh_button_styles()
            self.year_selected.emit(year_value)

        return handler


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


__all__ = ["CalendarYearView"]


