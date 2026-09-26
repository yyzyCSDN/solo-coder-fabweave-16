from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True, slots=True)
class TimeBox:
    """A half-open interval used by every scheduling domain."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("end must exceed start")

    @property
    def duration(self) -> int:
        return self.end - self.start

    def overlaps(self, other: "TimeBox") -> bool:
        return self.start < other.end and other.start < self.end

    def contains(self, instant: int) -> bool:
        return self.start <= instant < self.end

    def intersection(self, other: "TimeBox") -> "TimeBox | None":
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return TimeBox(start, end) if start < end else None


def merge_timeboxes(intervals: list[TimeBox]) -> list[TimeBox]:
    """Merge overlapping or touching intervals without double-counting time."""

    merged: list[TimeBox] = []
    for current in sorted(intervals):
        if not merged or merged[-1].end < current.start:
            merged.append(current)
            continue
        previous = merged[-1]
        merged[-1] = TimeBox(previous.start, max(previous.end, current.end))
    return merged


def covered_duration(intervals: list[TimeBox], within: TimeBox) -> int:
    clipped = [part for interval in intervals if (part := interval.intersection(within))]
    return sum(interval.duration for interval in merge_timeboxes(clipped))
