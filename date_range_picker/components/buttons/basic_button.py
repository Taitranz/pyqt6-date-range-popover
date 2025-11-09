from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QWidget

from ...styles import constants


class BasicButton(QPushButton):
    """Simple styled action button."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        label: str = "Done",
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        super().__init__(label, parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        font = constants.create_button_font()
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)

        if width is None:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(width)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        final_height = height if height is not None else constants.ACTION_BUTTON_HEIGHT
        self.setFixedHeight(final_height)
        self._vertical_padding = self._compute_vertical_padding(final_height)

    @property
    def vertical_padding(self) -> int:
        return self._vertical_padding

    def apply_stylesheet(self, stylesheet: str) -> None:
        self.setStyleSheet(stylesheet)

    def _compute_vertical_padding(self, final_height: int) -> int:
        font_height = self.fontMetrics().height()
        available_space = max(0, final_height - font_height)
        max_padding = constants.ACTION_BUTTON_VERTICAL_PADDING
        computed_padding = available_space // 2
        return min(max_padding, computed_padding)


__all__ = ["BasicButton"]


