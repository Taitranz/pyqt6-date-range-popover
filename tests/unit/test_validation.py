"""Tests for low-level validation helpers."""

from __future__ import annotations

import pytest
from date_range_popover.exceptions import (
    InvalidConfigurationError,
    InvalidDateError,
    ValidationError,
)
from date_range_popover.validation import (
    validate_date_range,
    validate_dimension,
    validate_hex_color,
    validate_qdate,
)
from PyQt6.QtCore import QDate


def test_validate_hex_color_accepts_valid_values() -> None:
    """Known-good hex strings should round-trip unchanged."""
    assert validate_hex_color("#abcdef") == "#abcdef"
    assert validate_hex_color("#ABCDEF") == "#ABCDEF"
    assert validate_hex_color("#12345678") == "#12345678"


def test_validate_hex_color_rejects_non_strings() -> None:
    """Non-string inputs must raise InvalidConfigurationError."""
    with pytest.raises(InvalidConfigurationError):
        validate_hex_color(123)
    with pytest.raises(InvalidConfigurationError):
        validate_hex_color("#12345")


def test_validate_dimension_enforces_bounds() -> None:
    """Dimensions must be ints within the specified range."""
    assert validate_dimension(10, field_name="width", min_value=1, max_value=20) == 10
    with pytest.raises(InvalidConfigurationError):
        validate_dimension(0, field_name="width", min_value=1)
    with pytest.raises(InvalidConfigurationError):
        validate_dimension(30, field_name="width", min_value=1, max_value=20)
    with pytest.raises(InvalidConfigurationError):
        validate_dimension("10", field_name="width")


def test_validate_qdate_allows_none_when_configured() -> None:
    """validate_qdate should accept None when allow_none=True."""
    assert validate_qdate(None, allow_none=True) is None
    today = QDate.currentDate()
    validated = validate_qdate(today, field_name="today")
    assert validated == today and validated is not today


def test_validate_qdate_rejects_invalid_dates() -> None:
    """Invalid QDate instances should raise InvalidDateError."""
    with pytest.raises(InvalidDateError):
        validate_qdate(None)
    with pytest.raises(InvalidDateError):
        validate_qdate(QDate())  # Invalid by default


def test_validate_date_range_requires_complete_bounds_when_partial_disallowed() -> None:
    """Missing endpoints must raise when allow_partial=False."""
    start = QDate(2024, 1, 1)
    with pytest.raises(ValidationError):
        validate_date_range(start, None, allow_partial=False)


def test_validate_date_range_normalizes_order() -> None:
    """The helper should return ordered tuples even when inputs are reversed."""
    later = QDate(2024, 1, 10)
    earlier = QDate(2024, 1, 1)
    start, end = validate_date_range(later, earlier, allow_partial=False)
    assert start == earlier
    assert end == later


def test_validate_date_range_preserves_partial_ranges_when_allowed() -> None:
    """Partial ranges should round-trip when allow_partial=True."""
    start = QDate(2024, 3, 5)
    start_value, end_value = validate_date_range(start, None, allow_partial=True)
    assert start_value == start
    assert end_value is None


def test_validate_date_range_accepts_missing_bounds_by_default() -> None:
    """Default configuration allows open ranges (both ends missing)."""
    start_value, end_value = validate_date_range(None, None)
    assert start_value is None
    assert end_value is None
