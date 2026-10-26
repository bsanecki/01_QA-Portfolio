import { sleep } from 'k6';
import { BASE_URL, THINK_TIME } from '../config/config.js';
import { getProduct, listProducts, searchProducts } from '../lib/api.js';
import { createSummaryReport } from '../lib/report.js';

const IS_PUBLIC_DUMMYJSON = BASE_URL.toLowerCase().includes('dummyjson.com');

if (!IS_PUBLIC_DUMMYJSON && __ENV.CONFIRM_AUTHORIZED !== 'yes') {
  throw new Error('Stress test refused: set CONFIRM_AUTHORIZED=yes to confirm authorization.');
}

if (IS_PUBLIC_DUMMYJSON && __ENV.ALLOW_PUBLIC_STRESS !== 'yes') {
  throw new Error('Public DummyJSON stress run requires ALLOW_PUBLIC_STRESS=yes. The profile is capped at 10 VUs.');
}

const MAX_VUS = Number(__ENV.STRESS_MAX_VUS || (IS_PUBLIC_DUMMYJSON ? 10 : 50));
const STEP = IS_PUBLIC_DUMMYJSON ? '10s' : (__ENV.STRESS_STEP_DURATION || '1m');
const RAMP_DOWN = IS_PUBLIC_DUMMYJSON ? '10s' : '30s';
const MAX_ALLOWED_VUS = IS_PUBLIC_DUMMYJSON ? 10 : 200;

if (!Number.isSafeInteger(MAX_VUS) || MAX_VUS < 1 || MAX_VUS > MAX_ALLOWED_VUS) {
  throw new Error(`STRESS_MAX_VUS must be an integer between 1 and ${MAX_ALLOWED_VUS} for this target.`);
}

if (IS_PUBLIC_DUMMYJSON) {
  console.warn('Public DummyJSON target: running a brief learning stress profile, fixed at 10-second stages and capped at 10 VUs.');
}

export const options = {
  stages: [
    ...[0.2, 0.4, 0.6, 0.8, 1].map((share) => ({
      duration: STEP,
      target: Math.max(1, Math.round(MAX_VUS * share)),
    })),
    { duration: RAMP_DOWN, target: 0 },
  ],
  thresholds: {
    checks: ['rate>0.95'],
    http_req_failed: [{ threshold: 'rate<0.05', abortOnFail: true, delayAbortEval: '30s' }],
    http_req_duration: [{ threshold: 'p(95)<3000', abortOnFail: true, delayAbortEval: '30s' }],
  },
};

export default function () {
  getProduct();
  listProducts();
  searchProducts();
  sleep(THINK_TIME);
}

export function handleSummary(data) {
  return createSummaryReport(data, 'stress', {
    target: BASE_URL,
    profile: `Ramp up to ${MAX_VUS} virtual users`,
    fileLabel: `${MAX_VUS}-vu${MAX_VUS === 1 ? '' : 's'}`,
  });
}
