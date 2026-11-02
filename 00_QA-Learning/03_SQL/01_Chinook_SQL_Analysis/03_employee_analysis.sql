-- Employees without customers
SELECT Employee.FirstName,Employee.LastName
FROM Employee
LEFT JOIN Customer
ON Employee.EmployeeId = Customer.SupportRepId
WHERE Customer.CustomerId IS NULL;

-- Customers and support representatives
SELECT Customer.FirstName,Customer.LastName,
       Employee.FirstName,Employee.LastName
FROM Customer
JOIN Employee
ON Customer.SupportRepId = Employee.EmployeeId;

-- Employee with most customers
SELECT Employee.FirstName,Employee.LastName,
       COUNT(Customer.CustomerId) AS Customers
FROM Employee
JOIN Customer
ON Employee.EmployeeId = Customer.SupportRepId
GROUP BY Employee.EmployeeId,Employee.FirstName,Employee.LastName
ORDER BY Customers DESC
LIMIT 1;

-- Employee with fewest customers
SELECT Employee.FirstName,Employee.LastName,
       COUNT(Customer.CustomerId) AS Customers
FROM Employee
JOIN Customer
ON Employee.EmployeeId = Customer.SupportRepId
GROUP BY Employee.EmployeeId,Employee.FirstName,Employee.LastName
ORDER BY Customers ASC
LIMIT 1;

-- Revenue by employee
SELECT Employee.FirstName,Employee.LastName,
       SUM(Invoice.Total) AS Revenue
FROM Employee
JOIN Customer
ON Employee.EmployeeId = Customer.SupportRepId
JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
GROUP BY Employee.EmployeeId,Employee.FirstName,Employee.LastName
ORDER BY Revenue DESC;
