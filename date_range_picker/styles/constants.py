"""Non-style constants for the date range picker widgets."""

from PyQt6.QtGui import QFont


ACTION_BUTTON_VERTICAL_PADDING = 12

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



