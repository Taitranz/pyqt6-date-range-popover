"""Ensure the custom exception hierarchy is exercised."""

from __future__ import annotations

import pytest
from date_range_popover.api.config import DatePickerConfig, DateRange
from date_range_popover.exceptions import (
    InvalidConfigurationError,
    InvalidDateError,
    InvalidThemeError,
)
from date_range_popover.managers.state_manager import DatePickerStateManager
from date_range_popover.styles.theme import Theme, theme_from_mapping
from PyQt6.QtCore import QDate


def test_state_manager_raises_invalid_date_error_for_inverted_bounds() -> None:
    """Constructing a state manager with min > max should fail fast."""
    min_date = QDate(2024, 6, 10)
    max_date = QDate(2024, 6, 1)

    with pytest.raises(InvalidDateError):
        DatePickerStateManager(min_date=min_date, max_date=max_date)


def test_config_raises_invalid_configuration_for_bad_theme_type() -> None:
    """DatePickerConfig should guard against arbitrary objects replacing Theme."""

    with pytest.raises(InvalidConfigurationError):
        DatePickerConfig(theme="not-a-theme")  # type: ignore[arg-type]


def test_theme_raises_invalid_theme_error_for_wrong_palette_type() -> None:
    """Theme should validate palette/layout instances to ensure consistency."""

    class NotAPalette:  # pragma: no cover - minimal helper
        pass

    with pytest.raises(InvalidThemeError):
        Theme(palette=NotAPalette())  # type: ignore[arg-type]


def test_date_picker_config_rejects_width_below_minimum() -> None:
    """Width should be clamped to the default layout minimum."""
    with pytest.raises(InvalidConfigurationError, match="width must be >="):
        DatePickerConfig(width=100)


def test_date_picker_config_rejects_height_below_minimum() -> None:
    """Height should be clamped to the default layout minimum."""
    with pytest.raises(InvalidConfigurationError, match="height must be >="):
        DatePickerConfig(height=100)


def test_date_picker_config_rejects_invalid_time_step() -> None:
    """Time step minutes must stay inside the supported range."""
    with pytest.raises(InvalidConfigurationError, match="time_step_minutes"):
        DatePickerConfig(time_step_minutes=0)
    with pytest.raises(InvalidConfigurationError, match="time_step_minutes"):
        DatePickerConfig(time_step_minutes=90)


def test_date_picker_config_validates_initial_range_bounds() -> None:
    """Initial range endpoints are clamped to [min_date, max_date]."""
    min_date = QDate(2024, 1, 10)
    max_date = QDate(2024, 1, 20)
    initial_range = DateRange(start_date=QDate(2024, 1, 1), end_date=QDate(2024, 1, 5))

    with pytest.raises(InvalidConfigurationError, match="initial_range.start_date"):
        DatePickerConfig(
            min_date=min_date,
            max_date=max_date,
            initial_range=initial_range,
        )


def test_theme_from_mapping_propagates_invalid_palette_values() -> None:
    """theme_from_mapping should surface hex validation failures."""
    payload = {"palette": {"window_background": "#GGGGGG"}}

    with pytest.raises(InvalidConfigurationError, match="window_background"):
        theme_from_mapping(payload)
