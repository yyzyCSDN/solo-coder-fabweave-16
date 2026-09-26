from __future__ import annotations


def incompatible_pairs(classes: set[str], matrix: dict[str, set[str]]) -> tuple[tuple[str, str], ...]:
    pairs: set[tuple[str, str]] = set()
    for left in classes:
        for right in classes:
            if left >= right:
                continue
            if right in matrix.get(left, set()) or left in matrix.get(right, set()):
                pairs.add((left, right))
    return tuple(sorted(pairs))


def compatible(classes: set[str], matrix: dict[str, set[str]]) -> bool:
    return not incompatible_pairs(classes, matrix)


def sequence_compatible(
    previous_classes: set[str],
    incoming_classes: set[str],
    matrix: dict[str, set[str]],
    cleaning_removes: set[str] | None = None,
) -> bool:
    residual = previous_classes - (cleaning_removes or set())
    return compatible(residual | incoming_classes, matrix)
