# MySQL slow-query capture and ranking

**Time:** 40 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** slow-query-ranking.md — frequency, total/average time, rows examined and next check; logging-change-record.md — original values, capture window and restoration confirmation

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Working team MySQL client configuration from exercise 01; instructor administrative MySQL access; mysqldumpslow installed on the application host.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Player reports are slow. Capture an intentional slow query and rank work by both frequency and total time.

## Learning goals

- Slow logging is a configuration change and must be restored after the exercise.
- Global long_query_time becomes the default for new sessions; existing sessions may retain their value.
- Frequency, total time, rows examined and lock time answer different questions.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-02" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Record the original logging configuration

**Where and who:** Instructor · administrative MySQL client

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The original ON/OFF value, threshold, output destination and file path are recorded before changes.

**If it differs:** If the admin session closes, restore from the written record; session variables do not survive reconnects.

### Step 2 — Enable a short capture window

**Where and who:** Instructor · same administrative MySQL client

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Settings change successfully on the training database.

**If it differs:** On access denied, stop; learners must not acquire administrative privileges to continue.

### Step 3 — Open a fresh learner connection

**Where and who:** Learner · application server · Bash terminal

Use a fresh client so it inherits the new global threshold.

```bash
mysql --defaults-extra-file="$HOME/.support-lab.cnf"
```

**Expected result:** mysql> appears in a new session.

**If it differs:** An existing session may retain its old long_query_time; do not assume a global change modifies it.

### Step 4 — Create bounded slow-query evidence

**Where and who:** Learner · application server · interactive MySQL client

Run one deliberate delay and one report query. Exit afterward.

```sql
SET SESSION long_query_time = 0.2;
SELECT SLEEP(0.3);
SELECT COUNT(*), SUM(amount) FROM support_lab.transactions WHERE player_id=42;
exit
```

**Expected result:** The intentional SLEEP query exceeds the threshold. The report may be too fast to enter the slow log on this host.

**If it differs:** Do not enlarge the workload to force severe slowness; use the supplied synthetic log for deterministic ranking.

### Step 5 — Inspect the capture and rank the fixture

**Where and who:** Learner · application server · Bash terminal

Instructor shows the new record from the previously identified live log path. In your shell, summarize the supplied synthetic log two ways.

```bash
cd "$COURSE_ROOT"
mysqldumpslow -s t -t 5 shared/fixtures/mysql-slow.log
mysqldumpslow -s c -t 5 shared/fixtures/mysql-slow.log
```

**Expected result:** The similar report queries group into three executions, totaling approximately 3.6 seconds; the single delay takes 3 seconds.

**If it differs:** If the live record is absent, instructor checks log_output, threshold and minimum examined-row settings; do not fabricate a capture.

### Step 6 — Restore the exact original values

**Where and who:** Instructor · original administrative MySQL client

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Values match the first step.

**If it differs:** If a saved variable is NULL because this is a different connection, stop and use the recorded original values explicitly.

### Step 7 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does Query_time alone prove CPU pressure?
2. Will changing a global threshold rewrite existing sessions?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-02` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] slow-query-ranking.md — frequency, total/average time, rows examined and next check
- [ ] logging-change-record.md — original values, capture window and restoration confirmation

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Complete the restoration step even if capture failed. Close learner capture sessions; retain logs according to the instructor retention policy rather than deleting database log files.

## Completion criteria

- [ ] Slow record appears with query time, lock time and row counts.
- [ ] Report explains why a frequent moderate query may cost more overall than one rare slow query.

[Previous exercise](01-db-baseline.md) · [Module agenda](../README.md) · [Next exercise](03-mysql-plans.md)
