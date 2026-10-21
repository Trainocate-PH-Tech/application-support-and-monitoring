# SQL Server Blocking, Wait Statistics, and Plan Regression

[Hands-on exercise](MSSQL_BLOCKING_PLAN_REGRESSION_EXERCISE.md) · [SQL Server diagnostics](MSSQL_SUPPORT_DIAGNOSTICS.md)

**Environment:** SQL Server 2022 Developer on a dedicated training host; Ubuntu Bash with ODBC `sqlcmd` or a SQL query window. SQL Server syntax does not run in the MySQL client. Follow [SQL Server setup and permissions](shared/instructor/sqlserver-setup.md) first. An administrator initializes `SupportLab` using [setup.sql](shared/sql/sqlserver/setup.sql); this creates training data, enables Query Store, and creates a deliberately failing Agent job. Do not run it against production.

For ODBC sqlcmd, replace `SQL_HOST` and `YOUR_LOGIN`, and let the client prompt for the password:

```bash
/opt/mssql-tools18/bin/sqlcmd -S tcp:SQL_HOST,1433 -U YOUR_LOGIN -d SupportLab
```

Use a trusted certificate. `-C` is only an explicit certificate-validation bypass for disposable labs, not a production fix. In interactive sqlcmd, `GO` submits the batch and `QUIT` exits. Diagnostic visibility requires the grants in the setup guide, including SQL Server 2022 `VIEW SERVER PERFORMANCE STATE`; SQL text, Query Store, and msdb job history can require additional permissions. Access denied means unavailable evidence. Do not solve it by using `sa` for every learner query.

## Section: Create bounded blocking on the training database

1. Open writer A, writer B, and observer C. Writers need UPDATE on the training table; the observer uses diagnostic grants. Record `SELECT @@SPID;` in each.
2. Writer A:

   ```sql
   USE SupportLab;
   BEGIN TRAN;
   UPDATE dbo.Players SET points=points+1 WHERE id=1;
   GO
   ```

3. Writer B:

   ```sql
   USE SupportLab;
   SET LOCK_TIMEOUT 15000;
   BEGIN TRAN;
   UPDATE dbo.Players SET points=points+1 WHERE id=1;
   GO
   ```

4. Before 15 seconds elapse, observe requests from C. B should wait; after timeout, its transaction still needs explicit cleanup. Keep A open for no more than a minute.

## Section: Follow the chain to its head

1. Observer C includes sleeping sessions:

   ```sql
   SELECT s.session_id,s.status,s.open_transaction_count,
          COALESCE(r.blocking_session_id,0) AS blocking_session_id,
          r.wait_type,r.wait_time,ib.event_info AS last_input
   FROM sys.dm_exec_sessions AS s
   LEFT JOIN sys.dm_exec_requests AS r ON r.session_id=s.session_id
   OUTER APPLY sys.dm_exec_input_buffer(s.session_id,NULL) AS ib
   WHERE s.is_user_process=1 AND s.session_id<>@@SPID;
   GO
   ```

2. Starting at the blocked request, follow each positive `blocking_session_id` until reaching a session not blocked by another positive ID. Check its transaction state and last submitted batch; an idle head blocker can be absent from `dm_exec_requests`.
3. Missing IDs, cycles in a copied sample, or special negative blocker IDs mean the chain is unresolved. Negative values represent special ownership states, not ordinary SPIDs. Consult the [request DMV reference](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-requests-transact-sql?view=sql-server-ver16) before interpreting them.
4. Run `IF @@TRANCOUNT>0 ROLLBACK;` in **both** writers, after B returns or times out. Then run `SET LOCK_TIMEOUT -1;` in B or close it. Verify `SELECT id,points FROM SupportLab.dbo.Players;` returns original 100 and 200. Do not use `KILL` as the classroom cleanup mechanism.

## Section: Compare wait snapshots without resetting counters

