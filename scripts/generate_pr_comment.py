#!/usr/bin/env python3
"""Post Wiz findings markdown as a PR comment."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib import error, request
import json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comment-file", required=True)
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not token or not repository or not pr_number:
        raise SystemExit("Missing required env vars: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER")

    body = Path(args.comment_file).read_text(encoding="utf-8")
    endpoint = f"https://api.github.com/repos/{repository}/issues/{pr_number}/comments"
    payload = json.dumps({"body": body}).encode("utf-8")

    req = request.Request(endpoint, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")

    try:
        with request.urlopen(req) as resp:
            if resp.status >= 300:
                raise SystemExit(f"Failed to post PR comment: HTTP {resp.status}")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"Failed to post PR comment: HTTP {exc.code} - {details}") from exc


if __name__ == "__main__":
    main()
