"""Rule engine for Article 50 transparency checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from art50pulse.audit.html_scan import scan_html
from art50pulse.audit.media_scan import scan_media_file
from art50pulse.audit.types import Violation


@dataclass
class AuditReport:
    ok: bool
    violations: list[Violation] = field(default_factory=list)
    scanned_at: str = ""
    targets: list[str] = field(default_factory=list)
    tool_version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": "art50pulse",
            "version": self.tool_version,
            "scanned_at": self.scanned_at,
            "targets": self.targets,
            "policy_violations": [v.to_dict() for v in self.violations],
            "ok": self.ok,
        }


def run_audit(
    *,
    html_paths: list[Path] | None = None,
    media_paths: list[Path] | None = None,
    require_c2pa: bool = False,
    version: str = "0.1.0",
) -> AuditReport:
    violations: list[Violation] = []
    targets: list[str] = []

    for path in html_paths or []:
        targets.append(str(path))
        violations.extend(scan_html(path.read_text(encoding="utf-8", errors="replace"), str(path)))

    for path in media_paths or []:
        targets.append(str(path))
        violations.extend(scan_media_file(path, require_c2pa=require_c2pa))

    return AuditReport(
        ok=len(violations) == 0,
        violations=violations,
        scanned_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        targets=targets,
        tool_version=version,
    )


def format_text(report: AuditReport) -> str:
    if report.ok:
        return "OK — no Article 50 transparency violations detected."
    lines = ["Article 50 transparency violations:"]
    for v in report.violations:
        lines.append(f"  [{v.code}] {v.message}")
    return "\n".join(lines)


def format_markdown(report: AuditReport) -> str:
    lines = ["# Art50Pulse audit report", "", f"- scanned_at: `{report.scanned_at}`", ""]
    if report.ok:
        lines.append("**Result:** OK")
        return "\n".join(lines)
    lines.append("**Result:** VIOLATIONS")
    lines.append("")
    for v in report.violations:
        lines.append(f"- **{v.code}**: {v.message}")
    return "\n".join(lines)
