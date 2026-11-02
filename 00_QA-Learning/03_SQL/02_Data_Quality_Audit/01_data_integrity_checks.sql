

-- Customers with a missing email address
SELECT customers.id,customers.first_name,customers.last_name,customers.email FROM customers
WHERE customers.email IS NULL
GROUP BY customers.email;

-- Duplicate email addresses
SELECT email, COUNT(*) 
FROM customers
GROUP BY email
HAVING COUNT(*) > 1;

-- Products with a negative price
SELECT name,price FROM products
WHERE price < 0;

-- Products with zero or negative stock
SELECT name,stock FROM productS
WHERE stock <= 0;

-- Orders referencing a non-existent customer
SELECT orders.id, orders.customer_id
FROM orders
LEFT JOIN customers
ON orders.customer_id = customers.id
WHERE customers.id IS NULL;

-- Orders placed before the customer's registration date
SELECT orders.customer_id,orders.order_date FROM orders
JOIN customers
ON orders.customer_id = customers.id
WHERE orders.order_date < customers.registration_date;

-- Orders where the stored total doesn't match the sum of order items
SELECT orders.id, SUM(order_items.quantity * order_items.unit_price) AS ord_total, orders.order_total
FROM order_items
JOIN orders
ON order_items.order_id = orders.id
GROUP BY orders.id
HAVING ord_total != orders.order_total;

-- Order items referencing a non-existent product
SELECT order_items.product_id,products.id FROM order_items
LEFT JOIN products
ON Order_items.product_id = products.id
WHERE products.id IS NULL;

