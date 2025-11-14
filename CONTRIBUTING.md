# Contributing

Thanks for helping improve `date_range_popover`! This guide describes how to set
up a development environment, run the quality gates, and submit changes.

## Maintenance cadence

I am not actively iterating on the project, so issues and pull requests may sit for
longer than usual. Please keep contributions focused and self-contained so they’re
easier to review when I can make time.

## Requirements

- Python 3.10 – 3.13
- Pip + virtualenv (recommended)
- System packages required by PyQt6 (on Ubuntu: `sudo apt-get install libxcb-xinerama0`)

## Environment Setup

```bash
git clone https://github.com/Taitranz/pyqt6-date-range-popover.git
cd pyqt6-date-range-popover
python -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -e ".[test,dev,docs]"
```

## Daily Workflow

```bash
# Lint & format
ruff check .
black .

# Type-check (strict mode)
mypy date_range_popover

# Tests + coverage (fail_under=90 via coverage config)
pytest --maxfail=1 --disable-warnings \
  --cov=date_range_popover \
  --cov-report=term-missing \
  --cov-report=xml

# Build the documentation site
mkdocs build --strict
```

CI mirrors these steps across Python 3.10–3.13 and PyQt6 6.5–6.7, so matching
the commands locally prevents surprises.

## Coding Standards

- Use Black (line length 100) and Ruff (rules E,F,W,I,UP).
- Public APIs must include docstrings with Args/Returns/Raises info.
- Keep pure logic in `date_range_popover/core/state_logic.py` when possible.
- New behaviour requires unit tests; regression/Qt tests live under `tests/unit`
  and `tests/qt`.

## Submitting Changes

1. Fork the repository & create a feature branch.
2. Make your changes + update docs if behaviour is user-visible.
3. Ensure all commands in the workflow above succeed.
4. Open a pull request describing motivation, testing, and any follow-up work.

Please open an issue first if you plan to add a large feature so we can discuss
scope and integration strategy. Thanks!

