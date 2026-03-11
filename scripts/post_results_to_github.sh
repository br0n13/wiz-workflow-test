#!/usr/bin/env bash
set -euo pipefail

SUMMARY_JSON="${1:-output/wiz-summary.json}"
SUMMARY_MD="${2:-output/wiz-summary.md}"

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${TARGET_OWNER:?TARGET_OWNER is required}"
: "${TARGET_REPO:?TARGET_REPO is required}"
: "${TARGET_REF:?TARGET_REF is required}"

critical="$(jq -r '.critical // 0' "$SUMMARY_JSON")"
high="$(jq -r '.high // 0' "$SUMMARY_JSON")"
medium="$(jq -r '.medium // 0' "$SUMMARY_JSON")"
low="$(jq -r '.low // 0' "$SUMMARY_JSON")"
info="$(jq -r '.info // 0' "$SUMMARY_JSON")"
summary_line="Critical: ${critical}, High: ${high}, Medium: ${medium}, Low: ${low}, Info: ${info}"
body="$(cat "$SUMMARY_MD")"

if [[ -n "${PULL_REQUEST_NUMBER:-}" ]]; then
  jq -n --arg body "$body" '{body: $body}' > /tmp/pr-comment.json
  curl -fsSL -X POST \
    -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${PULL_REQUEST_NUMBER}/comments" \
    -d @/tmp/pr-comment.json >/dev/null
fi

jq -n \
  --arg name "Wiz CLI Scan" \
  --arg head_sha "$TARGET_REF" \
  --arg title "Wiz CLI scan completed (non-blocking)" \
  --arg summary "$summary_line" \
  --arg text "$body" \
  '{name: $name, head_sha: $head_sha, status: "completed", conclusion: "success", output: {title: $title, summary: $summary, text: $text}}' > /tmp/check-run.json

curl -fsSL -X POST \
  -H "Authorization: Bearer ${GH_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${TARGET_OWNER}/${TARGET_REPO}/check-runs" \
  -d @/tmp/check-run.json >/dev/null
