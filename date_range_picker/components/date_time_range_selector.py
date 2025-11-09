from __future__ import annotations

from typing import Final, Literal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from .input_with_icon import InputWithIcon

ModeLiteral = Literal["go_to_date", "custom_date_range"]
GO_TO_DATE: Final[ModeLiteral] = "go_to_date"
CUSTOM_DATE_RANGE: Final[ModeLiteral] = "custom_date_range"


class DateTimeRangeSelector(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        mode: ModeLiteral = GO_TO_DATE,
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #cfe2f3;")

        self._mode: ModeLiteral = mode
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(16)

        self._build_ui()

    def set_mode(self, mode: ModeLiteral) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self._build_ui()

    def _build_ui(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if self._mode == GO_TO_DATE:
            self._layout.setSpacing(0)
            input_with_icon = InputWithIcon(self, text="component 2")
            self._layout.addWidget(input_with_icon)
            return

        if self._mode == CUSTOM_DATE_RANGE:
            self._layout.setSpacing(16)
            for index in range(2):
                input_with_icon = InputWithIcon(
                    self,
                    text=f"Date container {index + 1}",
                )
                self._layout.addWidget(input_with_icon)
            self._layout.addStretch()

