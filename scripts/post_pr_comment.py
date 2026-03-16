#!/usr/bin/env python3
"""Post Wiz summary as a GitHub pull request comment."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import error, request


def resolve_pr_number(explicit: str | None) -> str | None:
    if explicit:
        return explicit

    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return None

    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    pr = event.get("pull_request") if isinstance(event, dict) else None
    if isinstance(pr, dict) and pr.get("number"):
        return str(pr["number"])

    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--pr-number", required=False)
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = resolve_pr_number(args.pr_number or os.getenv("PR_NUMBER"))

    if not token or not repo or not pr_number:
        raise SystemExit("Missing required context: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER")

    summary = Path(args.summary_file).read_text(encoding="utf-8")

    endpoint = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = json.dumps({"body": summary}).encode("utf-8")

    req = request.Request(endpoint, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")

    try:
        with request.urlopen(req) as response:
            if response.status >= 300:
                raise SystemExit(f"Failed to post PR comment: HTTP {response.status}")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"Failed to post PR comment: HTTP {exc.code} - {detail}") from exc


if __name__ == "__main__":
    main()
