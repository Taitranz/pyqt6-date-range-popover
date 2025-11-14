"""Lightweight logging helpers."""

from __future__ import annotations

import logging
from typing import Final

_DEFAULT_LOGGER_NAME: Final[str] = "date_range_picker"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a namespaced logger for the picker."""
    return logging.getLogger(name or _DEFAULT_LOGGER_NAME)


def configure_basic_logging(level: int = logging.INFO) -> None:
    """Configure root logging if it has not been configured yet."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


__all__ = ["get_logger", "configure_basic_logging"]


