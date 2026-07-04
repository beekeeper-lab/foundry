"""Cost-summary helpers shared by the media generators.

The image and audio generators each carry their OWN cost tables (the rates
differ by provider and model). This module deliberately holds NO cost data;
it only provides the shape-agnostic helpers — lookup-with-fallback and
per-run summary formatting — so both generators format costs the same way.
"""

from __future__ import annotations

from typing import Mapping, TypeVar

__all__ = [
    "lookup_cost",
    "format_cost_summary",
    "summarize_run",
]

K = TypeVar("K")


def lookup_cost(table: Mapping[K, float], key: K, default: float = 0.0) -> float:
    """Return ``table[key]`` if present, else ``default``.

    A thin wrapper that gives both generators a single place to log/handle
    a missing rate. Callers can subclass the behavior by passing a custom
    default (e.g. ``float("nan")``) when they want missing rates to surface
    rather than silently zero out.
    """
    return table.get(key, default) if hasattr(table, "get") else default


def format_cost_summary(per_item_costs: list[float], label: str = "items") -> str:
    """Return a one-line summary like ``"42 items, total $5.46"``.

    The dollar amount is rounded to two decimals. An empty list yields
    ``"0 <label>, total $0.00"``.
    """
    total = sum(per_item_costs)
    return f"{len(per_item_costs)} {label}, total ${total:.2f}"


def summarize_run(
    per_item_costs: list[float],
    label: str = "items",
    *,
    average: bool = False,
) -> str:
    """One-line summary with optional per-item average.

    With ``average=False`` (the default) returns the same string as
    :func:`format_cost_summary`. With ``average=True`` appends the average
    cost per item, e.g. ``"42 items, total $5.46 (avg $0.13)"``. An empty
    list omits the average (no division by zero).
    """
    base = format_cost_summary(per_item_costs, label)
    if not average or not per_item_costs:
        return base
    avg = sum(per_item_costs) / len(per_item_costs)
    return f"{base} (avg ${avg:.2f})"
