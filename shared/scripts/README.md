# Script interfaces

Run from the repository root unless stated otherwise. Scripts require Bash and GNU/Linux tooling. Instructor-only operations are not student self-service commands.

| Script | Interface | Behavior / exit codes |
|---|---|---|
| preflight.sh | no arguments | Read-only host inventory; capacity warning |
| setup-ubuntu.sh | sudo, `--training-host` | Installs and deploys shared stack; 0 only after readiness succeeds |
| fault.sh | sudo, `startup`, `permissions`, `db-auth`, `latency`, `payment`, or `reset` | One saved fault at a time; reset restores saved config and startup override |
| storage-lab.sh | sudo, `create`, `grow`, `cleanup` | Owns a disposable loop image; refuses arbitrary devices |
| traffic.sh | `[base-url] [count]` | Sequential, 1–100 requests, 8-second timeout per request |
| health-check.sh | environment SERVICE, URL, DISK_LIMIT, DISK_PATH | 0 healthy; 1 failed check; 2 invalid input/missing dependency |
| collect-evidence.sh | `[output-parent] [journal-since]` | 0 full; 1 partial; 2 cannot create/package output; 15-second per-command timeout |
| monitor-log.sh | `LOG [error-percent] [latency-ms]` | CSV; 0 OK; 1 ALERT; 2 invalid input/NO_DATA; threshold equality alerts |
| mysql-log-report.sh | `ERROR_LOG SLOW_LOG OUTPUT_PARENT [LINES=200]` | Private log snapshots and text report; 0 collected (not a health verdict), 2 invalid input/read failure; other tool failures may be nonzero. See [exercise](../../MYSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md). |
| monitor-pipeline.sh | `WINDOW_LOG [output-parent] [MYSQL_SLOW_LOG]` | Timestamped CSV, optional slow summary and manifest; 0 healthy, 1 alert, 2 incomplete |
| db-health.sh | environment MYSQL_CNF | Mode-600 MySQL client config; read-only bounded checks; propagates timeout/client failure |
| retention.sh | `--dry-run` (default) or `--apply` | Only immediate regular incident-*.tar.gz files under ~/support-lab/evidence older than the documented boundary |

Use absolute paths in cron. Monitoring accepts a pre-sliced time window; it does not tail continuously or maintain a cursor. Collector redaction is a best-effort teaching example followed by manual review. Reference scripts intentionally collect evidence and report status rather than automatically restarting services or altering databases.

## Topic evidence-report utilities

All five use `SCRIPT INPUT_DIR OUTPUT_PARENT`, read local evidence, and produce a unique private directory with copied inputs and `report.txt`. They do not connect to databases or apply repairs. Exit 0 means collection succeeded, not that the database is healthy; validation failures exit 2, and other tool failures may be nonzero. See each exercise for exact input schemas and dependency requirements.

| Utility | Exercise |
|---|---|
| mysql-slow-report.sh | [Slow queries](../../MYSQL_SLOW_QUERY_ANALYSIS_EXERCISE.md) |
| mysql-contention-report.sh | [Contention/reliability](../../MYSQL_CONTENTION_RELIABILITY_EXERCISE.md) |
| mssql-diagnostics-report.sh | [SQL Server diagnostics](../../MSSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md) |
| mssql-regression-report.sh | [Blocking/regression](../../MSSQL_BLOCKING_PLAN_REGRESSION_EXERCISE.md) |
| app-db-correlation-report.sh | [Application/database correlation](../../APP_DB_CORRELATION_EXERCISE.md) |
