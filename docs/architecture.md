# Architecture & Design Notes

The picker separates pure state management from Qt widgets so the core logic
can be tested and reused independent of the GUI layer.

## High-Level Flow

1. **State Manager (`DatePickerStateManager`)** keeps the canonical selection
   state, clamps values to `[min_date, max_date]`, and exposes granular signals.
2. **Coordinator** listens to state changes and updates UI components (button
   strip, calendar, date/time inputs).
3. **Widgets** render the state and forward user input back through the
   coordinator.

This creates a predictable loop:

```
User input -> Coordinator -> State manager -> Signals -> Widgets
```

## Pure Logic vs GUI Modules

- **Pure Python**: `date_range_popover.core.state_logic`, `date_range_popover.utils.*`,
  and validation helpers. These modules never import Qt widgets and can be unit
  tested in headless environments.
- **GUI Modules**: Components under `date_range_popover.components.*`,
  animators, and the popover widget. They depend on PyQt6 for rendering.

Keeping logic isolated enables property-based tests (see
`tests/properties/test_invariants.py`) and makes it feasible to drive a future
non-Qt frontend from the same state/validation layer.

## Theming & Styling

`Theme` combines a `ColorPalette` and `LayoutConfig`. The palette validates every
hex string, while the layout clamps numeric values via `validate_dimension`.
`StyleRegistry` converts those tokens into widget-specific style objects, and
`StyleManager` applies them to widgets at runtime. Registering a new palette
or layout does not require touching widget code.

## Picker Modes

`PickerMode` currently defines two values:

- `DATE` – single-date selection with a compact layout.
- `CUSTOM_RANGE` – dual-date inputs plus additional actions.

Switching modes triggers a sliding indicator animation (`SlideAnimator`) and
resizes the popover to pre-defined heights, but the state manager retains the
underlying selection so users can bounce between modes without losing progress.

## Signals & Threading

All signals fire on the Qt GUI thread. The library does not spawn background
threads, so embedder code can safely mutate UI state inside signal handlers as
long as it adheres to Qt's threading rules.

## Extension Points

Upcoming documentation in `docs/extending.md` will cover:

- Registering custom themes and palettes.
- Hooking into range selection via callbacks in addition to Qt signals.
- Replacing calendar renderers while reusing the state manager.

If you plan to depend on internals, prefer filing an issue so we can discuss
promoting new hooks to the supported surface.

