#!/usr/bin/env python3
"""Summarize Wiz JSON results into markdown and machine-readable counts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


def extract_findings(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("findings", "vulnerabilities", "results", "issues", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return []


def normalize_finding(item: dict) -> dict:
    severity = str(item.get("severity", "UNKNOWN")).upper()
    title = (
        item.get("title")
        or item.get("name")
        or item.get("id")
        or item.get("vulnerabilityId")
        or "Unknown finding"
    )
    return {"severity": severity, "title": str(title)}


def render_summary(findings: list[dict]) -> tuple[str, dict]:
    normalized = [normalize_finding(item) for item in findings]
    counts = Counter(f["severity"] for f in normalized)

    top_findings = normalized[:10]

    lines = [
        "Wiz Security Scan Results",
        "",
        "Summary:",
        f"Critical: {counts.get('CRITICAL', 0)}",
        f"High: {counts.get('HIGH', 0)}",
        f"Medium: {counts.get('MEDIUM', 0)}",
        f"Low: {counts.get('LOW', 0)}",
        "",
        "Top Findings:",
    ]

    if top_findings:
        for finding in top_findings:
            lines.append(f"- {finding['severity']} - {finding['title']}")
    else:
        lines.append("- No vulnerabilities detected in the scoped scan.")

    total = sum(counts.get(sev, 0) for sev in SEVERITIES)
    structured = {
        "critical": counts.get("CRITICAL", 0),
        "high": counts.get("HIGH", 0),
        "medium": counts.get("MEDIUM", 0),
        "low": counts.get("LOW", 0),
        "total": total,
    }

    return "\n".join(lines) + "\n", structured


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to wiz-results.json")
    parser.add_argument("--summary-file", required=True, help="Output markdown/text summary")
    parser.add_argument("--counts-file", required=True, help="Output JSON counts")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    findings = extract_findings(payload)

    summary, counts = render_summary(findings)

    Path(args.summary_file).write_text(summary, encoding="utf-8")
    Path(args.counts_file).write_text(json.dumps(counts, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
