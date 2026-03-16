#!/usr/bin/env python3
"""Build scan scope from git changed file list."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".kt", ".rb", ".php", ".cs",
    ".tf", ".tfvars", ".yml", ".yaml", ".json", ".xml", ".sh", ".dockerfile", ".gradle",
}


def normalize_changed_paths(lines: Iterable[str]) -> list[str]:
    paths: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) == 1:
            status, path = "M", parts[0]
        else:
            status, path = parts[0], parts[-1]

        if status.startswith("D"):
            continue

        p = Path(path)
        if p.is_absolute():
            p = Path(*p.parts[1:])
        normalized = p.as_posix().strip()

        if normalized and normalized != ".":
            paths.append(normalized)

    return sorted(set(paths))


def derive_directories(paths: list[str]) -> list[str]:
    dirs = set()
    for path in paths:
        parent = Path(path).parent.as_posix()
        dirs.add("." if parent == "" else parent)
    return sorted(dirs)


def choose_mode(paths: list[str]) -> dict:
    if not paths:
        return {"mode": "repo", "targets": ["."]}

    file_like = [p for p in paths if Path(p).suffix.lower() in TEXT_EXTENSIONS]

    if file_like and len(file_like) <= 100:
        return {"mode": "files", "targets": file_like}

    dirs = derive_directories(paths)

    if len(dirs) == 1 and dirs[0] == ".":
        return {"mode": "repo", "targets": ["."]}

    if len(dirs) <= 25:
        return {"mode": "directories", "targets": dirs}

    return {"mode": "repo", "targets": ["."]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Wiz scan scope from changed_files.txt")
    parser.add_argument("--changed-files", required=True, help="Path to git diff output")
    parser.add_argument("--output", required=True, help="Path to output scan-scope.json")
    args = parser.parse_args()

    changed_file_path = Path(args.changed_files)
    lines = changed_file_path.read_text(encoding="utf-8").splitlines() if changed_file_path.exists() else []

    paths = normalize_changed_paths(lines)
    scope = choose_mode(paths)

    out_path = Path(args.output)
    out_path.write_text(json.dumps(scope, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
