"""Protocol definitions for Qt signals used throughout the picker."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, ParamSpec, Protocol, TypeAlias

from PyQt6.QtCore import QDate

P = ParamSpec("P")


class SignalProtocol(Protocol, Generic[P]):
    """Generic protocol describing the ``connect`` signature of PyQt signals."""

    def connect(self, slot: Callable[P, None]) -> object: ...


VoidSignal: TypeAlias = SignalProtocol[[]]
DateSignal: TypeAlias = SignalProtocol[[QDate]]
RangeSignal: TypeAlias = SignalProtocol[[QDate, QDate]]
IntSignal: TypeAlias = SignalProtocol[[int]]
StrSignal: TypeAlias = SignalProtocol[[str]]


if TYPE_CHECKING:
    from ..managers.state_manager import PickerMode
else:  # pragma: no cover - runtime fallback to avoid circular imports

    class PickerMode:  # noqa: D401 - runtime stub
        """Lightweight stand-in for ``PickerMode`` during runtime import cycles."""

        pass


ModeSignal: TypeAlias = SignalProtocol[[PickerMode]]


__all__ = [
    "SignalProtocol",
    "VoidSignal",
    "DateSignal",
    "RangeSignal",
    "ModeSignal",
    "IntSignal",
    "StrSignal",
]
