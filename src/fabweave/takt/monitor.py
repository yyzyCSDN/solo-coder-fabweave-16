from __future__ import annotations

from dataclasses import dataclass


def rolling_takt(completions: list[int], window_start: int, window_end: int) -> float | None:
    if window_end <= window_start:
        raise ValueError("invalid takt window")
    timestamps = sorted(set(time for time in completions if window_start <= time <= window_end))
    if len(timestamps) < 2:
        return None
    return (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)


@dataclass(frozen=True, slots=True)
class TaktResult:
    takt: float | None
    completion_count: int
    interval_count: int
    duplicate_count: int


def takt_result(completions: list[int], window_start: int, window_end: int) -> TaktResult:
    selected = [time for time in completions if window_start <= time <= window_end]
    unique = sorted(set(selected))
    takt = rolling_takt(unique, window_start, window_end)
    return TaktResult(takt, len(unique), max(0, len(unique) - 1), len(selected) - len(unique))
