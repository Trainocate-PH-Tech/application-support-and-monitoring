-- Admin only; dedicated training database, import WITHOUT --force.
-- Existing table causes failure; do not overwrite learner data on reruns.
USE mysql_support_demo;
CREATE TABLE analysis_orders (
 id INT PRIMARY KEY, customer_id INT NOT NULL, amount DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;
INSERT INTO analysis_orders (id,customer_id,amount)
WITH digits AS (SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3
 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7
 UNION ALL SELECT 8 UNION ALL SELECT 9)
SELECT 1+a.n+10*b.n+100*c.n+1000*d.n+10000*e.n,
 MOD(a.n+10*b.n+100*c.n+1000*d.n+10000*e.n,100)+1,10.00
FROM digits a CROSS JOIN digits b CROSS JOIN digits c CROSS JOIN digits d CROSS JOIN digits e;
SELECT COUNT(*) AS total_rows FROM analysis_orders;
SELECT COUNT(*) AS matching_rows,SUM(amount) AS total_amount
FROM analysis_orders WHERE customer_id=42;
