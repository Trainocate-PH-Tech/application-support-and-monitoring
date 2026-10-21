# EXPLAIN, indexes and misleading assumptions

**Time:** 35 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** plan-comparison.md — before/after plan fields, identical results and index tradeoffs

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Seeded support_lab with 100,000 transactions; no idx_transactions_player index from a previous team; instructor controls CREATE/DROP INDEX.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

The report scans many transactions. Decide whether a targeted index improves this workload.

## Learning goals

- EXPLAIN estimates access strategy and cardinality; it is not proof of actual elapsed time.
- Indexes add write/storage costs and must be justified by workload.
- A tiny training dataset may show plan differences without dramatic timing differences.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-03" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Connect and record the baseline

**Where and who:** Learner · application server · Bash terminal

Open the client; run the following SQL step at mysql>.

```bash
mysql --defaults-extra-file="$HOME/.support-lab.cnf"
```

**Expected result:** The client connects with the assigned team login.

**If it differs:** Resolve authentication before investigating query performance.

### Step 2 — Inspect data and the estimated plan

**Where and who:** Learner · application server · interactive MySQL client

Record both the plan and business result before changing an index.

```sql
USE support_lab;
SELECT COUNT(*) FROM transactions;
SHOW INDEX FROM transactions;
EXPLAIN SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
```

**Expected result:** Data count is 100000; the player-42 result is 1000 and 10000.00. Initial plan details depend on engine statistics.

**If it differs:** If idx_transactions_player already exists, ask the instructor to restore the baseline before comparing.

### Step 3 — Apply the approved training index

**Where and who:** Instructor · administrative MySQL client

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The named index is created.

**If it differs:** If an index already exists, inspect it first; do not drop unrelated indexes.

### Step 4 — Compare after-state without assuming faster timing

**Where and who:** Learner · application server · interactive MySQL client

Repeat the same query and inspect access method, key and estimated rows.

```sql
EXPLAIN SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42;
exit
```

**Expected result:** Business results remain the same; the plan can use the new index.

**If it differs:** An unchanged plan requires investigation of selectivity/statistics; command success alone is not proof of benefit.

### Step 5 — Restore the exercise baseline

**Where and who:** Instructor · administrative MySQL client

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The training index is absent and the original primary key remains.

**If it differs:** If another team is using the index experiment, coordinate before cleanup.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Is every full scan bad?
2. Can an index be present yet unused?
3. Does LIMIT guarantee cheap execution?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-03` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] plan-comparison.md — before/after plan fields, identical results and index tradeoffs

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Instructor drops the named training index after evidence is captured. Learners exit the client and retain before/after plans. Do not delete the seeded tables.

## Completion criteria

- [ ] Before/after plans and equivalent query results are retained.
- [ ] Recommendation includes an index tradeoff and measurement limitation.

[Previous exercise](02-mysql-slow.md) · [Module agenda](../README.md) · [Next exercise](04-mysql-locks.md)
