#!/usr/bin/env python3
"""Create or update deduplicated PR comment without failing workflows."""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path

MARKER = "<!-- WIZ-NORTH-SCAN -->"


def request(method: str, url: str, token: str, data: dict | None = None) -> dict | list | None:
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        body = json.dumps(data).encode("utf-8") if data is not None else None
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url=url, method=method, headers=headers, data=body)
        with urllib.request.urlopen(req, timeout=30) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except Exception as exc:
        print(f"GitHub API warning: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-md", required=True)
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--pr-number", default=os.getenv("PR_NUMBER", ""))
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN", ""))
    args = parser.parse_args()

    if not args.pr_number:
        print("No PR number found (workflow_dispatch/workflow_call without PR); skipping comment.")
        return 0
    if not args.repo or "/" not in args.repo or not args.token:
        print("Repository/token unavailable; skipping comment.")
        return 0

    owner, repo = args.repo.split("/", 1)
    summary = Path(args.summary_md).read_text(encoding="utf-8").strip()
    body = f"{MARKER}\n{summary}\n"

    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{args.pr_number}/comments"
    comments = request("GET", comments_url, args.token)
    existing_id = None
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict) and MARKER in str(c.get("body", "")):
                existing_id = c.get("id")
                break

    if existing_id:
        request("PATCH", f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{existing_id}", args.token, {"body": body})
        print(f"Updated comment id={existing_id}")
    else:
        request("POST", comments_url, args.token, {"body": body})
        print("Created comment")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
