export const DEFAULT_BASE_URL = 'https://dummyjson.com';

const configuredBaseUrl = __ENV.BASE_URL || DEFAULT_BASE_URL;

if (!/^https?:\/\//i.test(configuredBaseUrl)) {
  throw new Error('BASE_URL must start with http:// or https://.');
}

function positiveInteger(name, value, fallback) {
  const parsed = Number(value || fallback);
  if (!Number.isSafeInteger(parsed) || parsed < 1) {
    throw new Error(`${name} must be a positive integer.`);
  }
  return parsed;
}

export const BASE_URL = configuredBaseUrl.replace(/\/+$/, '');
export const PRODUCT_ID = positiveInteger('PRODUCT_ID', __ENV.PRODUCT_ID, 1);
export const LIST_LIMIT = positiveInteger('LIST_LIMIT', __ENV.LIST_LIMIT, 10);
export const SEARCH_QUERY = __ENV.SEARCH_QUERY || 'phone';
export const THINK_TIME = Number(__ENV.THINK_TIME || 1);

if (!Number.isFinite(THINK_TIME) || THINK_TIME < 0) {
  throw new Error('THINK_TIME must be a non-negative number.');
}
