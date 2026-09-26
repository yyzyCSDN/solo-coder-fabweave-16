from __future__ import annotations

from dataclasses import dataclass

from fabweave.core.ids import deterministic_id
from fabweave.core.quantities import require_conservation


def mergeable(a: dict[str, str | int], b: dict[str, str | int]) -> bool:
    keys = ("product", "route", "step", "recipe_rev")
    return all(a.get(key) == b.get(key) for key in keys) and a.get("hold", 0) == 0 and b.get("hold", 0) == 0


@dataclass(frozen=True, slots=True)
class Lot:
    lot_id: str
    product: str
    route: str
    step: str
    recipe_revision: int
    quantity: int
    active_holds: frozenset[str] = frozenset()


def merge_lots(request_id: str, lots: list[Lot]) -> Lot:
    if len(lots) < 2:
        raise ValueError("at least two lots are required")
    if len({lot.lot_id for lot in lots}) != len(lots):
        raise ValueError("the same lot cannot be merged twice")
    first = lots[0]
    identity = (first.product, first.route, first.step, first.recipe_revision)
    if any((lot.product, lot.route, lot.step, lot.recipe_revision) != identity for lot in lots):
        raise ValueError("lot route metadata differs")
    if any(lot.active_holds for lot in lots):
        raise ValueError("held lots cannot merge")
    before = {lot.lot_id: lot.quantity for lot in lots}
    after = {"merged": sum(before.values())}
    require_conservation(before, after)
    merged_id = deterministic_id("LOT", request_id, *(sorted(before)))
    return Lot(merged_id, *identity, after["merged"])
