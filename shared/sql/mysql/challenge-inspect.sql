-- Read-only evidence capture for the challenge dataset.
USE mysql_ticket_challenge;
SELECT UTC_TIMESTAMP() AS captured_utc, VERSION() AS server_version,
       @@hostname AS server_host, CURRENT_USER() AS account;
SHOW INDEX FROM ticket_sales;
EXPLAIN SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=42;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=42;
