"""Tests for the logging helper utilities."""

from __future__ import annotations

import logging

from date_range_popover.utils.logging import configure_basic_logging, get_logger


def test_get_logger_defaults_to_package_namespace() -> None:
    """Without a name, get_logger should return the package root logger."""
    logger = get_logger()
    assert logger.name == "date_range_popover"


def test_configure_basic_logging_initializes_root_when_missing_handlers() -> None:
    """basic logging configuration should install a handler when none exist."""
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    for handler in list(root.handlers):
        root.removeHandler(handler)
    try:
        configure_basic_logging(level=logging.DEBUG)
        assert root.handlers
    finally:
        for handler in list(root.handlers):
            root.removeHandler(handler)
        for handler in original_handlers:
            root.addHandler(handler)


def test_configure_basic_logging_is_noop_when_handlers_present() -> None:
    """If handlers already exist the helper should leave them untouched."""
    root = logging.getLogger()
    handler = logging.StreamHandler()
    root.addHandler(handler)
    original_count = len(root.handlers)
    try:
        configure_basic_logging(level=logging.CRITICAL)
        assert len(root.handlers) == original_count
    finally:
        root.removeHandler(handler)
