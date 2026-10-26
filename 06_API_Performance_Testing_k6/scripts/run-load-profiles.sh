#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v k6 >/dev/null 2>&1; then
  echo "Error: k6 is not installed or not on PATH." >&2
  exit 1
fi

BASE_URL="${BASE_URL:-https://dummyjson.com}"
if [[ "${BASE_URL,,}" == *"dummyjson.com"* ]]; then
  RAMP="10s"
  HOLD="15s"
  echo "Warning: using public DummyJSON with capped profiles (1, 5, and 10 VUs)."
  echo "These are short learning runs, not a reliable capacity benchmark."
else
  if [[ "${CONFIRM_AUTHORIZED:-}" != "yes" ]]; then
    echo "Error: set CONFIRM_AUTHORIZED=yes to confirm you are authorized to load-test this target." >&2
    exit 1
  fi
  RAMP="${LOAD_RAMP:-15s}"
  HOLD="${LOAD_HOLD:-30s}"
fi

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
RUN_DIR="results/load_data/${TIMESTAMP}"
SUFFIX=2
while [[ -e "$RUN_DIR" ]]; do
  RUN_DIR="results/load_data/${TIMESTAMP}_$(printf '%02d' "$SUFFIX")"
  SUFFIX=$((SUFFIX + 1))
done
mkdir -p "$RUN_DIR/jsons"

FAILED=0
PROFILES=(1 5 10)

for VUS in "${PROFILES[@]}"; do
  PROFILE_LABEL="load-${VUS}-vu"
  echo
  echo "============================================================"
  echo "Running load profile: ${VUS} virtual user(s)"
  echo "Ramp: ${RAMP}; hold: ${HOLD}"
  echo "Shared run folder: ${RUN_DIR}"
  echo "============================================================"

  REPORT_DIR="$RUN_DIR" \
  REPORT_LABEL="$PROFILE_LABEL" \
  REPORT_JSON_ONLY=yes \
  REPORT_MARKDOWN_PATH="load-comparison.md" \
  BASE_URL="$BASE_URL" \
  LOAD_VUS="$VUS" \
  LOAD_RAMP="$RAMP" \
  LOAD_HOLD="$HOLD" \
  "$SCRIPT_DIR/run-test.sh" load || FAILED=1
done

json_value() {
  local file="$1"
  local key="$2"
  grep -m 1 -E "^[[:space:]]*\"${key}\"[[:space:]]*:" "$file" \
    | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:],]+$//; s/^"//; s/"$//'
}

format_ms() {
  local value="${1:-}"
  if [[ -z "$value" || "$value" == "null" ]]; then
    printf 'N/A'
  else
    awk -v value="$value" 'BEGIN { if (value >= 1000) printf "%.2f s", value / 1000; else printf "%.2f ms", value }'
  fi
}

format_percent() {
  local value="${1:-}"
  if [[ -z "$value" || "$value" == "null" ]]; then
    printf 'N/A'
  else
    awk -v value="$value" 'BEGIN { printf "%.2f%%", value * 100 }'
  fi
}

for VUS in "${PROFILES[@]}"; do
  JSON_PATH="$RUN_DIR/jsons/load-${VUS}-vu-summary.json"
  if [[ ! -f "$JSON_PATH" ]] || [[ "$(json_value "$JSON_PATH" status)" != "PASSED" ]]; then
    FAILED=1
  fi
done

GENERATED_AT="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
OVERALL_STATUS="PASSED"
[[ "$FAILED" -eq 0 ]] || OVERALL_STATUS="FAILED"

