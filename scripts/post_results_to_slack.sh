#!/usr/bin/env bash
set -euo pipefail

SUMMARY_MD="${1:-output/wiz-summary.md}"

: "${SLACK_WEBHOOK_URL:?SLACK_WEBHOOK_URL is required}"
: "${TARGET_OWNER:?TARGET_OWNER is required}"
: "${TARGET_REPO:?TARGET_REPO is required}"
: "${TARGET_REF:?TARGET_REF is required}"

report="$(cat "$SUMMARY_MD")"
message="Wiz CLI scan finished for ${TARGET_OWNER}/${TARGET_REPO}@${TARGET_REF}\n\n${report}"

jq -n --arg text "$message" '{text: $text}' > /tmp/slack-payload.json
curl -fsSL -X POST -H 'Content-type: application/json' --data @/tmp/slack-payload.json "$SLACK_WEBHOOK_URL" >/dev/null
