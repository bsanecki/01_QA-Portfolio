-- Top 3 earning genres
SELECT Genre.Name, SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity)
FROM Genre
JOIN Track
ON Genre.GenreId = Track.GenreId
JOIN InvoiceLine
ON Track.TrackId = InvoiceLine.TrackId
GROUP BY Genre.Name
ORDER BY SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) DESC
LIMIT 3;

-- Tracks sold by genre
SELECT Genre.Name, COUNT(Invoice.InvoiceId) AS Total_sales FROM Genre
JOIN Track
ON Genre.GenreId = Track.GenreId
JOIN InvoiceLine
ON Track.TrackId = InvoiceLine.TrackId
JOIN Invoice
ON InvoiceLine.InvoiceId = Invoice.InvoiceId
GROUP BY Genre.Name
ORDER BY Total_sales DESC;

-- Top 5 best selling tracks
SELECT Track.Name,COUNT(Invoice.InvoiceId) AS SALES FROM Track
JOIN InvoiceLine
ON Track.TrackId = InvoiceLine.TrackId
JOIN Invoice 
ON InvoiceLine.InvoiceId = Invoice.InvoiceId
GROUP BY Track.Name
ORDER BY SALES DESC
LIMIT 5;

-- Top earning artist
SELECT Artist.Name,SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS Revenue
FROM Artist
JOIN Album
ON Artist.ArtistId = Album.ArtistId
JOIN Track
ON Album.AlbumId = Track.AlbumId
JOIN InvoiceLine
ON Track.TrackId = InvoiceLine.TrackId
GROUP BY Artist.Name
ORDER BY Revenue DESC
LIMIT 1;

-- Revenue by artist
SELECT Artist.Name,SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS Revenue
FROM Artist
JOIN Album
ON Artist.ArtistId = Album.ArtistId
JOIN Track
ON Album.AlbumId = Track.AlbumId
JOIN InvoiceLine
ON Track.TrackId = InvoiceLine.TrackId
GROUP BY Artist.Name
ORDER BY Revenue DESC;

-- Best selling album
SELECT Album.Title,SUM(InvoiceLine.Quantity) AS Sales
FROM Album
JOIN Track
ON Album.AlbumId = Track.AlbumId
JOIN InvoiceLine
ON Track.TrackId = InvoiceLine.TrackId
GROUP BY Album.Title
ORDER BY Sales DESC
LIMIT 1;

-- Track count per album
SELECT Album.Title,COUNT(Track.TrackId) AS Tracks
FROM Album
JOIN Track
ON Album.AlbumId = Track.AlbumId
GROUP BY Album.Title
ORDER BY Tracks DESC;
