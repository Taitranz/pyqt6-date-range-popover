from __future__ import annotations

import re
from pathlib import Path
from re import Pattern
from typing import Final

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QEnterEvent
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QWidget

from ...styles.theme import InputStyleConfig
from ...utils import connect_signal
from ...utils.svg_loader import load_svg_widget

DEFAULT_HEIGHT: Final[int] = 34
DEFAULT_WIDTH: Final[int] = 150
DEFAULT_ICON_PLACEHOLDER_WIDTH: Final[int] = 32
DEFAULT_ICON_SIZE: Final[int] = 28


class InputWithIcon(QWidget):
    """Input widget that hosts a text field with an optional icon."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        text: str = "",
        width: int | None = DEFAULT_WIDTH,
        icon_path: str | Path | None = None,
        style: InputStyleConfig | None = None,
        max_length: int | None = None,
        regex_pattern: str | None = None,
        revert_on_focus_out: bool = True,
        placeholder_text: str | None = None,
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(DEFAULT_HEIGHT)
        if width is not None:
            self.setFixedWidth(width)

        self._style = style or _default_style()
        self._icon_path = Path(icon_path) if icon_path is not None else None
        self._icon_template: str | None = None
        self._is_hovered = False
        self._was_previously_focused = False
        self._max_length = max_length
        self._regex_pattern = regex_pattern
        self._compiled_pattern: Pattern[str] | None = (
            re.compile(regex_pattern) if regex_pattern is not None else None
        )
        self._revert_on_focus_out = revert_on_focus_out
        self._placeholder_text = placeholder_text or ""
        self._last_valid_text = text
        self._is_invalid = False

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(2, 2, 2, 2)
        root_layout.setSpacing(4)

        self.input = QLineEdit(self)
        self.input.setText(text)
        if self._placeholder_text:
            self.input.setPlaceholderText(self._placeholder_text)
        self.input.setFrame(False)
        self.input.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.input.installEventFilter(self)
        self.input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        if self._max_length is not None:
            self.input.setMaxLength(self._max_length)
        connect_signal(self.input.textChanged, self._on_text_changed)

        root_layout.addWidget(self.input, stretch=1)

        self.icon_placeholder = QWidget(self)
        self.icon_placeholder.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.icon_placeholder.setFixedWidth(DEFAULT_ICON_PLACEHOLDER_WIDTH)
        self.icon_placeholder.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        icon_layout = QHBoxLayout(self.icon_placeholder)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_widget: QWidget = self._build_icon_widget(self._icon_path)
        self._install_focus_forwarding(self.icon_placeholder)
        self._install_focus_forwarding(self._icon_widget)
        icon_layout.addWidget(self._icon_widget)

        root_layout.addWidget(self.icon_placeholder)
        root_layout.setAlignment(self.icon_placeholder, Qt.AlignmentFlag.AlignVCenter)
        root_layout.setStretchFactor(self.input, 1)

        self.apply_style(self._style)
        self._initialize_validation_state()

    def enterEvent(self, event: QEnterEvent | None) -> None:
        self._is_hovered = True
        self._update_border_style()
        self._update_icon_color()
        super().enterEvent(event)

    def leaveEvent(self, a0: QEvent | None) -> None:
        self._is_hovered = False
        self._update_border_style()
        self._update_icon_color()
        super().leaveEvent(a0)

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        if a0 in {self.icon_placeholder, self._icon_widget}:
            if a1 is not None and a1.type() is QEvent.Type.MouseButtonPress:
                self.input.setFocus(Qt.FocusReason.MouseFocusReason)
                return True
        if a0 in {self, self.input} and a1 is not None:
            if a1.type() is QEvent.Type.FocusIn:
                self._was_previously_focused = False
                self._update_border_style()
            elif a1.type() is QEvent.Type.FocusOut:
                self._was_previously_focused = True
                if (
                    self._revert_on_focus_out
                    and self._is_invalid
                    and self.text() != self._last_valid_text
                ):
                    self.set_text(self._last_valid_text)
                self._update_border_style()
        return super().eventFilter(a0, a1)

    def apply_style(self, style: InputStyleConfig) -> None:
        self._style = style
        self._refresh_input_style()
        self._update_border_style()
        self._update_icon_color()

    def clear_previously_focused(self) -> None:
        if not self._was_previously_focused:
            return
        self._was_previously_focused = False
        self._update_border_style()

    def text(self) -> str:
        return self.input.text()

    def set_text(self, text: str) -> None:
        self.input.setText(text)

    def _initialize_validation_state(self) -> None:
        text = self.input.text()
        if self._max_length is not None and len(text) > self._max_length:
            trimmed = text[: self._max_length]
            if trimmed != text:
                self.input.blockSignals(True)
                self.input.setText(trimmed)
                self.input.blockSignals(False)
                text = trimmed
        self._update_validation_state(text, allow_last_valid_update=True)

    def _on_text_changed(self, text: str) -> None:
        if self._max_length is not None and len(text) > self._max_length:
            trimmed = text[: self._max_length]
            if trimmed != text:
                self.input.blockSignals(True)
                self.input.setText(trimmed)
                self.input.blockSignals(False)
                text = trimmed
        self._update_validation_state(text, allow_last_valid_update=True)

    def _update_validation_state(
        self,
        text: str,
        *,
        allow_last_valid_update: bool,
    ) -> None:
        is_valid = self._is_text_valid(text)
        if is_valid and allow_last_valid_update:
            self._last_valid_text = text
        self._is_invalid = bool(self._compiled_pattern) and not is_valid
        self._update_border_style()

    def _is_text_valid(self, text: str) -> bool:
        if self._compiled_pattern is None:
            return True
        return bool(self._compiled_pattern.fullmatch(text))

    def _build_icon_widget(self, icon_path: Path | None) -> QWidget:
        if icon_path is None:
            return self._create_letter_placeholder()

        loaded = load_svg_widget(icon_path, DEFAULT_ICON_SIZE)
        if loaded is None:
            return self._create_letter_placeholder()

        widget, template = loaded
        widget.setParent(self.icon_placeholder)
        self._icon_template = template
        return widget

    def _create_letter_placeholder(self) -> QLabel:
        label = QLabel("M", self.icon_placeholder)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _refresh_input_style(self) -> None:
        style = self._style
        self.icon_placeholder.setStyleSheet(
            f"""
            background-color: {style.background};
            border: none;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            """
        )
        self.input.setStyleSheet(
            f"""
            border: none;
            background-color: transparent;
            color: {style.text_color};
            padding-left: 4px;
            padding-right: 8px;
            letter-spacing: 1px;
            font-family: "Trebuchet MS";
            outline: none;
            selection-background-color: {style.selection_background};
            selection-color: {style.selection_text_color};
            QLineEdit::placeholder {{
                color: {style.placeholder_color};
                letter-spacing: 1px;
                font-family: "Trebuchet MS";
            }}
            QLineEdit:focus {{
                outline: none;
            }}
            """
        )

    def _update_border_style(self) -> None:
        style = self._style
        if self.input.hasFocus():
            border = style.border_focus
            width = style.border_focus_width
        elif self._is_hovered:
            border = style.border_hover
            width = style.border_hover_width
        elif self._was_previously_focused:
            border = style.border_previous_focus
            width = style.border_previous_focus_width
        else:
            border = style.border_default
            width = style.border_default_width
        self.setStyleSheet(
            f"""
            background-color: {style.background};
            border: {width}px solid {border};
            border-radius: 6px;
            """
        )

    def _update_icon_color(self) -> None:
        color = self._style.icon_hover_color if self._is_hovered else self._style.icon_color
        if isinstance(self._icon_widget, QLabel):
            self._icon_widget.setStyleSheet(
                f"""
                color: {color};
                font-size: 12px;
                font-weight: 600;
                """
            )
        elif isinstance(self._icon_widget, QSvgWidget) and self._icon_template is not None:
            svg_text = self._icon_template.replace("__SVG_COLOR__", color)
            self._icon_widget.load(svg_text.encode("utf-8"))

    def _install_focus_forwarding(self, widget: QWidget | None) -> None:
        if widget is None:
            return
        widget.installEventFilter(self)
        widget.setCursor(Qt.CursorShape.IBeamCursor)


def _default_style() -> InputStyleConfig:
    from ...styles.style_registry import StyleRegistry

    registry = StyleRegistry()
    return registry.input_config()


__all__ = ["InputWithIcon"]
