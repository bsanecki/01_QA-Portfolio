-- Top 10 highest invoices
SELECT Customer.FirstName,Customer.LastName,Invoice.Total
FROM Customer
JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
ORDER BY Invoice.Total DESC
LIMIT 10;

-- Highest invoice per country
SELECT BillingCountry,MAX(Total)
FROM Invoice
GROUP BY BillingCountry;

-- Revenue by country
SELECT BillingCountry,SUM(Total)
FROM Invoice
GROUP BY BillingCountry
ORDER BY SUM(Total) DESC;

-- Top revenue country
SELECT BillingCountry,SUM(Total)
FROM Invoice
GROUP BY BillingCountry
ORDER BY SUM(Total) DESC
LIMIT 1;

-- Invoice statistics
SELECT AVG(Total) AS Average_Invoice,
       MAX(Total) AS MAX_Invoice,
       MIN(Total) AS MIN_Invoice
FROM Invoice;

-- Customers per country
SELECT Country,COUNT(CustomerId) AS Customers
FROM Customer
GROUP BY Country
ORDER BY Customers DESC;

-- Customers per city
SELECT City,COUNT(CustomerId) AS Customers
FROM Customer
GROUP BY City
ORDER BY Customers DESC;

-- Invoices below average
SELECT Customer.FirstName,Customer.LastName,Invoice.Total
FROM Customer
JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
WHERE Invoice.Total <
(
    SELECT AVG(Total)
    FROM Invoice
)
ORDER BY Invoice.Total DESC;

-- Invoices above average
SELECT Customer.FirstName,Customer.LastName,Invoice.Total
FROM Customer
JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
WHERE Invoice.Total >
(
    SELECT AVG(Total)
    FROM Invoice
)
ORDER BY Invoice.Total DESC;

-- Invoice count per customer
SELECT CustomerId,COUNT(InvoiceId)
FROM Invoice
GROUP BY CustomerId
ORDER BY COUNT(InvoiceId) DESC;

-- Customers with more than 3 invoices
SELECT CustomerId,COUNT(InvoiceId)
FROM Invoice
GROUP BY CustomerId
HAVING COUNT(InvoiceId) > 3
ORDER BY COUNT(InvoiceId) DESC;

-- Top 5 countries by customers
SELECT Country,COUNT(CustomerId)
FROM Customer
GROUP BY Country
ORDER BY COUNT(CustomerId) DESC
LIMIT 5;

-- Customer spending report
SELECT Customer.FirstName,
       Customer.LastName,
       COUNT(Customer.CustomerId) AS quantity_invoices,
       SUM(Invoice.Total) AS total_expenditure,
       AVG(Invoice.Total) AS Average_invoice
FROM Customer
JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
GROUP BY Customer.CustomerId,
         Customer.FirstName,
         Customer.LastName;
