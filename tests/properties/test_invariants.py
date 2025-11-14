"""Property-based invariants for the date range picker."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta

import pytest
from date_range_popover.api.config import DateRange
from date_range_popover.managers.state_manager import DatePickerStateManager
from date_range_popover.utils import first_of_month
from hypothesis import given
from hypothesis import strategies as st
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


def _action_strategy(span_days: int) -> st.SearchStrategy[Action]:
    """Build a strategy that emits selection/visibility operations."""
    offsets = st.integers(min_value=0, max_value=max(0, span_days))
    return st.one_of(
        st.builds(lambda value: Action("select_date", value), offsets),
        st.builds(lambda start, end: Action("select_range", start, end), offsets, offsets),
        st.builds(lambda value: Action("set_visible_month", value), offsets),
    )


@st.composite
def manager_scenarios(draw) -> tuple[QDate, QDate, Iterable[Action]]:
    """Generate min/max bounds plus a sequence of actions to run."""
    min_py = draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2035, 1, 1)))
    span_days = draw(st.integers(min_value=5, max_value=120))
    max_py = min_py + timedelta(days=span_days)
    min_q = _to_qdate(min_py)
    max_q = _to_qdate(max_py)
    action_count = draw(st.integers(min_value=1, max_value=15))
    actions = draw(
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
