from __future__ import annotations

import calendar
from enum import Enum, auto
from functools import partial
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Protocol, cast

from PyQt6.QtCore import QByteArray, QDate, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QResizeEvent
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..styles import constants


NAV_LEFT_ICON_PATH: Path = Path(__file__).resolve().parent.parent / "assets" / "carrot_left.svg"
NAV_RIGHT_ICON_PATH: Path = Path(__file__).resolve().parent.parent / "assets" / "carrot_right.svg"


def _create_nav_icon(icon_path: Path, size: int, color: str) -> QIcon:
    """Create a colored SVG icon from a file path."""
    try:
        svg_text = icon_path.read_text(encoding="utf-8")
    except OSError:
        return QIcon()
    colored_svg = svg_text.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(colored_svg.encode("utf-8")))
    if not renderer.isValid():
        return QIcon()
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    icon = QIcon(pixmap)
    return icon


class _VoidSignal(Protocol):
    def connect(self, slot: Callable[[], None]) -> object: ...


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


class _CalendarViewMode(Enum):
    DAY = auto()
    MONTH = auto()
    YEAR = auto()


class _CalendarDayCell(QWidget):
    """Visual representation of a day cell in the calendar grid."""

    clicked = pyqtSignal(QDate)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date = QDate()

        self._button = QPushButton(self)
        self._button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._button.setFixedSize(
            constants.CALENDAR_DAY_CELL_SIZE, constants.CALENDAR_DAY_CELL_SIZE
        )
        self._button.setFont(constants.create_calendar_day_font())
        click_signal = cast(_VoidSignal, self._button.clicked)
        click_signal.connect(self._on_clicked)

        self.setFixedSize(
            constants.CALENDAR_DAY_CELL_SIZE, constants.CALENDAR_DAY_CELL_SIZE
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._position_elements()

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
        else:
            background = "transparent"
            hover_background = constants.CALENDAR_DAY_HOVER_BACKGROUND
            hover_text = constants.CALENDAR_DAY_HOVER_TEXT_COLOR

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

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        self._position_elements()

    def _position_elements(self) -> None:
        size = constants.CALENDAR_DAY_CELL_SIZE
        self._button.move(0, 0)
        self._button.resize(size, size)


class CalendarWidget(QWidget):
    """Standalone calendar component mirroring the visual design reference."""

    date_selected = pyqtSignal(QDate)

    _DAY_ORDER: List[int] = [1, 2, 3, 4, 5, 6, 7]  # Monday -> Sunday
    _MONTH_GRID_COLUMNS = 3
    _YEAR_GRID_COLUMNS = 4
    _YEAR_RANGE_SIZE = 20
    _MAX_YEAR = 9999

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {constants.CALENDAR_BACKGROUND};")

        self._today = QDate.currentDate()
        self._visible_month = QDate(self._today.year(), self._today.month(), 1)
        self._day_cells: list[_CalendarDayCell] = []
        self._month_buttons: list[QPushButton] = []
        self._year_buttons: list[QPushButton] = []
        self._view_mode: Optional[_CalendarViewMode] = None
        self._year_range_start = self._compute_year_range_start(self._visible_month.year())

        self._build_ui()
        self._switch_view(_CalendarViewMode.DAY)

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, constants.CALENDAR_TOP_MARGIN, 0, 0)
        main_layout.setSpacing(constants.CALENDAR_HEADER_BOTTOM_MARGIN)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        self._previous_button = self._create_nav_button("<")
        self._next_button = self._create_nav_button(">")

        self._header_button = self._create_header_button()

        header_layout.addWidget(self._previous_button, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch()
        header_layout.addWidget(self._header_button, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header_layout.addWidget(self._next_button, alignment=Qt.AlignmentFlag.AlignRight)

        previous_signal = cast(_VoidSignal, self._previous_button.clicked)
        previous_signal.connect(self._on_previous_clicked)
        next_signal = cast(_VoidSignal, self._next_button.clicked)
        next_signal.connect(self._on_next_clicked)
        header_signal = cast(_VoidSignal, self._header_button.clicked)
        header_signal.connect(self._on_header_clicked)

        main_layout.addLayout(header_layout)

        self._mode_label_container = QWidget(self)
        self._mode_label_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._mode_label_container.setStyleSheet(
            f"background-color: {constants.CALENDAR_MODE_LABEL_BACKGROUND};"
            " border-radius: 4px;"
            " border: none;"
        )
        self._mode_label_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._mode_label_container.setFixedWidth(262)

        mode_label_layout = QHBoxLayout(self._mode_label_container)
        mode_label_layout.setContentsMargins(0, 0, 0, 0)
        mode_label_layout.setSpacing(constants.CALENDAR_GRID_SPACING)

        self._mode_label = QLabel()
        self._mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_label.setFont(constants.create_calendar_day_label_font())
        self._mode_label.setStyleSheet(
            f"color: {constants.CALENDAR_MUTED_DAY_TEXT_COLOR};"
            " background-color: transparent;"
            " border: none;"
        )
        self._mode_label.setFixedHeight(constants.CALENDAR_DAY_LABEL_HEIGHT)
        mode_label_layout.addWidget(self._mode_label)

        self._mode_label_container.setVisible(False)
        main_layout.addWidget(self._mode_label_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self._content_stack = QStackedWidget(self)
        self._content_stack.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._day_view = self._build_day_view()
        self._content_stack.addWidget(self._day_view)
        self._month_view = self._build_month_view()
        self._content_stack.addWidget(self._month_view)
        self._year_view = self._build_year_view()
        self._content_stack.addWidget(self._year_view)

        main_layout.addWidget(self._content_stack, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_day_view(self) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(constants.CALENDAR_GRID_SPACING)

        day_label_container = QWidget(container)
        day_label_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        day_label_container.setStyleSheet(
            f"background-color: {constants.CALENDAR_DAY_LABEL_BACKGROUND};"
            " border-radius: 4px;"
            " border: none;"
        )
        day_label_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        day_label_layout = QHBoxLayout(day_label_container)
        day_label_layout.setContentsMargins(0, 0, 0, 0)
        day_label_layout.setSpacing(constants.CALENDAR_GRID_SPACING)

        for day_name in self._weekday_labels():
            label = QLabel(day_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(constants.create_calendar_day_label_font())
            label.setFixedWidth(constants.CALENDAR_DAY_CELL_SIZE)
            label.setFixedHeight(constants.CALENDAR_DAY_LABEL_HEIGHT)
            label.setStyleSheet(
                f"color: {constants.CALENDAR_MUTED_DAY_TEXT_COLOR};"
                " background-color: transparent;"
                " border: none;"
            )
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            day_label_layout.addWidget(label)

        layout.addWidget(day_label_container, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_container = QWidget(container)
        grid_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(constants.CALENDAR_GRID_SPACING)
        grid_layout.setVerticalSpacing(constants.CALENDAR_GRID_SPACING)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._day_cells.clear()
        for index in range(6 * 7):
            cell = _CalendarDayCell(grid_container)
            cell_signal = cast(_DateSignal, cell.clicked)
            cell_signal.connect(self._emit_date_selected)
            row = index // 7
            column = index % 7
            grid_layout.addWidget(cell, row, column, alignment=Qt.AlignmentFlag.AlignCenter)
            self._day_cells.append(cell)

        layout.addWidget(grid_container, alignment=Qt.AlignmentFlag.AlignCenter)
        return container

    def _build_month_view(self) -> QWidget:
        container = QWidget(self)
        container.setFixedSize(262, 236)
        container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container.setStyleSheet("background-color: #1f1f1f;")
        
        layout = QGridLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(constants.CALENDAR_GRID_SPACING)
        layout.setVerticalSpacing(32)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._month_buttons.clear()
        for index in range(1, 13):
            month_name = calendar.month_abbr[index]
            button = self._create_option_button(month_name, container)
            button.setFixedWidth(86)
            month_signal = cast(_VoidSignal, button.clicked)
            month_signal.connect(partial(self._on_month_clicked, index))
            row = (index - 1) // self._MONTH_GRID_COLUMNS
            column = (index - 1) % self._MONTH_GRID_COLUMNS
            layout.addWidget(button, row, column)
            layout.setColumnStretch(column, 1)
            layout.setRowStretch(row, 1)
            self._month_buttons.append(button)

        return container

    def _build_year_view(self) -> QWidget:
        container = QWidget(self)
        layout = QGridLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(constants.CALENDAR_GRID_SPACING)
        layout.setVerticalSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._year_buttons.clear()
        for index in range(self._YEAR_RANGE_SIZE):
            button = self._create_option_button("", container)
            button.setFixedWidth(64)
            year_signal = cast(_VoidSignal, button.clicked)
            year_signal.connect(partial(self._on_year_button_clicked, button))
            row = index // self._YEAR_GRID_COLUMNS
            column = index % self._YEAR_GRID_COLUMNS
            layout.addWidget(button, row, column)
            self._year_buttons.append(button)

        return container

    def _create_header_button(self) -> QPushButton:
        button = QPushButton(self)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFlat(True)
        button.setFont(constants.create_calendar_header_font())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            f"color: {constants.CALENDAR_HEADER_TEXT_COLOR};"
            "border: none;"
            "padding: 4px 11px 4px 11px;"
            "border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "background-color: #2e2e2e;"
            f"color: {constants.CALENDAR_DAY_HOVER_TEXT_COLOR};"
            "}"
        )
        return button

    def _create_option_button(self, text: str, parent: QWidget) -> QPushButton:
        button = QPushButton(text, parent)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFont(constants.create_calendar_day_font())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedHeight(constants.CALENDAR_DAY_CELL_SIZE)
        button.setMinimumWidth(constants.CALENDAR_DAY_CELL_SIZE * 2)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._style_option_button(button, is_selected=False)
        return button

    def _style_option_button(self, button: QPushButton, *, is_selected: bool) -> None:
        if is_selected:
            background = constants.CALENDAR_TODAY_BACKGROUND
            text_color = constants.CALENDAR_TODAY_TEXT_COLOR
        else:
            background = "transparent"
            text_color = constants.CALENDAR_DAY_TEXT_COLOR

        button.setStyleSheet(
            "QPushButton {"
            f"background-color: {background};"
            f"color: {text_color};"
            "border: none;"
            f"border-radius: {constants.CALENDAR_DAY_CELL_RADIUS}px;"
            "padding: 0;"
            "}"
            "QPushButton:hover {"
            f"background-color: {constants.CALENDAR_DAY_HOVER_BACKGROUND};"
            f"color: {constants.CALENDAR_DAY_HOVER_TEXT_COLOR};"
            "}"
        )

    def _create_nav_button(self, text: str) -> QPushButton:
        button = QPushButton(self)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFixedSize(32, 32)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Load SVG icon based on button text
        if text == "<":
            icon_path = NAV_LEFT_ICON_PATH
        else:  # text == ">"
            icon_path = NAV_RIGHT_ICON_PATH
        
        icon = _create_nav_icon(icon_path, 32, constants.CALENDAR_NAV_ICON_COLOR)
        button.setIcon(icon)
        button.setIconSize(icon.actualSize(button.size()))
        
        button.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            "border: none;"
            "}"
            "QPushButton:hover {"
            "background-color: #343434;"
            "}"
        )
        return button

    def _on_header_clicked(self) -> None:
        if self._view_mode is None:
            return

        if self._view_mode is _CalendarViewMode.DAY:
            self._switch_view(_CalendarViewMode.MONTH)
        elif self._view_mode is _CalendarViewMode.MONTH:
            self._switch_view(_CalendarViewMode.YEAR)
        else:
            self._switch_view(_CalendarViewMode.DAY)

    def _on_previous_clicked(self) -> None:
        if self._view_mode is _CalendarViewMode.DAY:
            self._change_month(-1)
        elif self._view_mode is _CalendarViewMode.MONTH:
            self._change_year(-1)
        else:
            self._shift_year_range(-self._YEAR_RANGE_SIZE)

    def _on_next_clicked(self) -> None:
        if self._view_mode is _CalendarViewMode.DAY:
            self._change_month(1)
        elif self._view_mode is _CalendarViewMode.MONTH:
            self._change_year(1)
        else:
            self._shift_year_range(self._YEAR_RANGE_SIZE)

    def _switch_view(self, view: _CalendarViewMode) -> None:
        if self._view_mode == view:
            if view is _CalendarViewMode.DAY:
                self._populate_days()
            elif view is _CalendarViewMode.MONTH:
                self._update_month_buttons()
            else:
                self._ensure_year_range_contains(self._visible_month.year())
                self._update_year_buttons()
            self._update_header()
            return

        self._view_mode = view

        if view is _CalendarViewMode.DAY:
            self._mode_label_container.setVisible(False)
            self._content_stack.setCurrentWidget(self._day_view)
            self._populate_days()
        elif view is _CalendarViewMode.MONTH:
            self._mode_label.setText("Months")
            self._mode_label_container.setVisible(True)
            self._content_stack.setCurrentWidget(self._month_view)
            self._update_month_buttons()
        else:
            self._mode_label.setText("Years")
            self._mode_label_container.setVisible(True)
            self._content_stack.setCurrentWidget(self._year_view)
            self._ensure_year_range_contains(self._visible_month.year())
            self._update_year_buttons()

        self._update_header()

    def _update_header(self) -> None:
        if self._view_mode is _CalendarViewMode.DAY:
            month_name = calendar.month_name[self._visible_month.month()]
            self._header_button.setText(f"{month_name} {self._visible_month.year()}")
        elif self._view_mode is _CalendarViewMode.MONTH:
            self._header_button.setText(str(self._visible_month.year()))
        elif self._view_mode is _CalendarViewMode.YEAR:
            start = self._year_range_start
            end = start + self._YEAR_RANGE_SIZE - 1
            self._header_button.setText(f"{start} - {end}")

    def _update_month_buttons(self) -> None:
        current_month = self._visible_month.month()
        for index, button in enumerate(self._month_buttons, start=1):
            is_selected = index == current_month
            self._style_option_button(button, is_selected=is_selected)

    def _update_year_buttons(self) -> None:
        current_year = self._visible_month.year()
        start = self._year_range_start
        for offset, button in enumerate(self._year_buttons):
            year = start + offset
            button.setText(str(year))
            button.setProperty("year", year)
            self._style_option_button(button, is_selected=year == current_year)

    def _on_month_clicked(self, month: int) -> None:
        self._visible_month = QDate(self._visible_month.year(), month, 1)
        self._switch_view(_CalendarViewMode.DAY)

    def _on_year_button_clicked(self, button: QPushButton) -> None:
        property_value = button.property("year")
        if not isinstance(property_value, int):
            return
        self._visible_month = QDate(property_value, self._visible_month.month(), 1)
        self._switch_view(_CalendarViewMode.MONTH)

    def _change_month(self, delta: int) -> None:
        self._visible_month = self._visible_month.addMonths(delta)
        self._populate_days()
        self._update_header()
        if self._view_mode is _CalendarViewMode.MONTH:
            self._update_month_buttons()
        elif self._view_mode is _CalendarViewMode.YEAR:
            self._ensure_year_range_contains(self._visible_month.year())
            self._update_year_buttons()

    def _change_year(self, delta: int) -> None:
        self._visible_month = self._visible_month.addYears(delta)
        self._update_month_buttons()
        self._ensure_year_range_contains(self._visible_month.year())
        self._update_year_buttons()
        self._update_header()

    def _shift_year_range(self, delta: int) -> None:
        proposed = self._year_range_start + delta
        min_start = 1
        max_start = self._MAX_YEAR - self._YEAR_RANGE_SIZE + 1
        if proposed < min_start:
            proposed = min_start
        if proposed > max_start:
            proposed = max_start
        self._year_range_start = self._compute_year_range_start(proposed)
        self._update_year_buttons()
        self._update_header()

    def _ensure_year_range_contains(self, year: int) -> None:
        end = self._year_range_start + self._YEAR_RANGE_SIZE - 1
        if year < self._year_range_start or year > end:
            self._year_range_start = self._compute_year_range_start(year)

    def _compute_year_range_start(self, year: int) -> int:
        span = self._YEAR_RANGE_SIZE
        if year < 1:
            return 1
        base = (year // span) * span
        if base < 1:
            base = 1
        max_start = self._MAX_YEAR - span + 1
        if base > max_start:
            base = max_start
        return base

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

    def _emit_date_selected(self, date: QDate) -> None:
        self.date_selected.emit(date)


