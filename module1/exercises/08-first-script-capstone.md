# Linux incident challenge with your evidence script

**Time:** 40 minutes  
**Working mode:** Guided setup; independent diagnosis

| Difficulty | Delivery | Sessions |
|---|---|---|
| Independent assessment | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** triage.sh — executable learner script; incident.md — timeline and evidence-backed diagnosis; reviewed evidence bundle and completed Linux checklist

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete Module 1 exercises 01–07. Instructor assigns one concealed fault and a shared-stack time slot.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A deployment left the loyalty application unavailable. Your team has 25 minutes to identify the fault and deliver a reusable evidence collector.

## Learning goals

- Build a small script from understood commands, then test failure behavior.
- Record command failures without losing the rest of the incident evidence.
- A recovery claim needs a customer-facing check and a clear incident summary.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-08" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Prepare your submission workspace

**Where and who:** Learner · application server · Bash terminal

Before copying: if prompted to overwrite, answer n, retain your earlier file and use a dated backup before editing. Create report copies in this exercise’s evidence directory. Open incident.md in your editor and fill the identity, scope and UTC start fields.

```bash
cp -i "$COURSE_ROOT/shared/templates/incident-report.md" "$HOME/support-lab/evidence/m1-08/incident.md"
date -u +%FT%TZ
nano "$HOME/support-lab/evidence/m1-08/incident.md"
```

**Expected result:** A report exists before the fault is introduced; roles and start time are recorded.

**If it differs:** If a prior report exists, make a dated copy before replacing it.

### Step 2 — Extend your existing evidence script

**Where and who:** Learner · application server · Bash terminal

Reuse triage.sh from exercise 04. Back it up before editing. Add bounded recent service errors and timestamps; preserve denied-command statuses. Do not replace it with a reference solution.

```bash
cp -p "$HOME/support-lab/bin/triage.sh" "$(mktemp "$HOME/support-lab/bin/triage-backup-XXXXXX")"
nano "$HOME/support-lab/bin/triage.sh"
bash -n "$HOME/support-lab/bin/triage.sh" && "$HOME/support-lab/bin/triage.sh"
```

**Expected result:** Your script runs and captures observations without silently treating failures as healthy.

**If it differs:** If syntax checking fails, fix it before execution. Compare the reference collector only after your first implementation.

### Step 3 — Receive the incident and assign roles

**Where and who:** Team briefing with instructor

The application was healthy before a change and now needs investigation. Assign investigator, scribe/reviewer and incident lead. Only the instructor injects or resets the concealed fault.

**Expected result:** You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.

**If it differs:** If the starting system was already unhealthy, ask the instructor to establish which symptoms belong to this scenario.

### Step 4 — Investigate within the time budget

**Where and who:** Learner · permitted shells/clients

Use 5 minutes to extend your script, 25 for investigation and recovery, and 10 for reporting. Record each hypothesis, discriminating check and observation.

**Expected result:** Your timeline contains evidence-linked observations rather than a list of guesses.

**If it differs:** When a check is denied or returns no data, record that limitation and choose another permitted source; do not broaden privileges.

### Step 5 — Collect and inspect evidence

**Where and who:** Learner · application server · Bash terminal

Use the collector as one input, not a replacement for your own reasoning. Check its manifest and preserve the returned path.

```bash
cd "$COURSE_ROOT"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m1-08/bundles" '20 minutes ago'
collector_rc=$?
printf 'collector_exit=%s\n' "$collector_rc"
```

**Expected result:** A full or partial bundle is available. Exit 1 can be valid partial evidence; inspect the manifest.

**If it differs:** If packaging fails, preserve individual available outputs and explain the gap in your report.

### Step 6 — Propose one mitigation and define recovery

**Where and who:** Team decision; instructor performs privileged changes

State the supporting evidence, affected scope, rollback, responsible person and business verification before requesting the change. Do not run every fix you know.

**Expected result:** The instructor can review a concrete action; the report distinguishes diagnosis from speculation.

**If it differs:** If evidence does not distinguish causes, request a further measurement instead of claiming certainty.

### Step 7 — Verify and hand over

**Where and who:** Learner · permitted probes and report editor

Validate the affected route plus a representative player lookup; explain what changed and why. Record before/after outcomes, residual risks and a next owner. Review the submission checklist and optional hints without opening instructor answers.

**Expected result:** Recovery is supported by the affected business function and a clear observation window.

**If it differs:** One green service indicator is insufficient if the original business request still fails.

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

1. Why can an evidence collector legitimately exit nonzero and still produce a useful bundle?
2. Does chmod +x guarantee a script will run on every shell?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-08` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] triage.sh — executable learner script
- [ ] incident.md — timeline and evidence-backed diagnosis
- [ ] reviewed evidence bundle and completed Linux checklist

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

After saving evidence, the instructor resets the assigned fault. Roll back any transactions opened during investigation in their owning sessions, close database clients and unset SQLCMDPASSWORD where used. Verify the affected business route again. Keep evidence and scripts; do not reset another team’s active scenario.

## Completion criteria

- [ ] Script runs without interactive input and records UTC timestamps.
- [ ] Incident report includes evidence, probable cause, mitigation and recovery validation.

[Previous exercise](07-resources-network.md) · [Module agenda](../README.md) · [Next exercise](09-command-challenge-bank.md)
