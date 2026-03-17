#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect_findings(data: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if any(k in node for k in ["cve", "CVE", "severity", "cvss", "package"]):
                findings.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return findings


def finding_key(item: dict[str, Any]) -> str:
    cve = item.get("cve") or item.get("CVE") or item.get("id") or "N/A"
    package = item.get("package") or item.get("packageName") or "N/A"
    file_name = item.get("file") or item.get("path") or "N/A"
    return f"{cve}|{package}|{file_name}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    baseline = collect_findings(load_json(args.baseline))
    pr = collect_findings(load_json(args.pr))

    baseline_keys = {finding_key(item) for item in baseline}
    new_findings = [item for item in pr if finding_key(item) not in baseline_keys]

    Path(args.output).write_text(
        json.dumps(
            {
                "policy": "North vulnerabilities scanning",
                "baseline_count": len(baseline),
                "pr_count": len(pr),
                "new_count": len(new_findings),
                "new_findings": new_findings,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote differential results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
