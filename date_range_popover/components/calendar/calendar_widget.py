from __future__ import annotations

import calendar
from enum import Enum, auto
from typing import cast

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget

from ...exceptions import InvalidDateError
from ...styles.style_templates import (
    ModeLabelStyle,
    mode_label_container_qss,
    mode_label_text_qss,
)
from ...styles.theme import CalendarStyleConfig, LayoutConfig
from ...utils import connect_signal, first_of_month
from ...validation import validate_date_range, validate_qdate
from .day_view import CalendarDayView
from .month_view import CalendarMonthView
from .navigation import CalendarNavigation
from .year_range_utils import (
    clamp_year_range_start,
    compute_year_range_start,
    year_range_limits,
)
from .year_view import CalendarYearView


class CalendarViewMode(Enum):
    DAY = auto()
    MONTH = auto()
    YEAR = auto()


class CalendarWidget(QWidget):
    """Coordinator widget that wraps day/month/year views."""

    date_selected = pyqtSignal(QDate)

    _YEAR_RANGE_SIZE = 20
    _YEAR_GRID_COLUMNS = 4
    _MAX_YEAR = 9999

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

        self._today: QDate = QDate.currentDate()
        self._selected_date: QDate = self._today
        self._visible_month: QDate = QDate(self._today.year(), self._today.month(), 1)
        self._view_mode: CalendarViewMode = CalendarViewMode.DAY
        self._range_start: QDate | None = None
        self._range_end: QDate | None = None
        self._min_date: QDate | None = None
        self._max_date: QDate | None = None
        self._year_range_start = compute_year_range_start(
            self._visible_month.year(),
            self._YEAR_RANGE_SIZE,
            max_year=self._MAX_YEAR,
        )

        self._navigation = CalendarNavigation(style=self._style)
        self._day_view = CalendarDayView(style=self._style, layout=self._layout_config)
        self._month_view = CalendarMonthView(style=self._style, layout=self._layout_config)
        self._year_view = CalendarYearView(
            style=self._style,
            layout=self._layout_config,
            range_size=self._YEAR_RANGE_SIZE,
            grid_columns=self._YEAR_GRID_COLUMNS,
        )
        self._content_stack = QStackedWidget(self)
        self._mode_label_container: QWidget | None = None
        self._mode_label: QLabel | None = None

        self._build_ui()
        self.apply_style(self._style)
        self._switch_view(CalendarViewMode.DAY)

    def apply_style(self, style: CalendarStyleConfig) -> None:
        self._style = style
        self.setStyleSheet(f"background-color: {style.background};")
        self._navigation.apply_style(style)
        self._day_view.apply_style(style)
        self._month_view.apply_style(style)
        self._year_view.apply_style(style)
        mode_label_style = ModeLabelStyle(
            background=style.mode_label_background,
            text_color=style.muted_day_text_color,
            radius=4,
        )
        if self._mode_label_container is not None:
            self._mode_label_container.setStyleSheet(mode_label_container_qss(mode_label_style))
        if self._mode_label is not None:
            self._mode_label.setStyleSheet(mode_label_text_qss(mode_label_style))

    def set_constraints(self, *, min_date: QDate | None, max_date: QDate | None) -> None:
        """Limit selectable dates and navigation range."""
        self._min_date = QDate(min_date) if isinstance(min_date, QDate) else None
        self._max_date = QDate(max_date) if isinstance(max_date, QDate) else None
        if self._range_start is not None:
            self._range_start = self._clamp_date(self._range_start)
        if self._range_end is not None:
            self._range_end = self._clamp_date(self._range_end)
        self._selected_date = self._clamp_date(self._selected_date)
        self._visible_month = self._clamp_month(self._visible_month)
        self._ensure_year_range_contains(self._visible_month.year())
        self._refresh_views()

    def set_selected_date(self, date: QDate) -> None:
        """Set the selected date and make it visible."""
        validated = cast(QDate, validate_qdate(date, field_name="selected_date"))
        validated = self._ensure_within_bounds(validated, "selected_date")
        if validated.year() < 1 or validated.year() > self._MAX_YEAR:
            raise InvalidDateError(f"selected_date must fall between years 1 and {self._MAX_YEAR}")
        self._selected_date = validated
        self._visible_month = self._clamp_month(validated)
        self._ensure_year_range_contains(validated.year())
        self._switch_view(CalendarViewMode.DAY)

    def set_selected_range(self, start: QDate, end: QDate) -> None:
        """Set the highlighted date range."""
        start_candidate, end_candidate = validate_date_range(
            start,
            end,
            field_name="selected_range",
            allow_partial=False,
        )
        self._range_start = self._ensure_within_bounds(
            cast(QDate, start_candidate), "selected_range.start"
        )
        self._range_end = self._ensure_within_bounds(
            cast(QDate, end_candidate), "selected_range.end"
        )
        self._refresh_views()

    def clear_selected_range(self) -> None:
        """Clear any highlighted range selection."""
        if self._range_start is None and self._range_end is None:
            return
        self._range_start = None
        self._range_end = None
        self._refresh_views()

    def set_visible_month(self, month: QDate) -> None:
        """Change the month currently rendered by the widget."""
        validated = cast(QDate, validate_qdate(month, field_name="visible_month"))
        target = self._clamp_month(validated)
        if target == self._visible_month:
            return
        self._visible_month = target
        self._ensure_year_range_contains(target.year())
        self._refresh_views()

    # Internal logic -----------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, self._layout_config.calendar_top_margin, 0, 0)
        layout.setSpacing(self._layout_config.calendar_header_bottom_margin)

        layout.addWidget(self._navigation)

        self._mode_label_container = self._setup_mode_label_container()
        layout.addWidget(self._mode_label_container)

        self._content_stack.setSizePolicy(
            self._day_view.sizePolicy().horizontalPolicy(),
            self._day_view.sizePolicy().verticalPolicy(),
        )
        layout.addWidget(self._content_stack, alignment=Qt.AlignmentFlag.AlignCenter)
        self._content_stack.addWidget(self._day_view)
        self._content_stack.addWidget(self._month_view)
        self._content_stack.addWidget(self._year_view)

        connect_signal(self._navigation.previous_clicked, self._on_previous_clicked)
        connect_signal(self._navigation.next_clicked, self._on_next_clicked)
        connect_signal(self._navigation.header_clicked, self._on_header_clicked)
        connect_signal(self._day_view.day_selected, self._on_day_selected)
        connect_signal(self._month_view.month_selected, self._on_month_selected)
        connect_signal(self._year_view.year_selected, self._on_year_selected)

    def _on_day_selected(self, date: QDate) -> None:
        self._selected_date = self._ensure_within_bounds(date, "selected_date")
        self._visible_month = self._clamp_month(self._selected_date)
        self._refresh_views()
        self.date_selected.emit(self._selected_date)

    def _on_month_selected(self, month: int) -> None:
        candidate = QDate(self._visible_month.year(), month, 1)
        self._visible_month = self._clamp_month(candidate)
        self._switch_view(CalendarViewMode.DAY)

    def _on_year_selected(self, year: int) -> None:
        candidate = QDate(year, self._visible_month.month(), 1)
        self._visible_month = self._clamp_month(candidate)
        self._switch_view(CalendarViewMode.MONTH)

    def _on_header_clicked(self) -> None:
        if self._view_mode is CalendarViewMode.DAY:
            self._switch_view(CalendarViewMode.MONTH)
        elif self._view_mode is CalendarViewMode.MONTH:
            self._switch_view(CalendarViewMode.YEAR)
        else:
            self._switch_view(CalendarViewMode.DAY)

    def _on_previous_clicked(self) -> None:
        if self._view_mode is CalendarViewMode.DAY:
            self._change_month(-1)
        elif self._view_mode is CalendarViewMode.MONTH:
            self._change_year(-1)
        else:
            self._shift_year_range(-self._YEAR_RANGE_SIZE)

    def _on_next_clicked(self) -> None:
        if self._view_mode is CalendarViewMode.DAY:
            self._change_month(1)
        elif self._view_mode is CalendarViewMode.MONTH:
            self._change_year(1)
        else:
            self._shift_year_range(self._YEAR_RANGE_SIZE)

    def _switch_view(self, view: CalendarViewMode) -> None:
        self._view_mode = view
        if view is CalendarViewMode.DAY:
            self._content_stack.setCurrentWidget(self._day_view)
            if self._mode_label_container is not None:
                self._mode_label_container.setVisible(False)
        elif view is CalendarViewMode.MONTH:
            self._content_stack.setCurrentWidget(self._month_view)
            if self._mode_label_container is not None and self._mode_label is not None:
                self._mode_label_container.setVisible(True)
                self._mode_label.setText("Months")
        else:
            self._content_stack.setCurrentWidget(self._year_view)
            self._ensure_year_range_contains(self._visible_month.year())
            if self._mode_label_container is not None and self._mode_label is not None:
                self._mode_label_container.setVisible(True)
                self._mode_label.setText("Years")

        self._refresh_views()

    def _update_header(self) -> None:
        if self._view_mode is CalendarViewMode.DAY:
            month_name = calendar.month_name[self._visible_month.month()]
            self._navigation.set_header_text(f"{month_name} {self._visible_month.year()}")
        elif self._view_mode is CalendarViewMode.MONTH:
            self._navigation.set_header_text(str(self._visible_month.year()))
        else:
            start = self._year_range_start
            end = start + self._YEAR_RANGE_SIZE - 1
            self._navigation.set_header_text(f"{start} - {end}")

    def _update_navigation_state(self) -> None:
        if self._view_mode is CalendarViewMode.DAY:
            previous_enabled = self._can_move_month(-1)
            next_enabled = self._can_move_month(1)
        elif self._view_mode is CalendarViewMode.MONTH:
            previous_enabled = self._can_move_year(-1)
            next_enabled = self._can_move_year(1)
        else:
            previous_enabled = self._can_shift_year_range(-self._YEAR_RANGE_SIZE)
            next_enabled = self._can_shift_year_range(self._YEAR_RANGE_SIZE)

        self._navigation.set_navigation_enabled(
            previous_enabled=previous_enabled,
            next_enabled=next_enabled,
        )

    def _change_month(self, delta: int) -> None:
        candidate = self._visible_month.addMonths(delta)
        self._visible_month = self._clamp_month(candidate)
        self._ensure_year_range_contains(self._visible_month.year())
        self._refresh_views()

    def _change_year(self, delta: int) -> None:
        candidate = self._visible_month.addYears(delta)
        self._visible_month = self._clamp_month(candidate)
        self._ensure_year_range_contains(self._visible_month.year())
        self._refresh_views()

    def _shift_year_range(self, delta: int) -> None:
        proposed = self._year_range_start + delta
        self._year_range_start = clamp_year_range_start(
            proposed,
            self._min_date,
            self._max_date,
            self._YEAR_RANGE_SIZE,
            max_year=self._MAX_YEAR,
        )
        self._refresh_views()

    def _ensure_year_range_contains(self, year: int) -> None:
        end = self._year_range_start + self._YEAR_RANGE_SIZE - 1
        if year < self._year_range_start or year > end:
            candidate = compute_year_range_start(
                year,
                self._YEAR_RANGE_SIZE,
                max_year=self._MAX_YEAR,
            )
            self._year_range_start = clamp_year_range_start(
                candidate,
                self._min_date,
                self._max_date,
                self._YEAR_RANGE_SIZE,
                max_year=self._MAX_YEAR,
            )

    def _refresh_views(self) -> None:
        self._day_view.update_days(
            visible_month=self._visible_month,
            today=self._today,
            selected_date=self._selected_date,
            range_start=self._range_start,
            range_end=self._range_end,
            min_date=self._min_date,
            max_date=self._max_date,
        )
        if self._view_mode is CalendarViewMode.MONTH:
            self._month_view.set_selected_month(self._visible_month.month())
        elif self._view_mode is CalendarViewMode.YEAR:
            self._ensure_year_range_contains(self._visible_month.year())
            self._year_view.set_year_range(
                self._year_range_start,
                current_year=self._visible_month.year(),
            )
        self._update_header()
        self._update_navigation_state()

    def _ensure_within_bounds(self, date: QDate, field_name: str) -> QDate:
        if self._min_date is not None and date < self._min_date:
            raise InvalidDateError(f"{field_name} must be on or after the configured min_date")
        if self._max_date is not None and date > self._max_date:
            raise InvalidDateError(f"{field_name} must be on or before the configured max_date")
        return date

    def _clamp_date(self, date: QDate) -> QDate:
        result = QDate(date)
        if self._min_date is not None and result < self._min_date:
            result = QDate(self._min_date)
        if self._max_date is not None and result > self._max_date:
            result = QDate(self._max_date)
        return result

    def _clamp_month(self, date: QDate) -> QDate:
        target = first_of_month(date)
        min_month = self._first_allowed_month()
        max_month = self._last_allowed_month()
        if min_month is not None and target < min_month:
            return QDate(min_month)
        if max_month is not None and target > max_month:
            return QDate(max_month)
        return target

    def _first_allowed_month(self) -> QDate | None:
        if self._min_date is None:
            return None
        return first_of_month(self._min_date)

    def _last_allowed_month(self) -> QDate | None:
        if self._max_date is None:
            return None
        return first_of_month(self._max_date)

    def _min_year(self) -> int | None:
        return self._min_date.year() if self._min_date is not None else None

    def _max_year(self) -> int | None:
        return self._max_date.year() if self._max_date is not None else None

    def _can_move_month(self, delta: int) -> bool:
        candidate = first_of_month(self._visible_month.addMonths(delta))
        min_month = self._first_allowed_month()
        if min_month is not None and candidate < min_month:
            return False
        max_month = self._last_allowed_month()
        if max_month is not None and candidate > max_month:
            return False
        return True

    def _can_move_year(self, delta: int) -> bool:
        candidate_year = self._visible_month.year() + delta
        min_year = self._min_year()
        max_year = self._max_year()
        if min_year is not None and candidate_year < min_year:
            return False
        if max_year is not None and candidate_year > max_year:
            return False
        return 1 <= candidate_year <= self._MAX_YEAR

    def _can_shift_year_range(self, delta: int) -> bool:
        min_start, max_start = year_range_limits(
            self._min_date,
            self._max_date,
            self._YEAR_RANGE_SIZE,
            max_year=self._MAX_YEAR,
        )
        if delta < 0:
            return self._year_range_start > min_start
        return self._year_range_start < max_start

    def _setup_mode_label_container(self) -> QWidget:
        """Build the optional mode label container embedded below the nav."""

        container = QWidget(self)
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        container.setFixedHeight(self._layout_config.calendar_day_label_height)
        container.setVisible(False)

        mode_label_layout = QHBoxLayout(container)
        mode_label_layout.setContentsMargins(0, 0, 0, 0)
        mode_label_layout.setSpacing(self._layout_config.calendar_grid_spacing)
        mode_label_layout.addStretch()

        self._mode_label = QLabel("", container)
        self._mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_label.setFixedHeight(self._layout_config.calendar_day_label_height)
        mode_label_layout.addWidget(self._mode_label)
        mode_label_layout.addStretch()
        return container


__all__ = ["CalendarWidget", "CalendarViewMode"]
