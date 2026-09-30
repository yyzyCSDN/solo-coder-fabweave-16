from __future__ import annotations

from fabweave.core.decision import Decision, allow, deny
from fabweave.core.timebox import TimeBox, covered_duration, merge_timeboxes


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


def shelf_life_decision(
    opened_at: int,
    shelf_hours: int,
    evaluated_at: int,
    frozen_periods: list[TimeBox],
) -> Decision:
    """Evaluate chemical shelf life from its own freeze records.

    Freeze periods are a chemical-specific clock source: queue-time pauses
    must never be passed here. Periods are clipped to the storage window and
    merged so replays and overlaps cannot subtract aging twice.
    """
    if shelf_hours < 0:
        raise ValueError("negative shelf life")
    if evaluated_at < opened_at:
        return deny("evaluation_precedes_opening", opened_at=opened_at, evaluated_at=evaluated_at)

    if evaluated_at == opened_at:
        effective_freezes: list[TimeBox] = []
    else:
        storage = TimeBox(opened_at, evaluated_at)
        clipped = [part for period in frozen_periods if (part := period.intersection(storage))]
        effective_freezes = merge_timeboxes(clipped)
    frozen_hours = sum(interval.duration for interval in effective_freezes)
    age = (evaluated_at - opened_at) - frozen_hours
    remaining = shelf_hours - age
    evidence = {
        "opened_at": opened_at,
        "evaluated_at": evaluated_at,
        "shelf_hours": shelf_hours,
        "age_hours": age,
        "frozen_hours": frozen_hours,
        "remaining_shelf_hours": remaining,
        "freeze_windows": tuple((interval.start, interval.end) for interval in effective_freezes),
    }
    return deny("chemical_shelf_life_expired", **evidence) if remaining < 0 else allow(**evidence)
