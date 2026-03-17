# wiz-north-scan

Production-grade reusable GitHub Actions integration for **informational** Wiz vulnerability scanning.

This repository scans pull request changes, enforces the hardcoded Wiz policy **"North vulnerabilities scanning"**, performs baseline-aware differential analysis, and posts a markdown table comment with enriched CVE metadata.

## Repository structure

```text
wiz-north-scan
├── actions
│   └── wiz-cli
│       └── action.yml
├── .github
│   └── workflows
│       └── wiz-scan.yml
├── scripts
│   ├── build_scan_scope.py
│   ├── diff_results.py
│   ├── summarize_results.py
│   └── post_pr_comment.py
└── README.md
```

## Key guarantees

- **Informational only:** scans never fail the workflow.
- **Wiz auth mode:** only `--client-id` and `--client-secret` are used.
- **Hardcoded policy:** all scans always run with `--policy "North vulnerabilities scanning"`.
- **PR diffing:** only vulnerabilities newly introduced in the PR are reported.
- **Top 10 table output:** severity icon, CVE, CVSS, package, installed/fixed versions, and file path.

## Secrets setup

Configure these repository or organization secrets in the caller repository:

- `WIZ_CLIENT_ID`
- `WIZ_CLIENT_SECRET`

## Integration instructions

Use the reusable workflow from another repository:

```yaml
name: Wiz Security Scan

on:
  pull_request:

jobs:
  wiz:
    uses: your-org/wiz-north-scan/.github/workflows/wiz-scan.yml@main
    secrets:
      WIZ_CLIENT_ID: ${{ secrets.WIZ_CLIENT_ID }}
      WIZ_CLIENT_SECRET: ${{ secrets.WIZ_CLIENT_SECRET }}
```

Supported triggers in the reusable workflow:

- `pull_request`
- `workflow_dispatch`
- `workflow_call`

For `workflow_dispatch`, the workflow compares against `main` by default and skips PR commenting when no PR exists.

## Output format

The PR comment body starts with:

```md
<!-- WIZ-NORTH-SCAN -->
```

Then includes:

- `Policy: North vulnerabilities scanning`
- Severity counts (Critical, High, Medium, Low)
- A markdown table with up to top 10 new findings

If no new vulnerabilities are introduced:

```md
✅ No new vulnerabilities introduced by this PR
```

## CVE and metadata enrichment

`diff_results.py` preserves enriched vulnerability fields whenever available:

- CVE ID
- CVSS score
- package name
- installed version
- fixed version
- file path
- severity

Missing values are normalized to `N/A` for clean table rendering.
