"""
Demonstrate how to layer custom callback interfaces on top of the Qt
signals exposed by :class:`DateRangePopover`. Large applications often
want their own plug-in / observer APIs; this example shows how to build
one without subclassing any of the library widgets.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Protocol

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QTextEdit, QVBoxLayout, QWidget

from date_range_popover import DatePickerConfig, DateRange, DateRangePopover, PickerMode


class SelectionObserver(Protocol):
    """Application-defined callback interface for selection events."""

    def on_single_date(self, date: QDate) -> None: ...

    def on_range(self, date_range: DateRange) -> None: ...

    def on_cancelled(self) -> None: ...


class SelectionDispatcher:
    """
    Convert Qt signals into a callback-friendly observer API.

    Embedders can register any object that satisfies ``SelectionObserver``.
    The dispatcher takes care of wiring the Qt signals once and then
    fan-outs updates to every observer.
    """

    def __init__(self) -> None:
        self._observers: list[SelectionObserver] = []

    def bind(self, popover: DateRangePopover) -> None:
        """Wire the dispatcher to the picker signals."""
        popover.date_selected.connect(self._handle_single)  # type: ignore[arg-type]
        popover.range_selected.connect(self._handle_range)  # type: ignore[arg-type]
        popover.cancelled.connect(self._handle_cancelled)  # type: ignore[arg-type]

    def register(self, observer: SelectionObserver) -> None:
        """Add a new observer at runtime."""
        self._observers.append(observer)

    def _notify(self, method_name: str, *args: object) -> None:
        for observer in self._observers:
            handler: Any = getattr(observer, method_name)
            handler(*args)

    def _handle_single(self, date: QDate) -> None:
        self._notify("on_single_date", date)

    def _handle_range(self, date_range: DateRange) -> None:
        self._notify("on_range", date_range)

    def _handle_cancelled(self) -> None:
        self._notify("on_cancelled")


@dataclass
class LoggingObserver:
    """Observer that forwards updates to a QTextEdit widget."""

    output: QTextEdit

    def on_single_date(self, date: QDate) -> None:
        self.output.append(f"[date] {date.toString('yyyy-MM-dd')}")

    def on_range(self, date_range: DateRange) -> None:
        start_date = (
            date_range.start_date.toString("yyyy-MM-dd")
            if date_range.start_date is not None
            else "?"
        )
        end_date = (
            date_range.end_date.toString("yyyy-MM-dd")
            if date_range.end_date is not None
            else "?"
        )
        self.output.append(f"[range] {start_date} -> {end_date}")

    def on_cancelled(self) -> None:
        self.output.append("[cancelled]")


@dataclass
class AnalyticsObserver:
    """Pretend analytics observer that could forward to an event bus."""

    captured_events: list[str]

    def on_single_date(self, date: QDate) -> None:
        self.captured_events.append(f"single:{date.toJulianDay()}")

    def on_range(self, date_range: DateRange) -> None:
        start_date = (
            date_range.start_date.toJulianDay() if date_range.start_date is not None else "none"
        )
        end_date = (
            date_range.end_date.toJulianDay() if date_range.end_date is not None else "none"
        )
        self.captured_events.append(f"range:{(start_date, end_date)}")

    def on_cancelled(self) -> None:
        self.captured_events.append("cancelled")


class ExtensionDemoWindow(QMainWindow):
    """Wire the dispatcher + observers to showcase the hook pattern."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Extension Hooks Demo")
        self.resize(720, 640)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("Observer output (fan-out from dispatcher):"))
        layout.addWidget(self.log_output, stretch=1)

        config = DatePickerConfig(
            mode=PickerMode.CUSTOM_RANGE,
            time_step_minutes=15,
        )
        self.popover = DateRangePopover(config=config)
        layout.addWidget(self.popover, alignment=Qt.AlignmentFlag.AlignTop)

        self.setCentralWidget(container)

        dispatcher = SelectionDispatcher()
        dispatcher.bind(self.popover)
        dispatcher.register(LoggingObserver(self.log_output))
        dispatcher.register(AnalyticsObserver([]))
        self._dispatcher = dispatcher


def main() -> None:
    """Launch the extension hook showcase."""
    app = QApplication(sys.argv)
    window = ExtensionDemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
