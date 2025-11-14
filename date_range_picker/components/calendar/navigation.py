from __future__ import annotations

from pathlib import Path


from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ...styles import constants
from ...styles.theme import CalendarStyleConfig
from ...utils import connect_signal
from ...utils.svg_loader import load_colored_svg_icon

NAV_LEFT_ICON_PATH = Path(__file__).resolve().parents[2] / "assets" / "carrot_left.svg"
NAV_RIGHT_ICON_PATH = Path(__file__).resolve().parents[2] / "assets" / "carrot_right.svg"
NAV_ICON_SIZE = 28


class CalendarNavigation(QWidget):
    """Header navigation for the calendar views."""

    previous_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    header_clicked = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        style: CalendarStyleConfig | None = None,
    ) -> None:
        super().__init__(parent)

        if style is None:
            style = CalendarStyleConfig(
                background="#1f1f1f",
                header_text_color="#f5f5f5",
                day_text_color="#f5f5f5",
                muted_day_text_color="#8c8c8c",
                today_background="#f5f5f5",
                today_text_color="#1f1f1f",
                today_underline_color="#1f1f1f",
            day_hover_background="#2e2e2e",
                day_hover_text_color="#f5f5f5",
                nav_icon_color="#dbdbdb",
                day_label_background="#2e2e2e",
                mode_label_background="#2e2e2e",
                header_hover_background="#2e2e2e",
                header_hover_text_color="#ffffff",
                range_edge_background="#f2f2f2",
                range_edge_text_color="#1f1f1f",
                range_between_background="#2e2e2e",
                range_between_text_color="#ffffff",
            )
        self._style = style

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._previous_button = self._create_nav_button("previous")
        self._next_button = self._create_nav_button("next")
        self._header_button = self._create_header_button()

        layout.addWidget(self._previous_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self._header_button, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self._next_button, alignment=Qt.AlignmentFlag.AlignRight)

        connect_signal(self._previous_button.clicked, self.previous_clicked.emit)
        connect_signal(self._next_button.clicked, self.next_clicked.emit)
        connect_signal(self._header_button.clicked, self.header_clicked.emit)

        self.apply_style(self._style)

    def apply_style(self, style: CalendarStyleConfig) -> None:
        self._style = style
        self._header_button.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            f"color: {style.header_text_color};"
            "border: none;"
            "padding: 4px 11px 4px 11px;"
            "border-radius: 4px;"
            "outline: none;"
            "}"
            "QPushButton:hover {"
            f"background-color: {style.header_hover_background};"
            f"color: {style.header_hover_text_color};"
            "outline: none;"
            "}"
        )
        self._update_nav_icons()

    def set_header_text(self, text: str) -> None:
        self._header_button.setText(text)

    def set_navigation_enabled(self, *, previous_enabled: bool, next_enabled: bool) -> None:
        self._previous_button.setEnabled(previous_enabled)
        self._next_button.setEnabled(next_enabled)
        self._update_nav_icons()

    def _update_nav_icons(self) -> None:
        prev_enabled = self._previous_button.isEnabled()
        next_enabled = self._next_button.isEnabled()
        prev_color = self._style.nav_icon_color if prev_enabled else self._style.muted_day_text_color
        next_color = self._style.nav_icon_color if next_enabled else self._style.muted_day_text_color

        prev_icon = load_colored_svg_icon(NAV_LEFT_ICON_PATH, NAV_ICON_SIZE, prev_color)
        next_icon = load_colored_svg_icon(NAV_RIGHT_ICON_PATH, NAV_ICON_SIZE, next_color)
        self._previous_button.setIcon(prev_icon)
        self._next_button.setIcon(next_icon)
        icon_qsize = QSize(NAV_ICON_SIZE, NAV_ICON_SIZE)
        self._previous_button.setIconSize(icon_qsize)
        self._next_button.setIconSize(icon_qsize)
        prev_cursor = Qt.CursorShape.PointingHandCursor if prev_enabled else Qt.CursorShape.ArrowCursor
        next_cursor = Qt.CursorShape.PointingHandCursor if next_enabled else Qt.CursorShape.ArrowCursor
        self._previous_button.setCursor(prev_cursor)
        self._next_button.setCursor(next_cursor)

    def _create_nav_button(self, role: str) -> QPushButton:
        button = QPushButton(self)
        button.setAccessibleName(f"calendar-navigation-{role}")
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFixedSize(32, 32)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFlat(True)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.setStyleSheet(
            "QPushButton {"
            "background-color: transparent;"
            "border: none;"
            "padding: 0px;"
            "border-radius: 4px;"
            "outline: none;"
            "}"
            "QPushButton:hover {"
            f"background-color: {self._style.day_hover_background};"
            "outline: none;"
            "}"
        )
        button.setText("")
        return button

    def _create_header_button(self) -> QPushButton:
        button = QPushButton(self)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFlat(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.setFont(constants.create_calendar_header_font())
        return button


__all__ = ["CalendarNavigation"]


