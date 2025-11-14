from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...styles.theme import ColorPalette, LayoutConfig


class SlidingTrackIndicator(QWidget):
    """Handles layout of the sliding indicator within its track."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        palette: ColorPalette | None = None,
        layout: LayoutConfig | None = None,
    ) -> None:
        super().__init__(parent)

        self._palette = palette or ColorPalette()
        self._layout = layout or LayoutConfig()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        self._track_container = QWidget(self)
        self._track_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._track_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._track_container.setFixedHeight(self._layout.sliding_indicator_height)

        track_layout = QHBoxLayout(self._track_container)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(0)

        self._left_spacer = QWidget(self._track_container)
        self._left_spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._left_spacer.setFixedWidth(0)

        self._indicator = QWidget(self._track_container)
        self._indicator.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._indicator.setFixedHeight(self._layout.sliding_indicator_height)

        self._right_spacer = QWidget(self._track_container)
        self._right_spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._right_spacer.setFixedWidth(0)

        track_layout.addWidget(self._left_spacer)
        track_layout.addWidget(self._indicator)
        track_layout.addWidget(self._right_spacer)

        wrapper_layout.addWidget(self._track_container)

        self._current_position = 0
        self._current_width = 0

        self.apply_palette(self._palette)

    def apply_palette(self, palette: ColorPalette) -> None:
        """Apply the palette colors to the track and indicator."""
        self._palette = palette
        self.setStyleSheet(f"background-color: {palette.window_background};")
        radius = self._layout.sliding_indicator_radius
        self._track_container.setStyleSheet(
            f"background-color: {palette.track_background}; "
            f"border-radius: {radius}px;"
        )
        self._indicator.setStyleSheet(
            f"background-color: {palette.track_indicator_color}; "
            f"border-radius: {radius}px;"
        )

    def apply_layout(self, layout: LayoutConfig) -> None:
        """Apply layout dimensions such as height, radius, and default width."""
        self._layout = layout
        height = layout.sliding_indicator_height
        radius = layout.sliding_indicator_radius
        self._track_container.setFixedHeight(height)
        self._indicator.setFixedHeight(height)
        self._track_container.setStyleSheet(
            f"background-color: {self._palette.track_background}; "
            f"border-radius: {radius}px;"
        )
        self._indicator.setStyleSheet(
            f"background-color: {self._palette.track_indicator_color}; "
            f"border-radius: {radius}px;"
        )
        self._update_layout()

    @property
    def current_position(self) -> int:
        return self._current_position

    @property
    def current_width(self) -> int:
        return self._current_width

    def set_state(self, *, position: int, width: int) -> None:
        """Update the indicator state and reposition within the track."""
        self._current_position = max(position, 0)
        self._current_width = max(width, 0)
        self._indicator.setFixedWidth(self._current_width)
        self._update_layout()

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:  # noqa: N802
        super().resizeEvent(a0)
        self._update_layout()

    def _update_layout(self) -> None:
        track_width = self._track_container.width() or self._layout.default_track_width
        max_position = max(track_width - self._current_width, 0)
        clamped_position = max(0, min(self._current_position, max_position))

        self._left_spacer.setFixedWidth(clamped_position)

        remaining = max(track_width - clamped_position - self._current_width, 0)
        self._right_spacer.setFixedWidth(remaining)


__all__ = ["SlidingTrackIndicator"]


