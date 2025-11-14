from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import QDate, QTime

from ..exceptions import InvalidConfigurationError
from ..managers.state_manager import PickerMode
from ..styles.theme import LayoutConfig, Theme
from ..validation import validate_date_range, validate_dimension, validate_qdate

_DEFAULT_LAYOUT = LayoutConfig()


@dataclass(slots=True)
class DateRange:
    """
    Immutable date/time container shared across the public API.

    The dataclass validates its inputs eagerly so host applications can rely
    on a fully normalized range when they receive it via picker signals.
    Dates are sanitised with
    :func:`date_range_popover.validation.validate_date_range` while time
    values are checked for ``QTime.isValid``. ``None`` values are preserved
    so callers can intentionally pass open ranges.

    Args:
        start_date: Inclusive start of the range (``None`` for an open range).
        end_date: Inclusive end of the range (``None`` for an open range).
        start_time: Optional time paired with ``start_date``.
        end_time: Optional time paired with ``end_date``.

    Raises:
        InvalidConfigurationError: If any ``QDate`` or ``QTime`` value is
            invalid or if ``start_date`` is after ``end_date``.

    Example:
        >>> from PyQt6.QtCore import QDate
        >>> DateRange(
        ...     start_date=QDate(2024, 1, 1),
        ...     end_date=QDate(2024, 1, 10),
        ... )
    """

    start_date: QDate | None = None
    end_date: QDate | None = None
    start_time: QTime | None = None
    end_time: QTime | None = None

    def __post_init__(self) -> None:
        """Normalise and validate date/time fields immediately after creation."""
        self.start_date, self.end_date = validate_date_range(
            self.start_date,
            self.end_date,
            field_name="initial_range",
        )
        self._validate_time(self.start_time, "start_time")
        self._validate_time(self.end_time, "end_time")

    @staticmethod
    def _validate_time(value: QTime | None, field_name: str) -> None:
        """
        Ensure the provided ``QTime`` instance is valid.

        :param value: ``QTime`` candidate that may be ``None``.
        :param field_name: Friendly field label for error reporting.
        :raises InvalidConfigurationError: If the ``QTime`` is provided but
            invalid.
        """
        if value is None:
            return
        if not value.isValid():
            raise InvalidConfigurationError(f"{field_name} is not a valid time: {value}")


@dataclass(slots=True)
class DatePickerConfig:
    """
    Canonical configuration object consumed by :class:`DateRangePicker`.

    The dataclass performs defensive sanitisation in ``__post_init__`` so
    embedding contexts can accept partially trusted input (for example,
    values entered in another widget) and still end up with a predictable
    picker. All numeric dimensions are clamped via :func:`validate_dimension`,
    all dates flow through :func:`validate_qdate`, and ranges are validated
    by :func:`validate_date_range`.

    Args:
        width: Fixed window width in pixels.
        height: Fixed window height in ``DATE`` mode.
        theme: Theme object containing palette and layout tokens.
        initial_date: Single-date default selection.
        initial_range: Pre-selected range that overrides ``initial_date``.
        mode: Initial :class:`PickerMode` (``DATE`` or ``CUSTOM_RANGE``).
        min_date: Absolute lower bound for selection/navigation.
        max_date: Absolute upper bound for selection/navigation. Defaults to
            ``QDate.currentDate()`` when omitted to prevent future selections.
        time_step_minutes: Step interval for the time selector component.

    Raises:
        InvalidConfigurationError: For any inconsistent value (dimensions out of
            bounds, ``min_date > max_date``, invalid ``Theme`` instances, etc.).

    Example:
        >>> from PyQt6.QtCore import QDate
        >>> DatePickerConfig(
        ...     mode=PickerMode.CUSTOM_RANGE,
        ...     min_date=QDate(2023, 1, 1),
        ...     max_date=QDate(2024, 12, 31),
        ... )
    """

    width: int = _DEFAULT_LAYOUT.window_min_width
    height: int = _DEFAULT_LAYOUT.window_min_height
    theme: Theme = field(default_factory=Theme)
    initial_date: QDate | None = None
    initial_range: DateRange | None = None
    mode: PickerMode = PickerMode.DATE
    min_date: QDate | None = None
    max_date: QDate | None = None
    time_step_minutes: int = 15

    def __post_init__(self) -> None:
        """
        Clamp and validate configuration values.

        Host applications frequently build ``DatePickerConfig`` instances
        from external inputs (API payloads, settings files, etc.). This
        lifecycle hook ensures all derived values are deterministic before
        the widget reads them, which significantly reduces the amount of
        manual sanitisation embedding contexts need to write.
        """
        self.width = validate_dimension(
            self.width,
            field_name="width",
            min_value=_DEFAULT_LAYOUT.window_min_width,
        )
        self.height = validate_dimension(
            self.height,
            field_name="height",
            min_value=_DEFAULT_LAYOUT.window_min_height,
        )
        self.time_step_minutes = validate_dimension(
            self.time_step_minutes,
            field_name="time_step_minutes",
            min_value=1,
            max_value=60,
        )
        self.initial_date = validate_qdate(
            self.initial_date, field_name="initial_date", allow_none=True
        )
        candidate_range = object.__getattribute__(self, "initial_range")
        if candidate_range is not None and not isinstance(candidate_range, DateRange):
            raise InvalidConfigurationError("initial_range must be a DateRange instance")
        mode_value = object.__getattribute__(self, "mode")
        if not isinstance(mode_value, PickerMode):
            raise InvalidConfigurationError("mode must be an instance of PickerMode")
        theme_value = object.__getattribute__(self, "theme")
        if not isinstance(theme_value, Theme):
            raise InvalidConfigurationError("theme must be an instance of Theme")
        self.min_date = validate_qdate(self.min_date, field_name="min_date", allow_none=True)
        max_candidate = validate_qdate(self.max_date, field_name="max_date", allow_none=True)
        self.max_date = max_candidate or QDate.currentDate()
        if self.min_date is not None and self.min_date > self.max_date:
            raise InvalidConfigurationError("min_date must be on or before max_date")
        if self.initial_date is not None:
            self._ensure_within_bounds(self.initial_date, "initial_date")
        if self.initial_range is not None:
            if self.initial_range.start_date is not None:
                self._ensure_within_bounds(
                    self.initial_range.start_date, "initial_range.start_date"
                )
            if self.initial_range.end_date is not None:
                self._ensure_within_bounds(self.initial_range.end_date, "initial_range.end_date")

    def _ensure_within_bounds(self, date: QDate, field_name: str) -> None:
        """
        Confirm that ``date`` respects the configured ``min_date`` and
        ``max_date`` values.

        :param date: Candidate ``QDate``.
        :param field_name: Friendly name that appears in exception messages.
        :raises InvalidConfigurationError: If the date is outside the bounds.
        """
        if self.min_date is not None and date < self.min_date:
            raise InvalidConfigurationError(f"{field_name} must be on or after min_date")
        if self.max_date is not None and date > self.max_date:
            raise InvalidConfigurationError(f"{field_name} must be on or before max_date")


__all__ = ["DatePickerConfig", "DateRange", "PickerMode"]
