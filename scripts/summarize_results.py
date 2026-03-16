#!/usr/bin/env python3
"""Generate markdown and JSON summaries from new findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SEVERITIES = ["critical", "high", "medium", "low", "informational"]


def read_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"counts_by_severity": {}, "total_new_findings": 0, "findings": []}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize new Wiz findings.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--summary-md", required=True)
    parser.add_argument("--policy-name", required=True)
    args = parser.parse_args()

    payload = read_payload(Path(args.input))
    findings = payload.get("findings", []) or []
    incoming_counts = payload.get("counts_by_severity", {}) or {}

    counts = {sev: int(incoming_counts.get(sev, 0)) for sev in SEVERITIES}
    total = int(payload.get("total_new_findings", len(findings)))

    top_findings = findings[:10]

    summary_obj = {
        "policy": args.policy_name,
        "total_new_findings": total,
        "counts": counts,
        "top_findings": top_findings,
    }

    lines = [
        "## Wiz Security Scan Results",
        "",
        f"**Policy:** {args.policy_name}",
        "",
        "### Summary",
        f"- Critical: {counts['critical']}",
        f"- High: {counts['high']}",
        f"- Medium: {counts['medium']}",
        f"- Low: {counts['low']}",
        f"- Informational: {counts['informational']}",
        "",
        "### New Findings Introduced by This PR",
    ]

    if total == 0:
        lines.append("✅ No new vulnerabilities introduced by this PR were detected under the configured Wiz policy.")
    else:
        for idx, finding in enumerate(top_findings, 1):
            sev = str(finding.get("severity", "unknown")).capitalize()
            title = finding.get("title", "Untitled finding")
            path = finding.get("path") or "."
            line = finding.get("line")
            location = f"{path}:{line}" if line is not None else path
            lines.append(f"{idx}. {sev} - {title} - {location}")

    Path(args.summary_json).write_text(json.dumps(summary_obj, indent=2) + "\n", encoding="utf-8")
    Path(args.summary_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
