# Major incident simulation

**Time:** 110 minutes  
**Working mode:** Guided setup; independent diagnosis

| Difficulty | Delivery | Sessions |
|---|---|---|
| Independent assessment | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** incident.md — report with impact, timeline, evidence and confidence; updates.md — updates at minutes 15, 30 and 45; reviewed evidence bundle and script execution transcript

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete the automation exercises. Instructor provides one incident card, allowed endpoints and a reserved team slot; scripts have passed their basic tests.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Run one of three scenarios: loyalty outage, delayed transactions, or payment integration failure. Rotate roles and deliver timed updates.

## Learning goals

- Separate facts, hypotheses and decisions in the incident log.
- Assign owners and keep one coordinated change stream on the shared host.
- Mitigation reduces impact; RCA may remain provisional at handover.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-07" && printf 'Workspace ready\n'
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
cp -i "$COURSE_ROOT/shared/templates/incident-report.md" "$HOME/support-lab/evidence/m3-07/incident.md"
date -u +%FT%TZ
nano "$HOME/support-lab/evidence/m3-07/incident.md"
```

**Expected result:** A report exists before the fault is introduced; roles and start time are recorded.

**If it differs:** If a prior report exists, make a dated copy before replacing it.

### Step 2 — Receive the incident and assign roles

**Where and who:** Team briefing with instructor

The instructor assigns loyalty outage, gaming delay or payment failure. Rotate incident commander, investigator and scribe; combine roles for teams of three. Write classroom stakeholder updates at minutes 15, 30 and 45 using the [stakeholder update template](../../shared/templates/stakeholder-update.md); do not send real external messages. Assign investigator, scribe/reviewer and incident lead. Only the instructor injects or resets the concealed fault.

**Expected result:** You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.

**If it differs:** If the starting system was already unhealthy, ask the instructor to establish which symptoms belong to this scenario.

### Step 3 — Investigate within the time budget

**Where and who:** Learner · permitted shells/clients

Use 10 minutes for briefing, 50 for investigation, 20 for mitigation/recovery and 30 for communications and handover preparation. Record each hypothesis, discriminating check, observation and next action. The optional hints below suggest layers, not a solution.

**Expected result:** Your timeline contains evidence-linked observations rather than a list of guesses.

**If it differs:** When a check is denied or returns no data, record that limitation and choose another permitted source; do not broaden privileges.

### Step 4 — Collect and inspect evidence

**Where and who:** Learner · application server · Bash terminal

Use the collector as one input, not a replacement for your own reasoning. Check its manifest and preserve the returned path.

```bash
cd "$COURSE_ROOT"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m3-07/bundles" '20 minutes ago'
collector_rc=$?
printf 'collector_exit=%s\n' "$collector_rc"
```

**Expected result:** A full or partial bundle is available. Exit 1 can be valid partial evidence; inspect the manifest.

**If it differs:** If packaging fails, preserve individual available outputs and explain the gap in your report.

### Step 5 — Propose one mitigation and define recovery

**Where and who:** Team decision; instructor performs privileged changes

State the supporting evidence, affected scope, rollback, responsible person and business verification before requesting the change. Do not run every fix you know.

**Expected result:** The instructor can review a concrete action; the report distinguishes diagnosis from speculation.

**If it differs:** If evidence does not distinguish causes, request a further measurement instead of claiming certainty.

### Step 6 — Verify and hand over

**Where and who:** Learner · permitted probes and report editor

Use your own deployment checks on the affected business function and report the observation window. Submit three stakeholder updates, a reviewed bundle, incident report and handover notes. Record before/after outcomes, residual risks and a next owner. Review the submission checklist and optional hints without opening instructor answers.

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

1. Should you announce root cause when you only have correlation?
2. Can unrelated background warnings distract from the affected business function?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-07` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] incident.md — report with impact, timeline, evidence and confidence
- [ ] updates.md — updates at minutes 15, 30 and 45
- [ ] reviewed evidence bundle and script execution transcript

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

After saving evidence, the instructor resets the assigned fault. Roll back any transactions opened during investigation in their owning sessions, close database clients and unset SQLCMDPASSWORD where used. Verify the affected business route again. Keep evidence and scripts; do not reset another team’s active scenario.

## Completion criteria

- [ ] Timeline links symptoms, actions and results to evidence.
- [ ] Updates communicate impact, current action, owner and next update time.

[Previous exercise](06-deployment-checks.md) · [Module agenda](../README.md) · [Next exercise](08-handover.md)
