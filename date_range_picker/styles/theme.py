from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ColorPalette:
    """Collection of color values used across the picker."""

    window_background: str = "#1f1f1f"
    header_background: str = "#1f1f1f"
    button_container_background: str = "#1f1f1f"
    track_background: str = "#4a4a4a"
    track_indicator_color: str = "#dbdbdb"
    button_selected_color: str = "#dbdbdb"
    button_default_color: str = "#f5f5f5"
    button_hover_color: str = "#8c8c8c"
    action_button_background: str = "#343434"
    action_button_hover_background: str = "#4a4a4a"
    action_button_pressed_background: str = "#2a2a2a"
    calendar_background: str = "#1f1f1f"
    calendar_header_text_color: str = "#f5f5f5"
    calendar_day_text_color: str = "#f5f5f5"
    calendar_muted_day_text_color: str = "#8c8c8c"
    calendar_today_background: str = "#f5f5f5"
    calendar_today_text_color: str = "#1f1f1f"
    calendar_today_underline_color: str = "#1f1f1f"
    calendar_day_hover_background: str = "#2e2e2e"
    calendar_day_hover_text_color: str = "#f5f5f5"
    calendar_nav_icon_color: str = "#dbdbdb"
    calendar_day_label_background: str = "#2e2e2e"
    calendar_mode_label_background: str = "#2e2e2e"
    calendar_header_hover_background: str = "#2e2e2e"
    calendar_header_hover_text_color: str = "#ffffff"
    calendar_range_edge_background: str = "#f2f2f2"
    calendar_range_edge_text_color: str = "#1f1f1f"
    calendar_range_between_background: str = "#2e2e2e"
    calendar_range_between_text_color: str = "#ffffff"
    input_background: str = "#1f1f1f"
    input_border_default: str = "#575757"
    input_border_hover: str = "#707070"
    input_border_focus: str = "#2962ff"
    input_border_previous_focus: str = "#8c8c8c"
    input_icon_color: str = "#8c8c8c"
    input_icon_hover_color: str = "#dbdbdb"
    input_text_color: str = "#f5f5f5"
    input_placeholder_color: str = "#8c8c8c"


@dataclass(frozen=True, slots=True)
class ButtonStyleConfig:
    """Configuration for button styles."""

    background: str
    hover_background: str
    pressed_background: str
    border_color: str
    text_color: str
    hover_text_color: str
    pressed_text_color: str
    border_radius: int
    hover_border_color: str | None = None
    pressed_border_color: str | None = None
    focus_border_color: str | None = None

    def stylesheet(self, *, vertical_padding: int) -> str:
        hover_border = self.hover_border_color or self.border_color
        pressed_border = self.pressed_border_color or self.border_color
        focus_border = self.focus_border_color or self.border_color
        return (
            "QPushButton {"
            f"background-color: {self.background};"
            f"color: {self.text_color};"
            f"border: 1px solid {self.border_color};"
            f"border-radius: {self.border_radius}px;"
            f"padding: {vertical_padding}px 0;"
            "outline: none;"
            "}"
            "QPushButton:hover {"
            f"background-color: {self.hover_background};"
            f"color: {self.hover_text_color};"
            f"border: 1px solid {hover_border};"
            "outline: none;"
            "}"
            "QPushButton:pressed {"
            f"background-color: {self.pressed_background};"
            f"color: {self.pressed_text_color};"
            f"border: 1px solid {pressed_border};"
            "outline: none;"
            "}"
            "QPushButton:focus {"
            f"border: 1px solid {focus_border};"
            "outline: none;"
            "}"
        )


@dataclass(frozen=True, slots=True)
class CalendarStyleConfig:
    """Configuration for the calendar widget visuals."""

    background: str
    header_text_color: str
    day_text_color: str
    muted_day_text_color: str
    today_background: str
    today_text_color: str
    today_underline_color: str
    day_hover_background: str
    day_hover_text_color: str
    nav_icon_color: str
    day_label_background: str
    mode_label_background: str
    header_hover_background: str
    header_hover_text_color: str
    range_edge_background: str = "#f2f2f2"
    range_edge_text_color: str = "#1f1f1f"
    range_between_background: str = "#2e2e2e"
    range_between_text_color: str = "#ffffff"


@dataclass(frozen=True, slots=True)
class InputStyleConfig:
    """Configuration for text inputs with icon."""

    background: str
    text_color: str
    placeholder_color: str
    icon_color: str
    icon_hover_color: str
    border_default: str
    border_hover: str
    border_focus: str
    border_previous_focus: str
    border_default_width: int = 1
    border_hover_width: int = 1
    border_focus_width: int = 2
    border_previous_focus_width: int = 2


@dataclass(frozen=True, slots=True)
class LayoutConfig:
    """Common spacing and dimension values."""

    window_min_width: int = 302
    window_min_height: int = 580
    window_min_height_custom_range: int = 640
    window_radius: int = 8
    main_padding: int = 20
    header_bottom_margin: int = 22
    button_strip_bottom_margin: int = 6
    button_gap: int = 20
    date_button_width: int = 40
    custom_range_button_width: int = 105
    date_indicator_width: int = 32
    custom_range_indicator_width: int = 100
    default_track_width: int = 262
    sliding_indicator_height: int = 5
    sliding_indicator_radius: int = 2
    action_button_height: int = 44
    calendar_top_margin: int = 16
    calendar_header_bottom_margin: int = 12
    calendar_grid_spacing: int = 4
    calendar_month_vertical_spacing: int = 30
    calendar_day_label_height: int = 20
    calendar_day_cell_size: int = 34
    calendar_day_cell_radius: int = 8
    calendar_day_underline_height: int = 2
    calendar_day_underline_offset: int = 6
    calendar_day_underline_width: int = 20


@dataclass(frozen=True, slots=True)
class Theme:
    """Combined configuration for styling."""

    palette: ColorPalette = field(default_factory=ColorPalette)
    layout: LayoutConfig = field(default_factory=LayoutConfig)


DEFAULT_THEME = Theme()


