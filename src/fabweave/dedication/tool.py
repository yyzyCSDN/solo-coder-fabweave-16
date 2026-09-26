from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.decision import Decision, allow, deny


def tool_allowed(product: str, tool: str, dedicated: dict[str, set[str]], blocked: set[tuple[str, str]]) -> bool:
    if (product, tool) in blocked:
        return False
    return product not in dedicated or tool in dedicated[product]


@dataclass(frozen=True, slots=True)
class DedicationPolicy:
    revision: int
    effective_at: int
    allowed: dict[str, frozenset[str]]
    blocked: frozenset[tuple[str, str]] = frozenset()


def policy_decision(product: str, tool: str, at: int, policies: list[DedicationPolicy]) -> Decision:
    active = [policy for policy in policies if policy.effective_at <= at]
    if not active:
        return deny("dedication_policy_missing")
    policy = max(active, key=lambda item: (item.effective_at, item.revision))
    evidence = {"policy_revision": policy.revision, "effective_at": policy.effective_at}
    if (product, tool) in policy.blocked:
        return deny("product_tool_explicitly_blocked", **evidence)
    permitted = policy.allowed.get(product)
    if permitted is not None and tool not in permitted:
        return deny("tool_not_in_dedication_allow_list", **evidence)
    return allow(**evidence)
