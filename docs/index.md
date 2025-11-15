# Date Range Popover

`date_range_popover` packages a production-ready PySide6 date & range picker that
drops cleanly into data-entry tools and internal desktop apps.

## Quick Start

```bash
pip install valgo-date-range-popover
python -m examples.basic_popover_demo
```

To embed the widget in your application:

```python
from PySide6.QtWidgets import QApplication
from date_range_popover import DatePickerConfig, DateRangePopover, PickerMode

app = QApplication([])
config = DatePickerConfig(mode=PickerMode.DATE)
popover = DateRangePopover(config=config)
popover.show()
app.exec()
```

## Documentation Map

- [Architecture](architecture.md) explains the state manager, coordination
  layer, and theming system.
- [Embedding Guide](embedding.md) shows how to configure the picker and wire it
  into host applications.
- [Public Surface](api/public_api.md) enumerates the officially supported API.
- [Python Reference](api/reference.md) is generated from docstrings using
  `mkdocstrings`.

## Support Matrix

- Python 3.10 â€“ 3.13
- PySide6 6.5 â€“ 6.10
- Linux, macOS, and Windows targets (Qt handles windowing differences).

Report issues or start discussions on
[GitHub](https://github.com/Taitranz/PySide6-Date-Range-Popover).


