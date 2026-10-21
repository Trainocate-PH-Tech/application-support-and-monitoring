# MySQL Support Diagnostics on Linux

A step-by-step guide for an Ubuntu EC2 instance with MySQL already installed. No course database or sample application is required. Examples target MySQL 8.0/8.4; confirm the installed version before interpreting output.

## Task 1 — Admin: start, stop, and restart MySQL as the ubuntu user

**Where:** Bash in your existing SSH session on the EC2 instance.

The Linux `ubuntu` account normally has sudo access. It is separate from a MySQL database account. These commands manage MySQL inside EC2; they do not stop or start the EC2 instance itself.

1. Confirm your host and Linux identity before changing a service:

   ```bash
   whoami
   hostname
   date -u
   sudo -v
   ```

   Expect `ubuntu` from `whoami`. If sudo is denied, ask the host administrator to perform the service action.

2. Inspect the current service state:

   ```bash
   sudo systemctl status mysql --no-pager --full
   ```

   `active (running)` indicates a running service. An inactive or failed service can make this command return a nonzero exit status.

3. To start a stopped service, run:

   ```bash
   sudo systemctl start mysql
   systemctl is-active mysql
   ```

   Expect `active`. A successful start command often prints nothing.

4. To stop the service during a planned training or maintenance window, run:

   ```bash
   sudo systemctl stop mysql
   systemctl is-active mysql
   ```

   Expect `inactive` and a nonzero status from `is-active`. Stopping MySQL disconnects clients and makes dependent applications unavailable. Do not run this step merely to diagnose an incident.

5. Start it again after the stop demonstration:

   ```bash
   sudo systemctl start mysql
   sudo systemctl status mysql --no-pager --full
   ```

6. When a restart is specifically required, use this alternative:

   ```bash
   sudo systemctl restart mysql
   systemctl is-active mysql
   ```

   Restart also interrupts connections. It is not necessary to restart after every diagnostic task.

**If it differs:** If the unit is missing, inspect `systemctl list-unit-files 'mysql*' 'mysqld*' 'mariadb*'`. Confirm which database is actually installed before substituting a service name; MariaDB is a different product. If startup fails, continue with Task 2 and Task 8 rather than repeatedly restarting.

