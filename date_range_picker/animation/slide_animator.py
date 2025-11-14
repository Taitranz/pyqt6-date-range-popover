"""Animation utilities for the sliding indicator."""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import QObject, QTimer

from ..styles.constants import ANIMATION_DURATION_MS, ANIMATION_FRAME_MS
from ..utils import connect_signal


StepCallback = Callable[[int, int], None]
CompleteCallback = Optional[Callable[[int, int], None]]


class SlideAnimator(QObject):
    """Interpolates position and width values for the sliding indicator."""

    def __init__(
        self,
        *,
        frame_interval: int = ANIMATION_FRAME_MS,
        duration: int = ANIMATION_DURATION_MS,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._frame_interval = frame_interval
        self._duration = max(duration, frame_interval)

        self._timer = QTimer(self)
        connect_signal(self._timer.timeout, self._on_timeout)

        self._elapsed = 0
        self._start_position = 0
        self._start_width = 0
        self._target_position = 0
        self._target_width = 0

        self._step_callback: Optional[StepCallback] = None
        self._complete_callback: CompleteCallback = None

    def animate(
        self,
        *,
        current_position: int,
        current_width: int,
        target_position: int,
        target_width: int,
        on_step: StepCallback,
        on_complete: CompleteCallback = None,
    ) -> None:
        """Animate from current values to target values."""
        if self._timer.isActive():
            self._timer.stop()

        self._elapsed = 0
        self._start_position = current_position
        self._start_width = current_width
        self._target_position = target_position
        self._target_width = target_width
        self._step_callback = on_step
        self._complete_callback = on_complete

        if current_position == target_position and current_width == target_width:
            self._emit_step(target_position, target_width)
            self._emit_complete(target_position, target_width)
            return

        self._emit_step(current_position, current_width)
        self._timer.start(self._frame_interval)

    def stop(self) -> None:
        """Stop any active animation."""
        if self._timer.isActive():
            self._timer.stop()

    def _on_timeout(self) -> None:
        self._elapsed += self._frame_interval
        progress = min(self._elapsed / self._duration, 1.0)

        next_position = self._lerp(self._start_position, self._target_position, progress)
        next_width = self._lerp(self._start_width, self._target_width, progress)

        self._emit_step(next_position, next_width)

        if progress >= 1.0:
            self._timer.stop()
            self._emit_complete(self._target_position, self._target_width)

    def _emit_step(self, position: int, width: int) -> None:
        if self._step_callback:
            self._step_callback(int(position), int(width))

    def _emit_complete(self, position: int, width: int) -> None:
        if self._complete_callback:
            self._complete_callback(int(position), int(width))

    @staticmethod
    def _lerp(start: int, end: int, progress: float) -> int:
        return int(start + (end - start) * progress)


