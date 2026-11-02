# Bug Report — Data Quality Audit

Findings from running `01_data_integrity_checks.sql` against `shop_qa.db`.

| Bug ID | Description | Query | Expected | Actual | Severity |
|---|---|---|---|---|---|
| BUG-001 | Customer record with a missing (NULL) email address | Check 1 | Every customer has a valid email | Customer id 6 has `email = NULL` | Medium |
| BUG-002 | Duplicate email address shared by two customer accounts | Check 2 | Each email is unique across customers | `anna.kowalska@mail.com` is used by 2 customer records | High |
| BUG-003 | Product listed with a negative price | Check 3 | Product prices are always ≥ 0 | "Webcam HD" has `price = -49.99` | High |
| BUG-004 | Product with zero or negative stock level | Check 4 | Stock quantity is always ≥ 0 | "Laptop Stand" has `stock = -5` | High |
| BUG-005 | Order linked to a customer ID that doesn't exist | Check 5 | Every order references a valid, existing customer | Order id 5 references `customer_id = 99`, which is not in `customers` | Critical |
| BUG-006 | Order placed before the customer's account registration date | Check 6 | `order_date` is always on or after `registration_date` | Order id 6 dated 2022-12-01, customer registered 2023-01-15 | Medium |
| BUG-007 | Order total does not match the sum of its line items | Check 7 | `order_total` equals `SUM(quantity * unit_price)` for that order | Order id 7 stores `order_total = 100.00`, calculated total is `59.97` | High |
| BUG-008 | Order item linked to a product ID that doesn't exist | Check 8 | Every order item references a valid, existing product | An order item references `product_id = 999`, which is not in `products` | Critical |

## Summary

- **8 issues found**, spanning missing data, duplicate records, invalid value ranges, broken referential integrity, and inconsistent calculated totals.
- **2 Critical**, **3 High**, **3 Medium** — no issues were rated Low, as every finding represents either broken data relationships or values that would visibly affect a customer-facing total or listing.
- All issues would need to be raised with the development team before this dataset could be considered production-ready.
