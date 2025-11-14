"""Regression tests that mirror the README/basic demo setup."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from date_range_popover import DatePickerConfig, DateRangePopover, PickerMode


def test_basic_popover_demo_configuration(qtbot: QtBot) -> None:
    """
    The configuration showcased in README/examples should construct cleanly.

    This acts as a smoke test for the public embed surface: if wiring changes
    break the default `DatePickerConfig` or the widget cannot be created in a
    headless environment, this test will fail early.
    """

    popover = DateRangePopover(config=DatePickerConfig(mode=PickerMode.DATE))
    qtbot.addWidget(popover)

    # A short show/hide cycle ensures paint paths keep working headlessly.
    popover.show()
    assert popover.isVisible()

    popover.cleanup()

