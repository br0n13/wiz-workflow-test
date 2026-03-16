# wiz-north-scan

Reusable GitHub CI/CD security scanning integration that runs Wiz CLI for pull requests, compares baseline and PR findings, and reports only newly introduced vulnerabilities under the **North vulnerabilities scanning** policy.

## What this repository does

This repository provides a reusable workflow and composite action that other repositories can call directly. It is designed for centralized, production-grade PR security scanning with:

- Wiz CLI execution only.
- Explicit CLI credential flags (`--client-id`, `--client-secret`) and no `wiz auth`.
- Policy enforcement for **North vulnerabilities scanning**.
- Baseline-vs-PR differential detection.
- Single deduplicated PR comment updates.
- Optional failure gate only when new findings are introduced.

## Architecture overview

- **Reusable workflow** (`.github/workflows/wiz-scan.yml`): Orchestrates checkout, diffing, scope derivation, baseline scan, PR scan, result diffing, summary generation, and PR comment management.
- **Composite action** (`actions/wiz-cli/action.yml`): Installs Wiz CLI and executes the scan command with explicit client credentials passed as flags.
- **Python scripts** (`scripts/*.py`):
  - `build_scan_scope.py`: derives scan target scope from changed files.
  - `diff_results.py`: computes newly introduced findings only.
  - `summarize_results.py`: creates `summary.json` and `summary.md`.
  - `post_pr_comment.py`: creates/updates one marker-based PR comment.

## How repositories consume the reusable workflow

```yaml
name: Security Scan

on:
  pull_request:

jobs:
  security-scan:
    uses: org-name/wiz-north-scan/.github/workflows/wiz-scan.yml@main
    secrets:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
```

## Required secrets

- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`

These secrets are passed to Wiz CLI as explicit command-line flags.

## Supported triggers

The workflow supports:

- `pull_request`
- `workflow_dispatch`
- `workflow_call`

## PR-focused scan scoping

1. Workflow computes changed files via `git diff --name-status base..head`.
2. `build_scan_scope.py` removes deleted entries, normalizes paths, and picks best scope:
   - `files` mode when safe and sufficiently narrow.
   - `directories` mode when file-based scope is too broad.
   - `repo` mode fallback (`.`) when scope cannot be safely narrowed.

## Baseline-aware differential scanning

1. Workflow checks out base commit and runs baseline scan.
2. Workflow checks out PR head commit and runs PR scan.
3. `diff_results.py` normalizes/deduplicates findings and outputs only findings present in PR results but not baseline results.

## Deduplicated PR comments

`post_pr_comment.py` searches PR comments for this marker:

```md
<!-- WIZ-NORTH-SCAN -->
```

- If found, it updates the existing comment.
- If not found, it creates one new comment.
- If no PR number exists (e.g., `workflow_dispatch`), it exits successfully without posting.

## fail-on-issues behavior

Input: `fail-on-issues` (default `false`)

- `false`: workflow never fails because of findings.
- `true`: workflow fails only when `total_new_findings > 0`.

## Artifacts generated

- `baseline-results.json`
- `pr-results.json`
- `new-findings.json`
- `summary.json`
- `summary.md`
- `changed_files.txt`
- `scan-scope.json`

## Adjusting Wiz CLI command syntax

The architecture is intentionally stable even if Wiz CLI syntax evolves.

If your Wiz tenant/version requires different scan flags, update **only** command assembly in `actions/wiz-cli/action.yml` (the `WIZ_SCAN_SUBCOMMAND` and argument section). This lets you tune exact CLI options without redesigning the reusable workflow, scripts, or repository contract.
