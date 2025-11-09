from __future__ import annotations

import warnings
from typing import Optional

from PyQt6.QtWidgets import QWidget

from .api.config import DatePickerConfig
from .api.picker import DateRangePicker


class DateRangePickerMenu(DateRangePicker):
    """Deprecated wrapper around :class:`DateRangePicker` for backwards compatibility."""

    def __init__(
        self,
        config: Optional[DatePickerConfig] = None,
        parent: QWidget | None = None,
    ) -> None:
        warnings.warn(
            "DateRangePickerMenu is deprecated. Use date_range_picker.api.DateRangePicker instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(config=config, parent=parent)

