from __future__ import annotations

from pathlib import Path
from typing import Final

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QWidget

DEFAULT_HEIGHT: Final[int] = 34
DEFAULT_WIDTH: Final[int] = 150
DEFAULT_ICON_PLACEHOLDER_WIDTH: Final[int] = 32
DEFAULT_ICON_SIZE: Final[int] = 28
ICON_COLOR: Final[str] = "#8c8c8c"
INPUT_TEXT_COLOR: Final[str] = "#f5f5f5"


class InputWithIcon(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        text: str = "",
        width: int | None = DEFAULT_WIDTH,
        icon_path: str | None = None,
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(DEFAULT_HEIGHT)
        if width is not None:
            self.setFixedWidth(width)
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(2, 2, 2, 2)
        root_layout.setSpacing(4)

        self._was_previously_focused = False

        self.input = QLineEdit(self)
        self.input.setText(text)
        self.input.setFrame(False)
        self.input.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.input.installEventFilter(self)
        self.input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.input.setStyleSheet(
            """
            border: none;
            background-color: transparent;
            color: %s;
            padding-left: 4px;
            padding-right: 8px;
            letter-spacing: 1px;
            font-family: "Trebuchet MS";
            QLineEdit::placeholder {
                color: %s;
                letter-spacing: 1px;
                font-family: "Trebuchet MS";
            }
            """
            % (INPUT_TEXT_COLOR, ICON_COLOR),
        )
        root_layout.addWidget(self.input, stretch=1)

        self.icon_placeholder = QWidget(self)
        self.icon_placeholder.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.icon_placeholder.setFixedWidth(DEFAULT_ICON_PLACEHOLDER_WIDTH)
        self.icon_placeholder.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self.icon_placeholder.setStyleSheet(
            """
            background-color: #1f1f1f;
            border: none;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            """,
        )
        icon_layout = QHBoxLayout(self.icon_placeholder)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_widget = self._build_icon_widget(icon_path)
        icon_layout.addWidget(icon_widget)

        root_layout.addWidget(self.icon_placeholder)
        root_layout.setAlignment(self.icon_placeholder, Qt.AlignmentFlag.AlignVCenter)
        root_layout.setStretchFactor(self.input, 1)
        self._update_border_style()

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        if a0 is self.input and a1 is not None and a1.type() in {
            QEvent.Type.FocusIn,
            QEvent.Type.FocusOut,
        }:
            if a1.type() is QEvent.Type.FocusIn:
                self._was_previously_focused = False
            elif a1.type() is QEvent.Type.FocusOut:
                self._was_previously_focused = True
            self._update_border_style()
        return super().eventFilter(a0, a1)

    def clear_previously_focused(self) -> None:
        if not self._was_previously_focused:
            return
        self._was_previously_focused = False
        self._update_border_style()

    def _update_border_style(self) -> None:
        if self.input.hasFocus():
            border_style = "2px solid #2962ff"
        elif self._was_previously_focused:
            border_style = "2px solid #575757"
        else:
            border_style = "1px solid #575757"
        self.setStyleSheet(
            f"""
            background-color: #1f1f1f;
            border: {border_style};
            border-radius: 6px;
            """,
        )

    def _build_icon_widget(self, icon_path: str | None) -> QWidget:
        if icon_path is None:
            return self._create_letter_placeholder()
        svg_widget = self._create_svg_widget(icon_path)
        if svg_widget is not None:
            return svg_widget
        return self._create_letter_placeholder()

    def _create_letter_placeholder(self) -> QLabel:
        label = QLabel("M", self.icon_placeholder)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            """
            color: %s;
            font-size: 12px;
            font-weight: 600;
            """
            % ICON_COLOR
        )
        return label

    def _create_svg_widget(self, icon_path: str) -> QSvgWidget | None:
        path = Path(icon_path)
        try:
            svg_data = path.read_bytes()
        except OSError:
            return None
        if not svg_data:
            return None
        svg_widget = QSvgWidget(self.icon_placeholder)
        svg_widget.setFixedSize(DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)
        svg_widget.setStyleSheet(
            """
            background-color: transparent;
            color: %s;
            """
            % ICON_COLOR
        )
        svg_text: str
        try:
            svg_text = svg_data.decode("utf-8")
        except UnicodeDecodeError:
            svg_text = svg_data.decode("utf-8", errors="ignore")
        if "currentColor" in svg_text:
            svg_text = svg_text.replace("currentColor", ICON_COLOR)
        svg_widget.load(svg_text.encode("utf-8"))
        return svg_widget

