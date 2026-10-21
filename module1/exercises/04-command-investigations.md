# Command investigations and first Bash script

**Time:** 75 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Foundation | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** pipeline.txt — tee output; pipeline-notes.md — annotated commands, counts and exit-code explanations; triage.sh — your first evidence collector; first-script.txt — output and explanation of service_exit

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

The extracted fixtures from Module 1 exercise 02 are available. No root access is needed.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Operations received mixed logs and filenames. Produce accurate incident counts without losing records or matching misleading text.

## Learning goals

- grep selects lines; awk interprets fields; sed transforms text; each has different quoting rules.
- Sort before uniq, choose numeric sorting for numbers and preserve filenames with NUL separators.
- Counts require a clear unit: lines, requests, users and incidents are not interchangeable.
- Create and execute a small Bash evidence collector before the incident challenge.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-04" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Inspect the evidence without editing it

**Where and who:** Learner · application server · Bash terminal

Start in the extracted fixture directory; q leaves less.

```bash
cd ~/support-lab/fixtures
less application.log
head -n 4 application.log
tail -n 4 application.log
wc -l application.log
```

**Expected result:** Seven lines exist: six requests and one malformed record.

**If it differs:** If the file is missing, return to exercise 02 and extract the archive; do not generate replacement logs.

### Step 2 — Compare a naive search with parsed status

**Where and who:** Learner · application server · Bash terminal

Run both searches and explain why they differ.

```bash
grep -n ERROR application.log
grep -n 'status=5[0-9][0-9]' application.log
awk '{for(i=1;i<=NF;i++) if($i ~ /^path=/) print $i}' application.log | sort | uniq -c | sort -nr
```

**Expected result:** ERROR matches three lines, but status=5xx matches two. /player appears three times.

**If it differs:** An ERROR word inside a successful request is a deliberate trap; inspect the status field.

### Step 3 — Extract and transform fields

**Where and who:** Learner · application server · Bash terminal

Explain each pipeline stage before executing it.

```bash
tail -n +2 latency.csv | cut -d, -f2 | sort -n
sed -n '2,6p' application.log
printf 'seen\n' | tee ~/support-lab/evidence/m1-04/pipeline.txt
date -u +%FT%TZ
```

**Expected result:** Numeric latencies are 5, 25, 30, 80, 1500 and 2100. tee writes to screen and file.

**If it differs:** Do not apply cut to general quoted CSV without checking its format.

### Step 4 — Handle unusual filenames safely

**Where and who:** Learner · application server · Bash terminal

Use NUL delimiters to preserve spaces and newlines. Create a new extraction directory for verification.

```bash
find filenames -type f -print0 | xargs -0 -r wc -c
mkdir -p ~/support-lab/archive
find filenames -type f -print0 | tar --null -T - -czf ~/support-lab/archive/selected.tar.gz
verify_dir=$(mktemp -d "$HOME/support-lab/archive/verify-XXXXXX")
tar -xzf ~/support-lab/archive/selected.tar.gz -C "$verify_dir"
diff -r filenames "$verify_dir/filenames"
```

**Expected result:** diff prints nothing and returns 0 when names and contents match.

**If it differs:** If files differ, inspect extraction paths and delimiters instead of editing the original fixtures.

### Step 5 — Observe an expected nonzero pipeline result

**Where and who:** Learner · application server · Bash terminal

Capture the status immediately; restore your prior pipefail setting afterward.

```bash
previous_pipefail=$(set +o | grep pipefail)
set -o pipefail
grep 'NO_SUCH_REQUEST' application.log | wc -l
pipeline_rc=$?
printf 'pipeline_exit=%s\n' "$pipeline_rc"
eval "$previous_pipefail"
```

**Expected result:** wc prints 0 and pipeline_exit is 1: grep found no matches, rather than a command error.

**If it differs:** If you print another command first, $? changes; repeat while capturing it immediately.

### Step 6 — Build your first evidence script

**Where and who:** Learner · application server · Bash terminal

Spend 20 minutes here. Explain the shebang, quoted variables, default argument, redirection and immediate capture of $?. The application may not be installed yet: NOT_ACTIVE is a valid observation. The last printf makes this a collector, not a health-status interface. Read every line, then run it.

```bash
mkdir -p "$HOME/support-lab/bin"
if [[ -e "$HOME/support-lab/bin/triage.sh" ]]; then
    printf 'Keep existing triage.sh; inspect it before editing.\n'
else
    cat > "$HOME/support-lab/bin/triage.sh" <<'SCRIPT'
#!/usr/bin/env bash
set -u
service=${1:-support-tomcat}
printf 'UTC=%s service=%s\n' "$(date -u +%FT%TZ)" "$service"
df -h "$HOME"
systemctl is-active "$service"
service_rc=$?
printf 'service_exit=%s\n' "$service_rc"
SCRIPT
fi
bash -n "$HOME/support-lab/bin/triage.sh" && chmod 750 "$HOME/support-lab/bin/triage.sh"
"$HOME/support-lab/bin/triage.sh" > "$HOME/support-lab/evidence/m1-04/first-script.txt"
cat "$HOME/support-lab/evidence/m1-04/first-script.txt"
```

**Expected result:** An executable script and timestamped evidence exist before the incident challenge. Syntax checking completes before execution.

**If it differs:** Fix a reported syntax error before running the script. A denied or unavailable service check must be reported as unknown, not healthy.

### Step 7 — Inspect and execute your saved script

**Where and who:** Learner · application server · Bash terminal

Read your saved script. Explain which line captures the service status and which command determines the overall script exit. Syntax-check before executing from another directory.

```bash
cat "$HOME/support-lab/bin/triage.sh"
if bash -n "$HOME/support-lab/bin/triage.sh"; then
    cd "$HOME"
    ./support-lab/bin/triage.sh support-tomcat
    printf 'collector_exit=%s\n' "$?"
fi
```

**Expected result:** The collector runs from another directory and reports the service check separately.

**If it differs:** Do not execute if the syntax check reports an error.

### Step 8 — Change the input, then choose your own check

**Where and who:** Learner · application server · Bash terminal

Predict the output for a deliberately nonexistent service. Run triage.sh with that service as its argument and save the result. Then add a read-only memory check without copying a reference solution. Explain why service_exit and the script’s overall exit status can differ.

**Expected result:** Your notes include the prediction, observed status and a justified additional command.

**If it differs:** Use man or --help to find an option; record the help used.

### Step 9 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does grep returning 1 always mean an error?
2. Will uniq find nonadjacent duplicates?
3. Can cut reliably parse arbitrary CSV with quoted commas?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-04` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] pipeline.txt — tee output
- [ ] pipeline-notes.md — annotated commands, counts and exit-code explanations
- [ ] triage.sh — your first evidence collector
- [ ] first-script.txt — output and explanation of service_exit

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Leave original fixtures unchanged. Keep your archive and evidence; you may remove only the newly created verification directory after recording its contents. Restore pipefail as shown.

## Completion criteria

- [ ] Counts match parsed fixture records; malformed rows are reported separately.
- [ ] All unusual filenames survive the archive round trip.
- [ ] Run triage.sh with two service arguments and explain the captured statuses.

[Previous exercise](03-storage.md) · [Module agenda](../README.md) · [Next exercise](05-install-stack.md)
