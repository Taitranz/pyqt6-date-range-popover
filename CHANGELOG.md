# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Codecov uploads in CI with a live coverage badge in the README.
- Additional picker mode regression tests covering multi-hop transitions.
- Expanded invalid configuration tests for dimensions, theme payloads, and time steps.

### Fixed
- Tightened theme validation to ensure invalid mapping payloads bubble up with clear errors.
- Pinned the runtime dependency to `PyQt6<6.7` to avoid upstream Qt 6.7 symbol
  loading failures on Linux runners (`_ZN5QFont11tagToStringEj`).

### Tests
- Broadened property/edge-case coverage for `DatePickerConfig`, `Theme`, and core validators.
- CI matrix now targets PyQt 6.5.x and 6.6.x while 6.7.x wheels remain unstable on linux.
- Removed the `PyQt6-Qt6-OpenGL` reinstall step in CI because no wheels exist for the pinned PyQt6 versions.
- Regression tests skip the popover `show()` cycle when ``QT_QPA_PLATFORM=offscreen`` to avoid PyQt headless crashes while still exercising the behavior locally.
- Re-enabled PyQt 6.7.x coverage (using 6.7.1+) now that the upstream Qt symbol issue is fixed.

## [0.1.0] - 2024-06-01

### Added
- Initial public release of the PyQt6 date range popover, including the picker widgets,
  state manager, theming system, and demo application.


