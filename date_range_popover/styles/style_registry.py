from __future__ import annotations

from typing import Any, Literal

from .theme import (
    ButtonStyleConfig,
    CalendarStyleConfig,
    DEFAULT_THEME,
    InputStyleConfig,
    Theme,
)

ComponentType = Literal["button", "calendar", "input"]


class StyleRegistry:
    """
    Stores style presets and provides helpers for retrieving styles.

    The registry is intentionally lightweight—it's just a lookup table that
    keeps per-component style tokens grouped by theme. Embedders typically do
    not interact with it directly; :class:`StyleManager` consumes it instead.
    """

    BUTTON_PRIMARY = "primary"
    BUTTON_ACCENT = "accent"
    BUTTON_GHOST = "ghost"
    BUTTON_DEFAULT = BUTTON_PRIMARY
    CALENDAR_DEFAULT = "default"
    INPUT_DEFAULT = "default"

    def __init__(self, theme: Theme | None = None) -> None:
        """Build lookup tables using the provided :class:`Theme`."""
        self._theme = theme or DEFAULT_THEME
        palette = self._theme.palette
        layout = self._theme.layout

        self.BUTTON_STYLES: dict[str, ButtonStyleConfig] = {
            self.BUTTON_PRIMARY: ButtonStyleConfig(
                background=palette.action_button_background,
                hover_background=palette.action_button_hover_background,
                pressed_background=palette.action_button_pressed_background,
                border_color=palette.track_background,
                text_color=palette.button_selected_color,
                hover_text_color=palette.button_selected_color,
                pressed_text_color=palette.button_selected_color,
                border_radius=layout.window_radius,
            ),
            self.BUTTON_ACCENT: ButtonStyleConfig(
                background=palette.button_selected_color,
                hover_background=palette.button_default_color,
                pressed_background=palette.button_hover_color,
                border_color=palette.button_selected_color,
                text_color=palette.window_background,
                hover_text_color=palette.window_background,
                pressed_text_color=palette.window_background,
                border_radius=layout.window_radius,
                hover_border_color=palette.button_default_color,
                pressed_border_color=palette.button_hover_color,
                focus_border_color=palette.button_selected_color,
            ),
            self.BUTTON_GHOST: ButtonStyleConfig(
                background=palette.window_background,
                hover_background=palette.button_default_color,
                pressed_background=palette.button_hover_color,
                border_color=palette.button_selected_color,
                text_color=palette.button_selected_color,
                hover_text_color=palette.window_background,
                pressed_text_color=palette.window_background,
                border_radius=layout.window_radius,
                hover_border_color=palette.button_default_color,
                pressed_border_color=palette.button_hover_color,
                focus_border_color=palette.button_selected_color,
            ),
        }

        self.CALENDAR_STYLES: dict[str, CalendarStyleConfig] = {
            self.CALENDAR_DEFAULT: CalendarStyleConfig(
                background=palette.calendar_background,
                header_text_color=palette.calendar_header_text_color,
                day_text_color=palette.calendar_day_text_color,
                muted_day_text_color=palette.calendar_muted_day_text_color,
                today_background=palette.calendar_today_background,
                today_text_color=palette.calendar_today_text_color,
                today_underline_color=palette.calendar_today_underline_color,
                day_hover_background=palette.calendar_day_hover_background,
                day_hover_text_color=palette.calendar_day_hover_text_color,
                nav_icon_color=palette.calendar_nav_icon_color,
                day_label_background=palette.calendar_day_label_background,
                mode_label_background=palette.calendar_mode_label_background,
                header_hover_background=palette.calendar_header_hover_background,
                header_hover_text_color=palette.calendar_header_hover_text_color,
                range_edge_background=palette.calendar_range_edge_background,
                range_edge_text_color=palette.calendar_range_edge_text_color,
                range_between_background=palette.calendar_range_between_background,
                range_between_text_color=palette.calendar_range_between_text_color,
            )
        }

        self.INPUT_STYLES: dict[str, InputStyleConfig] = {
            self.INPUT_DEFAULT: InputStyleConfig(
                background=palette.input_background,
                text_color=palette.input_text_color,
                placeholder_color=palette.input_placeholder_color,
                icon_color=palette.input_icon_color,
                icon_hover_color=palette.input_icon_hover_color,
                border_default=palette.input_border_default,
                border_hover=palette.input_border_hover,
                border_focus=palette.input_border_focus,
                border_previous_focus=palette.input_border_previous_focus,
                selection_background=palette.input_selection_background,
                selection_text_color=palette.input_selection_text_color,
            )
        }

    @property
    def theme(self) -> Theme:
        """Return the :class:`Theme` backing this registry."""
        return self._theme

    def get_stylesheet(
        self,
        component_type: ComponentType,
        variant: str = "default",
        **kwargs: Any,
    ) -> str:
        """
        Convenience wrapper that fetches a stylesheet for the given component.

        :param component_type: ``"button"``, ``"calendar"``, or ``"input"``.
        :param variant: Named style variant.
        :raises KeyError: If the component type or variant is unknown.
        """
        if component_type == "button":
            return self.button_stylesheet(variant=variant, **kwargs)
        if component_type == "calendar":
            return self.calendar_stylesheet(variant=variant)
        if component_type == "input":
            return self.input_stylesheet(variant=variant)
        raise KeyError(f"Unsupported component type: {component_type}")

    # Button helpers -----------------------------------------------------------------

    def button_config(self, variant: str = BUTTON_DEFAULT) -> ButtonStyleConfig:
        """Fetch a button style configuration."""
        try:
            return self.BUTTON_STYLES[variant]
        except KeyError as exc:
            raise KeyError(f"Unknown button style variant: {variant}") from exc

    def button_stylesheet(
        self,
        *,
        variant: str = BUTTON_DEFAULT,
        vertical_padding: int,
    ) -> str:
        """Render the stylesheet for a button variant."""
        config = self.button_config(variant)
        return config.stylesheet(vertical_padding=vertical_padding)

    # Calendar helpers ---------------------------------------------------------------

    def calendar_config(self, variant: str = CALENDAR_DEFAULT) -> CalendarStyleConfig:
        """Fetch a calendar style configuration."""
        try:
            return self.CALENDAR_STYLES[variant]
        except KeyError as exc:
            raise KeyError(f"Unknown calendar style variant: {variant}") from exc

    def calendar_stylesheet(self, *, variant: str = CALENDAR_DEFAULT) -> str:
        """Render a simple background stylesheet for calendar containers."""
        config = self.calendar_config(variant)
        return f"background-color: {config.background};"

    # Input helpers ------------------------------------------------------------------

    def input_config(self, variant: str = INPUT_DEFAULT) -> InputStyleConfig:
        """Fetch an input style configuration."""
        try:
            return self.INPUT_STYLES[variant]
        except KeyError as exc:
            raise KeyError(f"Unknown input style variant: {variant}") from exc

    def input_stylesheet(self, *, variant: str = INPUT_DEFAULT) -> str:
        """Render a minimal stylesheet for icon-enabled inputs."""
        config = self.input_config(variant)
        return (
            f"background-color: {config.background};"
            f"border: 1px solid {config.border_default};"
            "border-radius: 6px;"
        )


