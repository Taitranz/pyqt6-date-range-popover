"""Tests for the time completer utility helpers."""

from __future__ import annotations

from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QApplication, QLineEdit, QWidget

from date_range_popover.components.inputs.time_completer import (
    create_time_completer,
    dismiss_time_popup,
    generate_time_options,
    show_time_popup,
)
from date_range_popover.styles.theme import ColorPalette


def test_generate_time_options_respects_step_bounds() -> None:
    """Steps outside the [1, 60] range should be clamped safely."""

    minute_options = generate_time_options(0)
    assert minute_options[1] == "00:01"
    assert minute_options[-1] == "23:59"

    half_hour_options = generate_time_options(30)
    assert half_hour_options[0:3] == ["00:00", "00:30", "01:00"]
    assert half_hour_options[-1] == "23:30"


def test_create_time_completer_applies_palette_styles(qapp: QApplication) -> None:
    """The completer popup should inherit palette-driven styling."""

    parent = QWidget()
    palette = ColorPalette()
    model = QStringListModel(generate_time_options(15))
    completer = create_time_completer(parent=parent, palette=palette, time_model=model)
    assert completer.maxVisibleItems() == 7
    popup = completer.popup()
    assert popup is not None
    assert palette.time_popup_background in popup.styleSheet()
    assert palette.time_popup_selected_background in popup.styleSheet()


def test_show_and_dismiss_time_popup_toggles_visibility(qapp: QApplication) -> None:
    """The popup helper functions should toggle the completer visibility."""

    parent = QWidget()
    parent.show()
    palette = ColorPalette()
    model = QStringListModel(generate_time_options(15))
    completer = create_time_completer(parent=parent, palette=palette, time_model=model)

    line_edit = QLineEdit(parent)
    line_edit.setCompleter(completer)
    line_edit.setText("12:00")

    show_time_popup(line_edit)
    qapp.processEvents()
    popup = completer.popup()
    assert popup is not None
    assert popup.isVisible()  # type: ignore[union-attr]

    dismiss_time_popup(line_edit)
    qapp.processEvents()
    assert not popup.isVisible()  # type: ignore[union-attr]

