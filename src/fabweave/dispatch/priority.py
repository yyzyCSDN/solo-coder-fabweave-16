from __future__ import annotations

import math
from dataclasses import dataclass


def dispatch_score(hours_to_due: float, remaining_steps: float, hold_risk: float, setup_penalty: float) -> float:
    values = (hours_to_due, remaining_steps, hold_risk, setup_penalty)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("dispatch inputs must be finite")
    if remaining_steps <= 0:
        raise ValueError("remaining steps must be positive")
    urgency = 1.0 / max(hours_to_due, 0.25)
    flow = 1.0 / remaining_steps
    return 4.0 * urgency + 1.5 * flow + hold_risk - setup_penalty


@dataclass(frozen=True, slots=True)
class DispatchCandidate:
    lot_id: str
    hours_to_due: float
    remaining_steps: int
    hold_risk: float = 0.0
    setup_penalty: float = 0.0
    active_hold: bool = False
    frozen_until: int | None = None


def rank_candidates(candidates: list[DispatchCandidate], now: int) -> list[DispatchCandidate]:
    eligible = [
        candidate
        for candidate in candidates
        if not candidate.active_hold and (candidate.frozen_until is None or candidate.frozen_until <= now)
    ]
    return sorted(
        eligible,
        key=lambda candidate: (
            -dispatch_score(
                candidate.hours_to_due,
                candidate.remaining_steps,
                candidate.hold_risk,
                candidate.setup_penalty,
            ),
            candidate.lot_id,
        ),
    )
