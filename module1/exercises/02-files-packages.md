# Navigation, files and package installation

**Time:** 60 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Foundation | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** file-notes.md — directory navigation, package paths, archive listing and broken-link explanation

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete learner access. The instructor has supplied the absolute course folder; shared/fixtures/support-fixtures.tar.gz is readable.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A deployment arrives as an archive. Find the right directory, inspect it, copy it safely and install diagnostic tools.

## Learning goals

- Absolute paths start at /; relative paths start at the current working directory.
- Quote paths and distinguish copying a file from overwriting an existing destination.
- apt is the Ubuntu package manager; dnf examples are Red Hat comparisons, not commands for this host.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-02" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Create and navigate your workspace

**Where and who:** Learner · application server · Bash terminal

Use a fresh practice directory; if it already contains previous work, rename it before repeating the exercise.

```bash
mkdir -p ~/support-lab/files-practice/{incoming,work,archive}
cd ~/support-lab/files-practice
pwd
ls -lah
cd /var/log
pwd
cd -
```

**Expected result:** You return to ~/support-lab/files-practice. cd - prints the previous directory.

**If it differs:** Run pwd before any relative path operation; cd affects this terminal only.

### Step 2 — Create, copy and rename a file

**Where and who:** Learner · application server · Bash terminal

Keep the filename quoted because it contains a space.

```bash
printf 'alpha\nbeta\n' > 'incoming/status report.txt'
cp -i -- 'incoming/status report.txt' work/
mv -- 'work/status report.txt' work/status.txt
head -n 1 work/status.txt
ln -s status.txt work/latest
ls -l work
readlink work/latest
```

**Expected result:** head prints alpha; latest points to status.txt.

**If it differs:** If ln reports File exists on a repeat attempt, inspect the existing link instead of overwriting it blindly.

### Step 3 — Inspect packages and command lookup

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Installation completes or reports the packages already installed; package ownership is printed.

**If it differs:** If apt fails, resolve repository/network/lock errors before proceeding; learners should not start parallel package installations.

### Step 4 — Check the tools as a learner

**Where and who:** Learner · application server · Bash terminal

Return to the course directory explicitly before using shared paths.

```bash
cd "$COURSE_ROOT"
printf '%s\n' "$PATH"
command -v curl nc dig lsof pidstat
tar -tzf shared/fixtures/support-fixtures.tar.gz
mkdir -p ~/support-lab/fixtures
tar -xzf shared/fixtures/support-fixtures.tar.gz -C ~/support-lab/fixtures
```

**Expected result:** Tool paths print; the archive contains application.log, latency.csv and filenames/.

**If it differs:** If the archive is missing, confirm COURSE_ROOT rather than guessing a relative directory.

### Step 5 — Compress a copy and observe a broken link

**Where and who:** Learner · application server · Bash terminal

Remove only the practice target you created. Answer y to its deletion prompt.

```bash
printf 'compress me\n' > ~/support-lab/files-practice/work/compression.txt
gzip -k ~/support-lab/files-practice/work/compression.txt
gzip -dc ~/support-lab/files-practice/work/compression.txt.gz
rm -i -- ~/support-lab/files-practice/work/status.txt
ls -l ~/support-lab/files-practice/work/latest
cat ~/support-lab/files-practice/work/latest
```

**Expected result:** gzip prints compress me; the final cat fails because the link’s target was removed. That failure is expected.

**If it differs:** If gzip asks to overwrite an existing archive during a repeat, inspect your previous output first.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does cd /var/log change another terminal’s working directory?
2. Why is sudo echo text > /root/file different from echo text | sudo tee /root/file?
3. What happens when an unquoted variable contains spaces?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-02` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] file-notes.md — directory navigation, package paths, archive listing and broken-link explanation

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Keep ~/support-lab/fixtures for later exercises. Leave the broken link as evidence or remove that link only with rm -i; retain the original incoming file.

## Completion criteria

- [ ] Student explains why the symlink breaks after its target is removed.
- [ ] Commands are found through PATH; package installation is verified rather than assumed.

[Previous exercise](01-access-users.md) · [Module agenda](../README.md) · [Next exercise](03-storage.md)
