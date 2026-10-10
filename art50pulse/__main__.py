#!/usr/bin/env python3
"""CLI entrypoint for art50pulse."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from art50pulse import __version__
from art50pulse.audit import run_audit
from art50pulse.audit.engine import format_markdown, format_text


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="art50pulse",
        description="EU AI Act Article 50 transparency pre-audit",
    )
    p.add_argument("--version", action="version", version=f"art50pulse {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit HTML surfaces and optional media assets")
    audit.add_argument("--html", action="append", default=[], help="Local HTML file (repeatable)")
    audit.add_argument("--url", action="append", default=[], help="Fetch HTML from URL (repeatable)")
    audit.add_argument("--media", action="append", default=[], help="Image/video file for C2PA check")
    audit.add_argument(
        "--require-c2pa",
        action="store_true",
        help="Fail if listed media files lack C2PA/JUMBF markers",
    )
    audit.add_argument(
        "--output",
        choices=("text", "json", "markdown"),
        default="text",
        help="Report format",
    )
    audit.add_argument("--out-file", help="Write report to file")
    return p


def _fetch_url(url: str) -> str:
    req = Request(url, headers={"User-Agent": "art50pulse/0.1 (+https://github.com/sysrqio/art50pulse)"})
    with urlopen(req, timeout=20) as resp:  # noqa: S310 — explicit audit tool
        return resp.read().decode("utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "audit":
        return 1

    html_paths: list[Path] = []
    tmp_urls: list[tuple[str, str]] = []

    for raw in args.html:
        path = Path(raw)
        if not path.exists():
            print(f"error: html path not found: {path}", file=sys.stderr)
            return 1
        html_paths.append(path)

    for url in args.url:
        try:
            body = _fetch_url(url)
        except Exception as exc:  # noqa: BLE001
            print(f"error: failed to fetch {url}: {exc}", file=sys.stderr)
            return 1
        tmp = Path("/tmp") / f"art50pulse-{abs(hash(url))}.html"
        tmp.write_text(body, encoding="utf-8")
        html_paths.append(tmp)
        tmp_urls.append((url, str(tmp)))

    media_paths: list[Path] = []
    for raw in args.media:
        path = Path(raw)
        if not path.exists():
            print(f"error: media path not found: {path}", file=sys.stderr)
            return 1
        media_paths.append(path)

    try:
        report = run_audit(
            html_paths=html_paths,
            media_paths=media_paths,
            require_c2pa=args.require_c2pa,
            version=__version__,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output == "json":
        out = json.dumps(report.to_dict(), indent=2)
    elif args.output == "markdown":
        out = format_markdown(report)
    else:
        out = format_text(report)

    if args.out_file:
        Path(args.out_file).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0 if report.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
