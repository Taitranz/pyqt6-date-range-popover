"""Reusable ``QObject``-based event filters."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtWidgets import QWidget


class HoverEventFilter(QObject):
    """Invokes callbacks when the watched widget receives hover events."""

    def __init__(
        self,
        *,
        on_enter: Callable[[], None] | None = None,
        on_leave: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._on_enter = on_enter
        self._on_leave = on_leave

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:  # noqa: D401
        if a1 is None:
            return super().eventFilter(a0, a1)
        if a1.type() is QEvent.Type.Enter:
            if self._on_enter is not None:
                self._on_enter()
        elif a1.type() is QEvent.Type.Leave:
            if self._on_leave is not None:
                self._on_leave()
        return super().eventFilter(a0, a1)


class FocusForwardingFilter(QObject):
    """Forwards mouse interactions from the watched widget to ``target``."""

    def __init__(self, target: QWidget, *, focus_reason: Qt.FocusReason | None = None) -> None:
        super().__init__(target)
        self._target = target
        self._focus_reason = focus_reason or Qt.FocusReason.MouseFocusReason

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:  # noqa: D401
        if a1 is None:
            return super().eventFilter(a0, a1)
        if a1.type() is QEvent.Type.MouseButtonPress:
            self._target.setFocus(self._focus_reason)
            return True
        return super().eventFilter(a0, a1)


class MouseFocusFilter(QObject):
    """Applies focus to the watched widget on mouse presses."""

    def __init__(self, *, focus_reason: Qt.FocusReason | None = None) -> None:
        super().__init__()
        self._focus_reason = focus_reason or Qt.FocusReason.MouseFocusReason

    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:  # noqa: D401
        if a1 is None or a0 is None:
            return super().eventFilter(a0, a1)
        if a1.type() is QEvent.Type.MouseButtonPress and isinstance(a0, QWidget):
            a0.setFocus(self._focus_reason)
        return super().eventFilter(a0, a1)


__all__ = ["HoverEventFilter", "FocusForwardingFilter", "MouseFocusFilter"]


