# Blocking chains, Query Store and job failures

**Time:** 40 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core: blocking timeline; guided evidence: Query Store and job history; live plan changes/jobs: extension | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** sql-blocking.md — sessions, head blocker and release evidence; query-store-job-report.md — live versus synthetic findings, units and next checks

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete SQL Server connection setup. Open three independent query sessions A, B and Observer against SupportLab using sqlcmd interactive mode or the instructor-approved query editor. Instructor controls index changes, Query Store flushing and job starts.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A deployment coincides with latency and a failed reporting job. Establish whether the symptoms share a cause.

## Learning goals

- Identify the head blocker through sessions as well as active requests.
- Query Store compares plans and runtime intervals; correlation with deployment is not proof of causation.
- SQL Agent job outcome and step outcome need separate interpretation.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-07" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Session sequence

| Order | Session | Action |
|---|---|---|
| 1 | A | Open transaction and update |
| 2 | B | Begin transaction; issue bounded conflicting update |
| 3 | Observer | Capture blocker while B waits |
| 4 | A | Roll back |
| 5 | B | Roll back even after timeout; verify state |

## Step-by-step walkthrough

### Step 1 — Open three SQL client sessions

**Where and who:** Learner · three SQL client Bash terminals

In each terminal, repeat the connection-variable/password setup from exercise 06, including the approved SQL_TLS_ARGS choice. Launch an interactive client; omit -b here so an expected lock-timeout error does not terminate the session. Label the resulting connections A, B and Observer.

```bash
sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab
```

**Expected result:** Each terminal shows its own sqlcmd prompt, ready for T-SQL and GO.

**If it differs:** If SQL_HOST, SQL_LOGIN or credentials are not set in that terminal, stop and repeat exercise 06 connection setup.

### Step 2 — Prepare three independent query windows

**Where and who:** Learner · SQL Server query window (T-SQL)

In EACH window, select the database and record its session ID. For interactive sqlcmd, GO on its own line sends each batch; a query editor uses Execute.

```sql
USE SupportLab;
SELECT @@SPID AS session_id;
GO
```

**Expected result:** A, B and Observer have different session IDs.

**If it differs:** Reusing one connection cannot create a blocking relationship.

### Step 3 — Acquire a lock in A

**Where and who:** Session A · T-SQL

Leave this transaction open for less than one minute while the next two steps run.

```sql
BEGIN TRAN;
UPDATE dbo.Players SET points=points+1 WHERE id=1;
GO
```

**Expected result:** A’s update completes and retains its transaction lock.

**If it differs:** If A is already blocked, ask the instructor to identify the earlier owner first.

### Step 4 — Create a bounded wait in B

**Where and who:** Session B · T-SQL

B waits for at most 15 seconds. Switch promptly to Observer.

```sql
SET LOCK_TIMEOUT 15000;
BEGIN TRAN;
UPDATE dbo.Players SET points=points+1 WHERE id=1;
GO
```

**Expected result:** B waits, then may return lock timeout error 1222.

**If it differs:** Do not mistake timeout for proof that A released its lock.

### Step 5 — Observe the blocker

**Where and who:** Observer · T-SQL

Run the query while B waits. Save the blocking relation before releasing either transaction in the following steps.

```sql
SELECT session_id,status,wait_type,blocking_session_id
FROM sys.dm_exec_requests WHERE blocking_session_id > 0;
GO
```

**Expected result:** The waiting request names A as blocker. A may be sleeping while retaining an open transaction.

**If it differs:** If no row appears, repeat only after cleaning up A and confirming B is actively waiting.

### Step 6 — Release A’s transaction

**Where and who:** Session A · T-SQL

Release the head blocker only after the observation is recorded. B may now finish its UPDATE; it still needs its own rollback.

```sql
IF @@TRANCOUNT > 0 ROLLBACK;
SELECT @@TRANCOUNT AS open_transactions;
GO
```

**Expected result:** A has zero open transactions. B either finishes or has already reported its bounded timeout.

**If it differs:** Do not assume B’s transaction ended just because A rolled back.

### Step 7 — Release B and verify data

**Where and who:** Session B · T-SQL

Run this whether B succeeded after the release or timed out. Then verify the seeded points.

```sql
IF @@TRANCOUNT > 0 ROLLBACK;
SELECT @@TRANCOUNT AS open_transactions;
SELECT id,points FROM dbo.Players ORDER BY id;
GO
```

**Expected result:** B has zero open transactions; player 1 has 100 points and player 2 has 200 on the unchanged seed.

**If it differs:** If values differ, ask the instructor about other team writes; do not silently overwrite shared data.

### Step 8 — Live extension — Compare a controlled index change

**Where and who:** Instructor · T-SQL; learners run workload/diagnostics

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. This is an optional live extension.

**Expected result:** The new index can change reads/plan selection. Query Store runtime records may take time to populate.

**If it differs:** If the index exists, inspect/reset the training baseline first. Do not infer regression solely from a changed plan ID.

### Step 9 — Live extension — Start the intentional job failure

**Where and who:** Instructor · T-SQL

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. This is an optional live extension.

**Expected result:** The job is accepted for execution and fails deliberately shortly afterward.

**If it differs:** If SQL Agent is starting, wait and retry; do not create another job.

### Step 10 — Live extension — Read job history with the learner login

**Where and who:** Learner · Observer T-SQL session

After a few seconds, inspect history through the supported procedure.

```sql
EXEC msdb.dbo.sp_help_jobhistory @job_name=N'SupportLab-IntentionalFailure', @mode=N'FULL';
GO
```

**Expected result:** The failed step contains the synthetic training message.

**If it differs:** If history is denied, ask the instructor to check SQLAgentReaderRole; do not query protected base tables with an administrator account instead.

### Step 11 — Compare captured Query Store and job evidence

**Where and who:** Learner · application server · Bash terminal

Core guided evidence task: read the two fixture files. Compute duration and logical-read changes for query 17; identify the failed job step separately. Explain one alternative to a missing index and which observation would distinguish it. Live plan and job steps above are optional extensions.

```bash
cat "$COURSE_ROOT/shared/fixtures/query-store.csv"
cat "$COURSE_ROOT/shared/fixtures/job-history.csv"
```

**Expected result:** A quantitative before/after comparison and separate job diagnosis; neither fixture is claimed as live evidence.

**If it differs:** Units are microseconds and execution intervals must be comparable.

### Step 12 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does a changed plan guarantee a regression?
2. Is plan forcing always the safest first action?
3. Can a failed job explain stale reports without explaining API latency?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-07` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] sql-blocking.md — sessions, head blocker and release evidence
- [ ] query-store-job-report.md — live versus synthetic findings, units and next checks

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

In A and any explicit transaction-owning session run ROLLBACK if @@TRANCOUNT > 0. Instructor drops IX_Transactions_Player from SupportLab.dbo.Transactions if this exercise created it. Both writers use explicit transactions, so rollback restores their uncommitted changes; verify player values before handing the lab to another team. Close SQL sessions and unset SQLCMDPASSWORD.

## Completion criteria

- [ ] Capture a blocking relation and roll back both sessions.
- [ ] Compare Query Store duration/reads and identify the failed job step using live or explicitly synthetic evidence.

[Previous exercise](06-sqlserver-baseline.md) · [Module agenda](../README.md) · [Next exercise](08-app-db-correlation.md)
