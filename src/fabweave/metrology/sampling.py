from __future__ import annotations

from dataclasses import dataclass


def sample_indices(lot_size: int, sample_count: int) -> list[int]:
    if lot_size <= 0 or sample_count <= 0:
        raise ValueError("positive sizes required")
    n = min(lot_size, sample_count)
    if n == 1:
        return [0]
    return [round(index * (lot_size - 1) / (n - 1)) for index in range(n)]


@dataclass(frozen=True, slots=True)
class Wafer:
    wafer_id: str
    slot: int
    zone: str
    eligible: bool = True


def deterministic_sample(wafers: list[Wafer], sample_count: int, required_zones: set[str]) -> tuple[Wafer, ...]:
    if sample_count <= 0:
        raise ValueError("sample count must be positive")
    eligible = sorted((wafer for wafer in wafers if wafer.eligible), key=lambda wafer: (wafer.slot, wafer.wafer_id))
    zones = {wafer.zone for wafer in eligible}
    missing = required_zones - zones
    if missing:
        raise ValueError(f"required zones unavailable: {', '.join(sorted(missing))}")
    if sample_count < len(required_zones):
        raise ValueError("sample count cannot cover required zones")
    chosen: list[Wafer] = []
    for zone in sorted(required_zones):
        candidates = [wafer for wafer in eligible if wafer.zone == zone]
        chosen.append(candidates[len(candidates) // 2])
    remaining = [wafer for wafer in eligible if wafer not in chosen]
    needed = min(sample_count, len(eligible)) - len(chosen)
    if needed > 0:
        for index in sample_indices(len(remaining), needed):
            chosen.append(remaining[index])
    return tuple(sorted(chosen, key=lambda wafer: (wafer.slot, wafer.wafer_id)))
