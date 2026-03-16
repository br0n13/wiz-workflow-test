# wiz-north-scan

Reusable GitHub CI/CD security scanning integration using **Wiz CLI only**.

This repository provides:
- A **reusable workflow** (`.github/workflows/wiz-scan.yml`) for orchestration.
- A **composite action** (`actions/wiz-cli/action.yml`) for Wiz CLI installation and execution.
- Helper scripts to summarize findings and post a PR comment.

## Features

- Scans **only files modified** in a pull request (via `git diff --name-only origin/<base>...<sha>`).
- Enforces Wiz policy: **`North vulnerabilities scanning`**.
- Authenticates using environment variables (no `wiz auth`):
  - `WIZ_CLIENT_ID`
  - `WIZ_CLIENT_SECRET`
- Produces machine-readable output: `wiz-results.json`.
- Summarizes findings by severity and posts a **PR comment**.
- Supports `workflow_dispatch` for manual testing (diffs against `main`).
- Does **not fail by default**; optional `fail-on-issues` input enables failing on detected vulnerabilities.

## Repository Structure

```text
wiz-north-scan
│
├── actions
│   └── wiz-cli
│       └── action.yml
│
├── .github
│   └── workflows
│       └── wiz-scan.yml
│
├── scripts
│   ├── summarize_results.py
│   └── post_pr_comment.py
│
└── README.md
```

## Reusable Workflow Contract

### Inputs

- `fail-on-issues` (boolean, optional, default: `false`)
  - `true`: fail job when vulnerabilities are detected.
  - `false`: report only.

### Required Secrets

- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`

These are passed to Wiz CLI through environment variables:

```yaml
env:
  WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
  WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
```

## How Other Repositories Integrate

Add a workflow in the consuming repository:

```yaml
name: Security Scan

on:
  pull_request:
  workflow_dispatch:

jobs:
  security-scan:
    uses: org-name/wiz-north-scan/.github/workflows/wiz-scan.yml@main
    with:
      fail-on-issues: false
    secrets:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
```

## Behavior

### Pull Request runs
1. Checkout repository.
2. Detect changed files:
   - `git diff --name-only origin/${{ github.base_ref }}...${{ github.sha }}`
3. Composite action builds a temporary scan scope containing only changed files.
4. Run:
   - `wiz scan directory <scoped-dir> --policy "North vulnerabilities scanning" --format json --output wiz-results.json`
5. Summarize and comment on PR.

### Manual (`workflow_dispatch`) runs
- Diffs against `main`:
  - `git diff --name-only origin/main...${{ github.sha }}`
- Useful for dry runs and platform validation.

## Notes

- `wiz auth` is intentionally not used (deprecated).
- The workflow uploads artifacts:
  - `wiz-results.json`
  - `wiz-summary.md`
  - `wiz-counts.json`
  - `changed_files.txt`