Ubuntu package/service context: [Ubuntu MySQL server documentation](https://ubuntu.com/server/docs/install-and-configure-a-mysql-server/).

## Before the diagnostic tasks

- Run **Bash** blocks at your Linux shell and **SQL** blocks at the `mysql>` prompt. Do not paste prompt characters such as `$` or `mysql>`.
- Replace `YOUR_DB_USER` with your assigned MySQL login. Never put a password directly in a command or shared evidence.
- Tasks 2–8 and 12 inspect state. Tasks 9–11 change logging and belong in a controlled administrative exercise; skip them during a read-only investigation.
- Use your diagnostic account for routine checks. Linux sudo access does not automatically grant privileges to that database account.
- Keep timestamps with your observations. SQL text and logs can contain application data; redact sensitive values before sharing.

## Task 2 — Validate the service and local listener

**Where:** Bash on EC2.

1. Capture the service state and recent journal:

   ```bash
   date -u
   systemctl is-active mysql
   sudo systemctl status mysql --no-pager --full
   sudo journalctl -u mysql --since '15 minutes ago' --utc --no-pager -n 100
   ```

2. Check the default MySQL TCP port:

   ```bash
   sudo ss -ltnp 'sport = :3306'
   ```

   A `LISTEN` entry identifies a listening socket and its bound address. `127.0.0.1:3306` accepts local TCP connections only. No entry may mean a different port, socket-only operation, or a stopped service; it does not by itself prove failure.

3. Record whether the service is active, whether a listener exists, and any recent startup error. Test database access in Task 3.

**Expected result:** Service state, journal evidence, and listener state agree. A running service alone does not prove that credentials work or that application queries are healthy.

**If it differs:** For remote connection failures, have the owner verify private routing and EC2 security-group rules. Do not expose port 3306 publicly as a troubleshooting shortcut.

## Task 3 — Connect with the mysql client

**Where:** Bash on EC2, then the MySQL client.

1. Check whether the client is available:

   ```bash
   mysql --version
   ```

   This reports the client version, not necessarily the server version. If it is missing, have the administrator install the appropriate client package before continuing.

2. Open a local connection with your assigned database account:

   ```bash
   mysql --connect-timeout=5 -u YOUR_DB_USER -p
   ```

   Enter the password at the prompt. On Linux this normally uses a local Unix socket.

3. To test local TCP explicitly, exit the previous client with `exit`, then run:

   ```bash
   mysql --protocol=TCP -h 127.0.0.1 -P 3306 --connect-timeout=5 -u YOUR_DB_USER -p
   ```

   Socket and TCP connections can match different account/authentication rules. Use the connection method your administrator provisioned.

4. For administrative tasks only, Ubuntu installations using local root socket authentication may allow this command from Bash:

   ```bash
   sudo mysql
   ```

   If it fails, use the configured administrator login. Do not change authentication to make this example work.

**Expected result:** The `mysql>` prompt appears. Use your diagnostic login for Tasks 4–8.

| Error | Next check |
|---|---|
| `Access denied` / error 1045 | Confirm the account, password, host matching, and authentication method privately. |
| Cannot connect through socket / error 2002 | Check service state and the configured socket path. |
| Cannot connect to server / error 2003 | Check host, TCP port, listener, and network reachability. |
| Too many connections / error 1040 | Record the error and ask the DBA to inspect capacity; avoid repeated connection attempts. |

## Task 4 — Use the client and establish identity

**Where:** `mysql>`.

1. Run a minimal query and identify your session:

   ```sql
   SELECT 1 AS connection_ok;
   SELECT UTC_TIMESTAMP() AS captured_utc, VERSION() AS server_version,
          @@hostname AS server_host, @@port AS server_port,
          USER() AS supplied_identity, CURRENT_USER() AS matched_account,
          CONNECTION_ID() AS connection_id;
   ```

   Expect `connection_ok = 1`. `CURRENT_USER()` identifies the MySQL account used for privilege checking.

2. Inspect client connection details and visible databases:

   ```sql
   status
   SHOW DATABASES;
   SELECT DATABASE() AS selected_database;
   ```

   A `NULL` selected database is normal; this guide does not require selecting one. Database visibility depends on privileges.

3. Practice vertical output using `\G` instead of a semicolon:

   ```sql
   SELECT VERSION() AS server_version, CURRENT_USER() AS account\G
   ```

4. To cancel an unfinished statement, type `SELECT` without a semicolon, press Enter, then type `\c` at the continuation prompt. This clears input that has not been submitted; it does not cancel a running server query.

5. Type `\h` for client help. Type `exit` when you need to return to Bash. Reconnect using Task 3 before the next SQL task.

**Expected result:** You can distinguish the Linux shell from the MySQL client, terminate statements with `;`, and recover from unfinished input.

## Task 5 — Inspect sessions with SHOW PROCESSLIST

**Where:** `mysql>` using your diagnostic account.

1. Take a timestamped snapshot:

   ```sql
   SELECT UTC_TIMESTAMP() AS captured_utc;
   SHOW PROCESSLIST;
   SHOW FULL PROCESSLIST;
   ```

2. Interpret the important columns:

   | Column | What to inspect |
   |---|---|
   | `Id` | Connection identifier for correlation. |
   | `User`, `Host` | Account and client origin. |
   | `db` | Selected database; may be `NULL`. |
   | `Command` | `Sleep` means an idle connection; `Query` indicates a statement. |
   | `Time` | Seconds in the current state; not always total query duration. |
   | `State` | Current activity or wait description. |
   | `Info` | Statement text, when available. `FULL` avoids the normal 100-character truncation. |

3. Wait about 10 seconds and repeat the timestamp and full process list. Note whether the same connection remains in a wait state or continues running.

**Expected result:** You can identify idle sessions, active work, and possible waits without terminating anything. Sleeping pool connections are not automatically a fault.

**If it differs:** Without the `PROCESS` privilege, visibility is restricted to your own account's threads. A short list is not proof that the whole server is idle. Do not issue `KILL` during this task. See [MySQL SHOW PROCESSLIST](https://dev.mysql.com/doc/refman/8.4/en/show-processlist.html).

## Task 6 — Check connection counts and headroom

**Where:** `mysql>`.

1. Collect global counters and the configured connection limit:

   ```sql
   SELECT UTC_TIMESTAMP() AS captured_utc;
   SHOW GLOBAL STATUS WHERE Variable_name IN
     ('Threads_connected', 'Threads_running', 'Max_used_connections',
      'Connections', 'Aborted_connects', 'Connection_errors_max_connections', 'Uptime');
   SHOW GLOBAL VARIABLES LIKE 'max_connections';
   ```

2. Interpret the values:

   | Value | Meaning |
   |---|---|
   | `Threads_connected` | Current open connections, including idle sessions. |
   | `Threads_running` | Threads that are not sleeping. |
   | `Max_used_connections` | Peak simultaneous connections since startup or relevant reset. |
   | `Connections` | Cumulative connection attempts, successful or unsuccessful. |
   | `Aborted_connects` | Cumulative failed connection attempts. |
   | `Connection_errors_max_connections` | Connections refused because the connection limit was reached. |
   | `Uptime` | Server uptime in seconds; helps identify restarts between samples. |

3. Calculate approximate ordinary connection headroom: `max_connections - Threads_connected`. For example, 150 configured and 120 connected leaves approximately 30 slots at that instant; reserved administrative access and concurrent changes can affect what a new client experiences.

4. Repeat after 30 seconds. Compare counter differences only if the server has not restarted or counters been reset. Record changes rather than interpreting historical totals as current failures.

**Expected result:** You can distinguish current load from historical activity. If headroom is low, correlate sessions and application errors; raising `max_connections` is a separate capacity decision.

## Task 7 — Inspect global and session variables

**Where:** `mysql>`.

1. Inspect targeted server settings:

   ```sql
   SHOW GLOBAL VARIABLES WHERE Variable_name IN
     ('hostname', 'port', 'socket', 'datadir', 'max_connections',
      'wait_timeout', 'interactive_timeout', 'read_only', 'super_read_only',
      'log_error', 'log_timestamps', 'slow_query_log', 'slow_query_log_file',
      'log_output', 'long_query_time', 'min_examined_row_limit');
   ```

2. Compare session settings with their global defaults:

   ```sql
   SELECT @@GLOBAL.wait_timeout AS global_wait_timeout,
          @@SESSION.wait_timeout AS session_wait_timeout,
          @@GLOBAL.long_query_time AS global_long_query_time,
          @@SESSION.long_query_time AS session_long_query_time;
   ```

3. Record actual paths and values for subsequent tasks. Global values generally supply defaults for new sessions where a session counterpart exists; existing sessions can differ. Plain `SHOW VARIABLES` defaults to session values, so use explicit scope when comparing captures.

**Expected result:** Settings are observed without changes. `read_only` is a server mode, not proof that your account cannot perform writes. See [MySQL system variables](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html).

## Task 8 — Locate and inspect the error log

**Where:** `mysql>` for discovery, then Bash for reading logs.

1. Discover logging configuration:

   ```sql
   SHOW GLOBAL VARIABLES WHERE Variable_name IN
     ('log_error', 'datadir', 'log_timestamps', 'log_error_services');
   ```

2. If `log_error` names a file, note its path. Resolve a relative filename against the data directory. Exit the client, then enter the confirmed absolute path at this Bash prompt:

   ```bash
   read -r -p 'Absolute MySQL error-log path: ' MYSQL_ERROR_LOG
   sudo tail -n 100 -- "$MYSQL_ERROR_LOG"
   ```

3. Inspect service journal entries as well, especially if MySQL will not start or the destination is `stderr`:

   ```bash
   sudo journalctl -u mysql --since '30 minutes ago' --utc --no-pager -n 200
   ```

   An empty or stderr destination requires checking the service/logging configuration; do not assume every installation writes `/var/log/mysql/error.log`. If SQL access is unavailable, begin with the journal and ask the administrator to confirm the configured file destination.

4. To watch the confirmed file briefly while reproducing one known connection attempt, run:

   ```bash
   sudo tail -n 20 -f -- "$MYSQL_ERROR_LOG"
   ```

   Press Ctrl-C after collecting the relevant event. Skip this step when no file destination was identified.

5. Record timestamp, severity, message, and surrounding context. Look for startup failures, permission problems, disk exhaustion, or connection errors. Compare time zones before correlating with application logs.

**Expected result:** A bounded excerpt tied to the incident window. Missing entries do not establish absence of errors: destinations and filtering can vary. If access is denied, request the excerpt from the administrator rather than changing file permissions. See [MySQL error logging](https://dev.mysql.com/doc/refman/8.4/en/error-log.html).

## Task 9 — Admin: configure a temporary slow-query capture

**Where:** A dedicated administrative MySQL client on a training host. Keep this connection open through Task 11.

This changes server configuration. Use a short, agreed capture window (for example, two minutes). Global changes require `SYSTEM_VARIABLES_ADMIN` or the applicable legacy administrative privilege. Logs consume disk and can contain SQL literals. Do not run this exercise as part of a read-only production check.

1. Connect using the administrative method from Task 3. Save the original values in this connection:

   ```sql
   SET @original_slow_query_log = @@GLOBAL.slow_query_log;
   SET @original_log_output = @@GLOBAL.log_output;
   SET @original_long_query_time = @@GLOBAL.long_query_time;
   SELECT @original_slow_query_log, @original_log_output,
          @original_long_query_time, @@GLOBAL.slow_query_log_file,
          @@GLOBAL.min_examined_row_limit, @@GLOBAL.general_log;
   ```

   Copy the results into your private change notes as well. User variables disappear if the connection closes. Do not repeat this save step after changing settings, or you will overwrite the original values.

2. Confirm the existing slow-log path and available disk space. In a second Bash terminal, check the filesystem containing that path, for example with `df -h /var/lib/mysql` if that is its actual directory. Retain the configured filename; do not invent a new directory or loosen permissions.

3. Enable file output while retaining an existing table destination:

   ```sql
   SET GLOBAL log_output = IF(FIND_IN_SET('TABLE', @original_log_output) > 0,
                             'FILE,TABLE', 'FILE');
   SET GLOBAL long_query_time = 1;
   SET GLOBAL slow_query_log = ON;
   ```

   `log_output` also controls general-query-log destinations. If the general log is enabled, this change can add file output for it too; account for that before proceeding.

4. Verify the temporary values:

   ```sql
   SELECT @@GLOBAL.slow_query_log, @@GLOBAL.log_output,
          @@GLOBAL.long_query_time, @@GLOBAL.slow_query_log_file;
   ```

**Expected result:** Slow logging is on, output includes `FILE`, and the global threshold is one second. Existing application sessions may retain their previous threshold. If any change fails, restore any successful changes using Task 11.

These runtime settings do not survive restart; this exercise does not use `SET PERSIST` or edit configuration files. Logging controls are documented in [MySQL log destinations](https://dev.mysql.com/doc/refman/8.4/en/log-destinations.html) and [system variables](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html).

## Task 10 — Verify and inspect slow-query evidence

**Where:** A second, fresh diagnostic MySQL connection, then a Bash terminal. Leave the administrative connection open.

1. Connect again using Task 3 and check the inherited settings:

   ```sql
   SELECT @@SESSION.long_query_time, @@SESSION.min_examined_row_limit;
   ```

2. For this demonstration session only, set bounded capture conditions and execute one intentional delay:

   ```sql
   SET SESSION long_query_time = 1;
   SET SESSION min_examined_row_limit = 0;
   SELECT SLEEP(1.2) AS slow_log_demo;
   exit
   ```

   Expect a result of `0` after about 1.2 seconds. Closing this connection discards its session overrides. Do not loop the delay or increase application workload to manufacture slowness.

3. In Bash, enter the absolute slow-log filename discovered in Task 9 and inspect its tail:

   ```bash
   read -r -p 'Absolute MySQL slow-log path: ' MYSQL_SLOW_LOG
   sudo tail -n 80 -- "$MYSQL_SLOW_LOG"
   ```

4. Find the completed demonstration query and inspect `Query_time`, `Lock_time`, `Rows_sent`, and `Rows_examined`. These help describe the event; query time alone does not identify a CPU bottleneck.

5. For a small training log, summarize by average query time and then execution count:

   ```bash
   command -v mysqldumpslow
   sudo mysqldumpslow -s at -t 5 "$MYSQL_SLOW_LOG"
   sudo mysqldumpslow -s c -t 5 "$MYSQL_SLOW_LOG"
   ```

   `-t 5` limits displayed groups, not how much input is read. For large production logs, use an administrator-prepared bounded capture. If the utility is unavailable, use the raw excerpt and request the appropriate package separately.

**If no record appears:** Confirm that the query completed, slow logging is still on, output includes `FILE`, the file is correct, and the session threshold and examined-row limit match the demonstration. Inspect the error log for write failures. Record missing evidence instead of repeatedly generating work. Always complete Task 11. See [MySQL slow query log](https://dev.mysql.com/doc/refman/8.4/en/slow-query-log.html) and [mysqldumpslow](https://dev.mysql.com/doc/refman/8.4/en/mysqldumpslow.html).

## Task 11 — Admin: restore the original logging settings

**Where:** The same administrative MySQL connection used in Task 9.

1. Confirm your saved values still exist:

   ```sql
   SELECT @original_slow_query_log, @original_log_output,
          @original_long_query_time;
   ```

   If any value is `NULL`, stop before the next block. Recover the exact values from the written Task 9 record and assign them to the corresponding user variables in this connection. Do not guess defaults.

2. Restore all three changed global settings:

   ```sql
   SET GLOBAL slow_query_log = @original_slow_query_log;
   SET GLOBAL long_query_time = @original_long_query_time;
   SET GLOBAL log_output = @original_log_output;
   ```

3. Verify against the saved values:

   ```sql
   SELECT @@GLOBAL.slow_query_log = @original_slow_query_log AS logging_restored,
          @@GLOBAL.long_query_time = @original_long_query_time AS threshold_restored,
          @@GLOBAL.log_output = @original_log_output AS output_restored;
   ```

   Expect all three columns to be `1`. Record the restoration time and exit the administrator client.

4. Confirm the demonstration connection is closed. Sessions opened during the capture may retain the temporary global threshold; restoring the global value does not rewrite their session values. On a shared host, coordinate with the owner rather than terminating other connections.

**Expected result:** Original global configuration is restored even if capture failed. Keep collected logs under the host's retention policy; do not delete or truncate live logs as cleanup.

## Task 12 — Run a safe read-only baseline and record findings

**Where:** Bash and a diagnostic MySQL connection. No service or logging changes are needed.

1. In Bash, capture the host, time, service, and recent journal:

   ```bash
   hostname
   date -u
   systemctl status mysql --no-pager --full
   sudo journalctl -u mysql --since '15 minutes ago' --utc --no-pager -n 100
   ```

2. Connect with your diagnostic account and run this compact SQL baseline:

   ```sql
   SELECT UTC_TIMESTAMP() AS captured_utc, VERSION() AS server_version,
          @@hostname AS server_host, CURRENT_USER() AS account;
   SELECT 1 AS connection_ok;
   SHOW FULL PROCESSLIST;
   SHOW GLOBAL STATUS WHERE Variable_name IN
     ('Threads_connected', 'Threads_running', 'Max_used_connections',
      'Connections', 'Connection_errors_max_connections', 'Uptime');
   SHOW GLOBAL VARIABLES WHERE Variable_name IN
     ('max_connections', 'log_error', 'slow_query_log', 'slow_query_log_file',
      'log_output', 'long_query_time');
   exit
   ```

3. Inspect the bounded error-log excerpt from Task 8 if available. Do not enable logging merely to complete a read-only baseline.

4. Write a brief report using the following fields:

   | Field | What to record |
   |---|---|
   | Context | UTC time, host, server version, incident symptom. |
   | Access | Connection method, effective account, denied or unavailable checks. |
   | Health | Service state and result of `SELECT 1`. |
   | Sessions | Relevant connection IDs and states, with sensitive SQL redacted. |
   | Capacity | Current/peak connections, limit, and counter differences if sampled. |
   | Logs | Actual destination, time window, relevant messages, or missing evidence. |
   | Conclusion | Observed facts, remaining uncertainty, and the next targeted check. |
   | Changes | None for this baseline; if Tasks 9–11 ran separately, reference their change and restoration record. |

**Safe-check boundaries:** These examples inspect metadata and counters. Read-only SQL can still consume resources: avoid unbounded application-table scans, `SELECT ... FOR UPDATE`, and `EXPLAIN ANALYZE` (which executes the statement). Do not use `KILL`, writes, schema changes, `FLUSH`, global setting changes, or service restarts as part of this baseline. A successful `SELECT 1` proves this session can execute a trivial query; it does not prove application performance.

**Completion check:** You have identified the host and account, validated service and connectivity, interpreted sessions and connection counts, located logs, and documented evidence without treating unavailable data as a healthy result.

Optional course follow-up: [Database baseline and safe access](module2/exercises/01-db-baseline.md) and [MySQL slow-query capture and ranking](module2/exercises/02-mysql-slow.md).
