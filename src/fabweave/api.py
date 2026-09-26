from __future__ import annotations
from .dispatch.priority import dispatch_score
from .yielding.rollup import geometric_yield

def health() -> dict[str, str]:
    return {"status": "ok", "service": "fabweave"}

def demo_snapshot() -> dict[str, float | str]:
    return {
        "service": "fabweave",
        "dispatch_score": round(dispatch_score(12.0, 8.0, 1.5, 0.25), 4),
        "yield": round(geometric_yield([0.98, 0.97, 0.995]), 6),
    }
