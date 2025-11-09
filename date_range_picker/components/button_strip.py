"""Button strip that exposes signals for selecting a date range."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ..styles.constants import (
    BUTTON_CONTAINER_BACKGROUND,
    BUTTON_GAP,
    BUTTON_STRIP_BOTTOM_MARGIN,
    BUTTON_DEFAULT_COLOR,
    BUTTON_HOVER_COLOR,
    BUTTON_SELECTED_COLOR,
    CUSTOM_RANGE_BUTTON_WIDTH,
    DATE_BUTTON_WIDTH,
)
from ..styles.constants import create_button_font


class ButtonStrip(QWidget):
    """Displays Date and Custom Range buttons."""

    date_selected = pyqtSignal()
    custom_range_selected = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._selected_button = "date"
        self._hovered_button: Optional[str] = None

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {BUTTON_CONTAINER_BACKGROUND};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, BUTTON_STRIP_BOTTOM_MARGIN)
        layout.setSpacing(0)

        self.date_button = QPushButton("Date", self)
        self.date_button.setFont(create_button_font())
        self.date_button.setFixedWidth(DATE_BUTTON_WIDTH)
        self.date_button.setMinimumHeight(0)
        self.date_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.date_button.installEventFilter(self)

        self.custom_range_button = QPushButton("Custom range", self)
        self.custom_range_button.setFont(create_button_font())
        self.custom_range_button.setFixedWidth(CUSTOM_RANGE_BUTTON_WIDTH)
        self.custom_range_button.setMinimumHeight(0)
        self.custom_range_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.custom_range_button.installEventFilter(self)

        layout.addWidget(
            self.date_button,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )

        gap = QWidget(self)
        gap.setFixedWidth(BUTTON_GAP)
        layout.addWidget(gap)

        layout.addWidget(
            self.custom_range_button,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
        layout.addStretch()

        self.date_button.clicked.connect(self.date_selected.emit)  # type: ignore[attr-defined]
        self.custom_range_button.clicked.connect(self.custom_range_selected.emit)  # type: ignore[attr-defined]

        self._update_button_styles()

    def set_selected_button(self, button_name: str) -> None:
        if button_name not in {"date", "custom_range"}:
            return
        if self._selected_button == button_name:
            return
        self._selected_button = button_name
        self._update_button_styles()

    def eventFilter(self, obj: Optional[QObject], event: Optional[QEvent]) -> bool:  # type: ignore[override]
        if obj in {self.date_button, self.custom_range_button} and event is not None:
            target_name = "date" if obj is self.date_button else "custom_range"
            if event.type() == QEvent.Type.Enter:
                if self._hovered_button != target_name:
                    self._hovered_button = target_name
                    self._update_button_styles()
            elif event.type() == QEvent.Type.Leave:
                if self._hovered_button == target_name:
                    self._hovered_button = None
                    self._update_button_styles()
        return super().eventFilter(obj, event)

    def _update_button_styles(self) -> None:
        self._apply_style(self.date_button, "date")
        self._apply_style(self.custom_range_button, "custom_range")

    def _apply_style(self, button: QPushButton, button_name: str) -> None:
        if self._selected_button == button_name:
            color = BUTTON_SELECTED_COLOR
        elif self._hovered_button == button_name:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_DEFAULT_COLOR
        button.setStyleSheet(
            f"""
            text-align: left;
            padding: 0;
            margin: 0;
            border: none;
            outline: none;
            color: {color};
            """
        )


