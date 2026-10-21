# Replication delay and reporting freshness

**Time:** 15 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** replication-escalation.md — freshness table, error interpretation, routing tradeoff and next checks

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

The synthetic replication fixture is readable. No live replica is required or installed by this course.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A reporting screen shows stale points while the primary accepts transactions. This is a supplied evidence exercise, not a configured replica.

## Learning goals

- Application routing and replica freshness must be investigated together.
- Replication threads, errors and delay metrics need timestamps and context.
- An empty replica-status result on a standalone server is not a replication failure.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-05" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Read the fixture and record provenance

**Where and who:** Learner · application server · Bash terminal

Identify capture time, primary write time and replica-visible time before interpreting status.

```bash
cd "$COURSE_ROOT"
cat shared/fixtures/replication.json
```

**Expected result:** The file explicitly labels itself synthetic; receiver and applier states differ.

**If it differs:** Do not run replica repair commands against the standalone class database.

### Step 2 — Build a freshness table

**Where and who:** Learner · evidence notes

Create columns for source, UTC time, receiver state, applier state, error and freshness confidence. Copy the supplied values and mark NULL lag as unknown.

**Expected result:** You distinguish reception from application and can explain why a report may be stale.

**If it differs:** A NULL delay value is not zero. Missing data must remain unknown.

### Step 3 — Choose the next investigation

**Where and who:** Team discussion

Use the supplied relay-log filename and error as investigation leads. Describe what a DBA should inspect, what routing change could reduce impact, and what capacity/consistency risk that change creates.

**Expected result:** Your escalation asks for a specific consistency/applier investigation and a business freshness decision.

**If it differs:** Do not recommend skipping a transaction merely because it is blocking replication.

### Step 4 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does a running receiver thread prove the applier is current?
2. Can reporting freshness be inferred from one lag number alone?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-05` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] replication-escalation.md — freshness table, error interpretation, routing tradeoff and next checks

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

No live state was changed. Keep the original fixture unchanged and label all submitted findings as synthetic evidence analysis.

## Completion criteria

- [ ] Student recognizes NULL delay as unknown rather than healthy.
- [ ] Recommendation addresses stale reads and the replication error separately.

[Previous exercise](04-mysql-locks.md) · [Module agenda](../README.md) · [Next exercise](06-sqlserver-baseline.md)
