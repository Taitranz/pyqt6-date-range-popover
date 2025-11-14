from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget

from ..styles.style_registry import (
    ButtonVariant,
    CalendarVariant,
    InputVariant,
    StyleRegistry,
)
from ..styles.theme import Theme

if TYPE_CHECKING:  # pragma: no cover
    from ..components.buttons.basic_button import BasicButton
    from ..components.buttons.button_strip import ButtonStrip
    from ..components.calendar.calendar_widget import CalendarWidget
    from ..components.inputs.input_with_icon import InputWithIcon
    from ..components.layout.draggable_header import DraggableHeaderStrip
    from ..components.layout.sliding_track import SlidingTrackIndicator


class StyleManager:
    """
    Central point for applying :class:`Theme` tokens to widgets.

    The manager keeps :class:`StyleRegistry` lookups in one place so components
    do not each need to understand palette/layout internals. This makes it easy
    to swap entire themes when embedding the picker in different host apps.
    """

    def __init__(self, registry: StyleRegistry | None = None) -> None:
        """Initialise the manager with an optional pre-built registry."""
        self._registry = registry or StyleRegistry()

    @property
    def registry(self) -> StyleRegistry:
        """Access the underlying :class:`StyleRegistry`."""
        return self._registry

    @property
    def theme(self) -> Theme:
        """Return the current :class:`Theme` (palette + layout tokens)."""
        return self._registry.theme

    def use_theme(self, theme: Theme) -> None:
        """Swap to a new :class:`Theme`, rebuilding the registry for future lookups."""
        self._registry = StyleRegistry(theme)

    # Component-specific helpers -----------------------------------------------------

    def apply_basic_button(
        self,
        button: BasicButton,
        *,
        variant: str | ButtonVariant | None = None,
    ) -> None:
        """Apply the configured button variant stylesheet."""
        target_variant = variant or self._registry.BUTTON_DEFAULT
        config = self._registry.button_config(target_variant)
        stylesheet = config.stylesheet(vertical_padding=button.vertical_padding)
        button.apply_stylesheet(stylesheet)

    def apply_button_strip(self, button_strip: ButtonStrip) -> None:
        """Push palette and layout tokens to the button strip widget."""
        button_strip.apply_palette(self.theme.palette)
        button_strip.apply_layout(self.theme.layout)

    def apply_calendar(
        self,
        calendar: CalendarWidget,
        *,
        variant: str | CalendarVariant | None = None,
    ) -> None:
        """Apply a calendar style variant to the calendar widget."""
        target_variant = variant or self._registry.CALENDAR_DEFAULT
        config = self._registry.calendar_config(target_variant)
        calendar.apply_style(config)

    def apply_input(
        self,
        input_widget: InputWithIcon,
        *,
        variant: str | InputVariant | None = None,
    ) -> None:
        """Apply the configured input style variant to the widget."""
        target_variant = variant or self._registry.INPUT_DEFAULT
        config = self._registry.input_config(target_variant)
        input_widget.apply_style(config)

    def apply_sliding_track(self, sliding_track: SlidingTrackIndicator) -> None:
        """Apply palette/layout tokens to the sliding track indicator."""
        sliding_track.apply_palette(self.theme.palette)
        sliding_track.apply_layout(self.theme.layout)

    def apply_header(self, header: DraggableHeaderStrip) -> None:
        """Apply palette colors to the draggable header."""
        header.apply_palette(self.theme.palette)

    def apply_background(self, widget: QWidget) -> None:
        """Set the widget background to match the current theme window color."""
        widget.setStyleSheet(f"background-color: {self.theme.palette.window_background};")


__all__ = ["StyleManager"]
