from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from PyQt6.QtCore import QDate

from ..api.config import DateRange
from ..managers.state_manager import PickerMode


@dataclass(frozen=True, slots=True)
class SelectionSnapshot:
    """
    Lightweight struct describing the current selection state.

    Attributes:
        mode: Active picker mode.
        selected_date: Earliest selected date or ``None`` when no selection exists.
        selected_range: Normalized :class:`DateRange` representing the current
            selection. ``None`` when nothing is selected.
    """

    mode: PickerMode
    selected_date: QDate | None
    selected_range: DateRange | None


@runtime_checkable
class SelectionCallback(Protocol):
    """Protocol describing callbacks invoked when selections change."""

    def __call__(self, snapshot: SelectionSnapshot) -> None: ...


__all__ = ["SelectionSnapshot", "SelectionCallback"]
