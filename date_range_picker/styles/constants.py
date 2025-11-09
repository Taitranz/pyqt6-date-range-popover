"""Styling constants for the date range picker widgets."""

from PyQt6.QtGui import QFont


# Colors
WINDOW_BACKGROUND = "#1f1f1f"
HEADER_BACKGROUND = "#1f1f1f"
BUTTON_CONTAINER_BACKGROUND = "#1f1f1f"
TRACK_BACKGROUND = "#4a4a4a"
TRACK_INDICATOR_COLOR = "#dbdbdb"
BUTTON_SELECTED_COLOR = "#dbdbdb"
BUTTON_DEFAULT_COLOR = "#f5f5f5"
BUTTON_HOVER_COLOR = "#8c8c8c"


# Dimensions & spacing
WINDOW_MIN_WIDTH = 302
WINDOW_MIN_HEIGHT = 620
WINDOW_RADIUS = 8

MAIN_PADDING = 20
HEADER_BOTTOM_MARGIN = 22
BUTTON_STRIP_BOTTOM_MARGIN = 6
BUTTON_GAP = 20

DATE_BUTTON_WIDTH = 40
CUSTOM_RANGE_BUTTON_WIDTH = 105
DATE_INDICATOR_WIDTH = 32
CUSTOM_RANGE_INDICATOR_WIDTH = 100
DEFAULT_TRACK_WIDTH = 262
SLIDING_INDICATOR_HEIGHT = 5
SLIDING_INDICATOR_RADIUS = 2


# Animation
ANIMATION_FRAME_MS = 16  # ~60 FPS
ANIMATION_DURATION_MS = 40


# Fonts
FONT_FAMILY = "Trebuchet MS"


def create_header_font() -> QFont:
    font = QFont(FONT_FAMILY, 16)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 99.6)
    return font


def create_button_font() -> QFont:
    font = QFont(FONT_FAMILY, 12)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 96)
    return font


def create_label_font() -> QFont:
    font = QFont(FONT_FAMILY)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 96)
    return font


