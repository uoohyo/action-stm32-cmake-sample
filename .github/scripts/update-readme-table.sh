#!/bin/bash
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-uoohyo/action-stm32-cmake-sample}"
WORKFLOWS_URL="https://github.com/${REPO}/actions/workflows"

# 테이블 헤더 생성
TABLE=$(cat <<'EOF'
<!-- TEST_RESULTS_START -->

## Test Results

This table shows the build status for all tested STM32CubeCLT versions:

| STM32CubeCLT Version | Build Status | Configurations | Last Updated | Details |
|----------------------|--------------|----------------|--------------|---------|
EOF
)

# Check if test results directory exists and has JSON files
if [ ! -d ".github/test-results" ] || [ -z "$(ls -A .github/test-results/*.json 2>/dev/null)" ]; then
  echo "⚠️  No test results found. Skipping README update."
  echo "Run test workflows first, then trigger this workflow manually."
  echo "Directory exists: $([ -d ".github/test-results" ] && echo 'yes' || echo 'no')"
  echo "JSON files: $(find .github/test-results/ -name '*.json' 2>/dev/null | wc -l)"
  exit 0
fi

# 각 버전에 대한 행 추가 (버전 높은순으로 정렬)
ls .github/workflows/test-stm32-v*.yml | sed 's|.github/workflows/test-stm32-v||; s|.yml||' | sort -V -r > /tmp/versions_sorted.txt

while IFS= read -r VERSION; do
  RESULT_FILE=".github/test-results/${VERSION}.json"

  if [ -f "$RESULT_FILE" ]; then
    # 결과 파일에서 정보 추출
    STATUS=$(jq -r '.status' "$RESULT_FILE")
    TIMESTAMP=$(jq -r '.timestamp' "$RESULT_FILE")
    LOG_URL=$(jq -r '.log_url' "$RESULT_FILE")

    # GitHub Actions workflow status badge
    WORKFLOW_FILE="test-stm32-v${VERSION}.yml"
    BADGE_URL="https://img.shields.io/github/actions/workflow/status/${REPO}/${WORKFLOW_FILE}?branch=main&label="

    # 날짜 포맷팅
    FORMATTED_DATE=$(date -d "$TIMESTAMP" "+%Y-%m-%d")

    # 테이블 행 추가
    TABLE+="
| v${VERSION} | ![Build Status](${BADGE_URL}) | Debug, Release | ${FORMATTED_DATE} | [Logs](${LOG_URL}) |"
  else
    # 결과 파일이 없으면 워크플로우 배지 표시
    WORKFLOW_FILE="test-stm32-v${VERSION}.yml"
    BADGE_URL="https://img.shields.io/github/actions/workflow/status/${REPO}/${WORKFLOW_FILE}?branch=main&label="
    TABLE+="
| v${VERSION} | ![Build Status](${BADGE_URL}) | Debug, Release | - | [Workflow](${WORKFLOWS_URL}/${WORKFLOW_FILE}) |"
  fi
done < /tmp/versions_sorted.txt

# 테이블 마커 종료
TABLE+="

<!-- TEST_RESULTS_END -->"

# README.md 업데이트
if grep -q "<!-- TEST_RESULTS_START -->" README.md; then
  # 기존 섹션 교체
  awk -v table="$TABLE" '
    /<!-- TEST_RESULTS_START -->/ {
      print table
      skip=1
      next
    }
    /<!-- TEST_RESULTS_END -->/ {
      skip=0
      next
    }
    !skip
  ' README.md > README.md.tmp
  mv README.md.tmp README.md
else
  # README 끝에 추가
  echo "" >> README.md
  echo "$TABLE" >> README.md
fi

echo "✅ README.md updated successfully"
