# wiz-workflow-test

## Overview

This repository provides a reusable GitHub workflow that performs Wiz CLI security scans.

Repositories can integrate this workflow to automatically scan pull requests and main branch commits.

## Architecture

PR Workflow

Pull Request
     ↓
Detect Changed Files
     ↓
Convert Files → Directories
     ↓
Wiz CLI Scan
     ↓
Post Results to PR

Main Branch Workflow

Merge to main
     ↓
Full Repository Scan
     ↓
Upload Results Artifact

## Scanning Strategy

Pull Requests

Only the code changed in the PR is scanned.

This reduces security noise and ensures developers only see vulnerabilities related to their changes.

Main Branch

The entire repository is scanned after merges to ensure full coverage.

## Performance Optimization

Directory-based scanning is used instead of scanning individual files.

Example:

Changed files:

src/auth/login.py
src/auth/session.py
terraform/main.tf

Directories scanned:

src/auth
terraform

This significantly reduces scan time.

## Handling Edge Cases

New Files

New files added in the PR are scanned fully.

Renamed Files

Renamed files scan the new file path.

Deleted Files

Deleted files are ignored.

Root Files

Changes to dependency files trigger a root scan.

Examples:

Dockerfile
package.json
requirements.txt

## Setup Instructions

Step 1

Add repository secrets:

WIZ_CLIENT_ID
WIZ_CLIENT_SECRET

Step 2

Create workflow:

.github/workflows/security.yml

Example:

```yaml
name: Wiz Security Scan

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  wiz-scan:
    uses: stratus-ai/security-platform/.github/workflows/wiz-scan.yml@main
    secrets: inherit
```

Step 3

Commit and open a PR.

## Example PR Output

## Wiz Security Scan Results

| Severity | Vulnerability | Package | Version |
|----------|---------------|--------|--------|
| CRITICAL | CVE-XXXX | openssl | 1.1.1 |
| HIGH | CVE-XXXX | lodash | 4.17.15 |

## Viewing Full Scan Results

Go to:

Actions → Workflow Run → Artifacts → wiz-results.json

## Concurrency Behavior

When multiple PRs merge quickly, older scans are cancelled and only the newest main branch scan runs.

## Security Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```
