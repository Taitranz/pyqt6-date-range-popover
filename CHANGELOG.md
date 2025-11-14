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

### Tests
- Broadened property/edge-case coverage for `DatePickerConfig`, `Theme`, and core validators.

## [0.1.0] - 2024-06-01

### Added
- Initial public release of the PyQt6 date range popover, including the picker widgets,
  state manager, theming system, and demo application.


