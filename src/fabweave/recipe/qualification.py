from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.decision import Decision, allow, deny


def recipe_allowed(required_rev: int, tool_revs: set[int], expires_at: int, now: int) -> bool:
    return now <= expires_at and required_rev in tool_revs


@dataclass(frozen=True, slots=True)
class Qualification:
    tool_id: str
    chamber_id: str
    recipe_revision: int
    qualified_at: int
    expires_at: int
    revoked_at: int | None = None

    def active_at(self, instant: int) -> bool:
        return (
            self.qualified_at <= instant <= self.expires_at
            and (self.revoked_at is None or instant < self.revoked_at)
        )


def qualification_decision(
    tool_id: str,
    chamber_id: str,
    recipe_revision: int,
    at: int,
    qualifications: list[Qualification],
) -> Decision:
    candidates = [
        item
        for item in qualifications
        if item.tool_id == tool_id
        and item.chamber_id == chamber_id
        and item.recipe_revision == recipe_revision
    ]
    if not candidates:
        return deny("qualification_missing", recipe_revision=recipe_revision)
    active = [item for item in candidates if item.active_at(at)]
    if not active:
        return deny("qualification_inactive", recipe_revision=recipe_revision)
    chosen = max(active, key=lambda item: (item.qualified_at, item.expires_at))
    return allow(recipe_revision=chosen.recipe_revision, qualified_at=chosen.qualified_at, expires_at=chosen.expires_at)
