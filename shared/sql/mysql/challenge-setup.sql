-- Instructor only, dedicated training server. Import WITHOUT --force.
-- A pre-existing database makes this fail; no data is dropped or overwritten.
CREATE DATABASE mysql_ticket_challenge CHARACTER SET utf8mb4;
USE mysql_ticket_challenge;
CREATE TABLE ticket_sales (
    sale_id INT PRIMARY KEY,
    event_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;
INSERT INTO ticket_sales (sale_id,event_id,amount)
WITH digits AS (SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3
 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7
 UNION ALL SELECT 8 UNION ALL SELECT 9)
SELECT 1+a.n+10*b.n+100*c.n+1000*d.n+10000*e.n,
 MOD(a.n+10*b.n+100*c.n+1000*d.n+10000*e.n,100)+1,25.00
FROM digits a CROSS JOIN digits b CROSS JOIN digits c CROSS JOIN digits d CROSS JOIN digits e;
SELECT COUNT(*) AS total_sales, SUM(amount) AS total_amount FROM ticket_sales;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=42;
