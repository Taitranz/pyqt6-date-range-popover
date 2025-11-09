from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget

from ..styles.style_registry import StyleRegistry
from ..styles.theme import Theme

if TYPE_CHECKING:  # pragma: no cover
    from ..components.buttons.basic_button import BasicButton
    from ..components.buttons.button_strip import ButtonStrip
    from ..components.calendar.calendar_widget import CalendarWidget
    from ..components.inputs.input_with_icon import InputWithIcon
    from ..components.layout.draggable_header import DraggableHeaderStrip
    from ..components.layout.sliding_track import SlidingTrackIndicator


class StyleManager:
    """Applies theme styles to widgets using the registry."""

    def __init__(self, registry: StyleRegistry | None = None) -> None:
        self._registry = registry or StyleRegistry()

    @property
    def registry(self) -> StyleRegistry:
        return self._registry

    @property
    def theme(self) -> Theme:
        return self._registry.theme

    def use_theme(self, theme: Theme) -> None:
        self._registry = StyleRegistry(theme)

    # Component-specific helpers -----------------------------------------------------

    def apply_basic_button(self, button: "BasicButton", *, variant: str | None = None) -> None:
        target_variant = variant or self._registry.BUTTON_DEFAULT
        config = self._registry.button_config(target_variant)
        stylesheet = config.stylesheet(vertical_padding=button.vertical_padding)
        button.apply_stylesheet(stylesheet)

    def apply_button_strip(self, button_strip: "ButtonStrip") -> None:
        button_strip.apply_palette(self.theme.palette)

    def apply_calendar(self, calendar: "CalendarWidget", *, variant: str | None = None) -> None:
        target_variant = variant or self._registry.CALENDAR_DEFAULT
        config = self._registry.calendar_config(target_variant)
        calendar.apply_style(config)

    def apply_input(self, input_widget: "InputWithIcon", *, variant: str | None = None) -> None:
        target_variant = variant or self._registry.INPUT_DEFAULT
        config = self._registry.input_config(target_variant)
        input_widget.apply_style(config)

    def apply_sliding_track(self, sliding_track: "SlidingTrackIndicator") -> None:
        sliding_track.apply_palette(self.theme.palette)

    def apply_header(self, header: "DraggableHeaderStrip") -> None:
        header.apply_palette(self.theme.palette)

    def apply_background(self, widget: QWidget) -> None:
        widget.setStyleSheet(f"background-color: {self.theme.palette.window_background};")


__all__ = ["StyleManager"]


