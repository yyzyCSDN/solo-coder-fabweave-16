from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.decision import Decision, allow, deny


def authorize(rework_count: int, max_reworks: int, defect_code: str, allowed_codes: set[str]) -> bool:
    return rework_count >= 0 and max_reworks >= 0 and rework_count < max_reworks and defect_code in allowed_codes


@dataclass(frozen=True, slots=True)
class ReworkPolicy:
    revision: int
    limits_by_operation: dict[str, int]
    allowed_defects: frozenset[str]
    requires_engineer: frozenset[str] = frozenset()


def authorization_decision(
    policy: ReworkPolicy,
    operation: str,
    prior_reworks: int,
    defect_code: str,
    engineer_approval: str | None,
) -> Decision:
    reasons: list[str] = []
    limit = policy.limits_by_operation.get(operation)
    if limit is None:
        reasons.append("operation_not_covered")
    elif prior_reworks >= limit:
        reasons.append("rework_limit_exhausted")
    if defect_code not in policy.allowed_defects:
        reasons.append("defect_not_authorized")
    if defect_code in policy.requires_engineer and not engineer_approval:
        reasons.append("engineer_approval_missing")
    evidence = {"policy_revision": policy.revision, "prior_reworks": prior_reworks}
    return deny(*reasons, **evidence) if reasons else allow(**evidence)
