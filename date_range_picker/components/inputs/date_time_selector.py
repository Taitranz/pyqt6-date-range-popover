from __future__ import annotations

from pathlib import Path
from typing import Callable, Final, Literal

from PyQt6.QtCore import QDate, QEvent, QObject, Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QCompleter,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ...styles.theme import ColorPalette
from ...utils import connect_signal
from .input_with_icon import InputWithIcon

ModeLiteral = Literal["go_to_date", "custom_date_range"]
GO_TO_DATE: Final[ModeLiteral] = "go_to_date"
CUSTOM_DATE_RANGE: Final[ModeLiteral] = "custom_date_range"
CALENDAR_ICON_PATH: Final[Path] = (
    Path(__file__).resolve().parents[2] / "assets" / "calender.svg"
)
CLOCK_ICON_PATH: Final[Path] = (
    Path(__file__).resolve().parents[2] / "assets" / "clock.svg"
)


class DateTimeSelector(QWidget):
    """Widget hosting date/time inputs with selectable layout."""

    date_input_valid = pyqtSignal(QDate)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        mode: ModeLiteral = GO_TO_DATE,
        palette: ColorPalette | None = None,
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._palette = palette or ColorPalette()
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
        self._time_inputs: list[InputWithIcon] = []
        self._time_model: QStringListModel | None = None

        self.apply_palette(self._palette)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self._build_ui()

    def apply_palette(self, palette: ColorPalette) -> None:
        self._palette = palette
        self.setStyleSheet(f"background-color: {palette.window_background};")

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:  # noqa: N802
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
        if a1 is not None and a1.type() is QEvent.Type.MouseButtonPress:
            if not self._object_is_within_self(a0) and self._focus_within_self():
                self._clear_focus_from_inputs()
        if target is not None and a1 is not None and a1.type() in {
            QEvent.Type.FocusIn,
            QEvent.Type.FocusOut,
        }:
            if a1.type() is QEvent.Type.FocusIn:
                if (
                    self._previously_focused_input is not None
                    and self._previously_focused_input is not target
                ):
                    self._previously_focused_input.clear_previously_focused()
                self._previously_focused_input = target
                if target in self._date_inputs:
                    self._last_focused_date_input = target
                elif target in self._time_inputs:
                    self._show_time_popup(target.input)
        return super().eventFilter(a0, a1)

    def set_mode(self, mode: ModeLiteral) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self._build_ui()
        if mode == CUSTOM_DATE_RANGE and self._date_inputs:
            self._date_inputs[0].input.setFocus(Qt.FocusReason.OtherFocusReason)

    def update_go_to_date(self, date: QDate) -> None:
        """Update the date input field in go_to_date mode."""
        if self._go_to_date_input is not None and self._mode == GO_TO_DATE:
            self._go_to_date_input.set_text(date.toString("yyyy-MM-dd"))

    def apply_calendar_selection(self, date: QDate) -> None:
        """Apply a calendar-selected date to the most relevant date input."""
        target = self._last_focused_date_input or (self._date_inputs[0] if self._date_inputs else None)
        if target is None:
            return
        was_first_input_focused = (
            self._mode == CUSTOM_DATE_RANGE
            and len(self._date_inputs) >= 2
            and self._last_focused_date_input == self._date_inputs[0]
        )
        target.set_text(date.toString("yyyy-MM-dd"))
        self._last_focused_date_input = target
        if was_first_input_focused:
            self._date_inputs[1].input.setFocus(Qt.FocusReason.OtherFocusReason)

    def set_range(self, start: QDate, end: QDate) -> None:
        if self._mode == GO_TO_DATE:
            self.update_go_to_date(start)
            return
        if len(self._date_inputs) >= 2:
            self._date_inputs[0].set_text(start.toString("yyyy-MM-dd"))
            self._date_inputs[1].set_text(end.toString("yyyy-MM-dd"))

    def last_focused_date_index(self) -> int | None:
        if self._last_focused_date_input is None:
            return None
        try:
            return self._date_inputs.index(self._last_focused_date_input)
        except ValueError:
            return None

    def _build_ui(self) -> None:
        self._previously_focused_input = None
        self._last_focused_date_input = None
        self._date_inputs = []
        self._go_to_date_input = None
        self._date_input_handlers = {}
        self._time_inputs = []

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
        max_length = 10 if is_date else 5
        regex_pattern = (
            r"^\d{4}-\d{2}-\d{2}$"
            if is_date
            else r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        )

        placeholder = "YYYY-MM-DD" if is_date else "HH:MM"
        if width is None:
            input_with_icon = InputWithIcon(
                parent,
                text=text,
                icon_path=icon_path or str(CALENDAR_ICON_PATH),
                max_length=max_length,
                regex_pattern=regex_pattern,
                placeholder_text=placeholder,
            )
        else:
            input_with_icon = InputWithIcon(
                parent,
                text=text,
                width=width,
                icon_path=icon_path or str(CALENDAR_ICON_PATH),
                max_length=max_length,
                regex_pattern=regex_pattern,
                placeholder_text=placeholder,
            )
        input_with_icon.installEventFilter(self)
        input_with_icon.input.installEventFilter(self)
        if is_date:
            self._register_date_input(input_with_icon)
        else:
            self._register_time_input(input_with_icon)
        return input_with_icon

    def _register_date_input(self, input_with_icon: InputWithIcon) -> None:
        self._date_inputs.append(input_with_icon)
        handler = self._make_date_input_handler(input_with_icon)
        self._date_input_handlers[input_with_icon] = handler
        connect_signal(input_with_icon.input.textChanged, handler)

    def _register_time_input(self, input_with_icon: InputWithIcon) -> None:
        self._time_inputs.append(input_with_icon)
        self._attach_time_completer(input_with_icon.input)

    def _attach_time_completer(self, line_edit: QLineEdit) -> None:
        if self._time_model is None:
            self._time_model = QStringListModel(
                self._generate_time_options(15),
                self,
            )
        completer = QCompleter(self._time_model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setMaxVisibleItems(7)
        popup = completer.popup()
        if popup is not None:
            popup.setStyleSheet(
                "QListView { width: 98px; margin: 0px; padding: 0px; border: none; } "
                "QListView::item { height: 32px; margin: 0px; padding-left: 8px; padding-right: 8px; background-color: #1f1f1f; color: #ffffff; } "
                "QListView::item:hover { background-color: #2e2e2e; color: #ffffff; } "
                "QListView::item:selected { background-color: #f2f2f2; color: #000000; } "
                "QScrollBar:vertical { width: 0px; } QScrollBar:horizontal { height: 0px; }"
            )
            popup.setFixedWidth(98)
            popup.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            popup.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        line_edit.setCompleter(completer)

    def _generate_time_options(self, step_minutes: int) -> list[str]:
        return [
            f"{hour:02d}:{minute:02d}"
            for hour in range(24)
            for minute in range(0, 60, step_minutes)
        ]

    def _show_time_popup(self, line_edit: QLineEdit) -> None:
        completer = line_edit.completer()
        if completer is None:
            return
        popup = completer.popup()
        completer.setCompletionPrefix("")
        text = line_edit.text()
        if text and popup is not None:
            model = completer.model()
            if model is not None:
                match_indexes = model.match(
                    model.index(0, 0),
                    Qt.ItemDataRole.DisplayRole,
                    text,
                    1,
                    Qt.MatchFlag.MatchExactly,
                )
                if match_indexes:
                    popup.setCurrentIndex(match_indexes[0])
                    popup.scrollTo(match_indexes[0])
        popup_rect = line_edit.rect().translated(0, 3)
        completer.complete(popup_rect)

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

    def _object_is_within_self(self, obj: QObject | None) -> bool:
        widget: QWidget | None
        if isinstance(obj, QWidget):
            widget = obj
        else:
            widget = None
        while widget is not None:
            if widget is self:
                return True
            widget = widget.parentWidget()
        return False

    def _focus_within_self(self) -> bool:
        focus_widget = QApplication.focusWidget()
        if not isinstance(focus_widget, QWidget):
            return False
        return self._object_is_within_self(focus_widget)

    def _clear_focus_from_inputs(self) -> None:
        focus_widget = QApplication.focusWidget()
        if not isinstance(focus_widget, QWidget):
            return
        if not self._object_is_within_self(focus_widget):
            return
        focus_widget.clearFocus()


__all__ = [
    "DateTimeSelector",
    "ModeLiteral",
    "GO_TO_DATE",
    "CUSTOM_DATE_RANGE",
]