1. In one observer connection, capture a baseline:

   ```sql
   SELECT sqlserver_start_time INTO #server_before FROM sys.dm_os_sys_info;
   SELECT wait_type,waiting_tasks_count,wait_time_ms INTO #wait_before FROM sys.dm_os_wait_stats;
   SELECT SYSUTCDATETIME() AS baseline_utc;
   GO
   ```

2. Wait 30 seconds using your watch, then in the **same connection** run:

   ```sql
   SELECT SYSUTCDATETIME() AS after_utc;
   SELECT a.wait_type,a.wait_time_ms-b.wait_time_ms AS delta_wait_ms,
          a.waiting_tasks_count-b.waiting_tasks_count AS delta_tasks
   FROM sys.dm_os_wait_stats AS a
   JOIN #wait_before AS b ON b.wait_type=a.wait_type
   CROSS JOIN sys.dm_os_sys_info AS si
   CROSS JOIN #server_before AS sb
   WHERE si.sqlserver_start_time=sb.sqlserver_start_time
     AND a.wait_time_ms>=b.wait_time_ms
     AND a.waiting_tasks_count>=b.waiting_tasks_count
   ORDER BY delta_wait_ms DESC;
   GO
   ```

3. Record restarted/disconnected sessions or decreased counters as an invalid comparison. Resets cannot always be detected if counters exceed the old values again; confirm no reset occurred. Do not run `DBCC SQLPERF(..., CLEAR)` for this exercise.
4. Explain that aggregate wait milliseconds can exceed wall-clock time because sessions wait concurrently. A wait class is an investigation lead, not an automatic hardware diagnosis. Review idle/background waits in context. Close the observer connection to remove its temporary tables. See [wait statistics](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-wait-stats-transact-sql?view=sql-server-ver16).

## Section: Separate plan regression from blocking

1. Use Query Store aggregation from the [diagnostics guide](MSSQL_SUPPORT_DIAGNOSTICS.md), selecting the same query and comparable intervals. Preserve plan ID, execution counts, duration, CPU, reads, parameters, and returned rows.
2. Read the separate regression fixture context:

   ```bash
   cat shared/fixtures/db-topics/mssql-regression/context.txt
   cat shared/fixtures/db-topics/mssql-regression/plans.tsv
   ```

3. Weight the two baseline rows: `(80*50000 + 20*100000)/100 = 60000` microseconds, or 60 ms. The later average is 900 ms: a 15× increase. Weighted baseline reads are 220 versus 21000, approximately 95.45×. Both intervals contain 100 executions.
4. Compare plan XML when available; fixture plan descriptions are summaries only. A changed plan and nearby deployment support a hypothesis, not proof. Sampled absence of blocking does not exclude waits outside the samples.

## Section: Inspect statistics and deployment context

1. Inspect without updating:

   ```sql
   USE SupportLab;
   SELECT s.name,p.last_updated,p.rows,p.rows_sampled,p.modification_counter
   FROM sys.stats AS s
   OUTER APPLY sys.dm_db_stats_properties(s.object_id,s.stats_id) AS p
   WHERE s.object_id=OBJECT_ID(N'dbo.Transactions');
   GO
   ```

2. Compare deployment time, SQL/predicate changes, parameter distributions, compatibility settings, data growth, statistics, and plan choice. Old statistics are not automatically inaccurate statistics.
3. Request missing plan XML, statistics evidence, and the release SQL diff before recommending a fix. Do not automatically update statistics, rebuild indexes, flush caches, or force a plan.
4. For an optional instructor-led index comparison, follow [the bounded workload](shared/sql/sqlserver/workload.sql), record the same results and logical reads, create only the documented training index, and drop only that newly created index afterward. Performance improvement is measured, not guaranteed.

## Section: Report separate causes and next actions

Keep the blocking case and deployment-regression case separate. Include chain/root evidence, interval wait deltas, comparable plan metrics, missing evidence, a reversible proposal, and a rollback trigger. Use the [exercise utility](MSSQL_BLOCKING_PLAN_REGRESSION_EXERCISE.md) to calculate fixture results and handle incomplete snapshots.
