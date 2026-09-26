from __future__ import annotations

from collections import defaultdict

from fabweave.core.units import finite_non_negative


def coincident_peak(loads: list[tuple[int, float]], window: int) -> float:
    if window <= 0:
        raise ValueError("window must be positive")
    grouped: dict[int, float] = defaultdict(float)
    for timestamp, value in loads:
        grouped[timestamp] += finite_non_negative(value, "load")
    ordered = sorted(grouped.items())
    best = 0.0
    left = 0
    total = 0.0
    for timestamp, value in ordered:
        total += value
        while left < len(ordered) and timestamp - ordered[left][0] >= window:
            total -= ordered[left][1]
            left += 1
        best = max(best, total)
    return best


def demand_violations(loads: list[tuple[int, float]], windows: list[tuple[int, float]]) -> tuple[int, ...]:
    violations = []
    for width, limit in windows:
        if coincident_peak(loads, width) > finite_non_negative(limit, "demand limit"):
            violations.append(width)
    return tuple(sorted(violations))