{
  echo "# Load Test Profile Comparison"
  echo
  echo "| Run detail | Value |"
  echo "|---|---|"
  echo "| **Overall status** | **${OVERALL_STATUS}** |"
  echo "| Generated | ${GENERATED_AT} |"
  echo "| Target | ${BASE_URL} |"
  echo "| Profiles | 1, 5, and 10 virtual users |"
  echo "| Ramp / hold | ${RAMP} / ${HOLD} |"
  echo
  echo "## Results by profile"
  echo
  echo "| Profile | Status | Requests | Failed rate | Average | p90 | p95 | Checks | Thresholds |"
  echo "|---:|---|---:|---:|---:|---:|---:|---|---:|"

  for VUS in "${PROFILES[@]}"; do
    PROFILE_LABEL="load-${VUS}-vu"
    JSON_PATH="$RUN_DIR/jsons/${PROFILE_LABEL}-summary.json"
    if [[ ! -f "$JSON_PATH" ]]; then
      echo "| ${VUS} VU(s) | **FAILED** | N/A | N/A | N/A | N/A | N/A | N/A | N/A |"
      OVERALL_STATUS="FAILED"
      continue
    fi

    STATUS="$(json_value "$JSON_PATH" status)"
    REQUESTS="$(json_value "$JSON_PATH" requests)"
    FAILED_RATE="$(json_value "$JSON_PATH" failedRate)"
    AVG="$(json_value "$JSON_PATH" avg)"
    P90="$(json_value "$JSON_PATH" p90)"
    P95="$(json_value "$JSON_PATH" p95)"
    CHECKS_PASSED="$(json_value "$JSON_PATH" checksPassed)"
    CHECKS_TOTAL="$(json_value "$JSON_PATH" checksTotal)"
    CHECK_RATE="$(json_value "$JSON_PATH" checkRate)"
    THRESHOLDS_PASSED="$(json_value "$JSON_PATH" thresholdsPassed)"
    THRESHOLDS_TOTAL="$(json_value "$JSON_PATH" thresholdsTotal)"

    [[ "$STATUS" == "PASSED" ]] || OVERALL_STATUS="FAILED"
    [[ -n "$CHECKS_PASSED" ]] || CHECKS_PASSED=0
    [[ -n "$CHECKS_TOTAL" ]] || CHECKS_TOTAL=0
    CHECKS="${CHECKS_PASSED}/${CHECKS_TOTAL} ($(format_percent "$CHECK_RATE"))"
    THRESHOLDS="${THRESHOLDS_PASSED:-0}/${THRESHOLDS_TOTAL:-0}"

    echo "| ${VUS} VU(s) | ${STATUS:-FAILED} | ${REQUESTS:-N/A} | $(format_percent "$FAILED_RATE") | $(format_ms "$AVG") | $(format_ms "$P90") | $(format_ms "$P95") | ${CHECKS} | ${THRESHOLDS} |"
  done

  echo
  echo "## Interpretation"
  echo
  echo "- The profiles ran sequentially against the same target with the same request mix."
  echo "- Compare request counts and response-time percentiles across profiles; the elapsed wall-clock runs and public network conditions can affect results."
  echo "- DummyJSON is a shared public mock API. These short, capped runs are for learning and workflow validation, not a reliable capacity benchmark."
  echo "- A passing result means the configured checks and thresholds passed for that run; it does not establish the maximum capacity of the service."
  echo
  echo "## Raw data"
  echo
  for VUS in "${PROFILES[@]}"; do
    PROFILE_LABEL="load-${VUS}-vu"
    if [[ -f "$RUN_DIR/jsons/${PROFILE_LABEL}-summary.json" ]]; then
      echo "- [${VUS} VU profile JSON](./jsons/${PROFILE_LABEL}-summary.json)"
    else
      echo "- ${VUS} VU profile: JSON report missing"
    fi
  done
  echo
  echo "---"
  echo
  echo "*Generated automatically by scripts/run-load-profiles.sh.*"
} > "$RUN_DIR/load-comparison.md"

if [[ "$OVERALL_STATUS" != "PASSED" ]]; then
  FAILED=1
fi

printf '\nLoad comparison report saved to: %s/load-comparison.md\n' "$RUN_DIR"
printf 'JSON summaries saved under: %s/jsons/\n' "$RUN_DIR"
if [[ "$FAILED" -eq 0 ]]; then
  echo "All load profiles completed successfully."
else
  echo "One or more load profiles failed. Review the comparison report." >&2
fi
exit "$FAILED"
