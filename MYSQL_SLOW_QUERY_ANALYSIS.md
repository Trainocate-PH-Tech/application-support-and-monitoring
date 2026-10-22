# Identifying and Analyzing Slow MySQL Queries

[Hands-on exercise](MYSQL_SLOW_QUERY_ANALYSIS_EXERCISE.md) · [Module 2](module2/README.md)

**Environment:** Ubuntu Bash and MySQL 8.0/8.4. SQL blocks run at `mysql>`; Bash blocks run in the Linux shell. First follow [the diagnostic guide](MYSQL_SUPPORT_DIAGNOSTICS.md) to load `mysql_support_demo` and connect as `developer` with password `password` on the EC2 training host. No password belongs in a shell argument or submitted evidence. This account has administrator privileges; perform changes only in the explicitly labeled setup/change steps. Record UTC timestamps, host, version, and account with each capture.

## Section: Establish the symptom and capture settings

1. Identify the slow operation, user impact, incident window, and query parameters. Compare like-for-like calls, not unrelated averages.
2. At `mysql>`, inspect the current settings:

   ```sql
   SELECT UTC_TIMESTAMP(), VERSION(), CURRENT_USER();
   SHOW GLOBAL VARIABLES WHERE Variable_name IN
     ('slow_query_log','slow_query_log_file','log_output','long_query_time','min_examined_row_limit');
   SELECT @@SESSION.long_query_time, @@SESSION.min_examined_row_limit;
   ```

3. Record paths and values. Global thresholds become defaults for new connections; existing sessions can retain earlier values. Slow logs capture completed statements meeting logging conditions, not every currently running query. See [MySQL slow query log](https://dev.mysql.com/doc/refman/8.4/en/slow-query-log.html).

## Section: Admin: capture a short slow-log window

1. Use the exact save/change/restore sequence in the [diagnostic guide](MYSQL_SUPPORT_DIAGNOSTICS.md), under the temporary slow-query capture sections. Keep the administrative connection open, write original values in your notes, and use a two-minute training window.
2. Open a separate reader connection. Set only its demonstration thresholds and run one bounded query:

   ```sql
   SET SESSION long_query_time = 1;
   SET SESSION min_examined_row_limit = 0;
   SELECT order_id, SLEEP(1.2) AS deliberate_delay
   FROM mysql_support_demo.orders WHERE order_id=1001;
   exit
   ```

3. Read the confirmed file with `tail -n 80`, using authorized file access. Check the query text, `Query_time`, `Lock_time`, and examined/returned rows. If no record appears, inspect output destination, session thresholds, completion, and log write errors.
4. Restore original global settings using the original administrative session even if capture failed. Close the demonstration session. Do not persist settings or change permissions on log directories for this exercise.

**Expected:** A synthetic delayed query is visible. Its duration does not establish slow storage, high CPU, or a missing index.

## Section: Rank frequency and duration

1. From the repository root in Bash, inspect the complete supplied log:

   ```bash
   cat shared/fixtures/db-topics/mysql-slow/slow.log
   ```

2. Check `command -v mysqldumpslow`. If unavailable, ask the administrator to provide the matching MySQL utility; the exercise utility still reports basic totals and labels grouped rankings unavailable.
3. When available, compare three rankings:

   ```bash
   mysqldumpslow -s c shared/fixtures/db-topics/mysql-slow/slow.log
   mysqldumpslow -s at shared/fixtures/db-topics/mysql-slow/slow.log
   mysqldumpslow -s t shared/fixtures/db-topics/mysql-slow/slow.log
   ```

4. Record that three similar reports total about 3.6 seconds, while one rare delay takes 3 seconds. The highest average is not the highest aggregate cost. `mysqldumpslow` normalizes literals; verify that grouped queries have comparable business meaning. Its default timing treatment subtracts lock time; use `-l` when explicitly comparing unadjusted timing, and label the choice. These small-fixture examples display all groups. A top-group limit does not bound the amount of input read; some tool versions fail when the requested limit exceeds available groups. Printed aggregate seconds may be rounded/truncated, so calculate precise totals from the raw timings. See [mysqldumpslow options](https://dev.mysql.com/doc/refman/8.4/en/mysqldumpslow.html).

## Section: Admin: load a larger index experiment

1. Load the base sample using the diagnostic guide if needed. In Bash at the repository root, import the separate training table once:

   ```bash
   mysql -u developer -p < shared/sql/mysql/slow-analysis-setup.sql
   ```

   Enter `password` at the prompt. Do not add `--force`. Existing `analysis_orders` deliberately causes failure; inspect and reuse a completed load rather than overwriting it.
2. Expect 100000 rows. Customer 42 has 1000 rows and amount 10000.00. Existing `SELECT` on `mysql_support_demo.*` covers this table. No change is made to the original six orders.
3. In the MySQL client, inspect the baseline:

   ```sql
   USE mysql_support_demo;
   SHOW INDEX FROM analysis_orders;
   EXPLAIN SELECT COUNT(*), SUM(amount) FROM analysis_orders WHERE customer_id=42;
   SELECT COUNT(*), SUM(amount) FROM analysis_orders WHERE customer_id=42;
   ```

## Section: Test a missing-index hypothesis

1. Record `type`, `possible_keys`, `key`, `rows`, `filtered`, and `Extra`. Plain `EXPLAIN` estimates a plan; it does not measure execution time. A high examined-to-returned ratio is a lead, not proof an index is appropriate.
2. On the dedicated training table only, have the administrator create:

   ```sql
   CREATE INDEX idx_analysis_customer ON mysql_support_demo.analysis_orders(customer_id);
   ```

3. Repeat the exact reader queries and compare results and plans. Expect the same 1000 and 10000.00. The optimizer may choose the index, but record actual output rather than requiring a fixed plan or speedup.
4. As administrator, remove only the index created in this exercise:

   ```sql
   DROP INDEX idx_analysis_customer ON mysql_support_demo.analysis_orders;
   ```

5. Verify `SHOW INDEX` and the result again. Keep the training table for repeat practice. If that index already existed before the exercise, do not claim ownership or drop it; coordinate the baseline first.

## Section: Record conclusions without unsafe assumptions

- Query time is elapsed time, not CPU time. Reported lock time does not capture every possible wait.
- Rows examined are work evidence, not automatically wasted work. Scans can be reasonable on small or unselective inputs.
- Indexes add storage and write maintenance; check selectivity, predicate shape, ordering, and existing indexes before proposing one.
- Cache state, concurrent work, parameters, statistics, and result size can change timings. Reconcile these before claiming improvement.
- `EXPLAIN ANALYZE` executes the statement; it is outside the read-only planning workflow here.

Submit the original settings, capture window, ranking rationale, before/after plan evidence, unchanged results, and restoration confirmation. Continue with the [exercise and reporting utility](MYSQL_SLOW_QUERY_ANALYSIS_EXERCISE.md).
