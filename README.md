# Wiz Reusable GitHub Actions Security Scanning

## Overview
This repository provides a reusable GitHub Actions workflow that runs Wiz CLI scans for software vulnerabilities and security issues across repositories. It is optimized for fast pull request feedback and complete coverage on the `main` branch.

> **Important:** Wiz CLI authentication must be supplied directly in each `wizcli scan dir` command via `--client-id` and `--client-secret`. The legacy `wizcli auth` command is deprecated and must never be used.

## Architecture
The platform is implemented as a reusable workflow:

- Workflow file: `.github/workflows/wiz-scan.yml`
- Trigger model: `on: workflow_call`
- Consumer repositories call this workflow and pass Wiz secrets.

This design centralizes scanning logic while allowing many repositories to share the same secure scanning implementation.

## Scanning Strategy
The workflow supports two execution paths:

1. **Pull request differential scanning**
   - Detect changed files from base/head SHAs.
   - Ignore deleted files.
   - Include modified, added, and renamed file targets.
   - Convert file paths to unique directories.
   - Scan only those directories.

2. **Full repository scanning on main**
   - For `push` events on `main`, scan the entire repository (`.`).
   - Upload full `wiz-results.json` as an artifact.

## PR Differential Scanning
For pull requests, the workflow:

1. Fetches the PR base commit.
2. Runs:
   - `git diff --name-status <BASE_SHA> <HEAD_SHA>`
3. Applies status handling:
   - `M` (modified): include
   - `A` (added): include
   - `R` (renamed): include **new** path
   - `D` (deleted): ignore
4. Writes included files to `changed_files.txt`.
5. Converts files to directories in `changed_dirs.txt`.
6. Adds `.` if root dependency/build files changed:
   - `Dockerfile`
   - `package.json`
   - `requirements.txt`
   - `go.mod`
   - `pom.xml`
   - `pyproject.toml`

If no scan targets remain, the workflow exits scanning gracefully with an empty results payload.

## Full Repo Scanning
For pushes to `main`, the workflow runs:

```bash
wizcli scan dir . \
  --client-id "$WIZ_CLIENT_ID" \
  --client-secret "$WIZ_CLIENT_SECRET" \
  --format json \
  --output wiz-results.json \
  --fail-on-issues false
```

This ensures full coverage for baseline and compliance reporting.

## Performance Optimization
The workflow reduces runtime and cost by:

- Scanning only changed directories in pull requests.
- Automatically including root scan only when critical root files change.
- Avoiding full-repo scans for standard PR validation.
- Using reusable workflow architecture for consistent behavior.

## Setup Instructions
1. Add this repository workflow as the reusable source.
2. In each consuming repository, create a caller workflow that triggers on PR and push events.
3. Pass required secrets to the reusable workflow.

## Secrets Configuration
Configure these repository or organization secrets in every consuming repository:

- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`

The reusable workflow requires both secrets through `workflow_call`.

## Reusable Workflow Usage
The reusable workflow has:

- `on: workflow_call`
- Required permissions:
  - `contents: read`
  - `pull-requests: write`
  - `checks: write`
- Concurrency:
  - `group: wiz-main-scan`
  - `cancel-in-progress: true`

## Example Integration
Example caller workflow in a consuming repository:

```yaml
name: Repository Security Scan

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  wiz:
    uses: your-org/wiz-workflow-test/.github/workflows/wiz-scan.yml@main
    secrets:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
```

## Example PR Output
When HIGH/CRITICAL findings exist, the workflow posts a markdown comment with real Wiz findings in a table, for example:

```markdown
| Severity | Vulnerability | Package | Version |
|----------|---------------|---------|---------|
| CRITICAL | CVE-2024-XXXX | openssl | 1.1.1 |
| HIGH     | CVE-2023-YYYY | lodash  | 4.17.15 |
```

To minimize PR noise, no comment is posted when no HIGH/CRITICAL findings are present.

## Troubleshooting
- **No PR scan executed:** confirm event is `pull_request` and the caller workflow uses this reusable workflow.
- **No findings comment:** expected when no HIGH/CRITICAL findings exist.
- **Scan failed authentication:** verify `WIZ_CLIENT_ID` and `WIZ_CLIENT_SECRET` are set and valid.
- **Missing artifact:** verify the job reached artifact upload and did not fail earlier.
- **Deprecated command usage:** remove any `wizcli auth` references from caller workflows or custom scripts.
