"""Tests covering the configuration dataclasses exposed via the public API."""

from __future__ import annotations

import pytest
from date_range_popover.api.config import DatePickerConfig, DateRange
from date_range_popover.exceptions import InvalidConfigurationError
from date_range_popover.managers.state_manager import PickerMode
from date_range_popover.styles.theme import LayoutConfig
from PyQt6.QtCore import QDate, QTime


def test_date_range_orders_dates() -> None:
    """DateRange should automatically normalize start/end ordering."""
    later = QDate(2025, 5, 20)
    earlier = QDate(2025, 5, 2)

    value = DateRange(start_date=later, end_date=earlier)

    assert value.start_date == earlier
    assert value.end_date == later


def test_date_range_rejects_invalid_times() -> None:
    """Invalid QTime instances should raise an InvalidConfigurationError."""
    with pytest.raises(InvalidConfigurationError):
        DateRange(start_time=QTime())  # QTime() defaults to an invalid sentinel


def test_config_enforces_min_dimensions() -> None:
    """Width/height/time step values must respect LayoutConfig minimums."""
    layout = LayoutConfig()

    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(width=layout.window_min_width - 1)
    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(height=layout.window_min_height - 1)
    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(time_step_minutes=0)


def test_config_defaults_max_date_to_today() -> None:
    """When no max_date is supplied the config should clamp to today."""
    today = QDate.currentDate()
    config = DatePickerConfig()
    assert config.max_date == today


def test_config_rejects_non_date_range_initial_range() -> None:
    """initial_range must be a DateRange instance."""
    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(initial_range=("2024-01-01", "2024-01-02"))  # type: ignore[arg-type]


def test_config_requires_picker_mode_enum() -> None:
    """mode must be an instance of PickerMode."""
    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(mode="DATE")  # type: ignore[arg-type]
    assert DatePickerConfig(mode=PickerMode.CUSTOM_RANGE).mode is PickerMode.CUSTOM_RANGE


def test_config_validates_initial_selection_against_bounds() -> None:
    """initial_date and initial_range endpoints must respect min/max boundaries."""
    min_date = QDate(2024, 1, 1)
    max_date = QDate(2024, 1, 10)

    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(min_date=min_date, max_date=max_date, initial_date=min_date.addDays(-1))

    bad_range = DateRange(start_date=min_date.addDays(-3), end_date=max_date.addDays(1))
    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(min_date=min_date, max_date=max_date, initial_range=bad_range)
