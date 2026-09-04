#!/usr/bin/env python3
"""Render a static interactive HTML dashboard from evidence and analysis JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    evidence = load_json(args.evidence)
    analysis = load_json(args.analysis)
    template_path = Path(__file__).resolve().parent.parent / "assets" / "dashboard.html"
    template = template_path.read_text(encoding="utf-8")
    payload = json.dumps(
        {"evidence": evidence, "analysis": analysis},
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    title = analysis.get("headline") or f"{evidence.get('ticker', '股票')} 异动调查"
    html = template.replace("__REPORT_TITLE__", str(title)).replace("__REPORT_DATA__", payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    markdown = analysis.get("summary_markdown")
    if markdown:
        report_path = args.output.with_name("report.md")
        report_path.write_text(str(markdown).rstrip() + "\n", encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
