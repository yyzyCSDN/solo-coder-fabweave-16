from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Decision:
    allowed: bool
    reasons: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.allowed and self.reasons:
            raise ValueError("an allowed decision cannot contain rejection reasons")
        if not self.allowed and not self.reasons:
            raise ValueError("a rejected decision requires at least one reason")
        object.__setattr__(self, "evidence", MappingProxyType(dict(self.evidence)))


def allow(**evidence: Any) -> Decision:
    return Decision(True, evidence=evidence)


def deny(*reasons: str, **evidence: Any) -> Decision:
    unique = tuple(dict.fromkeys(reason for reason in reasons if reason))
    return Decision(False, unique, evidence)
