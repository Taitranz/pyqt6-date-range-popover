from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget

from .input_with_icon import InputWithIcon

ModeLiteral = Literal["go_to_date", "custom_date_range"]
GO_TO_DATE: Final[ModeLiteral] = "go_to_date"
CUSTOM_DATE_RANGE: Final[ModeLiteral] = "custom_date_range"
CALENDAR_ICON_PATH: Final[Path] = (
    Path(__file__).resolve().parent.parent / "assets" / "calender.svg"
)


class DateTimeRangeSelector(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        mode: ModeLiteral = GO_TO_DATE,
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #1f1f1f;")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self._mode: ModeLiteral = mode
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(16)
        self._previously_focused_input: InputWithIcon | None = None

        self._build_ui()

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        focus_widget = QApplication.focusWidget()
        if focus_widget is not None and focus_widget is not self:
            focus_widget.clearFocus()
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(a0)

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        target: InputWithIcon | None = None
        if isinstance(a0, InputWithIcon):
            target = a0
        elif isinstance(a0, QLineEdit):
            parent = a0.parentWidget()
            if isinstance(parent, InputWithIcon):
                target = parent
        if target is not None and a1 is not None and a1.type() is QEvent.Type.FocusIn:
            if (
                self._previously_focused_input is not None
                and self._previously_focused_input is not target
            ):
                self._previously_focused_input.clear_previously_focused()
            self._previously_focused_input = target
        return super().eventFilter(a0, a1)

    def set_mode(self, mode: ModeLiteral) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self._build_ui()

    def _build_ui(self) -> None:
        self._previously_focused_input = None
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if self._mode == GO_TO_DATE:
            self._layout.setSpacing(0)
            input_with_icon = self._create_input(self, text="component 2")
            self._layout.addWidget(input_with_icon)
            return

        if self._mode == CUSTOM_DATE_RANGE:
            self._layout.setSpacing(16)
            for index in range(2):
                input_with_icon = self._create_input(
                    self,
                    text=f"Date container {index + 1}",
                )
                self._layout.addWidget(input_with_icon)
            self._layout.addStretch()

    def _create_input(self, parent: QWidget, *, text: str) -> InputWithIcon:
        input_with_icon = InputWithIcon(
            parent,
            text=text,
            icon_path=str(CALENDAR_ICON_PATH),
        )
        input_with_icon.installEventFilter(self)
        input_with_icon.input.installEventFilter(self)
        return input_with_icon

