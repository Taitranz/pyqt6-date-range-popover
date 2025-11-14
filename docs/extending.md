# Extending the Picker

The library exposes several hooks so you can tailor the picker without forking
the codebase.

## Custom Themes

Custom palettes/layouts let you brand the picker without touching the widget
code. Two common approaches:

1. **Static Python definition** – great for themes embedded directly in source
   control:

   ```python
   from date_range_popover import DatePickerConfig
   from date_range_popover.styles.theme import ColorPalette, LayoutConfig, Theme

   ACCENT_THEME = Theme(
       palette=ColorPalette(
           window_background="#101820",
           track_indicator_color="#f2aa4c",
           calendar_today_background="#f2aa4c",
       ),
       layout=LayoutConfig(window_min_width=360, action_button_height=52),
   )

   config = DatePickerConfig(theme=ACCENT_THEME)
   ```

2. **Data-driven themes** – load palettes/layouts from JSON/YAML so they can be
   tweaked without code changes:

   ```python
   import json
   from date_range_popover.styles.theme import theme_from_mapping

   payload = json.load(open("theme.json", "r", encoding="utf-8"))
   custom_theme = theme_from_mapping(payload)
   config = DatePickerConfig(theme=custom_theme)
   ```

The [`examples/custom_theme_demo.py`](../examples/custom_theme_demo.py) script
renders two themes side-by-side (accent dark + pastel light) to illustrate how
palette/layout swaps ripple through the UI.

For dynamic themes, implement the `ThemeProvider` protocol—useful when themes
are supplied by plugins or remote endpoints:

```python
from dataclasses import dataclass
from date_range_popover.styles.theme import Theme, ThemeProvider, theme_from_mapping

@dataclass
class FileThemeProvider(ThemeProvider):
    path: str

    def build_theme(self) -> Theme:
        with open(self.path, "r", encoding="utf-8") as handle:
            return theme_from_mapping(json.load(handle))
```

## Style Variants

`StyleRegistry` exposes `register_button_style`, `register_calendar_style`, and
`register_input_style` so you can inject additional presets at runtime:

```python
registry = StyleRegistry()
registry.register_button_style("danger", ButtonStyleConfig(...))
style_manager = StyleManager(registry)
style_manager.apply_basic_button(button, variant="danger")
```

## Selection Callbacks

Qt signals remain the primary integration point, but you can layer additional
observer interfaces on top of them to align with your application's plugin
surface.

`DateRangePopover` exposes a `register_selection_callback` method that accepts
callables receiving a `SelectionSnapshot`:

```python
from date_range_popover.types.selection import SelectionSnapshot

def log_selection(snapshot: SelectionSnapshot) -> None:
    print("Mode:", snapshot.mode.name, "Range:", snapshot.selected_range)

popover.register_selection_callback(log_selection)
```

Callbacks fire synchronously on the Qt GUI thread, so keep handlers lightweight.
Unregister them with `deregister_selection_callback`.

### Building Custom Dispatchers

When you need a richer observer API (e.g., to mirror existing extension hooks)
wrap the Qt signals once and fan out updates yourself. See
[`examples/extension_hooks_demo.py`](../examples/extension_hooks_demo.py) for a
complete dispatcher + observer implementation:

```python
class SelectionObserver(Protocol):
    def on_single_date(self, date: QDate) -> None: ...
    def on_range(self, date_range: DateRange) -> None: ...

dispatcher = SelectionDispatcher()
dispatcher.bind(popover)          # Wire Qt signals once
dispatcher.register(ConsoleObserver())  # Fan-out to arbitrary callbacks
```

This pattern keeps picker internals untouched while still presenting a
domain-specific API to the rest of your application.

## Future Hooks

The architecture keeps state management Qt-free, which enables future extension
points such as:

- Swapping calendar renderers while reusing the state manager.
- Plugging in alternative animation strategies.
- Serialising themes to/from remote sources.

File an issue if you need a specific hook; promoting it to the supported surface
is usually easier than maintaining a fork.

### Design Rationale

- **Pure state logic** lives in `date_range_popover.core.state_logic`, making it
  trivial to test or port to another UI framework.
- **Style isolation** keeps palette/layout data separate from widgets so themes
  can be swapped dynamically (see the demo linked above).
- **Signal indirection** ensures you can layer the dispatcher pattern without
  subclassing Qt widgets.

