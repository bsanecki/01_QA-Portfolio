function metricValues(data, metricName) {
  return data.metrics?.[metricName]?.values || {};
}

function metricValue(data, metricName, valueName) {
  const value = metricValues(data, metricName)[valueName];
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function formatNumber(value, digits = 2) {
  return value === null ? 'N/A' : value.toFixed(digits);
}

function formatDuration(value) {
  if (value === null) return 'N/A';
  return value < 1000 ? `${formatNumber(value, 2)} ms` : `${formatNumber(value / 1000, 2)} s`;
}

function formatPercent(value) {
  return value === null ? 'N/A' : `${formatNumber(value * 100)}%`;
}

function markdownCell(value) {
  return String(value ?? 'N/A').replace(/\|/g, '\\|').replace(/[\r\n]+/g, ' ');
}

function getThresholdResults(data) {
  const results = [];

  for (const [metricName, metric] of Object.entries(data.metrics || {})) {
    for (const [name, result] of Object.entries(metric.thresholds || {})) {
      if (typeof result.ok === 'boolean') {
        results.push({ metricName, name, passed: result.ok });
      }
    }
  }

  return results;
}

function buildMarkdownReport({
  testName,
  generatedAt,
  target,
  profile,
  runId,
  status,
  metrics,
  thresholds,
  jsonRelativePath,
}) {
  const thresholdRows = thresholds.length
    ? thresholds.map((item) =>
      `| \`${markdownCell(item.metricName)}\` | \`${markdownCell(item.name)}\` | ${item.passed ? 'PASS' : '**FAIL**'} |`
    ).join('\n')
    : '| N/A | No thresholds were reported | N/A |';

  const checksSummary = metrics.checksTotal === null
    ? 'No check data was reported.'
    : `${metrics.checksPassed} of ${metrics.checksTotal} checks passed (${formatPercent(metrics.checkRate)}).`;

  const runNote = target.toLowerCase().includes('dummyjson.com')
    ? 'DummyJSON is a public mock API. These measurements are affected by network conditions and shared infrastructure; they are not a reliable capacity benchmark.'
    : 'Results describe this execution and target only. Compare runs only when the target and test conditions are comparable.';

  return `# ${testName.charAt(0).toUpperCase() + testName.slice(1)} Test Report

| Run detail | Value |
|---|---|
| **Status** | **${status}** |
| Generated (UTC) | ${generatedAt} |
| Run folder | ${markdownCell(runId)} |
| Target | ${markdownCell(target)} |
| Workload profile | ${markdownCell(profile)} |

## Summary

| Metric | Result |
|---|---:|
| HTTP requests | ${metrics.requests === null ? 'N/A' : metrics.requests} |
| Request rate | ${metrics.requestRate === null ? 'N/A' : `${formatNumber(metrics.requestRate)} requests/s`} |
| Failed request rate | ${formatPercent(metrics.failedRate)} |
| Average response time | ${formatDuration(metrics.avg)} |
| Median response time | ${formatDuration(metrics.med)} |
| Minimum response time | ${formatDuration(metrics.min)} |
| Maximum response time | ${formatDuration(metrics.max)} |
| p90 response time | ${formatDuration(metrics.p90)} |
| p95 response time | ${formatDuration(metrics.p95)} |
| Checks | ${checksSummary} |
| Peak virtual users | ${metrics.maxVus === null ? 'N/A' : metrics.maxVus} |
| Completed iterations | ${metrics.iterations === null ? 'N/A' : metrics.iterations} |
| Test duration | ${formatDuration(metrics.duration)} |
| Thresholds passed | ${metrics.thresholdsPassed}/${metrics.thresholdsTotal} |

## Threshold Results

| Metric | Threshold | Result |
|---|---|---|
${thresholdRows}

## Notes

- The status reflects the configured response checks and k6 thresholds for this run.
- ${runNote}
- No performance conclusion should be generalized beyond the conditions of this execution.

## Raw Data

[Open the full k6 summary JSON](./${jsonRelativePath})

---

*Generated automatically by the project's k6 reporting helper.*
`;
}

export function createSummaryReport(data, testName, details = {}) {
  const generatedAt = new Date().toISOString();
  const reportDir = String(__ENV.REPORT_DIR || '').replace(/\/+$/, '');

  if (!reportDir) {
    return {
      stdout: [
        '',
        `${testName.toUpperCase()} TEST REPORT`,
        'Reports were not saved because REPORT_DIR is not set.',
        `Run this scenario with: ./scripts/run-test.sh ${testName}`,
        '',
      ].join('\n'),
    };
  }

  const runId = reportDir.split('/').pop();
  const reportLabel = String(__ENV.REPORT_LABEL || testName).replace(/[^A-Za-z0-9_-]/g, '-');
  const jsonRelativePath = `jsons/${reportLabel}-summary.json`;
  const jsonPath = `${reportDir}/${jsonRelativePath}`;
  const markdownName = __ENV.REPORT_MARKDOWN_PATH || `${reportLabel}-report.md`;
  const markdownPath = `${reportDir}/${markdownName}`;
  const jsonOnly = __ENV.REPORT_JSON_ONLY === 'yes';

  const checks = metricValues(data, 'checks');
  const checksPassed = typeof checks.passes === 'number' ? checks.passes : null;
  const checkFails = typeof checks.fails === 'number' ? checks.fails : null;
  const checksTotal = checksPassed !== null && checkFails !== null
    ? checksPassed + checkFails
    : null;
  const checkRate = typeof checks.rate === 'number'
    ? checks.rate
    : checksTotal > 0 ? checksPassed / checksTotal : null;
  const requests = metricValue(data, 'http_reqs', 'count');
  const failedRate = metricValue(data, 'http_req_failed', 'rate');
  const thresholds = getThresholdResults(data);
  const thresholdsPassed = thresholds.filter((item) => item.passed).length;
  const thresholdsTotal = thresholds.length;
  const checksHaveFailed = checkFails !== null && checkFails > 0;
  const status = thresholdsTotal > 0 && thresholdsPassed === thresholdsTotal && !checksHaveFailed
    ? 'PASSED'
    : 'FAILED';

  const metrics = {
    requests,
    requestRate: metricValue(data, 'http_reqs', 'rate'),
    failedRate,
    avg: metricValue(data, 'http_req_duration', 'avg'),
    min: metricValue(data, 'http_req_duration', 'min'),
    med: metricValue(data, 'http_req_duration', 'med'),
    max: metricValue(data, 'http_req_duration', 'max'),
    p90: metricValue(data, 'http_req_duration', 'p(90)'),
    p95: metricValue(data, 'http_req_duration', 'p(95)'),
    checksPassed,
    checkFails,
    checksTotal,
    checkRate,
    maxVus: metricValue(data, 'vus_max', 'max') ?? metricValue(data, 'vus', 'max'),
    iterations: metricValue(data, 'iterations', 'count'),
    duration: typeof data.state?.testRunDurationMs === 'number' ? data.state.testRunDurationMs : null,
    thresholdsPassed,
    thresholdsTotal,
  };

  const target = details.target || 'Not provided';
  const profile = details.profile || 'Default';
  const metadata = {
    test: testName,
    status,
    generated_at_utc: generatedAt,
    target,
    profile,
    run_id: runId,
    markdown_report: markdownName,
    json_report: jsonPath,
    metrics,
  };
  const markdown = buildMarkdownReport({
    testName,
    generatedAt,
    target,
    profile,
    runId,
    status,
    metrics,
    thresholds,
    jsonRelativePath,
  });

  const thresholdSummary = thresholdsTotal
    ? `${thresholdsPassed}/${thresholdsTotal} passed`
    : 'No thresholds found';
  const consoleSummary = [
    '',
    `${testName.toUpperCase()} TEST REPORT`,
    `Status: ${status}`,
    `Generated (UTC): ${generatedAt}`,
    `Markdown report saved: ${markdownPath}`,
    `JSON data saved: ${jsonPath}`,
    `Checks pass rate: ${checkRate === null ? 'N/A' : formatPercent(checkRate)}`,
    `HTTP requests: ${requests === null ? 'N/A' : requests}`,
    `Failed request rate: ${formatPercent(failedRate)}`,
    `Response time p90: ${formatDuration(metrics.p90)}`,
    `Response time p95: ${formatDuration(metrics.p95)}`,
    `Thresholds: ${thresholdSummary}`,
    ...thresholds.filter((item) => !item.passed).map((item) => `FAILED: ${item.metricName}: ${item.name}`),
    '',
  ].join('\n');

  return {
    [jsonPath]: JSON.stringify({ report: metadata, summary: data }, null, 2),
    ...(jsonOnly ? {} : { [markdownPath]: markdown }),
    stdout: consoleSummary.replace(
      `Markdown report saved: ${markdownPath}`,
      jsonOnly
        ? `Markdown report will be created by the batch runner: ${markdownName}`
        : `Markdown report saved: ${markdownPath}`
    ),
  };
}
