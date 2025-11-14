# Roadmap & Design Notes

This page captures upcoming ideas, open questions, and constraints that guide
the evolution of `date_range_popover`. It is aspirational—items ship when they
have owners.

## Near-Term

- **Keyboard navigation & accessibility**: expose a11y roles on calendar cells,
  add arrow-key navigation, and document focus order.
- **Time-aware mode**: extend `PickerMode` with a time-inclusive variant so
  range selection can optionally require start/end times.
- **Theme import/export**: allow serialising palettes/layouts to JSON/YAML and
  add CLI helpers for generating starter themes.
- **More tests**: add Qt screenshot regression tests for high-DPI and RTL
  layouts, plus fuzzing for configuration validators.

## Medium-Term

- **Multiple calendar systems**: abstract `QDate` usage so alternate calendars
  (ISO week, fiscal calendars, etc.) can plug in.
- **Animation strategy injection**: swap the slide indicator animation with
  easing curves or disabled animations for accessibility.
- **State-machine visualiser**: ship a developer overlay that shows the current
  `DatePickerState` to simplify debugging embedder issues.
- **Plugin registry**: document a convention for discovering theme providers and
  selection callbacks via entry points (useful for larger apps).

## Long-Term / Research

- **Cross-toolkit frontends**: leverage the pure `core/state_logic` module to
  drive frontends in other UI frameworks (Tkinter, React via Pyodide, etc.).
- **Internationalisation**: integrate Qt's translation system so labels/month
  names come from `.qm` files rather than hard-coded strings.
- **Async state coordination**: explore asyncio-friendly state managers so the
  picker can live inside hybrid desktop/web runtimes.

## Not Planned (Yet)

- Building a scheduling/timeline UI (this component stays focused on popovers).
- Supporting legacy Python versions (<3.10).
- Shipping compiled resources; assets remain as SVGs for now.

Have an idea that's not listed? Open an issue so we can capture it here.

