"""
QSS template helpers shared by calendar widgets.

Qt style sheets end up as large inline strings sprinkled throughout widgets,
which makes it difficult to keep the visual system consistent. These helpers
centralise the common button styles used by the month/year views so themes can
swap palette tokens without editing every widget.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CircularButtonStyle:
    """Parameter bag used by the helper functions below."""

    background: str
    text_color: str
    radius: int


def circular_button_selected_qss(style: CircularButtonStyle) -> str:
    """Return the selected-state stylesheet for circular calendar buttons."""

    return (
        "QPushButton {"
        f"background-color: {style.background};"
        f"color: {style.text_color};"
        "border: none;"
        f"border-radius: {style.radius}px;"
        "padding: 0;"
        "outline: none;"
        "}"
    )


@dataclass(frozen=True, slots=True)
class CircularButtonHoverStyle:
    """Parameters for the hover/default button stylesheet."""

    text_color: str
    hover_background: str
    hover_text_color: str
    radius: int


def circular_button_default_qss(style: CircularButtonHoverStyle) -> str:
    """Return the default-state stylesheet with hover rules."""

    return (
        "QPushButton {"
        "background-color: transparent;"
        f"color: {style.text_color};"
        "border: none;"
        f"border-radius: {style.radius}px;"
        "padding: 0;"
        "outline: none;"
        "}"
        "QPushButton:hover {"
        f"background-color: {style.hover_background};"
        f"color: {style.hover_text_color};"
        "outline: none;"
        "}"
    )


@dataclass(frozen=True, slots=True)
class TimePopupStyle:
    """Visual tokens for the time completer popup."""

    background: str
    text_color: str
    hover_background: str
    hover_text_color: str
    selected_background: str
    selected_text_color: str


def time_popup_qss(style: TimePopupStyle) -> str:
    """Return the stylesheet applied to the QListView-backed popup."""

    return (
        "QListView {"
        "width: 98px;"
        "margin: 0px;"
        "padding: 0px;"
        "border: none;"
        "}"
        "QListView::item {"
        "height: 32px;"
        "margin: 0px;"
        "padding-left: 8px;"
        "padding-right: 8px;"
        f"background-color: {style.background};"
        f"color: {style.text_color};"
        "}"
        "QListView::item:hover {"
        f"background-color: {style.hover_background};"
        f"color: {style.hover_text_color};"
        "}"
        "QListView::item:selected {"
        f"background-color: {style.selected_background};"
        f"color: {style.selected_text_color};"
        "}"
        "QScrollBar:vertical { width: 0px; }"
        "QScrollBar:horizontal { height: 0px; }"
    )


@dataclass(frozen=True, slots=True)
class ModeLabelStyle:
    """Styling tokens for the calendar mode label container + label."""

    background: str
    text_color: str
    radius: int


def mode_label_container_qss(style: ModeLabelStyle) -> str:
    """QSS for the calendar mode label container."""

    return (
        f"background-color: {style.background};"
        f"border-radius: {style.radius}px;"
        "border: none;"
    )


def mode_label_text_qss(style: ModeLabelStyle) -> str:
    """QSS for the calendar mode label text."""

    return (
        f"color: {style.text_color};"
        "background-color: transparent;"
        "border: none;"
    )


def divider_qss(color: str) -> str:
    """Return a minimal divider stylesheet."""

    return f"background-color: {color}; border: none;"


@dataclass(frozen=True, slots=True)
class TransparentButtonStyle:
    """Tokens for icon-only transparent buttons."""

    background: str
    hover_background: str
    pressed_background: str


def transparent_button_qss(style: TransparentButtonStyle) -> str:
    """Return a stylesheet for transparent buttons with hover/press states."""

    return (
        "QPushButton {"
        f"background-color: {style.background};"
        "border: none;"
        "outline: none;"
        "}"
        "QPushButton:hover {"
        f"background-color: {style.hover_background};"
        "}"
        "QPushButton:pressed {"
        f"background-color: {style.pressed_background};"
        "}"
    )


def container_qss(background: str, *, radius: int, border: str | None = None) -> str:
    """Generic container helper that applies background and radius."""

    border_value = border or "none"
    return (
        f"background-color: {background};"
        f"border-radius: {radius}px;"
        f"border: {border_value};"
    )


__all__ = [
    "CircularButtonHoverStyle",
    "CircularButtonStyle",
    "ModeLabelStyle",
    "TimePopupStyle",
    "TransparentButtonStyle",
    "container_qss",
    "circular_button_default_qss",
    "circular_button_selected_qss",
    "divider_qss",
    "mode_label_container_qss",
    "mode_label_text_qss",
    "time_popup_qss",
    "transparent_button_qss",
]


