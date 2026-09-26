from __future__ import annotations

from fabweave.core.timebox import TimeBox, covered_duration


def usable(opened_at: int, shelf_hours: int, now: int, frozen_hours: int = 0) -> bool:
    if shelf_hours < 0 or frozen_hours < 0 or now < opened_at:
        raise ValueError("invalid duration")
    effective_age = max(0, now - opened_at - min(frozen_hours, now - opened_at))
    return effective_age <= shelf_hours


def effective_age(opened_at: int, evaluated_at: int, frozen_periods: list[TimeBox]) -> int:
    if evaluated_at < opened_at:
        raise ValueError("evaluation precedes opening")
    if evaluated_at == opened_at:
        return 0
    storage = TimeBox(opened_at, evaluated_at)
    frozen = covered_duration(frozen_periods, storage)
    return storage.duration - frozen


def shelf_life_remaining(
    opened_at: int,
    shelf_hours: int,
    evaluated_at: int,
    frozen_periods: list[TimeBox],
) -> int:
    if shelf_hours < 0:
        raise ValueError("negative shelf life")
    return shelf_hours - effective_age(opened_at, evaluated_at, frozen_periods)
