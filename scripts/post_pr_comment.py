#!/usr/bin/env python3
import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

MARKER = "<!-- WIZ-NORTH-SCAN -->"


def request_json(method: str, url: str, token: str, payload: dict | None = None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        print(f"GitHub API call failed: {method} {url} ({exc.code})")
        return {}
    except Exception as exc:
        print(f"GitHub API call failed: {exc}")
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-md", required=True)
    parser.add_argument("--pr-number", default="")
    args = parser.parse_args()

    repo = os.getenv("GITHUB_REPOSITORY", "")
    token = os.getenv("GITHUB_TOKEN", "")
    pr_number = args.pr_number.strip()

    if not pr_number:
        print("No PR number provided; skipping comment.")
        return 0

    if not token or not repo or "/" not in repo:
        print("Missing repo/token context; skipping comment.")
        return 0

    body = f"{MARKER}\n{Path(args.summary_md).read_text(encoding='utf-8')}"
    owner, name = repo.split("/", 1)
    list_url = f"https://api.github.com/repos/{owner}/{name}/issues/{pr_number}/comments"

    comments = request_json("GET", list_url, token)
    existing_id = None
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict) and MARKER in str(c.get("body", "")):
                existing_id = c.get("id")
                break

    if existing_id:
        update_url = f"https://api.github.com/repos/{owner}/{name}/issues/comments/{existing_id}"
        request_json("PATCH", update_url, token, {"body": body})
        print(f"Updated PR comment {existing_id}")
    else:
        request_json("POST", list_url, token, {"body": body})
        print("Created PR comment")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
