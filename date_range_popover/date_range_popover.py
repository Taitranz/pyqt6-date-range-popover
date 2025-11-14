from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from .api.config import DatePickerConfig
from .api.picker import DateRangePicker


class DateRangePopover(DateRangePicker):
    """
    Turn-key widget that wraps :class:`DateRangePicker` for embedding.

    Importing :class:`DateRangePopover` keeps application code terse; it
    exposes the same public API as :class:`DateRangePicker` but ships with
    a default configuration. That makes it handy for quick experiments and
    demos. Pass a pre-sanitised :class:`DatePickerConfig` so constraints
    (min/max dates, layout bounds, themes) stay explicit at construction
    time.

    Example:
        >>> popover = DateRangePopover()
        >>> popover.range_selected.connect(lambda r: print(r.start_date, r.end_date))
        >>> popover.show()
    """

    def __init__(
        self,
        config: DatePickerConfig | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the popover using the provided configuration and optional parent.

        :param config: Optional :class:`DatePickerConfig`. Falls back to
            defaults.
        :param parent: Parent widget responsible for lifetime management.
        """
        super().__init__(config=config, parent=parent)


__all__ = ["DateRangePopover"]
