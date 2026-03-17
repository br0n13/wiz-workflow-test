#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any


SEVERITY_ICON = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}


def load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def norm(value: Any) -> str:
    if value is None:
        return "N/A"
    text = str(value).strip()
    return text if text else "N/A"


def extract(item: dict[str, Any]) -> dict[str, str]:
    severity_raw = norm(item.get("severity") or item.get("Severity") or "N/A")
    sev_key = severity_raw.lower()
    icon = SEVERITY_ICON.get(sev_key, "⚪")
    return {
        "severity": f"{icon} {severity_raw}",
        "cve": norm(item.get("cve") or item.get("CVE") or item.get("id")),
        "cvss": norm(item.get("cvss") or item.get("CVSS") or item.get("score")),
        "package": norm(item.get("package") or item.get("packageName") or item.get("name")),
        "installed": norm(item.get("installed") or item.get("installedVersion") or item.get("version")),
        "fixed": norm(item.get("fixed") or item.get("fixedVersion")),
        "file": norm(item.get("file") or item.get("path") or item.get("location")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--summary-md", required=True)
    args = parser.parse_args()

    data = load(args.input)
    items = data.get("new_findings", []) if isinstance(data, dict) else []
    top = [extract(i) for i in items[:10] if isinstance(i, dict)]

    summary = {
        "policy": "North vulnerabilities scanning",
        "total_new_findings": len(items),
        "displayed_findings": len(top),
        "table_headers": ["Severity", "CVE", "CVSS", "Package", "Installed", "Fixed", "File"],
    }
    Path(args.summary_json).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "## Wiz Scan (Informational Only)",
        "Policy enforced: `North vulnerabilities scanning`",
        "",
        f"New findings vs baseline: **{len(items)}**",
        "",
        "| Severity | CVE | CVSS | Package | Installed | Fixed | File |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    if top:
        for row in top:
            lines.append(
                f"| {row['severity']} | {row['cve']} | {row['cvss']} | {row['package']} | {row['installed']} | {row['fixed']} | {row['file']} |"
            )
    else:
        lines.append("| N/A | N/A | N/A | N/A | N/A | N/A | N/A |")

    lines.append("")
    lines.append("_This scan is informational only and never fails the build._")

    Path(args.summary_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote summary outputs to {args.summary_json} and {args.summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
