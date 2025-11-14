"""
Helpers for constructing and managing the time entry completer popups.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtWidgets import QCompleter, QLineEdit, QWidget

from ...styles.style_templates import TimePopupStyle, time_popup_qss
from ...styles.theme import ColorPalette

_POPUP_WIDTH = 98
_MAX_VISIBLE_ITEMS = 7


def generate_time_options(step_minutes: int) -> list[str]:
    """Generate HH:MM strings for the provided minute increment."""

    step = max(1, min(step_minutes, 60))
    return [
        f"{hour:02d}:{minute:02d}"
        for hour in range(24)
        for minute in range(0, 60, step)
    ]


def create_time_completer(
    *,
    parent: QWidget,
    palette: ColorPalette,
    time_model: QStringListModel,
) -> QCompleter:
    """
    Build a :class:`QCompleter` configured for the time picker popup.
    """

    completer = QCompleter(time_model, parent)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    completer.setMaxVisibleItems(_MAX_VISIBLE_ITEMS)

    popup = completer.popup()
    if popup is not None:
        popup.setStyleSheet(
            time_popup_qss(
                TimePopupStyle(
                    background=palette.time_popup_background,
                    text_color=palette.time_popup_text_color,
                    hover_background=palette.time_popup_hover_background,
                    hover_text_color=palette.time_popup_hover_text_color,
                    selected_background=palette.time_popup_selected_background,
                    selected_text_color=palette.time_popup_selected_text_color,
                )
            )
        )
        popup.setFixedWidth(_POPUP_WIDTH)
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        popup.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return completer


def show_time_popup(line_edit: QLineEdit) -> None:
    """
    Display the completer popup for ``line_edit`` and scroll to the current value.
    """

    completer = line_edit.completer()
    if completer is None:
        return
    popup = completer.popup()
    completer.setCompletionPrefix("")
    text = line_edit.text()
    if text and popup is not None:
        model = completer.model()
        if model is not None:
            match_indexes = model.match(
                model.index(0, 0),
                Qt.ItemDataRole.DisplayRole,
                text,
                1,
                Qt.MatchFlag.MatchExactly,
            )
            if match_indexes:
                popup.setCurrentIndex(match_indexes[0])
                popup.scrollTo(match_indexes[0])
    popup_rect = line_edit.rect().translated(0, 3)
    completer.complete(popup_rect)


def dismiss_time_popup(line_edit: QLineEdit) -> None:
    """Hide the popup associated with ``line_edit`` if it is currently visible."""

    completer = line_edit.completer()
    if completer is None:
        return
    popup = completer.popup()
    if popup is not None and popup.isVisible():
        popup.hide()


__all__ = [
    "create_time_completer",
    "dismiss_time_popup",
    "generate_time_options",
    "show_time_popup",
]

