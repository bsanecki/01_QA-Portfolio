import { sleep } from 'k6';
import { BASE_URL, THINK_TIME } from '../config/config.js';
import { getProduct, listProducts, searchProducts } from '../lib/api.js';
import { createSummaryReport } from '../lib/report.js';

const IS_PUBLIC_DUMMYJSON = BASE_URL.toLowerCase().includes('dummyjson.com');

if (!IS_PUBLIC_DUMMYJSON && __ENV.CONFIRM_AUTHORIZED !== 'yes') {
  throw new Error('Load test refused: set CONFIRM_AUTHORIZED=yes to confirm authorization.');
}

const VUS = Number(__ENV.LOAD_VUS || 5);
const RAMP = IS_PUBLIC_DUMMYJSON ? '10s' : (__ENV.LOAD_RAMP || '30s');
const HOLD = IS_PUBLIC_DUMMYJSON ? '15s' : (__ENV.LOAD_HOLD || '1m');
const MAX_VUS = IS_PUBLIC_DUMMYJSON ? 10 : 100;

if (!Number.isSafeInteger(VUS) || VUS < 1 || VUS > MAX_VUS) {
  throw new Error(`LOAD_VUS must be an integer between 1 and ${MAX_VUS} for this target.`);
}

if (IS_PUBLIC_DUMMYJSON) {
  console.warn('Public DummyJSON target: using a short, capped learning load profile (max 10 VUs).');
}

export const options = {
  stages: [
    { duration: RAMP, target: VUS },
    { duration: HOLD, target: VUS },
    { duration: RAMP, target: 0 },
  ],
  thresholds: {
    checks: ['rate>0.99'],
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(90)<800', 'p(95)<1200'],
    'http_req_duration{name:product_by_id}': ['p(95)<1000'],
    'http_req_duration{name:product_list}': ['p(95)<1200'],
    'http_req_duration{name:product_search}': ['p(95)<1500'],
  },
};

export default function () {
  getProduct();
  listProducts();
  searchProducts();
  sleep(THINK_TIME);
}

export function handleSummary(data) {
  return createSummaryReport(data, 'load', {
    target: BASE_URL,
    profile: `${VUS} virtual user${VUS === 1 ? '' : 's'}`,
    fileLabel: `${VUS}-vu${VUS === 1 ? '' : 's'}`,
  });
}
