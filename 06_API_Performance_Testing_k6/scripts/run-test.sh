#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

TEST_NAME="${1:-}"
case "$TEST_NAME" in
  smoke|load|stress) ;;
  *)
    echo "Usage: ./scripts/run-test.sh {smoke|load|stress}" >&2
    exit 2
    ;;
esac

if ! command -v k6 >/dev/null 2>&1; then
  echo "Error: k6 is not installed or not on PATH." >&2
  exit 1
fi

if [[ ! -f "tests/${TEST_NAME}.js" ]]; then
  echo "Error: tests/${TEST_NAME}.js was not found." >&2
  exit 1
fi

if [[ -z "${REPORT_DIR:-}" ]]; then
  CATEGORY_DIR="results/${TEST_NAME}_data"
  TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
  RUN_DIR="${CATEGORY_DIR}/${TIMESTAMP}"
  SUFFIX=2
  while [[ -e "$RUN_DIR" ]]; do
    RUN_DIR="${CATEGORY_DIR}/${TIMESTAMP}_$(printf '%02d' "$SUFFIX")"
    SUFFIX=$((SUFFIX + 1))
  done
  REPORT_DIR="$RUN_DIR"
else
  RUN_DIR="$REPORT_DIR"
fi

REPORT_LABEL="${REPORT_LABEL:-$TEST_NAME}"
REPORT_MARKDOWN_PATH="${REPORT_MARKDOWN_PATH:-${REPORT_LABEL}-report.md}"
mkdir -p "$RUN_DIR/jsons"
export REPORT_DIR REPORT_LABEL REPORT_MARKDOWN_PATH

printf 'Starting %s test.\n' "$TEST_NAME"
printf 'Run folder: %s\n\n' "$RUN_DIR"

k6 run "tests/${TEST_NAME}.js"
K6_STATUS=$?

JSON_PATH="$RUN_DIR/jsons/${REPORT_LABEL}-summary.json"
if [[ "${REPORT_JSON_ONLY:-no}" == "yes" ]]; then
  if [[ ! -f "$JSON_PATH" ]]; then
    printf '\nWarning: k6 did not create the expected JSON report: %s\n' "$JSON_PATH" >&2
    exit 1
  fi
else
  MARKDOWN_PATH="$RUN_DIR/$REPORT_MARKDOWN_PATH"
  if [[ ! -f "$MARKDOWN_PATH" || ! -f "$JSON_PATH" ]]; then
    printf '\nWarning: k6 did not create both expected report files. Check the output above.\n' >&2
    exit 1
  fi
fi

printf '\nReports saved to: %s\n' "$RUN_DIR"
exit "$K6_STATUS"
