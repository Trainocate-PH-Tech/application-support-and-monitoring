# SQL Server requests, sessions and wait deltas

**Time:** 40 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** sql-baseline.txt — diagnostics output; wait-deltas.md — intervals, units, arithmetic and interpretation

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Separate SQL Server lab is ready; learner login/grants are provisioned. The application host or designated client workstation has ODBC sqlcmd available. Instructor supplies SQL_HOST and the approved certificate policy.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

SQL Server is blamed for high CPU. Capture active work and distinguish current activity from cumulative counters.

## Learning goals

- SQL Server 2022 diagnostic permissions differ from older examples; validate visibility first.
- Requests and sessions are related but not interchangeable.
- Wait statistics are cumulative; compare two captures over a known interval.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-06" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Set connection details in the client shell

**Where and who:** Learner · designated SQL client host · Bash

In this shell, define SQL_HOST and SQL_LOGIN. Read the password without echoing it. Use the instructor-provided hostname, not the example text.

```bash
read -r -p 'SQL Server hostname or private IP: ' SQL_HOST
read -r -p 'Assigned SQL login: ' SQL_LOGIN
read -r -s -p 'SQL password: ' SQLCMDPASSWORD
printf '\n'
export SQL_HOST SQL_LOGIN SQLCMDPASSWORD
SQL_TLS_ARGS=()
command -v sqlcmd
```

**Expected result:** sqlcmd is found; the password is not echoed.

**If it differs:** If not found, use the instructor-installed /opt/mssql-tools18/bin/sqlcmd or add that directory to PATH. Do not put passwords in -P arguments.

### Step 2 — Confirm identity and database access

**Where and who:** Learner · same SQL client Bash shell

Use a trusted server certificate. If the dedicated disposable lab uses a self-signed certificate, the instructor may explicitly direct setting SQL_TLS_ARGS=(-C) in this shell; do not bypass validation without that context.

```bash
sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab -b -Q 'SELECT SYSUTCDATETIME(), SUSER_SNAME(), @@VERSION;'
```

**Expected result:** The assigned login, timestamp and SQL Server 2022 version are returned.

**If it differs:** A TLS error differs from login failure; check the instructor certificate instructions before continuing.

### Step 3 — Capture baseline diagnostics

**Where and who:** Learner · same SQL client Bash shell

The course files must be present on this client host. Write output to your evidence directory, then read it.

```bash
cd "$COURSE_ROOT"
sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab -b -i shared/sql/sqlserver/diagnostics.sql -o "$HOME/support-lab/evidence/m2-06/sql-baseline.txt"
less "$HOME/support-lab/evidence/m2-06/sql-baseline.txt"
```

**Expected result:** Requests, sessions, waits, cached plans, Query Store and job-history results are captured. Some result sets may be empty.

**If it differs:** Inspect any permission errors; do not treat a failed query as an empty healthy result. SQL text/plans require review before sharing.

### Step 4 — Observe a bounded workload

**Where and who:** Learner · second SQL client Bash shell

Set the connection variables in this second shell as in step 1. Run the workload while the first shell repeats diagnostics. Do not use production targets.

```bash
cd "$COURSE_ROOT"
sqlcmd "${SQL_TLS_ARGS[@]}" -S "tcp:$SQL_HOST,1433" -U "$SQL_LOGIN" -d SupportLab -b -i shared/sql/sqlserver/workload.sql
```

**Expected result:** The workload completes after 30 report queries. A fast host may finish before the observer captures an active request.

**If it differs:** Use the synthetic interval evidence if live timing is inconclusive; do not increase workload without instructor direction.

### Step 5 — Compute interval wait deltas

**Where and who:** Learner · application server · Bash terminal

Read the two synthetic captures and subtract earlier counters from later counters for each wait type.

```bash
cd "$COURSE_ROOT"
cat shared/fixtures/sqlserver-waits.csv
```

**Expected result:** LCK_M_X increases 12000 ms, SOS_SCHEDULER_YIELD 1000 ms and PAGEIOLATCH_SH 200 ms.

**If it differs:** These cumulative wait deltas can exceed wall-clock time with concurrent sessions; they are not simple CPU percentages.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Can a sleeping session be the head blocker?
2. Does highest total_worker_time identify the currently slowest query?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-06` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] sql-baseline.txt — diagnostics output
- [ ] wait-deltas.md — intervals, units, arithmetic and interpretation

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Unset SQLCMDPASSWORD in each client shell after use. Workload.sql does not create the commented optional index. Leave SQL Server running; retain reviewed evidence.

## Completion criteria

- [ ] Report includes time window, permissions and correct units.
- [ ] Student separates historical high waits from interval changes.

[Previous exercise](05-replication.md) · [Module agenda](../README.md) · [Next exercise](07-sqlserver-blocking-plans-jobs.md)
