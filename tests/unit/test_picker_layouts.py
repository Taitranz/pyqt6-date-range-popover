"""Tests for the picker layout helper module."""

from __future__ import annotations

from date_range_popover.api.picker import CLOSE_ICON_PATH
from date_range_popover.api.picker_layouts import (
    build_actions_section,
    build_button_section,
    build_content_container,
    build_divider,
    build_header_layout,
)
from date_range_popover.components.buttons import BasicButton, ButtonStrip
from date_range_popover.components.calendar import CalendarWidget
from date_range_popover.components.inputs import DateTimeSelector
from date_range_popover.components.layout import DraggableHeaderStrip, SlidingTrackIndicator
from date_range_popover.styles.style_registry import StyleRegistry
from PyQt6.QtWidgets import QApplication, QWidget


def _build_common_components(
    parent: QWidget,
) -> tuple[
    StyleRegistry,
    DraggableHeaderStrip,
    ButtonStrip,
    SlidingTrackIndicator,
    DateTimeSelector,
    CalendarWidget,
    BasicButton,
    BasicButton,
]:
    registry = StyleRegistry()
    palette = registry.theme.palette
    layout_config = registry.theme.layout

    header = DraggableHeaderStrip(parent, palette=palette)
    button_strip = ButtonStrip(parent, layout_config=layout_config)
    sliding_track = SlidingTrackIndicator(parent, palette=palette, layout=layout_config)
    date_time_selector = DateTimeSelector(parent, palette=palette)
    calendar = CalendarWidget(parent, style=registry.calendar_config())
    cancel_button = BasicButton(parent, label="Cancel", width=72, layout=layout_config)
    go_button = BasicButton(parent, label="Go", width=64, layout=layout_config)
    return (
        registry,
        header,
        button_strip,
        sliding_track,
        date_time_selector,
        calendar,
        cancel_button,
        go_button,
    )


def test_build_header_layout_returns_close_button(qapp: QApplication) -> None:
    """The header builder should return a close button wired to the strip."""

    parent = QWidget()
    registry, header, *_ = _build_common_components(parent)
    close_button = build_header_layout(
        header_strip=header,
        layout_config=registry.theme.layout,
        palette=registry.theme.palette,
        close_icon_path=CLOSE_ICON_PATH,
    )
    assert close_button.parent() is header
    assert close_button.toolTip() == "Close"


def test_build_button_section_reparents_child_widgets(qapp: QApplication) -> None:
    """The button section should host the strip, track, selector, and calendar."""

    parent = QWidget()
    (
        registry,
        _header,
        button_strip,
        sliding_track,
        selector,
        calendar,
        _cancel_button,
        _go_button,
    ) = _build_common_components(parent)
    section = build_button_section(
        parent=parent,
        palette=registry.theme.palette,
        layout_config=registry.theme.layout,
        button_strip=button_strip,
        sliding_track=sliding_track,
        date_time_selector=selector,
        calendar=calendar,
    )
    assert button_strip.parent() is section
    assert selector.parent() is section
    assert calendar.parent() is section


def test_build_actions_section_wraps_cancel_and_go_buttons(qapp: QApplication) -> None:
    """The footer wrapper should embed the provided action buttons."""

    parent = QWidget()
    registry, *_, cancel_button, go_button = _build_common_components(parent)
    wrapper = build_actions_section(
        parent=parent,
        palette=registry.theme.palette,
        layout_config=registry.theme.layout,
        cancel_button=cancel_button,
        go_to_button=go_button,
    )
    assert cancel_button.parent() is wrapper
    assert go_button.parent() is wrapper


def test_build_divider_uses_palette_color(qapp: QApplication) -> None:
    """The divider style should reflect the palette divider color."""

    parent = QWidget()
    registry = StyleRegistry()
    divider = build_divider(parent=parent, palette=registry.theme.palette)
    assert registry.theme.palette.divider_color in divider.styleSheet()


def test_build_content_container_composes_header_and_section(qapp: QApplication) -> None:
    """The content container should wrap the header strip and button section."""

    parent = QWidget()
    (
        registry,
        header,
        button_strip,
        sliding_track,
        selector,
        calendar,
        *_,
    ) = _build_common_components(parent)
    section = build_button_section(
        parent=parent,
        palette=registry.theme.palette,
        layout_config=registry.theme.layout,
        button_strip=button_strip,
        sliding_track=sliding_track,
        date_time_selector=selector,
        calendar=calendar,
    )
    container = build_content_container(
        parent=parent,
        layout_config=registry.theme.layout,
        header_strip=header,
        button_section=section,
    )
    assert header.parent() is container
    assert section.parent() is container
