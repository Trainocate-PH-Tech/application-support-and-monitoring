# SQL Server Application Support Diagnostics

[Hands-on exercise](MSSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md) · [Module 2](module2/README.md)

**Environment:** SQL Server 2022 Developer on a dedicated training host; Ubuntu Bash with ODBC `sqlcmd` or a SQL query window. SQL Server syntax does not run in the MySQL client. Follow [SQL Server setup and permissions](shared/instructor/sqlserver-setup.md) first. An administrator initializes `SupportLab` using [setup.sql](shared/sql/sqlserver/setup.sql); this creates training data, enables Query Store, and creates a deliberately failing Agent job. Do not run it against production.

For ODBC sqlcmd, replace `SQL_HOST` and `YOUR_LOGIN`, and let the client prompt for the password:

```bash
/opt/mssql-tools18/bin/sqlcmd -S tcp:SQL_HOST,1433 -U YOUR_LOGIN -d SupportLab
```

Use a trusted certificate. `-C` is only an explicit certificate-validation bypass for disposable labs, not a production fix. In interactive sqlcmd, `GO` submits the batch and `QUIT` exits. Diagnostic visibility requires the grants in the setup guide, including SQL Server 2022 `VIEW SERVER PERFORMANCE STATE`; SQL text, Query Store, and msdb job history can require additional permissions. Access denied means unavailable evidence. Do not solve it by using `sa` for every learner query.

## Section: Identify the server and current requests

1. In a SQL query window or sqlcmd, establish identity:

   ```sql
   SELECT SYSUTCDATETIME() AS captured_utc, @@VERSION AS version,
          @@SERVERNAME AS server_name, ORIGINAL_LOGIN() AS login_name, DB_NAME() AS database_name;
   GO
   ```

2. Inspect requests with SQL text:

   ```sql
   SELECT r.session_id,r.status,r.command,r.cpu_time,r.total_elapsed_time,
          r.wait_type,r.wait_time,r.blocking_session_id,DB_NAME(r.database_id) AS db_name,
          t.text AS batch_text
   FROM sys.dm_exec_requests AS r
   OUTER APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
   WHERE r.session_id<>@@SPID;
   GO
   ```

3. Record that request CPU, elapsed, and wait times are milliseconds. Batch text can contain multiple statements and sensitive literals. A request snapshot does not establish what happened throughout the incident.

## Section: Include sessions and identify waits

1. Include sessions without active requests:

   ```sql
   SELECT s.session_id,s.status AS session_status,s.open_transaction_count,
          s.login_name,s.host_name,s.program_name,r.blocking_session_id,r.wait_type
   FROM sys.dm_exec_sessions AS s
   LEFT JOIN sys.dm_exec_requests AS r ON r.session_id=s.session_id
   WHERE s.is_user_process=1 AND s.session_id<>@@SPID;
   GO
   ```

2. Find waiting requests and follow positive blocker IDs. A sleeping session can hold locks. Use the [blocking guide](MSSQL_BLOCKING_PLAN_REGRESSION.md) to trace chains and special identifiers.
3. Do not infer that every wait is harmful or that an empty permitted result proves the server is idle. Check permissions and sample again at a known interval.

## Section: Find expensive cached queries and plans

1. Rank cumulative elapsed work and retain the execution count:

   ```sql
   SELECT TOP (10) qs.execution_count,
          qs.total_elapsed_time/1000.0 AS total_elapsed_ms,
          qs.total_elapsed_time/NULLIF(qs.execution_count,0)/1000.0 AS average_elapsed_ms,
          qs.total_worker_time/1000.0 AS total_cpu_ms,
          qs.total_logical_reads,t.text,p.query_plan
   FROM sys.dm_exec_query_stats AS qs
   CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS t
   OUTER APPLY sys.dm_exec_query_plan(qs.plan_handle) AS p
   ORDER BY qs.total_elapsed_time DESC;
   GO
   ```

2. Compare total versus per-execution cost. DMV elapsed/worker totals are microseconds before conversion, unlike the request fields above. Cache eviction or recompilation changes the observed lifetime.
3. Save plan XML when available using a capable SQL client. A cached plan is not an actual runtime plan; do not invent actual row counts from estimates. Missing plan XML is unavailable evidence, not a healthy plan. See [query statistics DMV](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-query-stats-transact-sql?view=sql-server-ver16).

## Section: Inspect Query Store history

1. In `SupportLab`, check availability:

   ```sql
   USE SupportLab;
   SELECT actual_state_desc,desired_state_desc,readonly_reason FROM sys.database_query_store_options;
   GO
   ```

2. Aggregate runtime rows by interval and plan, weighting by executions:

   ```sql
   USE SupportLab;
   SELECT TOP (20) q.query_id,p.plan_id,i.start_time,i.end_time,
          SUM(r.count_executions) AS executions,
          SUM(r.avg_duration*r.count_executions)/NULLIF(SUM(r.count_executions),0)/1000.0 AS avg_duration_ms,
          SUM(r.avg_logical_io_reads*r.count_executions)/NULLIF(SUM(r.count_executions),0) AS avg_reads
   FROM sys.query_store_query AS q
   JOIN sys.query_store_plan AS p ON p.query_id=q.query_id
   JOIN sys.query_store_runtime_stats AS r ON r.plan_id=p.plan_id
   JOIN sys.query_store_runtime_stats_interval AS i ON i.runtime_stats_interval_id=r.runtime_stats_interval_id
   WHERE r.execution_type=0
   GROUP BY q.query_id,p.plan_id,i.start_time,i.end_time
   ORDER BY i.start_time DESC;
   GO
   ```

3. Compare equal windows, parameters, and workload. Query Store writes asynchronously; an empty result immediately after setup can be expected. Do not enable it on a real server without the owner's configuration process. Runtime duration is in microseconds, and an active interval may contain multiple rows requiring aggregation. See [Query Store runtime statistics](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-query-store-runtime-stats-transact-sql?view=sql-server-ver16).

## Section: Investigate SQL Agent failures

1. Confirm with the instructor that Agent is enabled and the setup script created the deliberate failure job. SQL Server Express does not provide SQL Agent; edition/feature absence is different from no failures.
2. Administrator only, on the dedicated training server, run the unscheduled job once:

   ```sql
   EXEC msdb.dbo.sp_start_job @job_name=N'SupportLab-IntentionalFailure';
   GO
   ```

3. After completion, a diagnostic account with the configured msdb role reads:

   ```sql
   USE msdb;
   EXEC dbo.sp_help_jobhistory @job_name=N'SupportLab-IntentionalFailure',@mode=N'FULL';
   GO
   ```

4. Expect the explicit synthetic `THROW` failure. Inspect job, step, outcome, message, and run time. Step 0 is the job summary, not an additional failed step. History times are server-local; record/convert the time zone before correlating UTC application events. An Agent startup delay or missing history should remain unavailable/pending evidence.
5. No repeat schedule is created by this exercise. Preserve the failure history for the report; do not run unrelated jobs or modify their steps.

## Section: Produce the support report

Include server/account/time, affected operation, request/session evidence, blockers, query ranking basis, cache limitations, Query Store availability, and job-step context. Separate observed facts from proposed actions. Use the [exercise](MSSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md) for deterministic offline evidence and a Bash reporting utility.
