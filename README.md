# wiz-workflow-test

Centralized GitHub workflow for scanning target repositories with **Wiz CLI**.

## What's included

- `.github/workflows/semgrep-scan.yml`
  - Updated to run Wiz CLI instead of Semgrep.
  - Preserves centralized architecture: GitHub App token generation, target repo checkout, and dispatch-driven execution.
  - Authenticates with `WIZ_CLIENT_ID` and `WIZ_CLIENT_SECRET`.
  - Runs non-blocking scans with `--fail-on-issues false`.
  - Exports JSON scan output and posts summaries to PR comments and check runs.
- `scripts/parse_wiz_results.sh`
  - Parses Wiz JSON results with `jq`.
  - Generates `output/wiz-summary.json` and `output/wiz-summary.md`.
- `examples/downstream-repo-dispatch.yml`
  - Example downstream repo integration to trigger centralized scanning.

## Required secrets

- `GH_APP_ID`
- `GH_APP_PRIVATE_KEY`
- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`
- (downstream example) `CENTRAL_SCAN_PAT`, `GH_APP_INSTALLATION_ID`

## Notes

- The scan workflow is intentionally non-blocking and always reports via PR comments/check run summaries.
- If your Wiz CLI command syntax differs by version, adapt only the Wiz command line flags while keeping the same architecture.
