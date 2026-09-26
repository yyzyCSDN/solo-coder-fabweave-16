from __future__ import annotations

from dataclasses import dataclass


def geometric_yield(step_yields: list[float]) -> float:
    result = 1.0
    for value in step_yields:
        if not 0.0 <= value <= 1.0:
            raise ValueError("yield outside [0,1]")
        result *= value
    return result


@dataclass(frozen=True, slots=True)
class StepYield:
    step: str
    input_units: int
    good_units: int

    def __post_init__(self) -> None:
        if self.input_units <= 0 or not 0 <= self.good_units <= self.input_units:
            raise ValueError("invalid step quantities")

    @property
    def fraction(self) -> float:
        return self.good_units / self.input_units


def route_yield(steps: list[StepYield], expected_steps: list[str]) -> float:
    by_step: dict[str, StepYield] = {}
    for step in steps:
        if step.step in by_step:
            raise ValueError("duplicate step yield")
        by_step[step.step] = step
    missing = [step for step in expected_steps if step not in by_step]
    extra = sorted(set(by_step) - set(expected_steps))
    if missing or extra:
        raise ValueError(f"route step mismatch: missing={missing}, extra={extra}")
    return geometric_yield([by_step[step].fraction for step in expected_steps])
