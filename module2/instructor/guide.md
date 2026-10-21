# Module 2 instructor guide

Keep this answer key separate from student handouts. Rehearse setup and fault reset before class. Speaker notes include the same reasoning for live delivery. Review [shared setup](../../shared/instructor/setup-and-delivery.md), [scenario cards/rubric](../../shared/instructor/scenarios.md) and [storage procedures](../../shared/instructor/storage.md).

## Database baseline and safe access

Slides 5–9. Time: 35.

**Expected reasoning:** SELECT 1 checks a narrow path. PROCESS privilege controls visibility of other sessions; missing privileges can hide incident evidence. Do not distribute the application account password to learners. Use per-team diagnostic accounts and instructor-controlled writes.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Baseline identifies endpoint and effective database user. Learner distinguishes access denied from server unreachable.

**Submission:** A database baseline and a protected client configuration, never submitted with its password.

**Guided walkthrough checkpoints:**

1. Create a protected client configuration — The file exists with mode 600. Do not paste its contents into submitted evidence.
2. Enter the client settings — The instructor-provided login replaces the placeholder and no placeholder remains.
3. Run the bounded health check — Mode is 600; healthy output includes engine version, SELECT 1 result, connection counters and exit 0.
4. Enter MySQL and identify the session — The mysql> prompt appears.
5. Capture a read-only baseline — Identity and version print; connection headroom is assessed against the configured limit.
6. Inspect service and full diagnostics — Read-only checks execute; error-log destinations may be a file, journal or stderr depending on setup.
7. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Exit any open mysql client. Keep the mode-600 client file for later exercises and exclude it from submissions. No server configuration changes were required.

**Instructor execution sheet:**


## MySQL slow-query capture and ranking

Slides 10–14. Time: 40.

**Expected reasoning:** Elapsed time includes waiting and is not a CPU measurement. Use fresh sessions or an explicit session setting. Supplied evidence has a frequent player-report query and a rarer long query; compare total impact rather than selecting only the largest individual duration.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Slow record appears with query time, lock time and row counts. Report explains why a frequent moderate query may cost more overall than one rare slow query.

**Submission:** A ranked slow-query table with units, frequency and next checks.

**Guided walkthrough checkpoints:**

1. Record the original logging configuration — The original ON/OFF value, threshold, output destination and file path are recorded before changes.
2. Enable a short capture window — Settings change successfully on the training database.
3. Open a fresh learner connection — mysql> appears in a new session.
4. Create bounded slow-query evidence — The intentional SLEEP query exceeds the threshold. The report may be too fast to enter the slow log on this host.
5. Inspect the capture and rank the fixture — The similar report queries group into three executions, totaling approximately 3.6 seconds; the single delay takes 3 seconds.
6. Restore the exact original values — Values match the first step.
7. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Complete the restoration step even if capture failed. Close learner capture sessions; retain logs according to the instructor retention policy rather than deleting database log files.

**Instructor execution sheet:**

Record the original logging configuration

Keep this same administrative session open until settings are restored. Save session variables as well as a private written record of the printed values.

```sql
SET @saved_slow = @@GLOBAL.slow_query_log;
SET @saved_threshold = @@GLOBAL.long_query_time;
SET @saved_output = @@GLOBAL.log_output;
SELECT @saved_slow, @saved_threshold, @saved_output;
SHOW GLOBAL VARIABLES LIKE 'slow_query_log_file';
```

Enable a short capture window

These are temporary lab changes. FILE ensures this exercise produces a log that mysqldumpslow can read.

```sql
SET GLOBAL log_output = 'FILE';
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 0.2;
```

Restore the exact original values

Restore all three settings, then verify the values. Learners record that restoration occurred.

```sql
SET GLOBAL slow_query_log = @saved_slow;
SET GLOBAL long_query_time = @saved_threshold;
SET GLOBAL log_output = @saved_output;
SELECT @@GLOBAL.slow_query_log, @@GLOBAL.long_query_time, @@GLOBAL.log_output;
```
## EXPLAIN, indexes and misleading assumptions

Slides 15–19. Time: 35.

**Expected reasoning:** Full scans may be optimal for small tables or low-selectivity predicates. Expressions, types, selectivity and statistics affect index use. LIMIT can still require scanning or sorting many rows. For 100,000 seeded rows, player 42 has 1,000 transactions totaling 10,000.00.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Before/after plans and equivalent query results are retained. Recommendation includes an index tradeoff and measurement limitation.

**Submission:** A before/after plan comparison and an evidence-based recommendation.

**Guided walkthrough checkpoints:**

1. Connect and record the baseline — The client connects with the assigned team login.
2. Inspect data and the estimated plan — Data count is 100000; the player-42 result is 1000 and 10000.00. Initial plan details depend on engine statistics.
3. Apply the approved training index — The named index is created.
4. Compare after-state without assuming faster timing — Business results remain the same; the plan can use the new index.
5. Restore the exercise baseline — The training index is absent and the original primary key remains.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Instructor drops the named training index after evidence is captured. Learners exit the client and retain before/after plans. Do not delete the seeded tables.

**Instructor execution sheet:**

