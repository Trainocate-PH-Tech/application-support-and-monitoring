# Module 2: MySQL and SQL Server Diagnostics

One training day: 390 instructional minutes, 60-minute lunch and two 15-minute breaks. Advanced extensions are optional. Teams have 3–4 learners; rotate roles and schedule shared service changes.

[PowerPoint deck](Module2.pptx) · [Learner setup](../shared/learner-start.md) · [Assessment rubric](../shared/assessment-rubric.md)

## Agenda
| Exercise | Instructional minutes |
|---|---:|
| [Database baseline and safe access](exercises/01-db-baseline.md) | 35 |
| [MySQL slow-query capture and ranking](exercises/02-mysql-slow.md) | 40 |
| [EXPLAIN, indexes and misleading assumptions](exercises/03-mysql-plans.md) | 35 |
| [MySQL blocking and deadlocks](exercises/04-mysql-locks.md) | 40 |
| [Replication delay and reporting freshness](exercises/05-replication.md) | 15 |
| [SQL Server requests, sessions and wait deltas](exercises/06-sqlserver-baseline.md) | 40 |
| [Blocking chains, Query Store and job failures](exercises/07-sqlserver-blocking-plans-jobs.md) | 40 |
| [Application/database correlation](exercises/08-app-db-correlation.md) | 50 |
| [Final database incident challenge](exercises/09-database-capstone.md) | 75 |
| Checkpoints and recovery reserve | 20 |

The exercise blocks total 370 minutes. Use two 10-minute checkpoints to review evidence, recover interrupted work and confirm readiness. Demonstrations and extensions are labeled in each exercise; extensions do not displace the final assessment.

## Before starting
Read the [learner terminal/setup guide](../shared/learner-start.md). Each exercise now includes numbered actions, execution context, expected results and specific cleanup. Final challenges retain independent diagnosis with optional hints.

Use the course repository root for commands unless the exercise changes directory. Copy evidence into `~/support-lab`, never edit original fixtures. Commands marked instructor require the instructor; students do not need blanket sudo. Use individual SSH credentials. Modules 2 and 3 build on the prior day's application and evidence skills.

## Completion
Submit the deliverables listed in each required exercise. Keep passwords, private keys and unreviewed sensitive logs out of submissions. Distinguish synthetic evidence from live observations. The instructor scores evidence, diagnosis, recovery, automation and communication using the shared rubric.

## Standalone guides and Bash reporting exercises

These pairs provide step-by-step live procedures plus offline synthetic evidence. Each exercise teaches an executable reporting utility; a live database is optional for the fixture portion.

| Topic | Guide | Exercise |
|---|---|---|
| MySQL slow queries and indexes | [Guide](../MYSQL_SLOW_QUERY_ANALYSIS.md) | [Exercise](../MYSQL_SLOW_QUERY_ANALYSIS_EXERCISE.md) |
| MySQL contention and reliability | [Guide](../MYSQL_CONTENTION_RELIABILITY.md) | [Exercise](../MYSQL_CONTENTION_RELIABILITY_EXERCISE.md) |
| SQL Server support diagnostics | [Guide](../MSSQL_SUPPORT_DIAGNOSTICS.md) | [Exercise](../MSSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md) |
| SQL Server blocking and plan regression | [Guide](../MSSQL_BLOCKING_PLAN_REGRESSION.md) | [Exercise](../MSSQL_BLOCKING_PLAN_REGRESSION_EXERCISE.md) |
| Application/database correlation | [Guide](../APP_DB_CORRELATION.md) | [Exercise](../APP_DB_CORRELATION_EXERCISE.md) |
