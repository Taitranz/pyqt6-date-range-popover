"""Stateless helpers for assembling the DateRangePicker widget tree."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..components.buttons import ButtonStrip
from ..components.calendar import CalendarWidget
from ..components.inputs import DateTimeSelector
from ..components.layout import DraggableHeaderStrip, SlidingTrackIndicator
from ..styles import constants
from ..styles.style_templates import (
    TransparentButtonStyle,
    container_qss,
    divider_qss,
    transparent_button_qss,
)
from ..styles.theme import ColorPalette, LayoutConfig
from ..utils.svg_loader import load_colored_svg_icon


def build_header_layout(
    *,
    header_strip: DraggableHeaderStrip,
    layout_config: LayoutConfig,
    palette: ColorPalette,
    close_icon_path: Path,
) -> QPushButton:
    """
    Configure the draggable header and return the close button for signal wiring.
    """

    layout = QHBoxLayout(header_strip)
    layout.setContentsMargins(
        0,
        layout_config.main_padding,
        0,
        layout_config.header_bottom_margin,
    )
    layout.setSpacing(0)

    title = QLabel("Go to", header_strip)
    title_font = constants.create_header_font()
    title_font.setBold(True)
    title.setFont(title_font)
    layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

    close_button = QPushButton(header_strip)
    icon_size = QSize(18, 18)
    close_button.setIcon(load_colored_svg_icon(close_icon_path, 18, palette.button_selected_color))
    close_button.setIconSize(icon_size)
    close_button.setFixedSize(30, 30)
    close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    close_button.setCursor(Qt.CursorShape.PointingHandCursor)
    close_button.setToolTip("Close")
    close_button.setStyleSheet(
        transparent_button_qss(
            TransparentButtonStyle(
                background=palette.close_button_background,
                hover_background=palette.close_button_hover_background,
                pressed_background=palette.close_button_pressed_background,
            )
        )
    )
    layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
    return close_button


def build_button_section(
    *,
    parent: QWidget,
    palette: ColorPalette,
    layout_config: LayoutConfig,
    button_strip: ButtonStrip,
    sliding_track: SlidingTrackIndicator,
    date_time_selector: DateTimeSelector,
    calendar: CalendarWidget,
) -> QWidget:
    """Create the container that hosts buttons, inputs, and the calendar."""

    button_container = QWidget(parent)
    button_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    button_container.setStyleSheet(
        container_qss(
            palette.button_container_background,
            radius=0,
            border="none",
        )
    )
    layout = QVBoxLayout(button_container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(button_strip)
    layout.addWidget(sliding_track)
    layout.addSpacing(16)
    layout.addWidget(date_time_selector)
    layout.addWidget(calendar, alignment=Qt.AlignmentFlag.AlignCenter)
    return button_container


def build_content_container(
    *,
    parent: QWidget,
    layout_config: LayoutConfig,
    header_strip: DraggableHeaderStrip,
    button_section: QWidget,
) -> QWidget:
    """Wrap the header strip and button section with consistent padding."""

    container = QWidget(parent)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(
        layout_config.main_padding,
        0,
        layout_config.main_padding,
        0,
    )
    layout.setSpacing(0)
    layout.addWidget(header_strip)
    layout.addWidget(button_section)
    return container


def build_divider(
    *,
    parent: QWidget,
    palette: ColorPalette,
) -> QFrame:
    """Create a themed divider between content and footer sections."""

    divider = QFrame(parent)
    divider.setFrameShape(QFrame.Shape.NoFrame)
    divider.setFixedHeight(1)
    divider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    divider.setStyleSheet(divider_qss(palette.divider_color))
    return divider


def build_actions_section(
    *,
    parent: QWidget,
    palette: ColorPalette,
    layout_config: LayoutConfig,
    cancel_button: QPushButton,
    go_to_button: QPushButton,
) -> QWidget:
    """Create the footer wrapper used for the Cancel / Go To buttons."""

    wrapper = QWidget(parent)
    wrapper.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    wrapper.setStyleSheet(
        container_qss(
            palette.window_background,
            radius=0,
            border="none",
        )
    )
    layout = QHBoxLayout(wrapper)
    layout.setContentsMargins(
        layout_config.main_padding,
        0,
        layout_config.main_padding,
        0,
    )
    layout.setSpacing(12)
    layout.addStretch(1)
    layout.addWidget(cancel_button)
    layout.addWidget(go_to_button)
    return wrapper


__all__ = [
    "build_actions_section",
    "build_button_section",
    "build_content_container",
    "build_divider",
    "build_header_layout",
]

