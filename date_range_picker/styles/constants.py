"""Non-style constants for the date range picker widgets."""

from PyQt6.QtGui import QFont


ACTION_BUTTON_VERTICAL_PADDING = 12
# Dimensions & spacing
WINDOW_MIN_WIDTH = 302
WINDOW_MIN_HEIGHT = 580
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
ACTION_BUTTON_HEIGHT = 44

CALENDAR_TOP_MARGIN = 16
CALENDAR_HEADER_BOTTOM_MARGIN = 12
CALENDAR_GRID_SPACING = 4
CALENDAR_DAY_LABEL_HEIGHT = 20
CALENDAR_DAY_CELL_SIZE = 34
CALENDAR_DAY_CELL_RADIUS = 8
CALENDAR_DAY_UNDERLINE_HEIGHT = 2
CALENDAR_DAY_UNDERLINE_OFFSET = 6
CALENDAR_DAY_UNDERLINE_WIDTH = 20


# Animation
ANIMATION_FRAME_MS = 16  # ~60 FPS
ANIMATION_DURATION_MS = 40


# Fonts
FONT_FAMILY = "Trebuchet MS"
CALENDAR_DAY_FONT_POINT_SIZE = 12


def create_header_font() -> QFont:
    font = QFont(FONT_FAMILY, 16)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 96)
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


def create_calendar_header_font() -> QFont:
    font = QFont(FONT_FAMILY, 12)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 96)
    return font


def create_calendar_day_label_font() -> QFont:
    font = QFont(FONT_FAMILY, 10)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 96)
    return font


def create_calendar_day_font() -> QFont:
    font = QFont(FONT_FAMILY, CALENDAR_DAY_FONT_POINT_SIZE)
    font.setWeight(QFont.Weight.Normal)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 96)
    return font



