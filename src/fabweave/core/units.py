from __future__ import annotations

import math


def finite_non_negative(value: float, label: str = "value") -> float:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be finite and non-negative")
    return value


def ppm_to_fraction(ppm: float) -> float:
    return finite_non_negative(ppm, "ppm") / 1_000_000.0


def fraction_to_ppm(value: float) -> float:
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("fraction outside range")
    return value * 1_000_000.0
