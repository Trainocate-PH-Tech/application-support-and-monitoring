# Advanced automation challenge bank

**Time:** Optional extension  
**Working mode:** Guided setup; independent diagnosis

| Difficulty | Delivery | Sessions |
|---|---|---|
| Independent assessment | Optional extension | Application-server Bash; workstation only where labeled |

**Deliverables:** hardening-tests.md — test matrix with actual results; hardened script copies and a short change explanation; database-monitor-design.md — permissions and state semantics

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete the reference-script exercises and copy scripts to your own bin directory before editing. Optional extension; no production or live-host repair automation.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Harden the monitoring workflow against inconvenient inputs and execution contexts.

## Learning goals

- Test adverse inputs, not only the happy path.
- Concurrency, stale data and time zones can create false confidence.
- Maintenance scripts need explicit boundaries and recovery plans.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-09" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Create a hardening test matrix

**Where and who:** Learner · Markdown editor

Create rows for healthy input, no data, malformed data, threshold equality, stale input, spaces in output paths, denied log access, timeout, overlapping execution and unrelated-file retention. State expected output/status before testing.

**Expected result:** The matrix separates OK, ALERT and UNKNOWN/invalid conditions.

**If it differs:** Do not count unexecuted cases as passed.

### Step 2 — Run the reference boundary checks

**Where and who:** Learner · application server · Bash terminal

Interpret both exit codes immediately. The second parser call still sees a 2100 ms request above its 2000 ms limit.

```bash
cd "$COURSE_ROOT"
shared/scripts/monitor-log.sh shared/fixtures/application.log 10 1000
first_rc=$?
shared/scripts/monitor-log.sh shared/fixtures/application.log 34 2000
second_rc=$?
printf 'first=%s second=%s\n' "$first_rc" "$second_rc"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m3-09/output with spaces" '5 minutes ago'
```

**Expected result:** Both parser results are ALERT/1; the collector handles spaces in the output path and reports its own completeness.

**If it differs:** Do not assume raising the error-rate threshold disables the independent latency trigger.

### Step 3 — Implement and test your extensions

**Where and who:** Learner · own script copies

Add input freshness and overlap handling. Use a small local test input for stale timestamps, two local invocations for a lock, and the isolated retention HOME procedure from exercise 05. Do not change shared originals.

**Expected result:** Each claimed behavior has an observed pass/fail result and a bounded failure path.

**If it differs:** If a dependency is unavailable, report UNKNOWN rather than returning healthy by default.

### Step 4 — Design database automation boundaries

**Where and who:** Learner · notes

Use replication and SQL Agent evidence to specify authenticated read-only checks, required permissions, expected states, unknown states and escalation outputs. You do not need to install a replica.

**Expected result:** The design states what the script can observe and which repairs remain operator decisions.

**If it differs:** Do not create a fake live replication success result from the synthetic fixture.

### Step 5 — Review the final patch

**Where and who:** Peer review

Show your changed code and matrix to a peer. Ask them to reproduce one failure case and one recovery case.

**Expected result:** Your changes are understandable and the reported checks are reproducible.

**If it differs:** Document remaining limitations rather than expanding scope into uncontrolled repair automation.

## Optional hints

<details>
<summary>Hint 1 — narrow the question</summary>

State the affected business function, UTC window and the layer your next check tests. Compare the observation with a known baseline.

</details>

<details>
<summary>Hint 2 — interpret the result</summary>

Separate transport, authentication, service state and business behavior. For command challenges, identify input format, quoting, delimiters and exit-code assumptions. Record unavailable evidence explicitly.

</details>

<details>
<summary>Hint 3 — organize the next action</summary>

Use the relevant prior walkthrough or reference script to collect evidence. State what would disprove your hypothesis. Ask the instructor for the next permitted observation without requesting the answer key.

</details>

## Check your understanding

1. Can a successful parser be monitoring yesterday’s data?
2. What happens if a timeout exits 124 and the wrapper overwrites $?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-09` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] hardening-tests.md — test matrix with actual results
- [ ] hardened script copies and a short change explanation
- [ ] database-monitor-design.md — permissions and state semantics

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Stop your own test processes and remove any added test cron entries. Keep the hardening patch and matrix; preserve real evidence and unrelated files.

## Completion criteria

- [ ] Each new behavior has a meaningful adverse-case test.
- [ ] Unknown/unavailable dependencies are not reported as healthy.

[Previous exercise](08-handover.md) · [Module agenda](../README.md)
