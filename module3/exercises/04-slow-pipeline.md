# Slow-query summaries and correlation pipelines

**Time:** 20 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** summary-index.md — output directory, source windows, status and correlation limitations; report-directory — your CSV, rankings and manifest

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

mysqldumpslow is installed; Module 3 exercise 03 is complete. Synthetic slow and application logs are available.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Create one summary combining application errors with database slow-query evidence without pretending they share a guaranteed join key.

## Learning goals

- Use database-native summaries for multiline slow logs.
- Keep units, source window and provenance in exported results.
- A correlation hypothesis must be labeled if an exact join is unavailable.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-04" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Create your report directory and source record

**Where and who:** Learner · application server · Bash terminal

Use a unique output directory. The variable summary_dir remains in this terminal for the next steps.

```bash
mkdir -p ~/support-lab/summary
summary_dir=$(mktemp -d "$HOME/support-lab/summary/run-XXXXXX")
date -u +%FT%TZ > "$summary_dir/captured-at.txt"
printf '%s\n' "$summary_dir"
cd "$COURSE_ROOT"
```

**Expected result:** You have a fresh report directory and UTC capture record.

**If it differs:** If the terminal changes, re-enter the exact printed path; shell variables are not shared automatically.

### Step 2 — Produce two slow-query rankings

**Where and who:** Learner · application server · Bash terminal

Compare frequency ordering with time ordering.

```bash
mysqldumpslow -s t -t 5 shared/fixtures/mysql-slow.log > "$summary_dir/slow-time.txt"
mysqldumpslow -s c -t 5 shared/fixtures/mysql-slow.log > "$summary_dir/slow-count.txt"
cat "$summary_dir/slow-time.txt"
cat "$summary_dir/slow-count.txt"
```

**Expected result:** Similar queries group together; the report query runs three times.

**If it differs:** Do not grep SELECT lines and discard multiline record context.

### Step 3 — Save an alert result without losing it

**Where and who:** Learner · application server · Bash terminal

The parser exits 1 deliberately. Retain its CSV and record status rather than discarding it.

```bash
shared/scripts/monitor-log.sh shared/fixtures/application.log > "$summary_dir/application.csv"
monitor_rc=$?
printf 'application_exit=%s\n' "$monitor_rc" > "$summary_dir/status.txt"
cat "$summary_dir/application.csv"
```

**Expected result:** The CSV exists and reports ALERT even though exit status is 1.

**If it differs:** A wrapper using unconditional set -e may stop here; handle expected alert statuses explicitly.

### Step 4 — Run the reference wrapper and inspect its manifest

**Where and who:** Learner · application server · Bash terminal

Compare the wrapper’s timestamped directory with your manually assembled report.

```bash
shared/scripts/monitor-pipeline.sh shared/fixtures/application.log "$HOME/support-lab/monitoring" shared/fixtures/mysql-slow.log
pipeline_rc=$?
printf 'pipeline_exit=%s\n' "$pipeline_rc"
```

**Expected result:** With mysqldumpslow available, the wrapper retains the alert output and exits 1. Exit 2 indicates incomplete/invalid evidence.

**If it differs:** Read the manifest when the slow summary is unavailable; do not label an incomplete report healthy.

### Step 5 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does one SQL statement always fit on one line?
2. Can identical timestamps prove causal linkage?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-04` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] summary-index.md — output directory, source windows, status and correlation limitations
- [ ] report-directory — your CSV, rankings and manifest

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Keep your report directory and manifest. Original logs remain unchanged. No active monitoring daemon was started by these commands.

## Completion criteria

- [ ] Report preserves both frequency and time rankings.
- [ ] Wrapper does not discard useful ALERT output because its exit code is 1.

[Previous exercise](03-monitoring.md) · [Module agenda](../README.md) · [Next exercise](05-scheduling.md)
