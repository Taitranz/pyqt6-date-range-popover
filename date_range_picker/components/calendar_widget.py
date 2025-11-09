from __future__ import annotations

import calendar
from typing import Callable, Iterable, List, Protocol, cast

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..styles import constants


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


class _CalendarDayCell(QWidget):
    """Visual representation of a day cell in the calendar grid."""

    clicked = pyqtSignal(QDate)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date = QDate()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._button = QPushButton(self)
        self._button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._button.setFixedSize(
            constants.CALENDAR_DAY_CELL_SIZE, constants.CALENDAR_DAY_CELL_SIZE
        )
        self._button.setFont(constants.create_calendar_day_font())
        click_signal = cast(_VoidSignal, self._button.clicked)
        click_signal.connect(self._on_clicked)

        self._underline = QFrame(self)
        self._underline.setFixedHeight(2)
        self._underline.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout.addWidget(self._button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._underline)

        self.setFixedWidth(constants.CALENDAR_DAY_CELL_SIZE)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_day(self, date: QDate, *, in_current_month: bool, is_today: bool) -> None:
        self._date = date
        self._button.setText(str(date.day()))

        if in_current_month:
            text_color = constants.CALENDAR_DAY_TEXT_COLOR
        else:
            text_color = constants.CALENDAR_MUTED_DAY_TEXT_COLOR

        if is_today:
            background = constants.CALENDAR_TODAY_BACKGROUND
            hover_background = constants.CALENDAR_TODAY_BACKGROUND
            hover_text = constants.CALENDAR_TODAY_TEXT_COLOR
            text_color = constants.CALENDAR_TODAY_TEXT_COLOR
            self._underline.setStyleSheet(
                f"background-color: {constants.CALENDAR_TODAY_UNDERLINE_COLOR}; border: none;"
            )
            self._underline.setVisible(True)
        else:
            background = "transparent"
            hover_background = constants.CALENDAR_DAY_HOVER_BACKGROUND
            hover_text = constants.CALENDAR_DAY_HOVER_TEXT_COLOR
            self._underline.setStyleSheet("background-color: transparent; border: none;")
            self._underline.setVisible(False)

        self._button.setStyleSheet(
            "QPushButton {"
            f"background-color: {background};"
            f"color: {text_color};"
            "border: none;"
            f"border-radius: {constants.CALENDAR_DAY_CELL_RADIUS}px;"
            "padding: 0;"
            "}"
            "QPushButton:hover {"
            f"background-color: {hover_background};"
            f"color: {hover_text};"
            "}"
        )

    def _on_clicked(self) -> None:
        if self._date.isValid():
            self.clicked.emit(self._date)


class CalendarWidget(QWidget):
    """Standalone calendar component mirroring the visual design reference."""

    date_selected = pyqtSignal(QDate)

    _DAY_ORDER: List[int] = [1, 2, 3, 4, 5, 6, 7]  # Monday -> Sunday

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {constants.CALENDAR_BACKGROUND};")

        self._today = QDate.currentDate()
        self._visible_month = QDate(self._today.year(), self._today.month(), 1)
        self._day_cells: list[_CalendarDayCell] = []

        self._build_ui()
        self._populate_days()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, constants.CALENDAR_TOP_MARGIN, 0, 0)
        main_layout.setSpacing(constants.CALENDAR_HEADER_BOTTOM_MARGIN)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        self._previous_button = self._create_nav_button("<")
        self._next_button = self._create_nav_button(">")

        self._month_label = QLabel(self)
        self._month_label.setFont(constants.create_calendar_header_font())
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._month_label.setStyleSheet(
            f"color: {constants.CALENDAR_HEADER_TEXT_COLOR}; border: none;"
        )

        header_layout.addWidget(self._previous_button, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch()
        header_layout.addWidget(self._month_label, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header_layout.addWidget(self._next_button, alignment=Qt.AlignmentFlag.AlignRight)

        previous_signal = cast(_VoidSignal, self._previous_button.clicked)
        previous_signal.connect(self._go_to_previous_month)
        next_signal = cast(_VoidSignal, self._next_button.clicked)
        next_signal.connect(self._go_to_next_month)

        main_layout.addLayout(header_layout)

        day_label_layout = QHBoxLayout()
        day_label_layout.setContentsMargins(0, 0, 0, 0)
        day_label_layout.setSpacing(constants.CALENDAR_GRID_SPACING)

        for day_name in self._weekday_labels():
            label = QLabel(day_name, self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(constants.create_calendar_day_label_font())
            label.setFixedWidth(constants.CALENDAR_DAY_CELL_SIZE)
            label.setFixedHeight(constants.CALENDAR_DAY_LABEL_HEIGHT)
            label.setStyleSheet(
                f"color: {constants.CALENDAR_MUTED_DAY_TEXT_COLOR}; border: none;"
            )
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            day_label_layout.addWidget(label)

        main_layout.addLayout(day_label_layout)

        grid_container = QWidget(self)
        grid_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(constants.CALENDAR_GRID_SPACING)
        grid_layout.setVerticalSpacing(constants.CALENDAR_GRID_SPACING)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for index in range(6 * 7):
            cell = _CalendarDayCell(grid_container)
            cell_signal = cast(_DateSignal, cell.clicked)
            cell_signal.connect(self._emit_date_selected)
            row = index // 7
            column = index % 7
            grid_layout.addWidget(cell, row, column, alignment=Qt.AlignmentFlag.AlignCenter)
            self._day_cells.append(cell)

        main_layout.addWidget(grid_container, alignment=Qt.AlignmentFlag.AlignCenter)

    def _create_nav_button(self, text: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFixedSize(32, 32)
        button.setFont(constants.create_calendar_day_font())
        button.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            f"color: {constants.CALENDAR_NAV_ICON_COLOR};"
            "border: none;"
            "}"
            "QPushButton:hover {"
            f"color: {constants.CALENDAR_DAY_HOVER_TEXT_COLOR};"
            "}"
        )
        return button

    def _weekday_labels(self) -> Iterable[str]:
        locale = calendar.LocaleTextCalendar(firstweekday=0)
        # PyQt calendar uses Monday as day 1; we want Monday-first labels
        labels: list[str] = []
        for day_index in self._DAY_ORDER:
            # Convert to python weekday (0=Monday)
            python_weekday = (day_index - 1) % 7
            label = locale.formatweekday(python_weekday, width=2).strip()
            labels.append(label.capitalize())
        return labels

    def _populate_days(self) -> None:
        month_start = QDate(self._visible_month.year(), self._visible_month.month(), 1)
        start_offset = (month_start.dayOfWeek() - 1) % 7  # dayOfWeek: Monday=1
        start_date = month_start.addDays(-start_offset)

        month_name = calendar.month_name[self._visible_month.month()]
        self._month_label.setText(f"{month_name} {self._visible_month.year()}")

        for index, cell in enumerate(self._day_cells):
            day_date = start_date.addDays(index)
            in_current_month = (
                day_date.month() == self._visible_month.month()
                and day_date.year() == self._visible_month.year()
            )
            is_today = (
                day_date.year() == self._today.year()
                and day_date.month() == self._today.month()
                and day_date.day() == self._today.day()
            )
            cell.set_day(day_date, in_current_month=in_current_month, is_today=is_today)

    def _change_month(self, delta: int) -> None:
        self._visible_month = self._visible_month.addMonths(delta)
        self._populate_days()

    def _go_to_previous_month(self) -> None:
        self._change_month(-1)

    def _go_to_next_month(self) -> None:
        self._change_month(1)

    def _emit_date_selected(self, date: QDate) -> None:
        self.date_selected.emit(date)


