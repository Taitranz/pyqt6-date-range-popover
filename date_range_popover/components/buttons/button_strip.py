from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ...styles import constants
from ...styles.theme import ColorPalette, LayoutConfig
from ...utils import connect_signal


class ButtonStrip(QWidget):
    """Displays Date and Custom Range buttons."""

    date_selected = pyqtSignal()
    custom_range_selected = pyqtSignal()

    def __init__(
        self, parent: QWidget | None = None, *, layout_config: LayoutConfig | None = None
    ) -> None:
        super().__init__(parent)

        self._selected_button = "date"
        self._hovered_button: str | None = None
        self._gap: QWidget | None = None

        self._layout_config = layout_config or LayoutConfig()
        self._palette = ColorPalette()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, self._layout_config.button_strip_bottom_margin)
        layout.setSpacing(0)

        self.date_button = QPushButton("Date", self)
        self.date_button.setFont(constants.create_button_font())
        self.date_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.date_button.setFixedWidth(self._layout_config.date_button_width)
        self.date_button.setMinimumHeight(0)
        self.date_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.date_button.installEventFilter(self)

        self.custom_range_button = QPushButton("Custom range", self)
        self.custom_range_button.setFont(constants.create_button_font())
        self.custom_range_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.custom_range_button.setFixedWidth(self._layout_config.custom_range_button_width)
        self.custom_range_button.setMinimumHeight(0)
        self.custom_range_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.custom_range_button.installEventFilter(self)

        layout.addWidget(
            self.date_button,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )

        self._gap = QWidget(self)
        self._gap.setFixedWidth(self._layout_config.button_gap)
        layout.addWidget(self._gap)

        layout.addWidget(
            self.custom_range_button,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
        layout.addStretch()

        connect_signal(self.date_button.clicked, self.date_selected.emit)
        connect_signal(self.custom_range_button.clicked, self.custom_range_selected.emit)

        self.apply_palette(ColorPalette())

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:
        if a0 in {self.date_button, self.custom_range_button} and a1 is not None:
            target_name = "date" if a0 is self.date_button else "custom_range"
            if a1.type() == QEvent.Type.Enter:
                if self._hovered_button != target_name:
                    self._hovered_button = target_name
                    self._update_button_styles()
            elif a1.type() == QEvent.Type.Leave:
                if self._hovered_button == target_name:
                    self._hovered_button = None
                    self._update_button_styles()
        return super().eventFilter(a0, a1)

    def set_selected_button(self, button_name: str) -> None:
        """Visually highlight the requested button."""
        if button_name not in {"date", "custom_range"}:
            return
        if self._selected_button == button_name:
            return
        self._selected_button = button_name
        self._update_button_styles()

    def apply_palette(self, palette: ColorPalette) -> None:
        """Apply the supplied color palette to the strip."""
        self._palette = palette
        self.setStyleSheet(f"background-color: {palette.button_container_background};")
        self._update_button_styles()

    def apply_layout(self, layout_config: LayoutConfig) -> None:
        """Update layout-driven dimensions such as widths and gaps."""
        self._layout_config = layout_config
        self.date_button.setFixedWidth(layout_config.date_button_width)
        self.custom_range_button.setFixedWidth(layout_config.custom_range_button_width)
        if self._gap is not None:
            self._gap.setFixedWidth(layout_config.button_gap)
        self._update_button_styles()

    def _update_button_styles(self) -> None:
        self._apply_style(self.date_button, "date")
        self._apply_style(self.custom_range_button, "custom_range")

    def _apply_style(self, button: QPushButton, button_name: str) -> None:
        if self._selected_button == button_name:
            color = self._palette.button_selected_color
        elif self._hovered_button == button_name:
            color = self._palette.button_hover_color
        else:
            color = self._palette.button_default_color
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


__all__ = ["ButtonStrip"]