Apply the approved training index

Create only this named lab index, then announce completion to learners.

```sql
CREATE INDEX idx_transactions_player ON support_lab.transactions(player_id);
```

Restore the exercise baseline

Remove only the index created in this exercise.

```sql
DROP INDEX idx_transactions_player ON support_lab.transactions;
SHOW INDEX FROM support_lab.transactions;
```
## MySQL blocking and deadlocks

Slides 20–24. Time: 40.

**Expected reasoning:** Killing a waiter does not release locks held by the blocker. Deadlock detection rolls back a victim; the survivor may still need an explicit rollback in this exercise. Retry only a complete safe transaction, with bounds/backoff and idempotency considerations.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Evidence shows the blocking relation or deadlock cycle. Both sessions end their transactions and a subsequent update succeeds.

**Submission:** A lock diagram, deadlock interpretation and verified cleanup.

**Guided walkthrough checkpoints:**

1. Open all three MySQL sessions — Each terminal has its own mysql> prompt and independent session.
2. Acquire the first lock — UPDATE completes; A holds a lock on player 1 until commit/rollback.
3. Create a bounded waiter — B pauses waiting for A, or reports lock-wait timeout after 30 seconds.
4. Capture the wait relationship — A blocking relationship is visible while the wait is active.
5. Release both transactions — Both sessions return to a clean prompt and neither change is committed.
6. Build the deadlock in a precise order — A owns player 1.
7. Acquire the second lock — B owns player 2 and A owns player 1.
8. Make A request B’s row — A waits for B.
9. Complete the cycle — One session reports deadlock error 1213; the other can proceed. Victim selection is not fixed.
10. Capture the deadlock and recover — The latest detected deadlock contains the cycle and victim.
11. Verify restored data — Players 1, 2 and 42 have 100, 200 and 300 points if the starting data was unchanged.
12. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Run ROLLBACK in A and B even after errors, then type exit in all three clients. Closing the client also releases session locks, but demonstrate explicit rollback first. Do not kill arbitrary sessions.

**Instructor execution sheet:**


## Replication delay and reporting freshness

Slides 25–29. Time: 15.

**Expected reasoning:** The synthetic replica receiver is running but SQL applier stopped with duplicate-key error 1062. NULL lag is not zero. Investigate consistency and cause before repair; temporary primary reads require capacity and business approval.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Student recognizes NULL delay as unknown rather than healthy. Recommendation addresses stale reads and the replication error separately.

**Submission:** A replication escalation note with evidence and routing tradeoffs.

**Guided walkthrough checkpoints:**

1. Read the fixture and record provenance — The file explicitly labels itself synthetic; receiver and applier states differ.
2. Build a freshness table — You distinguish reception from application and can explain why a report may be stale.
3. Choose the next investigation — Your escalation asks for a specific consistency/applier investigation and a business freshness decision.
4. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** No live state was changed. Keep the original fixture unchanged and label all submitted findings as synthetic evidence analysis.

**Instructor execution sheet:**


## SQL Server requests, sessions and wait deltas

Slides 30–34. Time: 40.

**Expected reasoning:** A sleeping session may hold an uncommitted transaction. Cached totals aggregate executions since compilation and do not necessarily describe this incident. Inspect execution_count, interval evidence and plans together. In the fixture LCK_M_X grows 12,000 ms, SOS_SCHEDULER_YIELD 1,000 ms, and PAGEIOLATCH_SH 200 ms.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Report includes time window, permissions and correct units. Student separates historical high waits from interval changes.

**Submission:** A SQL Server baseline and a wait-delta interpretation.

**Guided walkthrough checkpoints:**

1. Set connection details in the client shell — sqlcmd is found; the password is not echoed.
2. Confirm identity and database access — The assigned login, timestamp and SQL Server 2022 version are returned.
3. Capture baseline diagnostics — Requests, sessions, waits, cached plans, Query Store and job-history results are captured. Some result sets may be empty.
4. Observe a bounded workload — The workload completes after 30 report queries. A fast host may finish before the observer captures an active request.
5. Compute interval wait deltas — LCK_M_X increases 12000 ms, SOS_SCHEDULER_YIELD 1000 ms and PAGEIOLATCH_SH 200 ms.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Unset SQLCMDPASSWORD in each client shell after use. Workload.sql does not create the commented optional index. Leave SQL Server running; retain reviewed evidence.

**Instructor execution sheet:**


## Blocking chains, Query Store and job failures

Slides 35–39. Time: 40.

**Expected reasoning:** Compare runtime evidence across comparable intervals and row counts. Plan forcing needs validation and rollback. The fixture shows query 17 changing from plan 3 to 8 with higher duration/reads after deployment, while the job failure is a separate permission issue. The live training job deliberately throws a synthetic error.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Capture a blocking relation and roll back both sessions. Compare Query Store duration/reads and identify the failed job step using live or explicitly synthetic evidence.

**Submission:** A blocking worksheet, plan comparison and job-failure escalation.

**Guided walkthrough checkpoints:**

