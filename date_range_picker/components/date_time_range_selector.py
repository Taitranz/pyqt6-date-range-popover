from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from .input_with_icon import InputWithIcon

ModeLiteral = Literal["go_to_date", "custom_date_range"]
GO_TO_DATE: Final[ModeLiteral] = "go_to_date"
CUSTOM_DATE_RANGE: Final[ModeLiteral] = "custom_date_range"
CALENDAR_ICON_PATH: Final[Path] = (
    Path(__file__).resolve().parent.parent / "assets" / "calender.svg"
)
CLOCK_ICON_PATH: Final[Path] = (
    Path(__file__).resolve().parent.parent / "assets" / "clock.svg"
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
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            date_input = self._create_input(self, text="2025-11-04")
            time_input = self._create_input(
                self,
                text="00:00",
                width=100,
                icon_path=str(CLOCK_ICON_PATH),
            )

            row_layout.addWidget(date_input)
            row_layout.addStretch()
            row_layout.addWidget(time_input)
            row_layout.setAlignment(time_input, Qt.AlignmentFlag.AlignRight)
            self._layout.addLayout(row_layout)
            return

        if self._mode == CUSTOM_DATE_RANGE:
            self._layout.setSpacing(16)
            for _ in range(2):
                row_layout = QHBoxLayout()
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(8)

                date_input = self._create_input(
                    self,
                    text="2025-11-04",
                )
                time_input = self._create_input(
                    self,
                    text="00:00",
                    width=100,
                    icon_path=str(CLOCK_ICON_PATH),
                )
                row_layout.addWidget(date_input)
                row_layout.addStretch()
                row_layout.addWidget(time_input)
                row_layout.setAlignment(time_input, Qt.AlignmentFlag.AlignRight)
                self._layout.addLayout(row_layout)
            self._layout.addStretch()

    def _create_input(
        self,
        parent: QWidget,
        *,
        text: str,
        width: int | None = None,
        icon_path: str | None = None,
    ) -> InputWithIcon:
        if width is None:
            input_with_icon = InputWithIcon(
                parent,
                text=text,
                icon_path=icon_path or str(CALENDAR_ICON_PATH),
            )
        else:
            input_with_icon = InputWithIcon(
                parent,
                text=text,
                width=width,
                icon_path=icon_path or str(CALENDAR_ICON_PATH),
            )
        input_with_icon.installEventFilter(self)
        input_with_icon.input.installEventFilter(self)
        return input_with_icon

