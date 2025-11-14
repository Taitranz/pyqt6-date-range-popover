"""
Showcase custom themes by instantiating :class:`DateRangePopover` with
two different `Theme` objects. This demonstrates that embedders can
swap palettes/layouts without touching any widget logic.
"""

from __future__ import annotations

import sys

from date_range_popover.styles.theme import ColorPalette, LayoutConfig, Theme, theme_from_mapping
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from date_range_popover import DatePickerConfig, DateRangePopover, PickerMode

ACCENT_DARK_THEME = Theme(
    palette=ColorPalette(
        window_background="#101820",
        header_background="#101820",
        button_container_background="#101820",
        track_indicator_color="#f2aa4c",
        button_selected_color="#f2aa4c",
        action_button_background="#172433",
        action_button_hover_background="#f2aa4c",
        action_button_pressed_background="#c97a00",
        calendar_today_background="#f2aa4c",
        calendar_today_text_color="#101820",
        calendar_range_edge_background="#f2aa4c",
        calendar_range_between_background="#172433",
        input_border_focus="#f2aa4c",
        mode_label_text_color="#f2aa4c",
    ),
    layout=LayoutConfig(
        window_min_width=360,
        window_min_height=640,
        action_button_height=52,
        calendar_day_cell_size=36,
        calendar_day_cell_radius=10,
    ),
)

PASTEL_LIGHT_THEME = theme_from_mapping(
    {
        "palette": {
            "window_background": "#ffffff",
            "header_background": "#f2f2f7",
            "button_container_background": "#f2f2f7",
            "track_background": "#ffd1dc",
            "track_indicator_color": "#ff779a",
            "button_selected_color": "#ff779a",
            "button_default_color": "#3a3a3a",
            "calendar_background": "#ffffff",
            "calendar_day_text_color": "#3a3a3a",
            "calendar_muted_day_text_color": "#a1a1a8",
            "calendar_today_background": "#ff779a",
            "calendar_today_text_color": "#ffffff",
            "calendar_range_between_background": "#ffe4ec",
            "calendar_range_between_text_color": "#3a3a3a",
            "input_background": "#ffffff",
            "input_text_color": "#3a3a3a",
            "input_border_focus": "#ff779a",
            "mode_label_text_color": "#ff779a",
            "mode_label_container_background": "#ffe4ec",
        },
        "layout": {
            "window_min_width": 340,
            "window_min_height": 600,
            "calendar_day_cell_size": 32,
            "calendar_day_cell_radius": 6,
        },
    }
)


class ThemePanel(QWidget):
    """Container widget that renders a popover with the provided theme."""

    def __init__(self, title: str, theme: Theme) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(QLabel(title))

        config = DatePickerConfig(
            mode=PickerMode.CUSTOM_RANGE,
            theme=theme,
            time_step_minutes=30,
        )
        popover = DateRangePopover(config=config)
        layout.addWidget(popover, alignment=Qt.AlignmentFlag.AlignTop)


class ThemeShowcaseWindow(QMainWindow):
    """Display two themed popovers side-by-side using tabs."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Custom Theme Showcase")
        self.resize(900, 700)

        tabs = QTabWidget()
        tabs.addTab(ThemePanel("Accent Dark Theme", ACCENT_DARK_THEME), "Accent Dark")
        tabs.addTab(ThemePanel("Pastel Light Theme", PASTEL_LIGHT_THEME), "Pastel Light")
        self.setCentralWidget(tabs)


def main() -> None:
    """Launch the custom theme showcase."""
    app = QApplication(sys.argv)
    window = ThemeShowcaseWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
