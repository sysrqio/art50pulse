from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Violation:
    code: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "severity": self.severity}
