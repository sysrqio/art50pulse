"""Art. 50(2) machine-readable marking heuristics (C2PA JUMBF / c2pa markers)."""

from __future__ import annotations

from pathlib import Path

from art50pulse.audit.types import Violation

_C2PA_MARKERS = (b"jumb", b"c2pa", b"contentauth")


def scan_media_file(path: Path, *, require_c2pa: bool) -> list[Violation]:
    if not require_c2pa:
        return []
    data = path.read_bytes()
    if any(marker in data for marker in _C2PA_MARKERS):
        return []
    return [
        Violation(
            code="MISSING_C2PA_MANIFEST",
            message=(
                f"{path}: no C2PA/JUMBF marker detected in binary (Art. 50(2) machine-readable marking)."
            ),
        )
    ]
