#!/usr/bin/env bash
set -euo pipefail

INPUT_JSON="${1:-output/wiz-results.json}"
OUTPUT_SUMMARY_JSON="${2:-output/wiz-summary.json}"
OUTPUT_SUMMARY_MD="${3:-output/wiz-summary.md}"

mkdir -p "$(dirname "$OUTPUT_SUMMARY_JSON")"
mkdir -p "$(dirname "$OUTPUT_SUMMARY_MD")"

# Supports common Wiz result layouts by checking a few possible paths.
critical="$(jq '[
  (.findings // []),
  (.vulnerabilities // []),
  (.results.findings // []),
  (.issues // [])
] | add | map(select((.severity // .severityLabel // "") | ascii_downcase == "critical")) | length' "$INPUT_JSON")"

high="$(jq '[
  (.findings // []),
  (.vulnerabilities // []),
  (.results.findings // []),
  (.issues // [])
] | add | map(select((.severity // .severityLabel // "") | ascii_downcase == "high")) | length' "$INPUT_JSON")"

medium="$(jq '[
  (.findings // []),
  (.vulnerabilities // []),
  (.results.findings // []),
  (.issues // [])
] | add | map(select((.severity // .severityLabel // "") | ascii_downcase == "medium")) | length' "$INPUT_JSON")"

low="$(jq '[
  (.findings // []),
  (.vulnerabilities // []),
  (.results.findings // []),
  (.issues // [])
] | add | map(select((.severity // .severityLabel // "") | ascii_downcase == "low")) | length' "$INPUT_JSON")"

info="$(jq '[
  (.findings // []),
  (.vulnerabilities // []),
  (.results.findings // []),
  (.issues // [])
] | add | map(select((.severity // .severityLabel // "") | ascii_downcase == "info")) | length' "$INPUT_JSON")"

total=$((critical + high + medium + low + info))

cat > "$OUTPUT_SUMMARY_JSON" <<JSON
{
  "total": $total,
  "critical": $critical,
  "high": $high,
  "medium": $medium,
  "low": $low,
  "info": $info
}
JSON

cat > "$OUTPUT_SUMMARY_MD" <<MD
## Wiz CLI Scan Results

- **Total findings**: $total
- **Critical**: $critical
- **High**: $high
- **Medium**: $medium
- **Low**: $low
- **Info**: $info

> Scan executed in non-blocking mode with \`--fail-on-issues false\`.
MD
