"""Property-based invariants for the date range picker."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Final

import pytest
from date_range_popover.api.config import DateRange
from date_range_popover.managers.state_manager import DatePickerStateManager
from date_range_popover.utils import first_of_month
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import DrawFn
from PyQt6.QtCore import QDate

pytestmark = pytest.mark.usefixtures("qapp")


def _to_qdate(value: date) -> QDate:
    """Convert ``datetime.date`` to ``QDate``."""
    return QDate(value.year, value.month, value.day)


@given(
    start=st.dates(min_value=date(2020, 1, 1), max_value=date(2035, 12, 31)),
    end=st.dates(min_value=date(2020, 1, 1), max_value=date(2035, 12, 31)),
)
def test_date_range_normalizes_start_and_end(start: date, end: date) -> None:
    """DateRange should always normalize ordering of endpoints."""
    candidate = DateRange(start_date=_to_qdate(start), end_date=_to_qdate(end))
    assert candidate.start_date is not None
    assert candidate.end_date is not None
    assert candidate.start_date <= candidate.end_date


@dataclass(frozen=True)
class Action:
    """Simple instruction used to drive the state manager."""

    kind: str
    primary_offset: int
    secondary_offset: int | None = None


def _build_select_date(offset: int) -> Action:
    return Action("select_date", offset)


def _build_select_range(start_offset: int, end_offset: int) -> Action:
    return Action("select_range", start_offset, end_offset)


def _build_visible_month(offset: int) -> Action:
    return Action("set_visible_month", offset)


def _action_strategy(span_days: int) -> st.SearchStrategy[Action]:
    """Build a strategy that emits selection/visibility operations."""
    max_offset: Final[int] = max(0, span_days)
    offsets = st.integers(min_value=0, max_value=max_offset)
    return st.one_of(
        st.builds(_build_select_date, offsets),
        st.builds(_build_select_range, offsets, offsets),
        st.builds(_build_visible_month, offsets),
    )


@st.composite
def manager_scenarios(draw: DrawFn) -> tuple[QDate, QDate, list[Action]]:
    """Generate min/max bounds plus a sequence of actions to run."""
    min_py: date = draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2035, 1, 1)))
    span_days: int = draw(st.integers(min_value=5, max_value=120))
    max_py: date = min_py + timedelta(days=span_days)
    min_q: QDate = _to_qdate(min_py)
    max_q: QDate = _to_qdate(max_py)
    action_count: int = draw(st.integers(min_value=1, max_value=15))
    actions: list[Action] = draw(
        st.lists(_action_strategy(span_days), min_size=action_count, max_size=action_count)
    )
    return min_q, max_q, actions


@given(manager_scenarios())
def test_state_manager_actions_preserve_bounds(
    scenario: tuple[QDate, QDate, Iterable[Action]],
) -> None:
    """After arbitrary sequences, selected dates and visible month stay within bounds."""
    min_date, max_date, actions = scenario
    manager = DatePickerStateManager(min_date=min_date, max_date=max_date)
    min_month = first_of_month(min_date)
    max_month = first_of_month(max_date)
    for action in actions:
        candidate = min_date.addDays(action.primary_offset)
        if action.kind == "select_date":
            manager.select_date(candidate)
        elif action.kind == "set_visible_month":
            manager.set_visible_month(candidate)
        else:
            secondary_offset = (
                action.secondary_offset
                if action.secondary_offset is not None
                else action.primary_offset
            )
            other = min_date.addDays(secondary_offset)
            manager.select_range(candidate, other)

        start, end = manager.state.selected_dates
        if start is not None:
            assert min_date <= start <= max_date
        if end is not None:
            assert min_date <= end <= max_date
        visible_month = manager.state.visible_month
        assert min_month <= visible_month <= max_month
