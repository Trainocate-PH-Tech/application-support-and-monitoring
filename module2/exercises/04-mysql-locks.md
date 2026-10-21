# MySQL blocking and deadlocks

**Time:** 40 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** locking-timeline.md — session IDs, sequence, lock wait and deadlock evidence; lock-diagram.md — held/requested rows, victim, survivor and recovery checks

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Team login has UPDATE on support_lab and lock-diagnostic visibility. Open THREE SSH terminals to the same application host and label them A, B and Observer. Reserve 10 minutes with the instructor to avoid other team writes.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Two concurrent updates stall. Separate an ordinary lock wait from a deadlock and recover both sessions.

## Learning goals

- A blocking chain can persist without a cycle; a deadlock requires a cycle.
- The deadlock victim is not necessarily the root cause.
- An open transaction can hold locks even while its client appears idle.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-04" && printf 'Workspace ready\n'
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
| 1 | A | Begin; update the first row |
| 2 | B | Begin; issue conflicting update |
| 3 | Observer | Capture the wait before the timeout |
| 4 | A then B | Roll back both sessions |
| 5 | A and B | Follow the separate deadlock sequence; roll back both afterward |

## Step-by-step walkthrough

### Step 1 — Open all three MySQL sessions

**Where and who:** Learner · Bash terminals A, B and Observer

Run this connection command in each terminal. All subsequent SQL steps name the terminal where they belong.

```bash
mysql --defaults-extra-file="$HOME/.support-lab.cnf" support_lab
```

**Expected result:** Each terminal has its own mysql> prompt and independent session.

**If it differs:** Do not run the whole exercise in a single connection; it cannot demonstrate contention.

### Step 2 — Acquire the first lock

**Where and who:** Session A · MySQL

Run these statements and leave the transaction open. The instructor keeps this demonstration under one minute.

```sql
SELECT CONNECTION_ID();
START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=1;
```

**Expected result:** UPDATE completes; A holds a lock on player 1 until commit/rollback.

**If it differs:** If UPDATE itself waits, another session owns a conflicting lock; ask the instructor to restore a clean baseline.

### Step 3 — Create a bounded waiter

**Where and who:** Session B · MySQL

The UPDATE below should wait. Do not type the next task in B while it waits; switch to Observer.

```sql
SET SESSION innodb_lock_wait_timeout=30;
START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=1;
```

**Expected result:** B pauses waiting for A, or reports lock-wait timeout after 30 seconds.

**If it differs:** If B finishes immediately, verify A is still in its transaction and both use the same database/row.

### Step 4 — Capture the wait relationship

**Where and who:** Observer · MySQL

Run while B is waiting; capture connection IDs and the requested lock.

```sql
SHOW FULL PROCESSLIST;
SELECT * FROM performance_schema.data_lock_waits;
```

**Expected result:** A blocking relationship is visible while the wait is active.

**If it differs:** If the timeout elapsed before capture, first roll back A and B, then repeat the short sequence.

### Step 5 — Release both transactions

**Where and who:** Session A, then Session B · MySQL

Run ROLLBACK in A first. B may finish its UPDATE after the lock releases; then run ROLLBACK in B too.

```sql
ROLLBACK;
```

**Expected result:** Both sessions return to a clean prompt and neither change is committed.

**If it differs:** A timeout does not reliably mean the whole transaction ended; explicitly roll back both sessions.

### Step 6 — Build the deadlock in a precise order

**Where and who:** Session A and Session B · MySQL

First run the A block. Then run the B block in the next step; do not paste both into one terminal.

```sql
START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=1;
```

**Expected result:** A owns player 1.

**If it differs:** If blocked already, roll back and restore the baseline before continuing.

### Step 7 — Acquire the second lock

**Where and who:** Session B · MySQL

B locks a different row.

```sql
START TRANSACTION;
UPDATE players SET points=points+1 WHERE id=2;
```

**Expected result:** B owns player 2 and A owns player 1.

**If it differs:** Confirm no other team is writing these rows.

### Step 8 — Make A request B’s row

**Where and who:** Session A · MySQL

This statement should block. Immediately switch to B for the next step.

```sql
UPDATE players SET points=points+1 WHERE id=2;
```

**Expected result:** A waits for B.

**If it differs:** If it times out before the next step, roll back both sessions and repeat.

### Step 9 — Complete the cycle

**Where and who:** Session B · MySQL

Request A’s row. Either A or B can be selected as the victim; inspect both terminals.

```sql
UPDATE players SET points=points+1 WHERE id=1;
```

**Expected result:** One session reports deadlock error 1213; the other can proceed. Victim selection is not fixed.

**If it differs:** If no deadlock occurs, check row order and whether either transaction was already rolled back.

### Step 10 — Capture the deadlock and recover

**Where and who:** Observer, then A and B · MySQL

Observer runs the status statement. After saving evidence, run ROLLBACK separately in A and B, then the final SELECT in Observer.

```sql
SHOW ENGINE INNODB STATUS\G
```

**Expected result:** The latest detected deadlock contains the cycle and victim.

**If it differs:** Capture promptly: a later deadlock can replace this diagnostic record.

### Step 11 — Verify restored data

**Where and who:** Observer · MySQL

After BOTH writers have rolled back, compare the seeded values.

```sql
SELECT id,points FROM players ORDER BY id;
```

**Expected result:** Players 1, 2 and 42 have 100, 200 and 300 points if the starting data was unchanged.

**If it differs:** A different result may reflect committed work from another team; do not overwrite it without instructor review.

### Step 12 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does killing the waiting session remove the head blocker?
2. Does retrying immediately forever solve deadlocks safely?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-04` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] locking-timeline.md — session IDs, sequence, lock wait and deadlock evidence
- [ ] lock-diagram.md — held/requested rows, victim, survivor and recovery checks

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Run ROLLBACK in A and B even after errors, then type exit in all three clients. Closing the client also releases session locks, but demonstrate explicit rollback first. Do not kill arbitrary sessions.

## Completion criteria

- [ ] Evidence shows the blocking relation or deadlock cycle.
- [ ] Both sessions end their transactions and a subsequent update succeeds.

[Previous exercise](03-mysql-plans.md) · [Module agenda](../README.md) · [Next exercise](05-replication.md)
