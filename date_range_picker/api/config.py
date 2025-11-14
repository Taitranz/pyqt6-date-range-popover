from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtCore import QDate, QTime

from ..exceptions import InvalidConfigurationError
from ..managers.state_manager import PickerMode
from ..styles.theme import LayoutConfig, Theme
from ..validation import validate_date_range, validate_dimension, validate_qdate


_DEFAULT_LAYOUT = LayoutConfig()


@dataclass(slots=True)
class DateRange:
    """Represents a selected date/time range."""

    start_date: Optional[QDate] = None
    end_date: Optional[QDate] = None
    start_time: Optional[QTime] = None
    end_time: Optional[QTime] = None

    def __post_init__(self) -> None:
        self.start_date, self.end_date = validate_date_range(
            self.start_date,
            self.end_date,
            field_name="initial_range",
        )
        self._validate_time(self.start_time, "start_time")
        self._validate_time(self.end_time, "end_time")

    @staticmethod
    def _validate_time(value: QTime | None, field_name: str) -> None:
        if value is None:
            return
        if not value.isValid():
            raise InvalidConfigurationError(f"{field_name} is not a valid time: {value}")


@dataclass(slots=True)
class DatePickerConfig:
    """Configuration for the date range picker."""

    width: int = _DEFAULT_LAYOUT.window_min_width
    height: int = _DEFAULT_LAYOUT.window_min_height
    theme: Theme = field(default_factory=Theme)
    initial_date: Optional[QDate] = None
    initial_range: Optional[DateRange] = None
    mode: PickerMode = PickerMode.DATE

    def __post_init__(self) -> None:
        self.width = validate_dimension(
            self.width,
            field_name="width",
            min_value=_DEFAULT_LAYOUT.window_min_width,
        )
        self.height = validate_dimension(
            self.height,
            field_name="height",
            min_value=_DEFAULT_LAYOUT.window_min_height,
        )
        self.initial_date = validate_qdate(self.initial_date, field_name="initial_date", allow_none=True)
        candidate_range = object.__getattribute__(self, "initial_range")
        if candidate_range is not None and not isinstance(candidate_range, DateRange):
            raise InvalidConfigurationError("initial_range must be a DateRange instance")
        mode_value = object.__getattribute__(self, "mode")
        if not isinstance(mode_value, PickerMode):
            raise InvalidConfigurationError("mode must be an instance of PickerMode")
        theme_value = object.__getattribute__(self, "theme")
        if not isinstance(theme_value, Theme):
            raise InvalidConfigurationError("theme must be an instance of Theme")


__all__ = ["DatePickerConfig", "DateRange", "PickerMode"]


