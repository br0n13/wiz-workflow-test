# wiz-workflow-test

Production-grade reusable GitHub CI/CD security scanning integration for Wiz CLI.

## Features

- Pull request scanning and manual dispatch support.
- Mandatory policy enforcement: `North vulnerabilities scanning`.
- Baseline-aware differential analysis (`baseline-results.json` vs `pr-results.json`).
- PR comment updates using marker `<!-- WIZ-NORTH-SCAN -->`.
- Markdown results table with CVE data (top 10 findings).
- Informational-only behavior (`wiz scan ... || true`) so builds never fail.

## Repository layout

- `.github/workflows/wiz-scan.yml`: reusable orchestration workflow.
- `actions/wiz-cli/action.yml`: composite action (strict template).
- `scripts/build_scan_scope.py`: changed-file scope metadata generator.
- `scripts/diff_results.py`: differential new-finding detector.
- `scripts/summarize_results.py`: markdown table + summary generation.
- `scripts/post_pr_comment.py`: create/update PR comment.

## Required secrets

- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`

Both are passed directly to Wiz CLI via:

- `--client-id`
- `--client-secret`

No `wiz auth` flow is used.
