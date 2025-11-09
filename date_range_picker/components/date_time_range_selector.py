from __future__ import annotations

from pathlib import Path
from typing import Callable, Final, Literal, Protocol, cast

from PyQt6.QtCore import QDate, QEvent, QObject, Qt, pyqtSignal
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


class _StrSignal(Protocol):
    def connect(self, slot: Callable[[str], None]) -> object: ...


class DateTimeRangeSelector(QWidget):
    date_input_valid = pyqtSignal(QDate)

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
        self._go_to_date_input: InputWithIcon | None = None
        self._date_inputs: list[InputWithIcon] = []
        self._last_focused_date_input: InputWithIcon | None = None
        self._date_input_handlers: dict[InputWithIcon, Callable[[str], None]] = {}

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
            if target in self._date_inputs:
                self._last_focused_date_input = target
        return super().eventFilter(a0, a1)

    def set_mode(self, mode: ModeLiteral) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self._build_ui()

    def update_go_to_date(self, date: QDate) -> None:
        """Update the date input field in go_to_date mode."""
        if self._go_to_date_input is not None and self._mode == GO_TO_DATE:
            date_str = date.toString("yyyy-MM-dd")
            self._go_to_date_input.set_text(date_str)

    def apply_calendar_selection(self, date: QDate) -> None:
        """Apply a calendar-selected date to the most relevant date input."""
        target = self._last_focused_date_input
        if target is None:
            if self._date_inputs:
                target = self._date_inputs[0]
        if target is None:
            return
        target.set_text(date.toString("yyyy-MM-dd"))
        self._last_focused_date_input = target

    def _build_ui(self) -> None:
        self._previously_focused_input = None
        self._last_focused_date_input = None
        self._date_inputs = []
        self._go_to_date_input = None
        self._date_input_handlers = {}
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

            date_input = self._create_input(self, text="2025-11-04", is_date=True)
            self._go_to_date_input = date_input
            time_input = self._create_input(
                self,
                text="00:00",
                width=100,
                icon_path=str(CLOCK_ICON_PATH),
                is_date=False,
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
                    is_date=True,
                )
                time_input = self._create_input(
                    self,
                    text="00:00",
                    width=100,
                    icon_path=str(CLOCK_ICON_PATH),
                    is_date=False,
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
        is_date: bool,
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
        self._register_input(input_with_icon, is_date=is_date)
        return input_with_icon

    def _register_input(
        self,
        input_with_icon: InputWithIcon,
        *,
        is_date: bool,
    ) -> None:
        input_with_icon.installEventFilter(self)
        input_with_icon.input.installEventFilter(self)
        if is_date:
            self._date_inputs.append(input_with_icon)
            handler = self._make_date_input_handler(input_with_icon)
            self._date_input_handlers[input_with_icon] = handler
            text_signal = cast(_StrSignal, input_with_icon.input.textChanged)
            text_signal.connect(handler)

    def _on_date_input_text_changed(self, target: InputWithIcon, text: str) -> None:
        if target not in self._date_inputs:
            return
        stripped = text.strip()
        if len(stripped) != 10:
            return
        parsed = QDate.fromString(stripped, "yyyy-MM-dd")
        if not parsed.isValid():
            return
        normalized = parsed.toString("yyyy-MM-dd")
        if normalized != stripped:
            return
        self._last_focused_date_input = target
        self.date_input_valid.emit(parsed)

    def _make_date_input_handler(self, target: InputWithIcon) -> Callable[[str], None]:
        def handler(text: str) -> None:
            self._on_date_input_text_changed(target, text)

        return handler

