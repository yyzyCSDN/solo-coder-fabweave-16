from __future__ import annotations


def excursion_periods(readings: list[tuple[int, float]], limit: float, min_consecutive: int) -> list[tuple[int, int]]:
    if min_consecutive <= 0:
        raise ValueError("min_consecutive must be positive")
    by_time: dict[int, float] = {}
    for timestamp, value in readings:
        previous = by_time.get(timestamp)
        if previous is not None and previous != value:
            raise ValueError("conflicting readings at the same event time")
        by_time[timestamp] = value
    ordered = sorted(by_time.items())
    out: list[tuple[int, int]] = []
    start: int | None = None
    count = 0
    for timestamp, value in ordered:
        if value > limit:
            start = timestamp if start is None else start
            count += 1
            continue
        if count >= min_consecutive and start is not None:
            out.append((start, timestamp))
        start = None
        count = 0
    if count >= min_consecutive and start is not None:
        out.append((start, ordered[-1][0]))
    return out


def active_excursion(
    readings: list[tuple[int, float]],
    open_limit: float,
    close_limit: float,
    required_open: int,
    required_close: int,
) -> bool:
    if close_limit > open_limit or min(required_open, required_close) <= 0:
        raise ValueError("invalid hysteresis policy")
    active = False
    run = 0
    for _, value in sorted(readings):
        if not active:
            run = run + 1 if value > open_limit else 0
            if run >= required_open:
                active, run = True, 0
        else:
            run = run + 1 if value <= close_limit else 0
            if run >= required_close:
                active, run = False, 0
    return active
