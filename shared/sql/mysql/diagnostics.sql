SELECT UTC_TIMESTAMP() AS captured_at,VERSION() AS version;
SHOW FULL PROCESSLIST;
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Max_used_connections';
SHOW VARIABLES WHERE Variable_name IN ('log_error','max_connections','slow_query_log','slow_query_log_file','long_query_time','read_only');
SELECT * FROM performance_schema.data_lock_waits;
SHOW ENGINE INNODB STATUS;
EXPLAIN SELECT COUNT(*),SUM(amount) FROM support_lab.transactions WHERE player_id=42;
-- SHOW REPLICA STATUS\G requires a replica and suitable permission; an empty result on a standalone host is expected.
