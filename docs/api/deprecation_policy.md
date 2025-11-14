# Deprecation Policy

This document clarifies how the `date_range_popover` project introduces,
communicates, and ultimately removes breaking changes so embedders can plan
upgrades with confidence.

## Versioning Model

- The project follows [Semantic Versioning](https://semver.org). Breaking API
  changes only occur in major releases (`vX.0.0`).
- Minor releases (`vX.Y.0`) may introduce new functionality but never remove or
  silently change documented behavior.
- Patch releases (`vX.Y.Z`) contain only bug fixes and documentation updates.

## Deprecation Timeline

1. **Announcement** – Deprecated APIs are documented in the changelog, README,
   and relevant docs with guidance on preferred alternatives.
2. **Warning Period** – The existing implementation continues to work for **at
   least two minor releases** while emitting a `DeprecationWarning`.
3. **Removal** – The API is removed in the next major release after the warning
   window closes.

Example:

- `v1.2.0` introduces a new API and marks the older method as deprecated.
- `v1.3.x` retains the deprecated method but continues to emit warnings.
- `v2.0.0` removes the deprecated method.

## Warning Mechanics

Use standard library warnings to surface upcoming removals without interrupting
host applications:

```python
import warnings

def legacy_method(*args, **kwargs):
    warnings.warn(
        "legacy_method() is deprecated and will be removed in v2.0.0; "
        "use modern_method() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return modern_method(*args, **kwargs)
```

## Documentation Requirements

Every deprecation must include:

- A changelog entry with the first release that introduced the warning.
- Updated API references noting the replacement and removal timeline.
- Inline docstrings that mention the deprecation and link to migration guidance.

## Guarantee Scope

Versioned behavior guarantees (see `docs/api/public_api.md`) remain valid unless
a deprecation notice states otherwise. Internal modules may evolve without
notice, but any object listed in the public API reference follows this policy.

