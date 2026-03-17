#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-files", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    changed_path = Path(args.changed_files)
    files = []

    if changed_path.exists():
        for line in changed_path.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value:
                files.append(value)

    payload = {
        "mode": "repo",
        "targets": ["."],
        "changed_files": files,
    }

    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote scan scope to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
