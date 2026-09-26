from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.decision import Decision, allow, deny


def releasable(required: set[str], completed: set[str], active_blockers: set[str]) -> bool:
    return not active_blockers and required.issubset(completed)


@dataclass(frozen=True, slots=True)
class HoldState:
    hold_id: str
    version: int
    required_dispositions: frozenset[str]
    completed_dispositions: frozenset[str] = frozenset()
    active_blockers: frozenset[str] = frozenset()
    released_at: int | None = None


def release_decision(state: HoldState, expected_version: int, at: int) -> Decision:
    if expected_version != state.version:
        return deny("stale_hold_version", current_version=state.version)
    if state.released_at is not None:
        return allow(hold_version=state.version, released_at=state.released_at, replay=True)
    missing = sorted(state.required_dispositions - state.completed_dispositions)
    reasons = [*(f"missing_disposition:{item}" for item in missing), *(f"active_blocker:{item}" for item in sorted(state.active_blockers))]
    evidence = {"hold_version": state.version, "evaluated_at": at}
    return deny(*reasons, **evidence) if reasons else allow(**evidence)
