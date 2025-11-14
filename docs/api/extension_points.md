# Extension Points

This document enumerates the supported hooks for extending `date_range_popover`
without vendoring the entire library. Anything listed here is considered stable
for releases `>= 0.1.0`. Internal modules not referenced here can change at any
time.

## Theme Providers

- Implement the [`ThemeProvider`](../styles/theme.py) protocol to lazily load
  palettes/layouts (for example, from JSON, YAML, or a database).
- Pass the provider into `StyleRegistry` or `StyleManager.use_theme()` and the
  picker will resolve the underlying `Theme` on demand.
- See `examples/custom_theme_demo.py` for two concrete implementations.

## Style Registry Variants

- `StyleRegistry.register_button_style`, `register_calendar_style`, and
  `register_input_style` let you add named style variants that can be activated
  at runtime.
- `StyleManager.apply_*` helpers accept variant names (`primary`, `accent`,
  `ghost`, etc.) and propagate them to widgets. Custom variants can use any
  string identifier.

## Selection Callbacks

- `DateRangePicker.register_selection_callback` accepts callables conforming to
  the [`SelectionCallback`](../types/selection.py) protocol. Each callback receives
  a `SelectionSnapshot` describing the current state.
- Callbacks fire synchronously on the Qt GUI thread. Keep handlers short-lived or
  offload work to background threads.
- For richer observer APIs, wrap the Qt signals once (see
  `examples/extension_hooks_demo.py`) and fan out to your own plugin surface.

## Animation Strategies

- The [`AnimationStrategy`](../animation/slide_animator.py) protocol describes the
  contract for sliding-track animations.
- Swap in your own implementation (e.g., easing curves, reduced motion) and pass
  it to the coordinator via `set_sliding_track_animator`.

## Coordinator Hooks

- `DatePickerCoordinator` exposes registration methods for the button strip,
  calendar, date-time selector, and sliding track. Embedders can swap widgets so
  long as they match the expected interfaces.
- The coordinator also exposes `handle_calendar_selection`, `switch_mode`, and
  `select_date` helpers for advanced embedding scenarios.

## Configuration Sanitizers

- Validation helpers under `date_range_popover.validation` (e.g.,
  `validate_hex_color`, `validate_dimension`) are public so hosting apps can
  reuse the exact same sanitisation logic when accepting user input.

## Roadmap for Future Hooks

- The architecture keeps the core state logic Qt-free, making it feasible to
  add alternate frontends (Tkinter, web-based) without rewriting validation or
  selection invariants.
- If you need a hook not listed here, open an issue—promoting new extension
  points is much easier than maintaining a fork.

