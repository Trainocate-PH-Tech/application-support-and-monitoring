-- Finite, read-only training batch. Run with the supplied challenge reader.
USE mysql_ticket_challenge;
SET SESSION long_query_time = 0;
SELECT SLEEP(8) AS heartbeat_probe;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=42;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=43;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=44;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=45;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=46;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=47;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=48;
SELECT COUNT(*) AS sales_count, SUM(amount) AS sales_total FROM ticket_sales WHERE event_id=49;
