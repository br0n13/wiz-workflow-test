#!/usr/bin/env python3
"""Extract HIGH/CRITICAL Wiz findings and render markdown for PR comments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SEVERITIES = {"HIGH", "CRITICAL"}


def load_findings(payload: dict) -> list[dict]:
    """Best-effort extraction across common Wiz JSON shapes."""
    candidates = [
        payload.get("findings"),
        payload.get("vulnerabilities"),
        payload.get("results"),
        payload.get("issues"),
    ]

    for candidate in candidates:
        if isinstance(candidate, list):
            return candidate

    if isinstance(payload, list):
        return payload

    return []


def normalize_finding(item: dict) -> dict:
    vuln_id = (
        item.get("id")
        or item.get("vulnerabilityId")
        or item.get("cve")
        or item.get("name")
        or "UNKNOWN"
    )
    severity = str(item.get("severity", "UNKNOWN")).upper()

    package_name = (
        item.get("packageName")
        or item.get("package", {}).get("name")
        or item.get("artifact", {}).get("name")
        or "-"
    )
    package_version = (
        item.get("packageVersion")
        or item.get("package", {}).get("version")
        or item.get("artifact", {}).get("version")
        or "-"
    )
    file_path = item.get("filePath") or item.get("path") or item.get("location") or "-"
    description = item.get("description") or item.get("title") or "No description provided."
    fix_version = (
        item.get("fixVersion")
        or item.get("fixedVersion")
        or item.get("fix", {}).get("version")
        or "-"
    )

    return {
        "vulnerability_id": vuln_id,
        "severity": severity,
        "package_name": package_name,
        "package_version": package_version,
        "file_path": file_path,
        "description": description,
        "fix_version": fix_version,
    }


def to_markdown(findings: list[dict]) -> str:
    header = "## Wiz Security Scan Results\n\n"
    if not findings:
        return header + "No High or Critical vulnerabilities detected.\n"

    table = [
        "| Severity | Vulnerability | Package | Version | File | Fix | Description |",
        "|---|---|---|---|---|---|---|",
    ]

    for finding in findings:
        desc = str(finding["description"]).replace("\n", " ").replace("|", "\\|")
        row = (
            f"| {finding['severity']} | {finding['vulnerability_id']} | "
            f"{finding['package_name']} | {finding['package_version']} | "
            f"{finding['file_path']} | {finding['fix_version']} | {desc} |"
        )
        table.append(row)

    return header + "\n".join(table) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    findings = [normalize_finding(item) for item in load_findings(payload)]
    filtered = [f for f in findings if f["severity"] in SEVERITIES]

    Path(args.output).write_text(json.dumps(filtered, indent=2), encoding="utf-8")
    Path(args.markdown).write_text(to_markdown(filtered), encoding="utf-8")


if __name__ == "__main__":
    main()
