from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.decision import Decision, allow, deny
from fabweave.core.timebox import TimeBox, merge_timeboxes


def remaining_minutes(max_minutes: float, elapsed_minutes: float, paused_minutes: float = 0.0) -> float:
    if min(max_minutes, elapsed_minutes, paused_minutes) < 0:
        raise ValueError("minutes must be non-negative")
    effective = max(0.0, elapsed_minutes - min(paused_minutes, elapsed_minutes))
    return max_minutes - effective


def breached(max_minutes: float, elapsed_minutes: float, paused_minutes: float = 0.0) -> bool:
    return remaining_minutes(max_minutes, elapsed_minutes, paused_minutes) < 0


@dataclass(frozen=True, slots=True)
class QueueLimit:
    route_step: str
    max_minutes: int
    revision: int

    def __post_init__(self) -> None:
        if self.max_minutes <= 0 or self.revision <= 0:
            raise ValueError("queue limit and revision must be positive")


def queue_time_decision(
    limit: QueueLimit,
    entered_at: int,
    evaluated_at: int,
    authorized_pauses: list[TimeBox],
) -> Decision:
    if evaluated_at < entered_at:
        return deny("evaluation_precedes_entry", limit_revision=limit.revision)

    elapsed = evaluated_at - entered_at
    if elapsed == 0:
        effective_pauses: list[TimeBox] = []
    else:
        window = TimeBox(entered_at, evaluated_at)
        # Replays may append the very same TimeBox more than once, and
        # separately recorded pauses may overlap. Clip to the queue window
        # first and merge before measuring, so every covered minute is
        # counted at most once.
        clipped = [part for pause in authorized_pauses if (part := pause.intersection(window))]
        effective_pauses = merge_timeboxes(clipped)
    paused = sum(interval.duration for interval in effective_pauses)

    remaining = remaining_minutes(limit.max_minutes, elapsed, paused)
    evidence = {
        "route_step": limit.route_step,
        "limit_revision": limit.revision,
        "entered_at": entered_at,
        "evaluated_at": evaluated_at,
        "max_minutes": limit.max_minutes,
        "elapsed_minutes": elapsed,
        "paused_minutes": paused,
        "remaining_minutes": remaining,
        "pause_windows": tuple((interval.start, interval.end) for interval in effective_pauses),
    }
    return deny("queue_time_breached", **evidence) if remaining < 0 else allow(**evidence)
