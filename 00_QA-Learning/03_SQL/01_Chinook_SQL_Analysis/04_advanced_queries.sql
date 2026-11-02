-- Customers without invoices
SELECT Customer.FirstName,Customer.LastName FROM Customer
LEFT JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
WHERE Invoice.InvoiceId IS NULL;

-- Customers with purchases in multiple countries
SELECT Customer.FirstName,
       Customer.LastName,
       COUNT(DISTINCT Invoice.BillingCountry) AS Billing_countries
FROM Customer
JOIN Invoice
ON Customer.CustomerId = Invoice.CustomerId
GROUP BY Customer.CustomerId,
         Customer.FirstName,
         Customer.LastName
HAVING COUNT(DISTINCT Invoice.BillingCountry) > 1
ORDER BY Billing_countries DESC;

-- Top sales month
SELECT strftime('%m', InvoiceDate) AS Month,
       SUM(Total) AS Revenue
FROM Invoice
GROUP BY Month
ORDER BY Revenue DESC
LIMIT 1;

-- Artists above average album count
SELECT Artist.Name,
       COUNT(Album.AlbumId) AS Albums
FROM Artist
JOIN Album
ON Artist.ArtistId = Album.ArtistId
GROUP BY Artist.ArtistId,
         Artist.Name
HAVING COUNT(Album.AlbumId) >
(
    SELECT AVG(AlbumCount)
    FROM
    (
        SELECT COUNT(AlbumId) AS AlbumCount
        FROM Album
        GROUP BY ArtistId
    )
)
ORDER BY Albums DESC;
