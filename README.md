# Security Platform: Reusable Wiz CLI Workflow

## 1. Overview

This repository provides a reusable GitHub Actions workflow for running Wiz CLI security scans across repositories without webhook infrastructure. Repositories call a centralized workflow using `workflow_call`, and findings are posted directly to pull requests.

## 2. Architecture Diagram

```text
Target Repo (PR / Push)
          |
          v
Repository Workflow
          |
          v
Reusable Workflow (.github/workflows/wiz-scan.yml)
          |
          v
Wiz CLI Scan -> Filter High/Critical -> PR Comment + Artifact
```

Flow summary:

Target Repo → Reusable Workflow → Wiz Scan → PR Comment

## 3. Prerequisites

Before integrating, make sure you have:

- Wiz CLI credentials:
  - `WIZ_CLIENT_ID`
  - `WIZ_CLIENT_SECRET`
- GitHub repository access to configure Actions and secrets.
- Permissions for workflows to comment on pull requests.

## 4. Setup Wiz Credentials

Add the following secrets in each target repository (or org-level secrets if preferred):

- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`

Path in GitHub UI:

1. `Settings`
2. `Secrets and variables`
3. `Actions`
4. `New repository secret`

Screenshot placeholder guidance:

- Capture the **Settings → Secrets → Actions** page.
- Capture the form where `WIZ_CLIENT_ID` and `WIZ_CLIENT_SECRET` are entered.

## 5. How to Add Scanning to an Existing Repository

### Step 1

Create a workflow file:

`.github/workflows/security.yml`

### Step 2

Add this workflow:

```yaml
name: Wiz Security Scan

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  wiz-scan:
    uses: my-org/security-platform/.github/workflows/wiz-scan.yml@main
    secrets: inherit
```

### Step 3

Commit the workflow:

```bash
git add .github/workflows/security.yml
git commit -m "Add reusable Wiz security scan workflow"
```

### Step 4

Open a pull request to trigger scanning.

## 6. Example Output

Example PR comment containing actual findings:

```markdown
## Wiz Security Scan Results

| Severity | Vulnerability | Package | Version | Fix |
|---------|---------------|---------|---------|-----|
| CRITICAL | CVE-2024-XXXX | openssl | 1.0.1 | 1.0.2 |
| HIGH | CVE-2023-XXXX | lodash | 4.17.15 | 4.17.21 |
```

If no high or critical vulnerabilities are detected, the workflow posts:

`No High or Critical vulnerabilities detected.`

## 7. Viewing Full Scan Results

Download the complete JSON report from GitHub Actions:

1. Open `Actions`
2. Select the workflow run
3. Open `Artifacts`
4. Download `wiz-results` (contains `wiz-results.json`)

## 8. Troubleshooting

### Wiz authentication failure

Symptoms:
- `wizcli auth` fails

Checks:
- Verify `WIZ_CLIENT_ID` and `WIZ_CLIENT_SECRET`
- Confirm credentials are active and not rotated/expired
- Confirm secrets were added in the correct repository/environment

### Missing secrets

Symptoms:
- Workflow errors before or during authentication

Checks:
- Validate secret names are exact (`WIZ_CLIENT_ID`, `WIZ_CLIENT_SECRET`)
- If using reusable workflow in another repo, ensure secrets are inherited or explicitly mapped

### Workflow permissions issues

Symptoms:
- PR comment step fails with `403` or permission errors

Checks:
- Ensure workflow/job has:
  - `contents: read`
  - `pull-requests: write`
  - `checks: write`
- Ensure repository settings allow GitHub Actions to create/approve PR comments as needed

## 9. Security Model

The reusable workflow uses minimal permissions:

- `contents: read` for checkout
- `pull-requests: write` for posting PR comments
- `checks: write` for checks integration compatibility

The workflow behavior is intentionally non-blocking:

- Scan runs with `--fail-on-issues false`
- Findings are reported to PRs for visibility
- Build status is not failed solely due to vulnerabilities

## Repository Structure

```text
security-platform/
  .github/workflows/wiz-scan.yml
  scripts/
    extract_wiz_findings.py
    generate_pr_comment.py
  docs/
    integration.md
  example/
    repo-workflow.yml
  README.md
```

## Reusable Workflow Details

Location: `.github/workflows/wiz-scan.yml`

- Trigger: `workflow_call`
- Input: `scan_path`
- Required secrets:
  - `WIZ_CLIENT_ID`
  - `WIZ_CLIENT_SECRET`
- Steps:
  1. Checkout repository
  2. Install Wiz CLI
  3. Authenticate Wiz CLI
  4. Run scan with Wiz policy `default vulnerability management` and emit `wiz-results.json`
  5. Filter to `CRITICAL`/`HIGH`
  6. Format markdown table
  7. Post PR comment
  8. Upload full JSON artifact

## Migration Summary

This implementation removes webhook listeners and GitHub App dispatch logic in favor of native reusable workflows, replacing Semgrep scans with Wiz CLI while preserving centralized governance and PR-level visibility.
