#!/usr/bin/env python3
"""Create or update a single deduplicated PR comment for Wiz scan output."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

MARKER = "<!-- WIZ-NORTH-SCAN -->"


def github_request(method: str, url: str, token: str, data: dict | None = None) -> dict | list:
    payload = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, method=method, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API request failed: {method} {url} -> {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Post/update Wiz PR comment.")
    parser.add_argument("--summary-md", required=True)
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--pr-number", default=os.getenv("PR_NUMBER", ""))
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN", ""))
    args = parser.parse_args()

    if not args.pr_number:
        print("No PR number detected; skipping PR comment creation.")
        return 0

    if not args.repo or "/" not in args.repo:
        print("GITHUB_REPOSITORY is missing or invalid; skipping PR comment creation.")
        return 0

    if not args.token:
        print("GITHUB_TOKEN is missing; skipping PR comment creation.")
        return 0

    summary = Path(args.summary_md).read_text(encoding="utf-8").strip()
    body = f"{MARKER}\n{summary}\n"

    owner, repo = args.repo.split("/", 1)
    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{args.pr_number}/comments"

    comments = github_request("GET", comments_url, args.token)
    existing = None

    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict) and MARKER in str(comment.get("body", "")):
                existing = comment
                break

    if existing:
        comment_id = existing.get("id")
        update_url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
        github_request("PATCH", update_url, args.token, data={"body": body})
        print(f"Updated existing Wiz scan PR comment (id={comment_id}).")
    else:
        github_request("POST", comments_url, args.token, data={"body": body})
        print("Created new Wiz scan PR comment.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise
