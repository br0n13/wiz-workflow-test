# Migration Guide: Webhook/Semgrep to Reusable Wiz Workflow

This guide explains how to migrate from the previous centralized webhook + dispatch + Semgrep model to a reusable `workflow_call` model that runs Wiz CLI directly from GitHub Actions.

## What is removed

- Webhook listener infrastructure
- GitHub App dispatch and repository_dispatch logic
- Semgrep scanning jobs and Semgrep result formatting

## What replaces it

- A reusable workflow at `.github/workflows/wiz-scan.yml`
- Wiz CLI installation and authentication in GitHub Actions
- Wiz scan execution with policy `default vulnerability management`
- JSON findings extraction for `CRITICAL` and `HIGH` severities only
- Pull request comments containing actual Wiz findings
- Artifact upload of full `wiz-results.json`

## Migration steps

1. Delete legacy webhook and dispatch workflow files from your security platform and target repositories.
2. Add/validate repository secrets:
   - `WIZ_CLIENT_ID`
   - `WIZ_CLIENT_SECRET`
3. Add a repository workflow in each onboarded repo to call this reusable workflow.
4. Open a pull request to verify:
   - scan executes
   - PR comment is posted with findings table
   - `wiz-results.json` artifact is present

## Behavioral differences

- The reusable workflow does **not** fail builds when vulnerabilities are present.
- Only `HIGH` and `CRITICAL` findings are included in PR comments.
- Full raw JSON is still available as an artifact for deeper triage.
