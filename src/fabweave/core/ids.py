from __future__ import annotations

import hashlib
import re


PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]{2,31}$")


def validate_id(value: str) -> str:
    if not PATTERN.fullmatch(value):
        raise ValueError("invalid identifier")
    return value


def deterministic_id(prefix: str, *parts: object, length: int = 12) -> str:
    validate_id(prefix)
    if not 8 <= length <= 32:
        raise ValueError("identifier digest length outside supported range")
    material = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()[:length].upper()
    return f"{prefix}-{digest}"
