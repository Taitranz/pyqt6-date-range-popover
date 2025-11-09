import sys
from typing import Callable, Protocol, cast

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from date_range_picker import DatePickerConfig, DateRange, DateRangePicker, PickerMode


class _DateSignal(Protocol):
    def connect(self, slot: Callable[[QDate], None]) -> object: ...


class _RangeSignal(Protocol):
    def connect(self, slot: Callable[[DateRange], None]) -> object: ...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Application")
        self.setGeometry(100, 100, 800, 600)
        
        # Set white background
        self.setStyleSheet("background-color: white;")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        config = DatePickerConfig(mode=PickerMode.DATE)
        self.date_range_picker = DateRangePicker(config=config)
        layout.addWidget(self.date_range_picker, alignment=Qt.AlignmentFlag.AlignCenter)

        cast(_DateSignal, self.date_range_picker.date_selected).connect(self._on_date_selected)
        cast(_RangeSignal, self.date_range_picker.range_selected).connect(self._on_range_selected)

    def _on_date_selected(self, date: QDate) -> None:
        print(f"Selected date: {date.toString('yyyy-MM-dd')}")

    def _on_range_selected(self, date_range: DateRange) -> None:
        if date_range.start_date is not None:
            start = date_range.start_date.toString("yyyy-MM-dd")
        else:
            start = "?"
        if date_range.end_date is not None:
            end = date_range.end_date.toString("yyyy-MM-dd")
        else:
            end = "?"
        print(f"Selected range: {start} -> {end}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

