-- Training database only. Destructive reset is explicit in setup/reset runbooks.
CREATE DATABASE IF NOT EXISTS support_lab;
USE support_lab;
CREATE TABLE IF NOT EXISTS players(id INT PRIMARY KEY,name VARCHAR(80),points INT NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS transactions(id INT PRIMARY KEY,player_id INT NOT NULL,amount DECIMAL(10,2),created_at DATETIME NOT NULL);
INSERT IGNORE INTO players VALUES(1,'Synthetic Player One',100),(2,'Synthetic Player Two',200),(42,'Synthetic Player Forty Two',300);
INSERT IGNORE INTO transactions
WITH digits AS (SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9)
SELECT a.n+10*b.n+100*c.n+1000*d.n+10000*e.n+1,
 MOD(a.n+10*b.n+100*c.n+1000*d.n+10000*e.n,100)+1,
 10.00,DATE_ADD('2026-01-01',INTERVAL MOD(a.n+10*b.n+100*c.n,365) DAY)
FROM digits a CROSS JOIN digits b CROSS JOIN digits c CROSS JOIN digits d CROSS JOIN digits e;
