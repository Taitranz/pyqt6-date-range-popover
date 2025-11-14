"""Theme/Palette validation regression tests."""

from __future__ import annotations

import pytest
from date_range_popover.exceptions import InvalidConfigurationError
from date_range_popover.styles.theme import ColorPalette, LayoutConfig


def test_color_palette_rejects_invalid_hex_values() -> None:
    """All palette tokens must be valid hex strings."""
    with pytest.raises(InvalidConfigurationError):
        ColorPalette(window_background="rgb(255,255,255)")


def test_layout_config_rejects_negative_dimensions() -> None:
    """LayoutConfig values should respect their minimum bounds."""
    with pytest.raises(InvalidConfigurationError):
        LayoutConfig(window_min_width=0)


def test_layout_config_accepts_large_dimensions() -> None:
    """Large but positive values remain valid to support bigger popovers."""
    config = LayoutConfig(window_min_height=900, action_button_height=80)
    assert config.window_min_height == 900
    assert config.action_button_height == 80
