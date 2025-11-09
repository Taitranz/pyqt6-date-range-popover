from __future__ import annotations

from pathlib import Path
from typing import Final, Optional, Tuple

from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QSvgWidget

_SVG_COLOR_PLACEHOLDER: Final[str] = "__SVG_COLOR__"


def _read_svg_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def load_colored_svg_icon(path: str | Path, size: int, color: str) -> QIcon:
    """Load an SVG and recolor it to build a ``QIcon``."""
    svg_path = Path(path)
    svg_text = _read_svg_text(svg_path)
    if not svg_text:
        return QIcon()

    normalized = (
        svg_text.replace("currentColor", _SVG_COLOR_PLACEHOLDER)
        .replace("#000000", _SVG_COLOR_PLACEHOLDER)
        .replace("#000", _SVG_COLOR_PLACEHOLDER)
    )
    colored_svg = normalized.replace(_SVG_COLOR_PLACEHOLDER, color)

    renderer = QSvgRenderer(QByteArray(colored_svg.encode("utf-8")))
    if not renderer.isValid():
        return QIcon()

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def load_svg_widget(path: str | Path, size: int) -> Optional[Tuple[QSvgWidget, str]]:
    """Load an SVG widget and return the widget and color template string."""
    svg_path = Path(path)
    try:
        svg_data = svg_path.read_bytes()
    except OSError:
        return None
    if not svg_data:
        return None

    svg_widget = QSvgWidget()
    svg_widget.setFixedSize(size, size)
    svg_widget.setStyleSheet("background-color: transparent;")

    try:
        svg_text = svg_data.decode("utf-8")
    except UnicodeDecodeError:
        svg_text = svg_data.decode("utf-8", errors="ignore")

    template = (
        svg_text.replace("currentColor", _SVG_COLOR_PLACEHOLDER)
        .replace("#8c8c8c", _SVG_COLOR_PLACEHOLDER)
        .replace("#000000", _SVG_COLOR_PLACEHOLDER)
    )

    svg_widget.load(template.replace(_SVG_COLOR_PLACEHOLDER, "#8c8c8c").encode("utf-8"))
    return svg_widget, template


__all__ = ["load_colored_svg_icon", "load_svg_widget"]


