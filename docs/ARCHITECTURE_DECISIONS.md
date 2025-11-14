# Architecture Decisions

This appendix records the most impactful design choices that shape
`date_range_popover`. The intent is to make trade-offs explicit so future
maintainers (or consumers) understand why things look the way they do.

## 1. Pure State Manager (2024-01-10)

- **Decision:** Keep all selection logic in `date_range_popover.core.state_logic`
  and drive it via `DatePickerStateManager`.
- **Why:** PyQt widgets are difficult to test in isolation. Separating state
  transitions into a pure module enables deterministic unit tests and clears the
  path for future non-Qt frontends.
- **Trade-offs:** Slightly more indirection inside coordinators, but it pays off
  with property tests and reusable validation helpers.

## 2. Data-Driven Theming (2024-01-18)

- **Decision:** Represent themes as immutable dataclasses (palette + layout) and
  feed them into a `StyleRegistry`.
- **Why:** Desktop apps frequently need branded widgets. Keeping colors and
  dimensions declarative lets hosts load themes from files or factories without
  rewriting widgets.
- **Trade-offs:** More boilerplate when adding new palette tokens, but the
  strong typing prevents subtle style mismatches.

## 3. Qt Signals + Callback Layer (2024-02-02)

- **Decision:** Expose Qt signals (`date_selected`, `range_selected`) as the
  canonical integration surface, but also ship a Python callback dispatcher.
- **Why:** Qt users expect signals, while other ecosystems prefer pure-Python
  callbacks. Supporting both keeps the public API small and future-proofs the
  component for non-Qt consumers.
- **Trade-offs:** `SelectionSnapshot` introduces a tiny amount of duplication,
  but the ergonomic win outweighs it.

## 4. Strict Validation by Default (2024-02-15)

- **Decision:** Clamp every config value (dates, dimensions, colors) during
  construction and fail fast with descriptive exceptions.
- **Why:** Host applications can feed partially trusted data into the picker
  without writing bespoke sanitizers. It also makes CI quality gates meaningful.
- **Trade-offs:** Slightly longer construction time, but still `O(1)` and worth
  the guarantees.

## 5. Reduced Motion Friendly Animations (2024-03-05)

- **Decision:** Keep the sliding-track animation isolated behind an
  `AnimationStrategy` protocol so hosts can swap in reduced-motion strategies.
- **Why:** Accessibility requirements vary; providing a documented seam makes it
  trivial to disable or customise animations.
- **Trade-offs:** Coordinators need one more dependency (`set_sliding_track_animator`),
  but swapping animations is now a single-line change.

