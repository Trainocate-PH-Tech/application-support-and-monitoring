# Outline coverage map

The four-page supplied PDF is the curriculum source. Each module has 50 slides: 4 opening slides, 9 exercise blocks of 5 slides each, and a reference/completion slide. Exercise block N maps to slides `5 + 5*(N−1)` through `9 + 5*(N−1)`. Instructor guides list exact ranges. Day 1 expands fundamentals while preserving the PDF’s incident objectives.

| Outline topic / requested addition | Exercise mapping | Delivery / evidence |
|---|---|---|
| SSH, identities, prompts, paths, permissions, sudo, environment, history | M1 01–02 | Live; use `history` locally but do not export commands containing secrets |
| User creation and disk allocation | M1 01, 03 | Supervised accounts; disposable quota and partition labs |
| File navigation, file handling, package installation | M1 02, 05 | Ubuntu apt; Red Hat dnf comparison |
| pwd, cd, ls, find, grep, awk, sed, cut, sort, uniq, wc, xargs, less, tail, head, tee, date, tar, gzip | M1 02, 04, 09 | Executable pipelines, archive practice and 18-question bank |
| systemctl, service state, units, startup, restart policies, journalctl | M1 05–06 | Live Tomcat unit and startup fault |
| /var/log, rotation, journal filters, request/correlation IDs, latency | M1 04–06; M2 08; M3 02–04 | Live logs plus synthetic windows |
| top, ps, free, uptime, df, du, lsof, pidstat, log growth, handles | M1 03, 07 | Bounded CPU and deleted-open-file demonstrations |
| ss, curl, nc, ping, traceroute, nslookup, dig | M1 07 | Layered connectivity investigation |
| Firewall, DNS, TLS, SELinux indicators | M1 07 | Live listener/TCP tests; platform evidence cards and firewall review |
| Tomcat startup, application errors, disk utilization, DB connectivity | M1 03, 06–08 | Resettable faults and disposable storage |
| Linux checklist, evidence bundle, basic Bash collector | M1 08 | Required submitted outputs |
| mysql client, service, PROCESSLIST, variables, connection counts, error/slow logs | M2 01–02 | Live MySQL plus slow-log fixtures |
| slow_query_log, long_query_time, mysqldumpslow, rows examined, lock time, frequency | M2 02 | Controlled log setting change and restore |
| EXPLAIN, missing indexes, unsafe assumptions | M2 03 | Before/after plans and logical reasoning |
| Deadlocks, InnoDB status, blocked sessions | M2 04 | Two writers and observer, explicit rollback |
| Replication delay, routing, relay logs, freshness | M2 05 | Synthetic replica status; no replica installed |
| SQL requests, sessions, waits, expensive queries, plans | M2 06 | Separate SQL Server, DMV diagnostics and interval fixtures |
| Query Store, plan/statistics regression, deployment correlation | M2 07 | Live index comparison; deterministic regression fixture; statistics investigation |
| SQL Agent job failure/history | M2 07 | Live intentional failure plus separate permission-error evidence |
| Head blocker / sleeping sessions | M2 07 | Live bounded blocking and IIS evidence card |
| Request IDs, latency, pool exhaustion, retries, downstream checks | M2 08 | Live delay plus synthetic pooled-app timeline |
| MySQL triage report, SQL worksheet, DB health outline | M2 09 | Required outputs and rubric |
| Bash variables, substitution, functions, statuses, conditions, loops, args, logging | M3 01 | Student script plus reference health checker |
| UTC folders, output capture, time windows, masking, packaging | M3 02 | Partial-failure collector and reviewed archive |
| grep/awk/sed pipelines, CSV, thresholds, rates, latency, slow summaries | M3 03–04 | Deterministic parser/slow-log results |
| Services, endpoints, disk thresholds, retention, backups/log cleanup | M3 05–06 | Cron, dry-run archive retention; backup limitations discussed |
| Replication and SQL Agent automation checks | M3 09; M2 05, 07 | Evidence-based extension; permissions/unknown states required |
| Deployment checks suitable for cron/runbooks | M3 05–06 | Executable health checks, minimal environment, lock |
| Casino loyalty, gaming delays, payment failure, CPU, DB slowness | M3 07; M1 07; M2 06 | Three scenario variants plus bounded resource/DB exercises |
| IIS + SQL support | M2 07; platform-incidents.md | Synthetic Windows/IIS evidence, explicitly not live Ubuntu |
| RCA, evidence, escalation, monitoring backlog, technical recommendations | M3 07–08 | Incident report, handover, assessment |
| Comprehensive trick questions and final challenges | All modules, especially M1 09 / M2 09 / M3 07–09 | Separate answer keys and scenario cards |

## Distribution distinctions

Ubuntu is the live application host. Red Hat file paths, dnf/firewalld and SELinux checks are comparisons/evidence exercises. SQL Server is a separate supported host. Replication, IIS, production pooling and real payment integrations are not falsely represented as installed features of the small sample application.

## Reviewed delivery and assessment mapping

- Module 1 exercise 04 now introduces the first Bash collector; exercise 08 extends it during independent triage. Module 3 exercise 01 develops its interface, argument validation, arrays and failure tests.
- Storage: learner diagnosis and disposable growth are core; quota is a supervised demonstration; deleted-open-file and inode exhaustion are extensions. EBS operations remain an explained instructor procedure.
- SQL Server exercise 07: blocking is core live practice, Query Store/job interpretation is core evidence work, and live plan changes/job execution are extensions.
- Module 2 final: independent synthetic reporting regression with staged evidence release and comparable before/after measurements; no live authentication fault is required.
- Every day has 370 scheduled activity minutes and 20 checkpoint/recovery minutes. Extensions are outside the core budget; timing awaits a beginner pilot.
- The learner archive has its own validated links, executable reference scripts and sanitized deck notes. The master retains concealed cases, answers, host setup and authoring tools.
