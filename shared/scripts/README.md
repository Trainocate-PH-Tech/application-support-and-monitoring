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
| monitor-pipeline.sh | `WINDOW_LOG [output-parent] [MYSQL_SLOW_LOG]` | Timestamped CSV, optional slow summary and manifest; 0 healthy, 1 alert, 2 incomplete |
| db-health.sh | environment MYSQL_CNF | Mode-600 MySQL client config; read-only bounded checks; propagates timeout/client failure |
| retention.sh | `--dry-run` (default) or `--apply` | Only immediate regular incident-*.tar.gz files under ~/support-lab/evidence older than the documented boundary |

Use absolute paths in cron. Monitoring accepts a pre-sliced time window; it does not tail continuously or maintain a cursor. Collector redaction is a best-effort teaching example followed by manual review. Reference scripts intentionally collect evidence and report status rather than automatically restarting services or altering databases.
