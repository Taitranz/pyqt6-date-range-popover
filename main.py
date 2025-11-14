"""
Legacy entry point for running the basic popover demo.

Prefer invoking ``python -m examples.basic_popover_demo`` so the README can link
to a stable module path. This file simply proxies to that module to avoid
breaking existing workflows while still giving downstream projects a simple way
to embed the widget via ``python -m date_range_popover`` when prototyping.
"""

from examples.basic_popover_demo import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
