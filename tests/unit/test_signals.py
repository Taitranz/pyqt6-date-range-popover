"""Tests for signal connection helpers."""

from __future__ import annotations

from collections.abc import Callable

from date_range_popover.utils.signals import connect_if_present, connect_signal


class DummySignal:
    """Minimal stand-in that mimics the PyQt connect API."""

    def __init__(self) -> None:
        self._slots: list[Callable[[], None]] = []

    def connect(self, slot: Callable[[], None]) -> Callable[[], None]:
        self._slots.append(slot)
        return slot

    @property
    def slots(self) -> list[Callable[[], None]]:
        return self._slots


def test_connect_signal_invokes_underlying_connect() -> None:
    """connect_signal should delegate to the underlying signal."""
    signal = DummySignal()

    def slot() -> None:
        return None

    handle = connect_signal(signal, slot)

    assert handle is slot
    assert signal.slots == [slot]


def test_connect_if_present_returns_none_when_signal_missing() -> None:
    """connect_if_present should short-circuit when signal is None."""
    assert connect_if_present(None, lambda: None) is None

    signal = DummySignal()

    def slot() -> None:
        return None

    handle = connect_if_present(signal, slot)
    assert handle is slot
    assert signal.slots == [slot]
