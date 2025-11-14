"""Theme/Palette validation regression tests."""

from __future__ import annotations

import pytest
from date_range_popover.exceptions import InvalidConfigurationError
from date_range_popover.styles.theme import ColorPalette, LayoutConfig


@pytest.mark.parametrize(
    "candidate",
    [
        "rgb(255,255,255)",
        "#12345",
        "#GGGGGG",
        123,  # type: ignore[arg-type]
    ],
)
def test_color_palette_rejects_invalid_hex_values(candidate: object) -> None:
    """All palette tokens must be valid hex strings."""
    with pytest.raises(InvalidConfigurationError, match="window_background"):
        ColorPalette(window_background=candidate)  # type: ignore[arg-type]


def test_color_palette_accepts_alpha_hex_values() -> None:
    """8-digit hex codes pass through unchanged to support alpha tokens."""
    palette = ColorPalette(window_background="#12345678")
    assert palette.window_background == "#12345678"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("window_min_width", 0),
        ("window_min_height", -1),
        ("action_button_height", 0),
    ],
)
def test_layout_config_rejects_invalid_dimensions(field: str, value: int) -> None:
    """LayoutConfig values should respect their minimum bounds."""
    with pytest.raises(InvalidConfigurationError, match=field):
        LayoutConfig(**{field: value})


def test_layout_config_accepts_large_dimensions() -> None:
    """Large but positive values remain valid to support bigger popovers."""
    config = LayoutConfig(window_min_height=900, action_button_height=80)
    assert config.window_min_height == 900
    assert config.action_button_height == 80
