-- Synthetic data for MYSQL_SUPPORT_DIAGNOSTICS.md; MySQL 8.0/8.4.
-- Run once on a training server. Deliberately fails if the database exists:
-- no DROP, replacement, or silent modification of an existing database.
-- Import without --force so an error stops execution.
CREATE DATABASE mysql_support_demo CHARACTER SET utf8mb4;
USE mysql_support_demo;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(80) NOT NULL,
    region VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),
    INDEX idx_orders_customer_date (customer_id, order_date)
) ENGINE=InnoDB;

START TRANSACTION;
INSERT INTO customers (customer_id, customer_name, region) VALUES
    (1, 'Demo Customer Alpha', 'Manila'),
    (2, 'Demo Customer Beta', 'Cebu'),
    (3, 'Demo Customer Gamma', 'Davao');

INSERT INTO orders (order_id, customer_id, order_date, status, total_amount) VALUES
    (1001, 1, '2026-10-01 09:00:00', 'paid', 49.90),
    (1002, 1, '2026-10-02 10:00:00', 'paid', 120.00),
    (1003, 2, '2026-10-03 11:00:00', 'pending', 35.00),
    (1004, 2, '2026-10-04 12:00:00', 'paid', 80.00),
    (1005, 3, '2026-10-05 13:00:00', 'cancelled', 19.95),
    (1006, 3, '2026-10-06 14:00:00', 'paid', 200.00);
COMMIT;

SELECT DATABASE() AS loaded_database,
       (SELECT COUNT(*) FROM customers) AS customers_loaded,
       (SELECT COUNT(*) FROM orders) AS orders_loaded;
SELECT status, COUNT(*) AS order_count, SUM(total_amount) AS total_amount
FROM orders GROUP BY status ORDER BY status;
