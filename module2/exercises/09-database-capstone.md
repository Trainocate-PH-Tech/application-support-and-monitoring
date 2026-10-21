# Final database incident challenge

**Time:** 75 minutes  
**Working mode:** Guided setup; independent diagnosis

| Difficulty | Delivery | Sessions |
|---|---|---|
| Independent assessment | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** incident.md — integrated timeline and recovery; database-report.md — MySQL and SQL Server analysis; db-health-outline.md — interface, permissions, checks, output and failure handling

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete the preceding database exercises. Use the concealed database-performance evidence case supplied by the instructor. No live fault injection is required for this assessment.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A reporting request regressed after a release while ordinary player lookup remains responsive. Distinguish competing database causes using a separate synthetic incident pack.

## Learning goals

- Quantify changes in workload, query cost and result equivalence.
- Test competing causes with discriminating evidence.
- Define a reversible correction and bounded database-health checks.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-09" && printf 'Workspace ready\n'
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
cp -i "$COURSE_ROOT/shared/templates/incident-report.md" "$HOME/support-lab/evidence/m2-09/incident.md"
date -u +%FT%TZ
nano "$HOME/support-lab/evidence/m2-09/incident.md"
```

**Expected result:** A report exists before opening the synthetic case; roles and start time are recorded.

**If it differs:** If a prior report exists, make a dated copy before replacing it.

### Step 2 — Prepare database-specific evidence

**Where and who:** Learner · application server · Bash terminal

Before copying: if prompted to overwrite, answer n, retain your earlier file and use a dated backup before editing. Copy the worksheet without overwriting an earlier report. Read shared/fixtures/database-incident.md. Keep this synthetic case separate from the optional healthy live baseline.

```bash
cp -i -i "$COURSE_ROOT/shared/templates/database-report.md" ~/support-lab/evidence/m2-09/database-report.md
cat "$COURSE_ROOT/shared/fixtures/database-incident.md"
```

**Expected result:** The worksheet and synthetic case are available; do not confuse case evidence with live baseline checks.

**If it differs:** Do not place passwords in the worksheet or infer that every synthetic file is part of the same outage.

### Step 3 — Receive the incident and assign roles

**Where and who:** Team briefing with instructor

Investigate why a report became slower after a release. Use the linked evidence case, test at least two plausible explanations and justify a scoped correction. Roles rotate; no fault name or solution is provided.

**Expected result:** You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.

**If it differs:** Confirm which capture belongs to this case; unrelated fixtures are not additional evidence.

### Step 4 — Investigate within the time budget

**Where and who:** Learner · permitted shells/clients

Use 10 minutes for impact and roles, 25 for analysis, 15 for a remediation proposal and validation criteria, and 25 for reporting and individual review.

**Expected result:** Your timeline contains evidence-linked observations rather than a list of guesses.

**If it differs:** When a check is denied or returns no data, record that limitation and choose another permitted source; do not broaden privileges.

### Step 5 — Collect and inspect evidence

**Where and who:** Learner · application server · Bash terminal

Preserve the initial case evidence with your pre-change reasoning. Record additional evidence supplied by the instructor in a separate file; keep capture times and provenance.

```bash
cp -i "$COURSE_ROOT/shared/fixtures/database-incident.md" "$HOME/support-lab/evidence/m2-09/case-before.md"
```

**Expected result:** Original and additional evidence remain distinguishable.

**If it differs:** Do not substitute unrelated live collector output for case evidence.

### Step 6 — Propose one mitigation and define recovery

**Where and who:** Team proposal; instructor releases synthetic evidence

Submit the proposed scoped correction, supporting evidence, owner, rollback trigger and comparable verification criteria. No privileged change is performed for this case.

**Expected result:** The instructor can review a concrete action; the report distinguishes diagnosis from speculation.

**If it differs:** If evidence does not distinguish causes, request a further measurement instead of claiming certainty.

### Step 7 — Verify and hand over

**Where and who:** Learner · permitted probes and report editor

Request the instructor’s post-change evidence only after submitting a hypothesis and proposed change. Compare the same workload, rows, duration and reads before/after. Record residual uncertainty and a rollback trigger. Submit the database-health script outline with timeouts and unknown states.

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

1. Do three unblocked snapshots rule out all intermittent blocking?
2. Does a plan change alone prove which repair is correct?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-09` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] incident.md — integrated timeline and recovery
- [ ] database-report.md — MySQL and SQL Server analysis
- [ ] db-health-outline.md — interface, permissions, checks, output and failure handling

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

This case uses synthetic evidence; do not modify the shared database. Close any optional baseline clients and unset SQLCMDPASSWORD. Preserve submitted pre-change reasoning and post-change comparisons.

## Completion criteria

- [ ] Quantify the report regression and test at least two explanations.
- [ ] Propose a scoped change and compare instructor-released before/after evidence.
- [ ] Submit a bounded database-health automation design and an individual explanation.

[Previous exercise](08-app-db-correlation.md) · [Module agenda](../README.md)
