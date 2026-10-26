import { sleep } from 'k6';
import { BASE_URL, THINK_TIME } from '../config/config.js';
import { getProduct, listProducts, searchProducts } from '../lib/api.js';
import { createSummaryReport } from '../lib/report.js';

const ITERATIONS = Number(__ENV.SMOKE_ITERATIONS || 3);

if (!Number.isSafeInteger(ITERATIONS) || ITERATIONS < 1) {
  throw new Error('SMOKE_ITERATIONS must be a positive integer.');
}

export const options = {
  vus: 1,
  iterations: ITERATIONS,
  thresholds: {
    checks: ['rate==1'],
    http_req_failed: ['rate==0'],
    http_req_duration: ['p(90)<1000', 'p(95)<1500'],
    http_reqs: [`count>=${ITERATIONS * 3}`],
  },
};

export default function () {
  getProduct();
  listProducts();
  searchProducts();
  sleep(THINK_TIME);
}

export function handleSummary(data) {
  return createSummaryReport(data, 'smoke', {
    target: BASE_URL,
    profile: `1 VU, ${ITERATIONS} iterations`,
    fileLabel: `${ITERATIONS}-iterations`,
  });
}
