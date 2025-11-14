"""Utilities for connecting PyQt signals while preserving type information."""

from __future__ import annotations

from typing import Callable, ParamSpec, cast

from ..types.signals import SignalProtocol

P = ParamSpec("P")


def connect_signal(signal: object, slot: Callable[P, None]) -> object:
    """Connect ``slot`` to ``signal`` and return the Qt connection handle."""
    bound_signal = cast(SignalProtocol[P], signal)
    return bound_signal.connect(slot)


def connect_if_present(signal: object | None, slot: Callable[P, None]) -> object | None:
    """Connect ``slot`` only when ``signal`` is not ``None``."""
    if signal is None:
        return None
    return connect_signal(signal, slot)


__all__ = ["connect_signal", "connect_if_present"]


