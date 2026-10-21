# Health checks, cron and safe retention

**Time:** 35 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** cron-verification.md — reviewed entry, manual versus scheduled timestamps and removal confirmation; retention-results.txt — dry-run, deletion and unrelated-file survival

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

A working reference health checker; crontab and flock available. Learners may edit only their own crontab. The retention demonstration uses an isolated HOME containing dummy files.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Your script works in a terminal but fails under cron. Make paths, permissions, concurrency and output explicit.

## Learning goals

- Cron supplies a smaller environment and different working directory.
- Use absolute paths, a controlled PATH and a lock to prevent overlapping runs.
- Cleanup is dry-run first, narrowly scoped and separate from incident evidence collection.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-05" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Install learner-owned scripts and test the cron environment

**Where and who:** Learner · application server · Bash terminal

Keep absolute paths. The subshell below changes directory only for the test.

```bash
mkdir -p ~/support-lab/{bin,logs,evidence}
cp "$COURSE_ROOT/shared/scripts/health-check.sh" ~/support-lab/bin/
cp "$COURSE_ROOT/shared/scripts/retention.sh" ~/support-lab/bin/
(cd /tmp && env -i HOME="$HOME" PATH=/usr/bin:/bin "$HOME/support-lab/bin/health-check.sh")
check_rc=$?
printf 'minimal_environment_exit=%s\n' "$check_rc"
```

**Expected result:** The script runs from /tmp without relying on your interactive PATH or working directory.

**If it differs:** A failed health check may legitimately return 1; a missing command/path is a different problem.

### Step 2 — Back up and edit your own crontab

**Where and who:** Learner · application server · Bash terminal

Save current entries before editing. No crontab for this user is an expected message for a new account. Preserve all unrelated entries.

```bash
crontab -l > ~/support-lab/evidence/m3-05/crontab-before.txt
cat "$COURSE_ROOT/shared/templates/crontab.example"
printf 'Your HOME is %s\n' "$HOME"
crontab -e
```

**Expected result:** An editor opens for your account. Copy the template entries and replace every /home/learner01 with the actual HOME printed above.

**If it differs:** Choose an available editor when prompted. Never use sudo crontab -e for this learner exercise.

### Step 3 — Verify the saved entry and observe execution

**Where and who:** Learner · application server · Bash terminal

Save and exit the editor. Check paths and the lock file location. Allow up to five minutes while continuing the retention exercise.

```bash
crontab -l
"$HOME/support-lab/bin/health-check.sh" >> "$HOME/support-lab/logs/health.log" 2>&1
tail -n 10 "$HOME/support-lab/logs/health.log"
```

**Expected result:** The installed entry uses absolute paths and flock. Later scheduled entries have new timestamps.

**If it differs:** The immediate manual run only tests the command; it does not prove cron fired. Verify a later timestamp after the scheduled boundary.

### Step 4 — Create disposable retention input

**Where and who:** Learner · application server · Bash terminal

Use a temporary HOME so applying retention cannot touch your real evidence. Keep demo_home in this terminal.

```bash
demo_home=$(mktemp -d)
mkdir -p "$demo_home/support-lab/evidence"
printf 'dummy\n' > "$demo_home/support-lab/evidence/incident-old.tar.gz"
printf 'keep\n' > "$demo_home/support-lab/evidence/unrelated.txt"
touch -d '10 days ago' "$demo_home/support-lab/evidence/incident-old.tar.gz"
printf 'Demo HOME: %s\n' "$demo_home"
```

**Expected result:** Only dummy files exist in this isolated directory; the .tar.gz name is a retention test filename, not a real archive.

**If it differs:** Do not replace demo_home with your actual HOME.

### Step 5 — Preview, apply and verify narrowly scoped cleanup

**Where and who:** Learner · application server · Bash terminal

First review dry-run output. Apply only after confirming it names the dummy archive under the printed temporary directory.

```bash
HOME="$demo_home" "$COURSE_ROOT/shared/scripts/retention.sh" --dry-run
HOME="$demo_home" "$COURSE_ROOT/shared/scripts/retention.sh" --apply
find "$demo_home/support-lab/evidence" -maxdepth 1 -type f -print
```

**Expected result:** The old incident file is removed and unrelated.txt remains.

**If it differs:** If another path appears, stop before --apply and inspect your variables.

### Step 6 — Remove only the exercise’s scheduled entries

**Where and who:** Learner · application server · Bash terminal

Open your crontab and delete the health/retention lines added for this exercise, preserving pre-existing entries. Do not restore a whole old crontab over newer unrelated work.

```bash
crontab -e
crontab -l
```

**Expected result:** The exercise entries are gone; previous entries remain.

**If it differs:** If unsure which lines you added, compare with crontab-before.txt before saving.

### Step 7 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Will a cron job inherit your interactive exported secrets?
2. Why can overlapping checks create a monitoring problem?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-05` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] cron-verification.md — reviewed entry, manual versus scheduled timestamps and removal confirmation
- [ ] retention-results.txt — dry-run, deletion and unrelated-file survival

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Remove the exercise’s cron entries as shown unless the instructor explicitly asks to retain them. Delete the two dummy files/directory under the recorded demo_home after verification; keep real evidence and the crontab backup. Archive retention is not a database backup or restore strategy.

## Completion criteria

- [ ] Scheduled execution uses absolute paths and a per-user lock.
- [ ] Dry-run identifies only intended incident archives older than the retention boundary.

[Previous exercise](04-slow-pipeline.md) · [Module agenda](../README.md) · [Next exercise](06-deployment-checks.md)
