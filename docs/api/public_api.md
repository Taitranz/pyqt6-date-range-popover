# Public API Surface

The objects documented in this file represent the supported, stable surface
area of `date_range_popover`. Everything else (managers, widgets, coordinators,
validators, etc.) is considered internal and can change without notice.
Breaking changes to the sections below follow semantic versioning once the
package reaches `v1.0.0`.

## Stability Contract

- Import only from the package root (`date_range_popover`) or the modules listed
  here.
- Signals, methods, and properties that are not documented should be treated as
  internal helpers.
- All guarantees apply to releases `>= 1.0.0`. Pre-release builds may change
  without deprecation.
- Deprecation timelines and expectations are documented in
  [`docs/api/deprecation_policy.md`](docs/api/deprecation_policy.md).

## Versioned Behavior Guarantees

The following behaviors are contractually guaranteed beginning with `v0.1.0` and
apply to all future releases unless a formal deprecation has been announced.

- `selected_range` is always either `None` or a normalized `DateRange` whose
  `start_date <= end_date`.
- `DatePickerStateManager` clamps every selection attempt to `[min_date, max_date]`
  and raises `InvalidDateError` when the bounds are violated.
- `DatePickerConfig` replaces a missing `max_date` with `QDate.currentDate()`,
  ensuring future dates remain disabled by default.
- `DateRangePopover` never mutates `DatePickerConfig` instances passed to it;
  treat configs as immutable snapshots.
- All Qt signals (`date_selected`, `range_selected`, `cancelled`) fire on the UI
  thread and emit defensive copies of `QDate`/`DateRange`.
- Mode transitions are idempotent; reassigning the active mode to its current value
  does not emit duplicate signals.
- Theme validation rejects invalid hex codes and zero/negative dimensions before any
  widgets are instantiated.

## `DateRangePopover` / `DateRangePicker`

- **Location:** `from date_range_popover import DateRangePopover, DateRangePicker`
- **Purpose:** Turn-key widgets that expose a minimal embedding surface.
- **Stable members:**
  - Properties: `selected_date`, `selected_range`
  - Methods: `set_mode(mode: PickerMode)`, `reset()`, `cleanup()`
  - Qt signals: `date_selected(QDate)`, `range_selected(DateRange)`,
    `cancelled()`
- **Guarantees:**
  - `selected_date` returns an invalid `QDate` when no single-date selection
    exists; otherwise it is clamped to `[min_date, max_date]`.
  - `selected_range` always has `start <= end` when both endpoints are present.
  - Signals emit on the Qt GUI thread in the following order:
    1. `date_selected` / `range_selected`
    2. `cancelled` (for dismissals)
  - `reset()` restores the initial configuration without creating a new widget.
  - Methods must be invoked on the Qt GUI thread.

## `DatePickerConfig`

- **Location:** `from date_range_popover import DatePickerConfig`
- **Purpose:** Validated configuration object consumed by the picker widgets.
- **Stable fields:**
  - Layout: `width`, `height`, `theme`
  - Selection defaults: `initial_date`, `initial_range`, `mode`
  - Bounds: `min_date`, `max_date`
  - Time controls: `time_step_minutes`
- **Guarantees:**
  - `max_date` defaults to `QDate.currentDate()` when omitted.
  - `initial_range` and `initial_date` are clamped to `[min_date, max_date]`.
  - Instantiating with invalid values raises `InvalidConfigurationError`.

## `DateRange`

- **Location:** `from date_range_popover import DateRange`
- **Purpose:** Immutable container used by signals and configs.
- **Stable attributes:** `start_date`, `end_date`, `start_time`, `end_time`
- **Guarantees:**
  - When both endpoints exist, `start_date <= end_date`.
  - Time values are either both valid `QTime` instances or `None`.
  - Instances are safe to cache; they never return references to internal state.

## `PickerMode`

- **Location:** `from date_range_popover import PickerMode`
- **Values:** `PickerMode.DATE`, `PickerMode.CUSTOM_RANGE`
- **Guarantees:** Additional modes may be added in minor releases, but existing
  enum values will not change or be removed without deprecation.

## Behavior Guarantees

- `range_selected` always emits a fully normalized `DateRange` with defensive
  copies of `QDate` objects.
- The state manager clamps every selection to the configured bounds. Invalid
  inputs raise `InvalidDateError`.
- `DateRangePopover` never mutates `DatePickerConfig` instances passed to the
  constructor; treat configs as immutable.
- The library does not spawn threads; all callbacks and signals fire on the Qt
  GUI thread.
- Deprecation notices remain in place for at least two minor releases; see the
  dedicated deprecation policy for migration expectations.

## Non-Guaranteed / Internal Modules

The following areas are internal and subject to change between releases:

- `date_range_popover.components.*`
- `date_range_popover.managers.*`
- `date_range_popover.utils.*`
- `date_range_popover.styles.*`
- `date_range_popover.validation.*`

Rely on them only if you are prepared to vendor or fork the library.


