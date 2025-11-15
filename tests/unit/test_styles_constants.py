"""Tests for style helper constants and font factories."""

from __future__ import annotations

from date_range_popover.styles import constants
from PyQt6.QtGui import QFont


def test_create_label_font_uses_expected_weight_and_spacing() -> None:
    """Label fonts should use the configured family, weight, and spacing."""
    font = constants.create_label_font()

    assert font.family() == constants.FONT_FAMILY
    assert font.weight() == QFont.Weight.Bold
    assert font.letterSpacingType() == QFont.SpacingType.PercentageSpacing
    assert font.letterSpacing() == 96
