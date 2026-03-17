#!/usr/bin/env python3
"""Build scan scope from git changed file list."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def normalize_changed_paths(lines: Iterable[str]) -> list[str]:
    paths: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0] if parts else "M"
        path = parts[-1] if len(parts) > 1 else status
        if status.startswith("D"):
            continue
        normalized = Path(path).as_posix().strip().lstrip("/")
        if normalized and normalized != ".":
            paths.append(normalized)
    return sorted(set(paths))


def choose_mode(paths: list[str]) -> dict[str, list[str] | str]:
    if not paths:
        return {"mode": "repo", "targets": ["."]}
    if len(paths) <= 100:
        return {"mode": "files", "targets": paths}
    directories = sorted({Path(p).parent.as_posix() or "." for p in paths})
    if len(directories) <= 25:
        return {"mode": "directories", "targets": directories}
    return {"mode": "repo", "targets": ["."]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-files", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        changed = Path(args.changed_files)
        lines = changed.read_text(encoding="utf-8").splitlines() if changed.exists() else []
        scope = choose_mode(normalize_changed_paths(lines))
    except Exception:
        scope = {"mode": "repo", "targets": ["."]}

    Path(args.output).write_text(json.dumps(scope, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
