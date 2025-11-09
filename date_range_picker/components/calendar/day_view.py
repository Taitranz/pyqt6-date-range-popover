from __future__ import annotations

import calendar
from typing import Callable, Iterable, List, Protocol, cast

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...styles import constants
from ...styles.theme import CalendarStyleConfig, LayoutConfig
from .day_cell import CalendarDayCell


class CalendarDayView(QWidget):
    """Displays the day grid with weekday labels."""

    day_selected = pyqtSignal(QDate)

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

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(self._layout_config.calendar_grid_spacing)

        self._labels_container = QWidget(self)
        self._labels_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._labels_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        root_layout.addWidget(self._labels_container, alignment=Qt.AlignmentFlag.AlignCenter)

        labels_layout = QHBoxLayout(self._labels_container)
        labels_layout.setContentsMargins(0, 0, 0, 0)
        labels_layout.setSpacing(self._layout_config.calendar_grid_spacing)

        self._weekday_labels: list[QLabel] = []
        for day_name in self._weekday_names():
            label = QLabel(day_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(constants.create_calendar_day_label_font())
            label.setFixedWidth(self._layout_config.calendar_day_cell_size)
            label.setFixedHeight(self._layout_config.calendar_day_label_height)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            labels_layout.addWidget(label)
            self._weekday_labels.append(label)

        self._grid_container = QWidget(self)
        self._grid_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        root_layout.addWidget(self._grid_container, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout = QGridLayout(self._grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(self._layout_config.calendar_grid_spacing)
        grid_layout.setVerticalSpacing(self._layout_config.calendar_grid_spacing)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._cells: list[CalendarDayCell] = []
        for index in range(6 * 7):
            cell = CalendarDayCell(
                self._grid_container,
                style=self._style,
                layout=self._layout_config,
            )
            cast(_DateSignal, cell.clicked).connect(self.day_selected.emit)
            row = index // 7
            column = index % 7
            grid_layout.addWidget(cell, row, column, alignment=Qt.AlignmentFlag.AlignCenter)
            self._cells.append(cell)

        self.apply_style(self._style)

    def apply_style(self, style: CalendarStyleConfig) -> None:
        self._style = style
        self.setStyleSheet(f"background-color: {style.background};")
        self._labels_container.setStyleSheet(
            f"background-color: {style.day_label_background};"
            " border-radius: 4px;"
            " border: none;"
        )
        for label in self._weekday_labels:
            label.setStyleSheet(
                f"color: {style.muted_day_text_color};"
                " background-color: transparent;"
                " border: none;"
            )
        for cell in self._cells:
            cell.apply_style(style)

    def update_days(
        self,
        *,
        visible_month: QDate,
        today: QDate,
        selected_date: QDate,
    ) -> None:
        month_start = QDate(visible_month.year(), visible_month.month(), 1)
        start_offset = (month_start.dayOfWeek() - 1) % 7
        start_date = month_start.addDays(-start_offset)

        for index, cell in enumerate(self._cells):
            day_date = start_date.addDays(index)
            in_current_month = (
                day_date.month() == visible_month.month()
                and day_date.year() == visible_month.year()
            )
            is_selected: bool = day_date.toJulianDay() == selected_date.toJulianDay()
            is_future: bool = bool(today.daysTo(day_date) > 0)
            cell.set_day(
                day_date,
                in_current_month=in_current_month,
                is_selected=is_selected,
                is_future=is_future,
            )

    def _weekday_names(self) -> Iterable[str]:
        locale = calendar.LocaleTextCalendar(firstweekday=0)
        labels: List[str] = []
        for day_index in range(7):
            label = locale.formatweekday(day_index, width=2).strip()
            labels.append(label.capitalize())
        return labels


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


__all__ = ["CalendarDayView"]


