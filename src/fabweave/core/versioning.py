from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Revision(Generic[T]):
    version: int
    effective_at: int
    value: T


class RevisionHistory(Generic[T]):
    def __init__(self) -> None:
        self._revisions: list[Revision[T]] = []

    def publish(self, version: int, effective_at: int, value: T) -> Revision[T]:
        if version <= 0:
            raise ValueError("version must be positive")
        if self._revisions:
            last = self._revisions[-1]
            if version <= last.version or effective_at < last.effective_at:
                raise ValueError("revision history must move forward")
        revision = Revision(version, effective_at, deepcopy(value))
        self._revisions.append(revision)
        return deepcopy(revision)

    def at(self, instant: int) -> Revision[T]:
        matches = [revision for revision in self._revisions if revision.effective_at <= instant]
        if not matches:
            raise LookupError("no revision was effective at that time")
        return deepcopy(matches[-1])

    def latest(self) -> Revision[T]:
        if not self._revisions:
            raise LookupError("no revisions published")
        return deepcopy(self._revisions[-1])
