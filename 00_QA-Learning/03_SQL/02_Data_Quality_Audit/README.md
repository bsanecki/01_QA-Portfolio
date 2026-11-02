# Data Quality Audit

SQL project focused on validating data integrity in a small e-commerce database — the kind of checks a QA tester runs to catch data-related bugs before they reach production.

## Dataset

Custom SQLite database (`shop_qa.db`) simulating a simple e-commerce shop: `customers`, `products`, `orders`, `order_items`. The dataset was seeded with intentionally injected data issues to simulate real-world QA validation scenarios (duplicate records, missing values, broken relationships between tables, and inconsistent totals).

## Files

- `01_data_integrity_checks.sql`
- `shop_qa.db`

## Checks Performed

1. Duplicate email addresses in `customers`
2. Missing (NULL) email addresses
3. Products with a negative price
4. Products with a negative stock level
5. Orders referencing a non-existent customer (orphaned foreign key)
6. Orders placed before the customer's registration date
7. Orders where the stored total doesn't match the sum of their line items
8. Order items referencing a non-existent product (orphaned foreign key)

## Skills Used

- SELECT
- JOIN (INNER, LEFT)
- GROUP BY
- HAVING
- COUNT()
- SUM()
- WHERE
- Data validation
- Referential integrity checks
- Duplicate detection
- NULL handling
