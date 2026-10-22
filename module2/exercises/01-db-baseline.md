# Database baseline and safe access

**Time:** 35 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** db-baseline.txt — time, version, identity, counters and check statuses; db-baseline-notes.md — interpretation and unavailable evidence

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Module 1 stack is healthy. The EC2 training administrator is developer with password password; alternatively, use a per-team account with the diagnostic grants in the setup guide.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

The application reports database errors. Establish engine, endpoint, identity and connectivity before tuning anything.

## Learning goals

- Use a protected client option file instead of putting passwords in command arguments.
- Read-only application rights differ from administrative diagnostic permissions.
- Capture UTC time, engine version and connection counts with every baseline.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-01" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Create a protected client configuration

**Where and who:** Learner · application server · Bash terminal

Open nano after creating the file with restrictive permissions. Enter the four configuration lines below in the editor; use the EC2 training credentials shown below, or your assigned team credentials. Save with Ctrl-O, Enter; exit with Ctrl-X.

```bash
umask 077
touch "$HOME/.support-lab.cnf"
chmod 600 "$HOME/.support-lab.cnf"
nano "$HOME/.support-lab.cnf"
```

**Expected result:** The file exists with mode 600. Do not paste its contents into submitted evidence.

**If it differs:** If the file already has valid credentials, inspect/edit locally rather than overwriting another configuration.

### Step 2 — Enter the client settings

**Where and who:** Learner · nano editor for ~/.support-lab.cnf

This is configuration text, not shell commands. These examples use the local EC2 administrator developer with password password. Use your assigned team credentials instead when provided.

```ini
[client]
user=developer
password=password
host=localhost
```

**Expected result:** The file contains the EC2 training login or your assigned team login.

**If it differs:** Account host matching matters; do not switch localhost to 127.0.0.1 unless the instructor created the matching account.

### Step 3 — Run the bounded health check

**Where and who:** Learner · application server · Bash terminal

Return to Bash. Capture status immediately; do not log the configuration file.

```bash
stat -c '%a %n' "$HOME/.support-lab.cnf"
cd "$COURSE_ROOT"
MYSQL_CNF="$HOME/.support-lab.cnf" shared/scripts/db-health.sh
check_rc=$?
printf 'db_health_exit=%s\n' "$check_rc"
```

**Expected result:** Mode is 600; healthy output includes engine version, SELECT 1 result, connection counters and exit 0.

**If it differs:** Exit 2 means configuration prerequisites failed; client access-denied and connection-timeout errors require different checks.

### Step 4 — Enter MySQL and identify the session

**Where and who:** Learner · application server · Bash terminal

Open the interactive client. The next step runs at the mysql> prompt.

```bash
mysql --defaults-extra-file="$HOME/.support-lab.cnf"
```

**Expected result:** The mysql> prompt appears.

**If it differs:** If the prompt never appears, verify credentials privately and the MySQL service; do not run SQL in Bash.

### Step 5 — Capture a read-only baseline

**Where and who:** Learner · application server · interactive MySQL client

Run each statement and record its meaning. Then type exit to return to Bash.

```sql
SELECT UTC_TIMESTAMP(), CURRENT_USER(), VERSION();
SHOW FULL PROCESSLIST;
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'log_error';
exit
```

**Expected result:** Identity and version print; connection headroom is assessed against the configured limit.

**If it differs:** Visibility depends on privileges. A denied query is unavailable evidence, not proof that no sessions exist.

### Step 6 — Inspect service and full diagnostics

**Where and who:** Learner · application server · Bash terminal

You should now be back at the Bash prompt. Read the instructor-designated MySQL error log only with the granted access.

```bash
cd "$COURSE_ROOT"
systemctl status mysql --no-pager
journalctl -u mysql --since '15 minutes ago' --utc --no-pager
mysql --defaults-extra-file="$HOME/.support-lab.cnf" < shared/sql/mysql/diagnostics.sql
```

**Expected result:** Read-only checks execute; error-log destinations may be a file, journal or stderr depending on setup.

**If it differs:** If journal access is denied, ask the instructor to capture the relevant window; do not broaden privileges yourself.

### Step 7 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Can a successful SELECT 1 prove every business query is fast?
2. Does SHOW PROCESSLIST necessarily show all users to an unprivileged login?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-01` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] db-baseline.txt — time, version, identity, counters and check statuses
- [ ] db-baseline-notes.md — interpretation and unavailable evidence

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Exit any open mysql client. Keep the mode-600 client file for later exercises and exclude it from submissions. No server configuration changes were required.

## Completion criteria

- [ ] Baseline identifies endpoint and effective database user.
- [ ] Learner distinguishes access denied from server unreachable.

[Module agenda](../README.md) · [Next exercise](02-mysql-slow.md)
