# Log parsing and threshold monitoring

**Time:** 40 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** monitor-policy.md — definitions, thresholds, no-data and freshness handling; monitor-results.txt — fixture and boundary-case outputs

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Synthetic application.log is readable. Understand that this parser accepts a bounded input window; it does not choose freshness automatically.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Build a monitor that counts actual requests, rejects malformed rows and reports slow requests.

## Learning goals

- Define the time window, denominator, threshold comparison and no-data behavior.
- Count status fields rather than words such as ERROR in free text.
- A monitoring result is only as useful as its handling of missing or stale input.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-03" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Run the known fixture

**Where and who:** Learner · application server · Bash terminal

The command intentionally produces an alert. Capture its status without stopping the exercise.

```bash
cd "$COURSE_ROOT"
shared/scripts/monitor-log.sh shared/fixtures/application.log 10 1000
monitor_rc=$?
printf 'monitor_exit=%s\n' "$monitor_rc"
```

**Expected result:** CSV: 6 requests, 2 errors, 33.33 percent, 2 slow, 1 malformed, ALERT; exit 1.

**If it differs:** If your result differs, confirm that the original fixture has not been edited.

### Step 2 — Create isolated boundary inputs

**Where and who:** Learner · application server · Bash terminal

These files belong to this exercise’s evidence folder, not the original fixture directory.

```bash
printf 'status=200 latency_ms=10\n' > ~/support-lab/evidence/m3-03/healthy.log
: > ~/support-lab/evidence/m3-03/empty.log
printf 'malformed record\n' > ~/support-lab/evidence/m3-03/malformed.log
```

**Expected result:** Three small test files exist; the empty file is intentionally zero bytes.

**If it differs:** Do not redirect into a real application log.

### Step 3 — Compare healthy, empty and malformed cases

**Where and who:** Learner · application server · Bash terminal

Run each check and record its immediate exit status.

```bash
for case_name in healthy empty malformed; do
    "$COURSE_ROOT/shared/scripts/monitor-log.sh" "$HOME/support-lab/evidence/m3-03/$case_name.log" 10 1000
    monitor_rc=$?
    printf '%s exit=%s\n' "$case_name" "$monitor_rc"
done
```

**Expected result:** Healthy returns OK/0; empty and malformed-only inputs return NO_DATA/2.

**If it differs:** NO_DATA is not proof that the service is healthy; inspect the data source and time window.

### Step 4 — Parse a current journal window

**Where and who:** Learner · application server · Bash terminal

Capture recent application messages with their original message text. Record the capture time separately.

```bash
date -u +%FT%TZ > ~/support-lab/evidence/m3-03/captured-at.txt
journalctl -u support-tomcat --since '5 minutes ago' --utc -o cat --no-pager > ~/support-lab/evidence/m3-03/window.log
"$COURSE_ROOT/shared/scripts/monitor-log.sh" ~/support-lab/evidence/m3-03/window.log 10 1000
```

**Expected result:** Live results vary with traffic; non-request startup lines count as malformed.

**If it differs:** If there are no requests, ask the instructor to permit a few bounded healthy probes; do not report NO_DATA as zero errors.

### Step 5 — Document the monitoring policy

**Where and who:** Learner · notes

Specify the window, valid-record rule, 5xx definition, denominator, inclusive thresholds and behavior for stale/missing data. Add a freshness check as an extension.

**Expected result:** Someone else can explain why each fixture alerts or does not alert.

**If it differs:** A parser’s success does not prove that its input is recent.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Is zero observed errors equivalent to a healthy service when no requests exist?
2. Should 404 responses count as server failures in this policy?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-03` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] monitor-policy.md — definitions, thresholds, no-data and freshness handling
- [ ] monitor-results.txt — fixture and boundary-case outputs

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Keep the small test files and CSV results as evidence. No service configuration changed; do not delete the live journal or source fixture.

## Completion criteria

- [ ] Fixture result is 6 requests, 2 errors, 33.33%, 2 slow, 1 malformed, ALERT.
- [ ] Empty input yields NO_DATA and exit 2, never healthy.

[Previous exercise](02-evidence.md) · [Module agenda](../README.md) · [Next exercise](04-slow-pipeline.md)
