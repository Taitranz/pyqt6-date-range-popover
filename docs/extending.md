# Extending the Picker

The library exposes several hooks so you can tailor the picker without forking
the codebase.

## Custom Themes

Build a theme from JSON/YAML and pass it to `DatePickerConfig`:

```python
import json
from date_range_popover.styles.theme import theme_from_mapping

payload = json.load(open("theme.json", "r", encoding="utf-8"))
custom_theme = theme_from_mapping(payload)

config = DatePickerConfig(theme=custom_theme)
```

For dynamic themes, implement the `ThemeProvider` protocol:

```python
from dataclasses import dataclass
from date_range_popover.styles.theme import Theme, ThemeProvider

@dataclass
class FileThemeProvider(ThemeProvider):
    path: str

    def build_theme(self) -> Theme:
        return theme_from_mapping(json.load(open(self.path, "r", encoding="utf-8")))

registry = StyleRegistry(theme=FileThemeProvider("dark.json"))
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

Qt signals remain the primary integration point, but you can also register
Python callables that receive `SelectionSnapshot` objects:

```python
from date_range_popover.types.selection import SelectionSnapshot

def log_selection(snapshot: SelectionSnapshot) -> None:
    print("Mode:", snapshot.mode.name, "Range:", snapshot.selected_range)

picker.register_selection_callback(log_selection)
```

Callbacks fire synchronously on the Qt GUI thread, so keep handlers lightweight.
Unregister them with `deregister_selection_callback`.

## Future Hooks

The architecture keeps state management Qt-free, which enables future extension
points such as:

- Swapping calendar renderers while reusing the state manager.
- Plugging in alternative animation strategies.
- Serialising themes to/from remote sources.

File an issue if you need a specific hook; promoting it to the supported surface
is usually easier than maintaining a fork.

