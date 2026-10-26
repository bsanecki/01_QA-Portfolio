import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, PRODUCT_ID, LIST_LIMIT, SEARCH_QUERY } from '../config/config.js';

function parseJson(res) {
  try {
    return res.json();
  } catch (error) {
    return null;
  }
}

function isJson(res) {
  const headerName = Object.keys(res.headers).find((name) => name.toLowerCase() === 'content-type');
  return Boolean(headerName && String(res.headers[headerName]).toLowerCase().includes('application/json'));
}

function hasIdAndTitle(product) {
  return product !== null &&
    typeof product === 'object' &&
    Number.isInteger(product.id) &&
    typeof product.title === 'string' &&
    product.title.trim() !== '';
}

export function getProduct() {
  const res = http.get(`${BASE_URL}/products/${PRODUCT_ID}`, {
    tags: { name: 'product_by_id' },
  });
  const body = parseJson(res);

  check(res, {
    'GET /products/{id}: status is 200': (r) => r.status === 200,
    'GET /products/{id}: content type is JSON': isJson,
    'GET /products/{id}: id matches the request': () => body !== null && body.id === PRODUCT_ID,
    'GET /products/{id}: has title and numeric price': () =>
      body !== null && hasIdAndTitle(body) && Number.isFinite(body.price),
  });
  return res;
}

export function listProducts() {
  const res = http.get(`${BASE_URL}/products?limit=${LIST_LIMIT}`, {
    tags: { name: 'product_list' },
  });
  const body = parseJson(res);
  const products = body !== null && Array.isArray(body.products) ? body.products : null;

  check(res, {
    'GET /products: status is 200': (r) => r.status === 200,
    'GET /products: content type is JSON': isJson,
    'GET /products: returns the expected page size': () =>
      products !== null &&
      Number.isInteger(body.total) &&
      body.total >= 0 &&
      body.limit === LIST_LIMIT &&
      products.length === Math.min(LIST_LIMIT, body.total),
    'GET /products: total is not smaller than the page': () =>
      products !== null && Number.isInteger(body.total) && body.total >= products.length,
    'GET /products: every product has id and title': () =>
      products !== null && products.every(hasIdAndTitle),
  });
  return res;
}

export function searchProducts() {
  const res = http.get(`${BASE_URL}/products/search?q=${encodeURIComponent(SEARCH_QUERY)}`, {
    tags: { name: 'product_search' },
  });
  const body = parseJson(res);
  const products = body !== null && Array.isArray(body.products) ? body.products : null;

  check(res, {
    'GET /products/search: status is 200': (r) => r.status === 200,
    'GET /products/search: content type is JSON': isJson,
    'GET /products/search: returns at least one product': () =>
      products !== null && products.length > 0,
    'GET /products/search: total is not smaller than the page': () =>
      products !== null && Number.isInteger(body.total) && body.total >= products.length,
    'GET /products/search: every product has id and title': () =>
      products !== null && products.every(hasIdAndTitle),
  });
  return res;
}
