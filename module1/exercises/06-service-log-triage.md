# Service failures and application log diagnosis

**Time:** 35 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** startup-timeline.md — startup evidence and repair verification; permission-timeline.md — runtime error, ownership evidence and recovered request IDs

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

A healthy stack from exercise 05; journal access; a reserved instructor-controlled fault slot.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

The application worked before a change. One team investigates a startup fault; another receives a permission fault after reset.

## Learning goals

- Capture unit state, exit status and journal before changing configuration.
- Correlate an HTTP response request ID with its application log line.
- Distinguish startup failure, runtime failure and failed dependency checks.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-06" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Capture the healthy baseline

**Where and who:** Learner · application server · Bash terminal

Record time and a readiness response before the instructor changes anything.

```bash
date -u +%FT%TZ
curl -i http://127.0.0.1:8080/loyalty/health
```

**Expected result:** HTTP 200 establishes the before-state.

**If it differs:** If already unhealthy, ask the instructor to resolve the pre-existing fault first.

### Step 2 — Introduce and observe a startup fault

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** A deliberate service-start error is expected; the instructor announces that the investigation can begin.

**If it differs:** If a saved fault already exists, stop and coordinate ownership before resetting it.

### Step 3 — Locate the failing startup configuration

**Where and who:** Learner · application server · Bash terminal

Do not restart the service yet. Inspect the effective unit and journal.

```bash
systemctl status support-tomcat --no-pager
systemctl cat support-tomcat
journalctl -u support-tomcat -n 60 --utc --no-pager
```

**Expected result:** status may return nonzero. The training drop-in points to a nonexistent executable.

**If it differs:** If you only inspect the main unit file, you may miss the override; use systemctl cat.

### Step 4 — Reset, then introduce a different failure

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Readiness is healthy between faults; the permission fault affects configuration readability.

**If it differs:** If readiness has not recovered, do not inject another fault.

### Step 5 — Inspect runtime symptoms and file access

**Where and who:** Learner · application server · Bash terminal

Capture the request ID and journal. Ask the instructor to run the privileged path checks shown next.

```bash
curl -i http://127.0.0.1:8080/loyalty/health
journalctl -u support-tomcat --since '5 minutes ago' --utc --no-pager
```

**Expected result:** HTTP 503 accompanies a file-access error even though Tomcat can be active.

**If it differs:** A running process alone does not establish application health.

### Step 6 — Verify permissions, restore and retest

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Before reset the root-owned config is 600; restored access is root:supportapp mode 640. HTTP checks recover.

**If it differs:** Do not print the configuration contents or replace the mode with 777.

### Step 7 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does a restart policy repair a bad executable path?
2. Does a missing ERROR line prove the service started?
3. Why is chmod 777 an inappropriate application-config fix?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-06` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] startup-timeline.md — startup evidence and repair verification
- [ ] permission-timeline.md — runtime error, ownership evidence and recovered request IDs

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Instructor confirms fault reset and healthy business requests. Keep the two fault timelines separate; leave the shared services running.

## Completion criteria

- [ ] Evidence names the actual failed executable or unreadable file.
- [ ] Recovery includes HTTP and business checks, not only active service status.

[Previous exercise](05-install-stack.md) · [Module agenda](../README.md) · [Next exercise](07-resources-network.md)
