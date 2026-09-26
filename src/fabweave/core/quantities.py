from __future__ import annotations

from collections.abc import Mapping


def require_non_negative(quantities: Mapping[str, int]) -> None:
    invalid = sorted(name for name, value in quantities.items() if not isinstance(value, int) or value < 0)
    if invalid:
        raise ValueError(f"invalid quantities: {', '.join(invalid)}")


def require_conservation(before: Mapping[str, int], after: Mapping[str, int]) -> None:
    require_non_negative(before)
    require_non_negative(after)
    if sum(before.values()) != sum(after.values()):
        raise ValueError("quantity conservation violated")
