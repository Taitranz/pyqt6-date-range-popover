"""Low-level validation helpers for configuration and runtime values."""

from __future__ import annotations

import re
from typing import Final

from PyQt6.QtCore import QDate

from ..exceptions import InvalidConfigurationError, InvalidDateError, ValidationError

_HEX_RE: Final[re.Pattern[str]] = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def validate_hex_color(value: object, *, field_name: str = "color") -> str:
    """Ensure that ``value`` is a valid hex color string."""
    if not isinstance(value, str):
        raise InvalidConfigurationError(f"{field_name} must be a string, got {type(value)!r}")
    normalized = value.strip()
    if not _HEX_RE.fullmatch(normalized):
        raise InvalidConfigurationError(f"{field_name} must be a #RRGGBB or #RRGGBBAA value, got {value!r}")
    return normalized


def validate_dimension(
    value: object,
    *,
    field_name: str,
    min_value: int = 0,
    max_value: int | None = None,
) -> int:
    """Validate UI dimension values."""
    if not isinstance(value, int):
        raise InvalidConfigurationError(f"{field_name} must be an integer, got {type(value)!r}")
    if value < min_value:
        raise InvalidConfigurationError(f"{field_name} must be >= {min_value}, got {value}")
    if max_value is not None and value > max_value:
        raise InvalidConfigurationError(f"{field_name} must be <= {max_value}, got {value}")
    return value


def validate_qdate(
    date: QDate | None,
    *,
    field_name: str = "date",
    allow_none: bool = False,
) -> QDate | None:
    """Ensure a ``QDate`` is valid (or accept ``None`` when allowed)."""
    if date is None:
        if allow_none:
            return None
        raise InvalidDateError(f"{field_name} cannot be None")
    if not date.isValid():
        raise InvalidDateError(f"{field_name} is not a valid calendar date: {date}")
    return QDate(date)


def validate_date_range(
    start: QDate | None,
    end: QDate | None,
    *,
    field_name: str = "date_range",
    allow_partial: bool = True,
) -> tuple[QDate | None, QDate | None]:
    """Validate that a date range is well-formed."""
    validated_start = validate_qdate(start, field_name=f"{field_name}.start", allow_none=allow_partial)
    validated_end = validate_qdate(end, field_name=f"{field_name}.end", allow_none=allow_partial)

    if not allow_partial and (validated_start is None or validated_end is None):
        raise ValidationError(f"{field_name} requires both start and end dates")

    if validated_start is None or validated_end is None:
        return validated_start, validated_end

    if validated_start > validated_end:
        validated_start, validated_end = validated_end, validated_start

    return validated_start, validated_end


__all__ = [
    "validate_hex_color",
    "validate_dimension",
    "validate_qdate",
    "validate_date_range",
]


