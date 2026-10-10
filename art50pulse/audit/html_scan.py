"""Heuristic Art. 50(1) chatbot / AI interaction disclosure checks on HTML."""

from __future__ import annotations

import re

from art50pulse.audit.types import Violation

# Patterns aligned with EC Art. 50 guidelines (July 2026) — must be visible, not only in ToS.
_DISCLOSURE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"you\s+are\s+(?:now\s+)?(?:chatting|speaking|interacting)\s+with\s+(?:an?\s+)?ai",
        r"interacting\s+with\s+(?:an?\s+)?(?:artificial\s+intelligence|ai\s+system)",
        r"dies\s+ist\s+(?:ein\s+)?(?:ki[\s-]?system|chatbot)",
        r"sie\s+(?:chatten|sprechen)\s+mit\s+(?:einem?\s+)?ki",
        r"data-ai-disclosure",
        r"art50-disclosure",
        r"aria-label=[\"'][^\"']*ai\s+assistant",
        r"role=[\"']dialog[\"'][^>]*data-.*ai",
    )
]

_CHATBOT_HINTS = re.compile(
    r"(chat-?widget|intercom|drift|crisp|tidio|hubspot.*chat|livechat|botpress|voiceflow)",
    re.IGNORECASE,
)


def scan_html(html: str, label: str) -> list[Violation]:
    violations: list[Violation] = []
    has_widget_hint = bool(_CHATBOT_HINTS.search(html))
    has_disclosure = any(p.search(html) for p in _DISCLOSURE_PATTERNS)

    if has_widget_hint and not has_disclosure:
        violations.append(
            Violation(
                code="MISSING_CHATBOT_DISCLOSURE",
                message=(
                    f"{label}: third-party chat widget indicators found without a clear "
                    "Art. 50(1) AI interaction disclosure in HTML."
                ),
            )
        )
    return violations
