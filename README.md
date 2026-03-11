# wiz-workflow-test

Centralized GitHub workflow for scanning target repositories with **Wiz CLI**.

## What's included

- `.github/workflows/semgrep-scan.yml`
  - Updated to run Wiz CLI instead of Semgrep.
  - Preserves centralized architecture: GitHub App token generation, target repo checkout, and dispatch-driven execution.
  - Supports both `repository_dispatch` (`wiz-cli-scan`) and manual `workflow_dispatch`.
  - Authenticates with `WIZ_CLIENT_ID` and `WIZ_CLIENT_SECRET`.
  - Runs non-blocking scans with `--fail-on-issues false` and default policy.
  - Exports JSON scan output and posts summaries to PR comments and check runs.
- `scripts/parse_wiz_results.sh`
  - Parses Wiz JSON results with `jq`.
  - Generates `output/wiz-summary.json` and `output/wiz-summary.md`.
- `scripts/post_results_to_github.sh`
  - Posts PR comments and GitHub Check Runs through the GitHub API.
- `scripts/post_results_to_slack.sh`
  - Posts summarized scan output to Slack via webhook.
- `examples/downstream-repo-dispatch.yml`
  - Example downstream repo integration to trigger centralized scanning.
- `webhook/listener.md`
  - Contract for external webhook listener service dispatch payload.

## Required secrets

- `GH_APP_ID`
- `GH_APP_PRIVATE_KEY`
- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`
- `SLACK_WEBHOOK_URL` (optional)
- (downstream example) `CENTRAL_SCAN_PAT`, `GH_APP_INSTALLATION_ID`

## Are missing files needed?

Yes — if you want this to run in the **same fashion** as the prior Semgrep setup (with webhook dispatch and external posting integrations), you need all of the following in the central repo:

1. The scan workflow (`.github/workflows/semgrep-scan.yml`).
2. Result parser (`scripts/parse_wiz_results.sh`).
3. Result publishers (`scripts/post_results_to_github.sh`, `scripts/post_results_to_slack.sh`).
4. A defined webhook dispatch contract (`webhook/listener.md`) so your listener sends the expected `repository_dispatch` payload.
5. A downstream trigger example (`examples/downstream-repo-dispatch.yml`) for repository integration.

Without these, the architecture may still scan locally but won’t mirror the centralized, dispatch-driven operating model end-to-end.
