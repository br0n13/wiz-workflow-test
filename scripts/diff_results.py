#!/usr/bin/env python3
"""Diff Wiz baseline and PR scan outputs and preserve enriched metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}


def list_findings(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("findings", "issues", "results", "vulnerabilities", "data", "matches"):
            if isinstance(payload.get(key), list):
                return [x for x in payload[key] if isinstance(x, dict)]
    return []


def nested(d: dict[str, Any], *keys: str) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def first(item: dict[str, Any], *candidates: Any) -> Any:
    for c in candidates:
        value = c(item) if callable(c) else item.get(c)
        if value not in (None, ""):
            return value
    return None


def normalize(item: dict[str, Any]) -> dict[str, Any]:
    severity = str(first(item, "severity", "level", lambda i: nested(i, "finding", "severity")) or "unknown").lower()
    cve = str(first(item, "cve", "cve_id", "cveId", lambda i: nested(i, "vulnerability", "cve"), lambda i: nested(i, "vulnerability", "id")) or "N/A")
    cvss_raw = first(item, "cvss", "cvss_score", "cvssScore", lambda i: nested(i, "vulnerability", "cvss"), lambda i: nested(i, "vulnerability", "cvssScore"))
    try:
        cvss = float(cvss_raw) if cvss_raw not in (None, "", "N/A") else None
    except Exception:
        cvss = None
    package = str(first(item, "package", "package_name", "packageName", lambda i: nested(i, "artifact", "name"), lambda i: nested(i, "dependency", "name")) or "N/A")
    installed = str(first(item, "installed_version", "installedVersion", "version", lambda i: nested(i, "artifact", "version")) or "N/A")
    fixed = str(first(item, "fixed_version", "fixedVersion", lambda i: nested(i, "vulnerability", "fixedVersion"), lambda i: nested(i, "fix", "version")) or "N/A")
    file_path = str(first(item, "path", "file", "filePath", lambda i: nested(i, "location", "path")) or "N/A")

    return {
        "severity": severity,
        "cve": cve,
        "cvss": cvss,
        "package": package,
        "installed_version": installed,
        "fixed_version": fixed,
        "file_path": file_path,
    }


def key(f: dict[str, Any]) -> tuple[Any, ...]:
    return (
        f.get("severity", "unknown"),
        f.get("cve", "N/A"),
        f.get("package", "N/A"),
        f.get("installed_version", "N/A"),
        f.get("fixed_version", "N/A"),
        f.get("file_path", "N/A"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        baseline = [normalize(x) for x in list_findings(load_json(Path(args.baseline)))]
        pr_findings = [normalize(x) for x in list_findings(load_json(Path(args.pr)))]
        baseline_keys = {key(x) for x in baseline}
        new_findings = [x for x in pr_findings if key(x) not in baseline_keys]

        dedup: dict[tuple[Any, ...], dict[str, Any]] = {}
        for finding in new_findings:
            dedup[key(finding)] = finding
        new_findings = list(dedup.values())

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in new_findings:
            sev = finding.get("severity", "unknown")
            if sev in counts:
                counts[sev] += 1

        payload = {
            "policy": "North vulnerabilities scanning",
            "counts_by_severity": counts,
            "total_new_findings": len(new_findings),
            "findings": new_findings,
        }
    except Exception:
        payload = {
            "policy": "North vulnerabilities scanning",
            "counts_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "total_new_findings": 0,
            "findings": [],
        }

    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
