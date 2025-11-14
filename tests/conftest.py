"""Pytest configuration for the date range popover test suite."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest
from PyQt6.QtWidgets import QApplication

from date_range_popover.api.config import DatePickerConfig, DateRange

# Force headless Qt rendering in CI and local terminals that lack a display server.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """
    Provide a single ``QApplication`` instance for the entire test session.

    ``pytest-qt`` normally instantiates a QApplication per test module. Sharing a
    session-scoped instance speeds up widget-heavy suites and avoids crashes when
    multiple QApplication objects are constructed in the same process.
    """
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


@pytest.fixture(name="config_factory")
def fixture_config_factory() -> Callable[..., DatePickerConfig]:
    """Return a helper that builds :class:`DatePickerConfig` instances."""

    def _factory(**overrides: Any) -> DatePickerConfig:
        return DatePickerConfig(**overrides)

    return _factory


@pytest.fixture(name="date_range_factory")
def fixture_date_range_factory() -> Callable[..., DateRange]:
    """Return a helper that builds :class:`DateRange` instances."""

    def _factory(**overrides: Any) -> DateRange:
        return DateRange(**overrides)

    return _factory

