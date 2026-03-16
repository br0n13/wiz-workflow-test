#!/usr/bin/env python3
"""Diff Wiz baseline and PR scan outputs to isolate newly introduced findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SEVERITY_ORDER = ["critical", "high", "medium", "low", "informational", "unknown"]


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def ensure_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]

    if isinstance(payload, dict):
        for key in ("findings", "issues", "results", "vulnerabilities", "data"):
            if isinstance(payload.get(key), list):
                return [p for p in payload[key] if isinstance(p, dict)]

    return []


def normalize_finding(item: dict[str, Any]) -> dict[str, Any]:
    rule_id = str(item.get("rule_id") or item.get("ruleId") or item.get("policy_id") or item.get("id") or "").strip()
    title = str(item.get("title") or item.get("name") or item.get("finding") or "Untitled finding").strip()
    severity = str(item.get("severity") or item.get("level") or "unknown").strip().lower()

    path = (
        item.get("path")
        or item.get("file")
        or item.get("filePath")
        or item.get("location", {}).get("path") if isinstance(item.get("location"), dict) else ""
    )
    path = str(path or "").strip()

    line = (
        item.get("line")
        or item.get("line_number")
        or item.get("lineNumber")
        or item.get("location", {}).get("line") if isinstance(item.get("location"), dict) else None
    )

    try:
        line_int = int(line) if line is not None else None
    except (TypeError, ValueError):
        line_int = None

    normalized = {
        "severity": severity,
        "title": title,
        "path": path,
        "line": line_int,
        "rule_id": rule_id,
    }
    return normalized


def stable_key(f: dict[str, Any]) -> tuple:
    return (
        f.get("rule_id") or "",
        f.get("title") or "",
        f.get("severity") or "",
        f.get("path") or "",
        f.get("line") if f.get("line") is not None else -1,
    )


def count_by_severity(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {sev: 0 for sev in SEVERITY_ORDER}
    for finding in findings:
        sev = finding.get("severity", "unknown")
        if sev not in counts:
            counts["unknown"] += 1
        else:
            counts[sev] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute new Wiz findings introduced by PR.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    baseline_findings = [normalize_finding(f) for f in ensure_list(load_json(Path(args.baseline)))]
    pr_findings = [normalize_finding(f) for f in ensure_list(load_json(Path(args.pr)))]

    baseline_keys = {stable_key(f) for f in baseline_findings}

    new_map: dict[tuple, dict[str, Any]] = {}
    for finding in pr_findings:
        key = stable_key(finding)
        if key in baseline_keys:
            continue
        new_map[key] = finding

    new_findings = sorted(
        new_map.values(),
        key=lambda x: (
            SEVERITY_ORDER.index(x.get("severity")) if x.get("severity") in SEVERITY_ORDER else len(SEVERITY_ORDER),
            x.get("path") or "",
            x.get("line") if x.get("line") is not None else -1,
            x.get("title") or "",
        ),
    )

    result = {
        "counts_by_severity": count_by_severity(new_findings),
        "total_new_findings": len(new_findings),
        "findings": new_findings,
    }

    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
