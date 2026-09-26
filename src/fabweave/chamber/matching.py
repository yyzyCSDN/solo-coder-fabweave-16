from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.units import finite_non_negative


def matched(reference: dict[str, float], candidate: dict[str, float], tolerances: dict[str, float]) -> bool:
    return not mismatch_reasons(reference, candidate, {key: Tolerance(absolute=value) for key, value in tolerances.items()})


@dataclass(frozen=True, slots=True)
class Tolerance:
    absolute: float = 0.0
    relative: float = 0.0

    def __post_init__(self) -> None:
        finite_non_negative(self.absolute, "absolute tolerance")
        finite_non_negative(self.relative, "relative tolerance")


def mismatch_reasons(
    reference: dict[str, float],
    candidate: dict[str, float],
    tolerances: dict[str, Tolerance],
) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, tolerance in sorted(tolerances.items()):
        if key not in reference or key not in candidate:
            reasons.append(f"{key}:missing")
            continue
        expected, actual = reference[key], candidate[key]
        try:
            finite_non_negative(expected, f"{key} reference")
            finite_non_negative(actual, f"{key} candidate")
        except ValueError:
            reasons.append(f"{key}:non_finite_or_negative")
            continue
        limit = max(tolerance.absolute, abs(expected) * tolerance.relative)
        if abs(expected - actual) > limit:
            reasons.append(f"{key}:outside_tolerance")
    return tuple(reasons)
