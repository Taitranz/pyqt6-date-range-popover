from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtCore import QDate, QTime

from ..managers.state_manager import PickerMode
from ..styles import constants
from ..styles.theme import Theme, DEFAULT_THEME


@dataclass(slots=True)
class DateRange:
    """Represents a selected date/time range."""

    start_date: Optional[QDate] = None
    end_date: Optional[QDate] = None
    start_time: Optional[QTime] = None
    end_time: Optional[QTime] = None


@dataclass(slots=True)
class DatePickerConfig:
    """Configuration for the date range picker."""

    width: int = constants.WINDOW_MIN_WIDTH
    height: int = constants.WINDOW_MIN_HEIGHT
    theme: Theme = field(default_factory=lambda: DEFAULT_THEME)
    initial_date: Optional[QDate] = None
    initial_range: Optional[DateRange] = None
    mode: PickerMode = PickerMode.DATE


__all__ = ["DatePickerConfig", "DateRange", "PickerMode"]


