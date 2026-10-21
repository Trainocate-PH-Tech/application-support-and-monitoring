SELECT SYSUTCDATETIME() AS captured_at,@@VERSION AS version;
SELECT session_id,status,command,cpu_time,total_elapsed_time,wait_type,wait_time,
 blocking_session_id,DB_NAME(database_id) AS database_name
FROM sys.dm_exec_requests WHERE session_id<>@@SPID;
SELECT session_id,login_name,host_name,program_name,status,open_transaction_count
FROM sys.dm_exec_sessions WHERE is_user_process=1;
SELECT TOP(20) wait_type,waiting_tasks_count,wait_time_ms,signal_wait_time_ms
FROM sys.dm_os_wait_stats ORDER BY wait_time_ms DESC;
SELECT TOP(10) qs.execution_count,qs.total_worker_time,qs.total_elapsed_time,
 qs.total_logical_reads,t.text,p.query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) t
CROSS APPLY sys.dm_exec_query_plan(qs.plan_handle) p
ORDER BY qs.total_worker_time DESC;
USE SupportLab;
SELECT TOP(20) q.query_id,p.plan_id,r.count_executions,r.avg_duration,
 r.avg_cpu_time,r.avg_logical_io_reads,i.start_time,i.end_time,t.query_sql_text
FROM sys.query_store_query q
JOIN sys.query_store_query_text t ON q.query_text_id=t.query_text_id
JOIN sys.query_store_plan p ON p.query_id=q.query_id
JOIN sys.query_store_runtime_stats r ON r.plan_id=p.plan_id
JOIN sys.query_store_runtime_stats_interval i ON i.runtime_stats_interval_id=r.runtime_stats_interval_id
ORDER BY i.start_time DESC,r.avg_duration DESC;
USE msdb;
-- Use the supported history procedure so SQLAgentReaderRole can inspect jobs
-- without granting direct SELECT on msdb system base tables.
EXEC dbo.sp_help_jobhistory @job_name=N'SupportLab-IntentionalFailure', @mode=N'FULL';
GO
USE SupportLab;
SELECT s.name AS statistic_name,p.last_updated,p.rows,p.rows_sampled,p.modification_counter
FROM sys.stats s
CROSS APPLY sys.dm_db_stats_properties(s.object_id,s.stats_id) p
WHERE s.object_id=OBJECT_ID(N'dbo.Transactions');
-- Instructor-only hypothesis test if justified:
-- UPDATE STATISTICS dbo.Transactions;
-- Repeat the same workload/plan comparison; never infer success from command completion alone.