1. Open three SQL client sessions — Each terminal shows its own sqlcmd prompt, ready for T-SQL and GO.
2. Prepare three independent query windows — A, B and Observer have different session IDs.
3. Acquire a lock in A — A’s update completes and retains its transaction lock.
4. Create a bounded wait in B — B waits, then may return lock timeout error 1222.
5. Observe the blocker — The waiting request names A as blocker. A may be sleeping while retaining an open transaction.
6. Release A’s transaction — A has zero open transactions. B either finishes or has already reported its bounded timeout.
7. Release B and verify data — B has zero open transactions; player 1 has 100 points and player 2 has 200 on the unchanged seed.
8. Live extension — Compare a controlled index change — The new index can change reads/plan selection. Query Store runtime records may take time to populate.
9. Live extension — Start the intentional job failure — The job is accepted for execution and fails deliberately shortly afterward.
10. Live extension — Read job history with the learner login — The failed step contains the synthetic training message.
11. Compare captured Query Store and job evidence — A quantitative before/after comparison and separate job diagnosis; neither fixture is claimed as live evidence.
12. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** In A and any explicit transaction-owning session run ROLLBACK if @@TRANCOUNT > 0. Instructor drops IX_Transactions_Player from SupportLab.dbo.Transactions if this exercise created it. Both writers use explicit transactions, so rollback restores their uncommitted changes; verify player values before handing the lab to another team. Close SQL sessions and unset SQLCMDPASSWORD.

**Instructor execution sheet:**

Live extension — Compare a controlled index change

Learners first capture workload.sql and diagnostics.sql results. Instructor then runs the index statement. Learners repeat the same workload and inspect Query Store.

```sql
USE SupportLab;
CREATE INDEX IX_Transactions_Player ON dbo.Transactions(player_id) INCLUDE(amount);
EXEC sys.sp_query_store_flush_db;
GO
```

Live extension — Start the intentional job failure

Start only the named synthetic job, then tell learners when it has finished.

```sql
EXEC msdb.dbo.sp_start_job @job_name=N'SupportLab-IntentionalFailure';
GO
```
## Application/database correlation

Slides 40–44. Time: 50.

**Expected reasoning:** The supplied request waits 4,000 ms for a pool connection, spends 40 ms in SQL and 960 ms elsewhere. The live latency fault intentionally delays after connecting; it is not a real pool implementation. Repeated retries can increase load and duplicate non-idempotent work.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Timeline accounts for measured time without inventing an exact database-request-ID join. Learner distinguishes the sample app’s behavior from the supplied pooled-app evidence.

**Submission:** A correlated timeline and a targeted escalation request.

**Guided walkthrough checkpoints:**

1. Read and reconcile the synthetic request timing — For r900, 4000 + 40 + 960 = 5000 ms. Retries and pooled connection wait are supplied evidence, not live app features.
2. Measure the healthy live baseline — A healthy baseline has successful responses; times depend on the host.
3. Introduce application-side delay — The app now adds 1500 ms during the request path.
4. Compare latency with application evidence — Responses are roughly 1.5 seconds slower; logs provide request IDs and latency_ms.
5. Reset and confirm the comparison — The added delay disappears; compare equivalent routes and sample counts.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Instructor confirms reset. Keep the synthetic pooled-app timeline and live delay experiment in separate sections of the report.

**Instructor execution sheet:**

Introduce application-side delay

Tell learners when the bounded fault is active.

```bash
cd "$COURSE_ROOT"
sudo shared/scripts/fault.sh latency
```

Reset and confirm the comparison

Reset; learners repeat the same traffic command once more.

```bash
sudo shared/scripts/fault.sh reset
shared/scripts/traffic.sh http://127.0.0.1:8080/loyalty 5
```
## Final database incident challenge

Slides 45–49. Time: 75.

**Expected reasoning:** Case D: execution count and returned rows are stable; reads and per-call duration rose after a plan changed. No observed blocker explains the sampled window. Compare plan/statistics/deployment evidence before proposing an index. Post-change capture is consistent with reduced work but does not prove which production change would be best. See the concealed case D release card.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Quantify the report regression and test at least two explanations. Propose a scoped change and compare instructor-released before/after evidence. Submit a bounded database-health automation design and an individual explanation.

**Submission:** A case report with calculations, alternative hypotheses, before/after comparison and a database-health design.

**Guided walkthrough checkpoints:**

1. Prepare your submission workspace — A report exists before opening the synthetic case; roles and start time are recorded.
2. Prepare database-specific evidence — The worksheet and synthetic case are available; do not confuse case evidence with live baseline checks.
3. Receive the incident and assign roles — You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.
4. Investigate within the time budget — Your timeline contains evidence-linked observations rather than a list of guesses.
5. Collect and inspect evidence — Original and additional evidence remain distinguishable.
6. Propose one mitigation and define recovery — The instructor can review a concrete action; the report distinguishes diagnosis from speculation.
7. Verify and hand over — Recovery is supported by the affected business function and a clear observation window.

**Exercise-specific recovery:** This case uses synthetic evidence; do not modify the shared database. Close any optional baseline clients and unset SQLCMDPASSWORD. Preserve submitted pre-change reasoning and post-change comparisons.

**Instructor execution sheet:**
