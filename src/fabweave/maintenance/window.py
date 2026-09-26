from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.decision import Decision, allow, deny
from fabweave.core.timebox import TimeBox


def maintenance_due(last_pm_hour: float, interval_hours: float, run_hours: float, calendar_hour: float) -> bool:
    if interval_hours <= 0 or min(last_pm_hour, run_hours, calendar_hour) < 0:
        raise ValueError("maintenance clocks must be valid")
    elapsed_calendar = max(0.0, calendar_hour - last_pm_hour)
    return max(run_hours, elapsed_calendar) >= interval_hours


@dataclass(frozen=True, slots=True)
class MaintenancePolicy:
    revision: int
    run_interval: float
    calendar_interval: float

    def __post_init__(self) -> None:
        if self.revision <= 0 or min(self.run_interval, self.calendar_interval) <= 0:
            raise ValueError("invalid maintenance policy")


def assignment_decision(
    policy: MaintenancePolicy,
    last_pm_at: float,
    accumulated_run_hours: float,
    now: int,
    job_window: TimeBox,
    planned_maintenance: list[TimeBox],
) -> Decision:
    reasons: list[str] = []
    if accumulated_run_hours >= policy.run_interval:
        reasons.append("run_hour_maintenance_due")
    if now - last_pm_at >= policy.calendar_interval:
        reasons.append("calendar_maintenance_due")
    if any(window.overlaps(job_window) for window in planned_maintenance):
        reasons.append("planned_maintenance_overlap")
    evidence = {"policy_revision": policy.revision, "job_start": job_window.start, "job_end": job_window.end}
    return deny(*reasons, **evidence) if reasons else allow(**evidence)
