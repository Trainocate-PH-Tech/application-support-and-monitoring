# Deployment verification and maintenance boundaries

**Time:** 20 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** deployment-check.sh — completed learner script; deployment-test-matrix.md — before/fault/after outcomes and remaining blind spots

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

A learner health script from exercise 01; healthy seeded player 1; instructor has a reserved fault slot.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A deployment health gate must catch a business failure even if the process is active.

## Learning goals

- Check service, readiness and one representative business response.
- Timeouts and nonzero exits must propagate to the caller.
- Automated diagnosis does not authorize automatic destructive repair.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-06" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Record the business response

**Where and who:** Learner · application server · Bash terminal

Inspect the exact successful response before writing an assertion.

```bash
curl --fail --silent --max-time 5 'http://127.0.0.1:8080/loyalty/player?id=1'
curl --fail --silent --max-time 5 http://127.0.0.1:8080/loyalty/payment
```

**Expected result:** Player response is 1,Synthetic Player One,100 and payment simulator reports ready.

**If it differs:** If earlier transaction labs changed player points, ask the instructor to confirm the intended baseline before hard-coding an assertion.

### Step 2 — Create your deployment gate

**Where and who:** Learner · editor

Create ~/support-lab/bin/deployment-check.sh. Use the example to add a business assertion; also include a payment-route check yourself.

```bash
#!/usr/bin/env bash
set -u
if ! body=$(curl --fail --silent --show-error --max-time 5 'http://127.0.0.1:8080/loyalty/player?id=1'); then
    printf 'player=UNREACHABLE\n'; exit 1
fi
if [[ $body != '1,Synthetic Player One,100' ]]; then
    printf 'player=UNEXPECTED_RESULT\n'; exit 1
fi
printf 'player=OK\n'
# Add a bounded payment check here; return nonzero if it fails.
exit 0
```

**Expected result:** Your own file checks content, not just process existence.

**If it differs:** The scaffold alone does not yet test payment. Complete that part before calling it a payment deployment gate.

### Step 3 — Check and run the gate

**Where and who:** Learner · application server · Bash terminal

Make the file executable only after syntax succeeds.

```bash
bash -n ~/support-lab/bin/deployment-check.sh
chmod 750 ~/support-lab/bin/deployment-check.sh
~/support-lab/bin/deployment-check.sh
gate_rc=$?
printf 'gate_exit=%s\n' "$gate_rc"
```

**Expected result:** Healthy business checks pass with exit 0.

**If it differs:** If output differs, inspect the response rather than weakening the assertion immediately.

### Step 4 — Test an affected business function

**Where and who:** Instructor injects; learner runs gate

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Your completed gate fails on the affected business route even if generic readiness remains green.

**If it differs:** A gate that checks only /health may miss payment failure. Add route-specific assertions.

### Step 5 — Restore and verify

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The same business checks that failed now succeed.

**If it differs:** Do not declare recovery based only on the service becoming active.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Can a generic /health route detect every business outage?
2. Should the first failed probe trigger a database restart?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-06` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] deployment-check.sh — completed learner script
- [ ] deployment-test-matrix.md — before/fault/after outcomes and remaining blind spots

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Instructor confirms reset. Leave your deployment script in your bin directory; do not add automatic restarts, database repairs or cron scheduling to this gate.

## Completion criteria

- [ ] Gate fails on affected business functionality even when Tomcat remains active.
- [ ] Recovery checks cover the same function that originally failed.

[Previous exercise](05-scheduling.md) · [Module agenda](../README.md) · [Next exercise](07-war-room.md)
