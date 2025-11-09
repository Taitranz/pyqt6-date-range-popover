from __future__ import annotations

from typing import Final

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QSizePolicy, QWidget

DEFAULT_HEIGHT: Final[int] = 34
DEFAULT_WIDTH: Final[int] = 150
DEFAULT_ICON_WIDTH: Final[int] = 34


class InputWithIcon(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        text: str = "",
        width: int | None = DEFAULT_WIDTH,
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            background-color: #ffffff;
            border: 2px solid yellow;
            """,
        )
        self.setFixedHeight(DEFAULT_HEIGHT)
        if width is not None:
            self.setFixedWidth(width)
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(2, 2, 2, 2)
        root_layout.setSpacing(4)

        self.input = QLineEdit(self)
        self.input.setText(text)
        self.input.setFrame(False)
        self.input.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.input.setStyleSheet(
            """
            border: none;
            background-color: transparent;
            padding-left: 8px;
            padding-right: 8px;
            """,
        )
        root_layout.addWidget(self.input, stretch=1)

        self.icon_placeholder = QWidget(self)
        self.icon_placeholder.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.icon_placeholder.setFixedWidth(DEFAULT_ICON_WIDTH)
        self.icon_placeholder.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self.icon_placeholder.setStyleSheet(
            """
            background-color: #ffc0cb;
            border: none;
            """,
        )
        root_layout.addWidget(self.icon_placeholder)
        root_layout.setAlignment(self.icon_placeholder, Qt.AlignmentFlag.AlignVCenter)
        root_layout.setStretchFactor(self.input, 1)

