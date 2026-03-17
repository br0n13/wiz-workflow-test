#!/usr/bin/env python3
"""Generate markdown and JSON summary with top-10 enriched findings table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_ICON = {"critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}


def cvss_value(item: dict[str, Any]) -> float:
    try:
        return float(item.get("cvss"))
    except Exception:
        return -1.0


def fmt(value: Any) -> str:
    if value in (None, ""):
        return "N/A"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--summary-md", required=True)
    args = parser.parse_args()

    payload = read_json(Path(args.input))
    findings = payload.get("findings", []) if isinstance(payload.get("findings", []), list) else []
    counts = payload.get("counts_by_severity", {}) if isinstance(payload.get("counts_by_severity", {}), dict) else {}
    normalized_counts = {k: int(counts.get(k, 0)) for k in ["critical", "high", "medium", "low"]}

    findings.sort(key=lambda x: (SEVERITY_ORDER.get(str(x.get("severity", "")).lower(), 9), -cvss_value(x)))
    top = findings[:10]

    summary_json = {
        "policy": "North vulnerabilities scanning",
        "total_new_findings": int(payload.get("total_new_findings", len(findings))),
        "counts": normalized_counts,
        "top_findings": top,
    }

    lines = [
        "## Wiz Security Scan Results",
        "",
        "Policy: North vulnerabilities scanning",
        "",
        "### Summary",
        f"- Critical: {normalized_counts['critical']}",
        f"- High: {normalized_counts['high']}",
        f"- Medium: {normalized_counts['medium']}",
        f"- Low: {normalized_counts['low']}",
        "",
        "---",
        "",
        "### New Findings Introduced by This PR",
        "",
    ]

    if not findings:
        lines.append("✅ No new vulnerabilities introduced by this PR")
    else:
        lines.extend([
            "| Severity | CVE | CVSS | Package | Installed | Fixed | File |",
            "|----------|-----|------|---------|-----------|-------|------|",
        ])
        for finding in top:
            sev = str(finding.get("severity", "low")).lower()
            lines.append(
                f"| {SEVERITY_ICON.get(sev, '🟢 Low')} | {fmt(finding.get('cve'))} | {fmt(finding.get('cvss'))} | {fmt(finding.get('package'))} | {fmt(finding.get('installed_version'))} | {fmt(finding.get('fixed_version'))} | {fmt(finding.get('file_path'))} |"
            )

    Path(args.summary_json).write_text(json.dumps(summary_json, indent=2) + "\n", encoding="utf-8")
    Path(args.summary_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
