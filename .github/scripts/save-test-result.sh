#!/bin/bash
set -euo pipefail

VERSION=$1
STATUS=$2  # "success" or "failure"
LOG_URL=$3

RESULT_FILE=".github/test-results/${VERSION}.json"

mkdir -p .github/test-results

cat > "$RESULT_FILE" <<EOF
{
  "version": "${VERSION}",
  "status": "${STATUS}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "log_url": "${LOG_URL}"
}
EOF

echo "Test result saved: $RESULT_FILE"
