from __future__ import annotations

import math


def western_electric_rules(values: list[float], center: float, sigma: float) -> tuple[str, ...]:
    if sigma <= 0 or not math.isfinite(sigma) or not math.isfinite(center):
        raise ValueError("center and sigma must be finite; sigma must be positive")
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("SPC values must be finite and non-empty")
    rules: list[str] = []
    if any(abs(value - center) > 3 * sigma for value in values):
        rules.append("one_beyond_3_sigma")
    if len(values) >= 3:
        tail = values[-3:]
        above = sum(value - center > 2 * sigma for value in tail)
        below = sum(center - value > 2 * sigma for value in tail)
        if above >= 2 or below >= 2:
            rules.append("two_of_three_beyond_2_sigma_same_side")
    if len(values) >= 5:
        tail = values[-5:]
        above = sum(value - center > sigma for value in tail)
        below = sum(center - value > sigma for value in tail)
        if above >= 4 or below >= 4:
            rules.append("four_of_five_beyond_1_sigma_same_side")
    return tuple(rules)


def western_electric_signal(values: list[float], center: float, sigma: float) -> bool:
    return bool(western_electric_rules(values, center, sigma))
