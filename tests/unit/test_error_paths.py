"""Ensure the custom exception hierarchy is exercised."""

from __future__ import annotations

import pytest
from date_range_popover.api.config import DatePickerConfig
from date_range_popover.exceptions import (
    InvalidConfigurationError,
    InvalidDateError,
    InvalidThemeError,
)
from date_range_popover.managers.state_manager import DatePickerStateManager
from date_range_popover.styles.theme import Theme
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
