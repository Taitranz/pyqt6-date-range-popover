"""Custom exception hierarchy for the date range picker."""

from __future__ import annotations


class ValidationError(ValueError):
    """Base class for validation-related failures."""


class InvalidDateError(ValidationError):
    """Raised when a ``QDate`` or date range fails validation."""


class InvalidConfigurationError(ValidationError):
    """Raised when configuration objects contain invalid values."""


class InvalidThemeError(InvalidConfigurationError):
    """Raised when theme or palette definitions are inconsistent."""


__all__ = [
    "ValidationError",
    "InvalidDateError",
    "InvalidConfigurationError",
    "InvalidThemeError",
]


