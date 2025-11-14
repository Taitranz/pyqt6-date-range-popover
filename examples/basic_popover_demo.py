"""
Minimal PyQt application that embeds :class:`DateRangePopover`.

The demo intentionally mirrors the snippets in ``README.md`` so developer
tooling and tests always execute the same setup path. It also showcases basic
input sanitisation: the ``DatePickerConfig`` is instantiated once, validated,
and then re-used for the lifetime of the popover.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Protocol, cast

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from date_range_popover import DatePickerConfig, DateRange, DateRangePopover, PickerMode


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


class _RangeSignal(Protocol):
    def connect(self, slot: Callable[[DateRange], None]) -> object: ...


class MainWindow(QMainWindow):
    """Simple host window that centers the popover widget."""

    def __init__(self) -> None:
        """Initialise the demo window and wire popover signals."""
        super().__init__()
        self.setWindowTitle("Date Range Popover Demo")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        config = DatePickerConfig(mode=PickerMode.DATE)
        self.date_range_popover = DateRangePopover(config=config)
        layout.addWidget(self.date_range_popover, alignment=Qt.AlignmentFlag.AlignCenter)

        cast(_DateSignal, self.date_range_popover.date_selected).connect(self._on_date_selected)
        cast(_RangeSignal, self.date_range_popover.range_selected).connect(self._on_range_selected)

    def _on_date_selected(self, date: QDate) -> None:
        """Print the currently selected date whenever the signal fires."""
        print(f"Selected date: {date.toString('yyyy-MM-dd')}")

    def _on_range_selected(self, date_range: DateRange) -> None:
        """Print the selected range in a friendly ``start -> end`` format."""
        if date_range.start_date is not None:
            start = date_range.start_date.toString("yyyy-MM-dd")
        else:
            start = "?"
        if date_range.end_date is not None:
            end = date_range.end_date.toString("yyyy-MM-dd")
        else:
            end = "?"
        print(f"Selected range: {start} -> {end}")


def main() -> None:
    """Launch the demo application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
