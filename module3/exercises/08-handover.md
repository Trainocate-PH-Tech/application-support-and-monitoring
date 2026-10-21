# Final challenges and operational handover

**Time:** 30 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** handover.md — shift-ready incident summary; improvements.md — three owned, measurable actions; script-test-index.md — paths to scripts and their test evidence

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete the incident simulation. Have the report, evidence index, scripts and recovery transcript ready; no new fault is injected.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Another shift must continue your work without a verbal briefing.

## Learning goals

- A handover describes remaining work, evidence locations and safe next steps.
- RCA distinguishes trigger, root cause, contributing factors and detection gaps.
- Monitoring improvements need an owner and measurable acceptance criterion.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-08" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Collect your handover inputs

**Where and who:** Learner · application server · Bash terminal

List your own scripts and check each separately. This avoids treating later filenames as arguments to a single bash invocation.

```bash
syntax_rc=0
for script in "$HOME"/support-lab/bin/*.sh; do
    [[ -f "$script" ]] || continue
    bash -n "$script" || syntax_rc=1
done
printf 'syntax_exit=%s\n' "$syntax_rc"
```

**Expected result:** Each script passes syntax checks before submission.

**If it differs:** A syntax pass is not a functional test; retain your healthy/failure transcripts too.

### Step 2 — Prepare a five-minute handover

**Where and who:** Learner · report editor

Summarize impact, UTC timeline, evidence paths, probable cause and confidence, mitigation, recovery tests and remaining risks. Name the next owner and next check.

**Expected result:** Another shift can locate evidence and repeat checks without a verbal explanation.

**If it differs:** Do not present a hypothesis as a confirmed root cause just to make the report sound complete.

### Step 3 — Defend a counterexample

**Where and who:** Team review

Ask a peer to propose evidence that would contradict your diagnosis. Identify which captured observation distinguishes the alternatives.

**Expected result:** Your explanation connects a conclusion to evidence and acknowledges uncertainty.

**If it differs:** If no discriminating evidence exists, state that limitation and propose the next measurement.

### Step 4 — Write three actionable improvements

**Where and who:** Learner · notes

For each improvement, state signal, threshold/window, owner, response and acceptance check. Separate detection, prevention and runbook improvements.

**Expected result:** Each recommendation can be assigned and tested; “monitor more” is replaced by a measurable action.

**If it differs:** Do not invent production thresholds from a tiny training workload without labeling them provisional.

### Step 5 — Review and submit

**Where and who:** Learner · local review

Use the submission checklist below. Remove credentials from copies and verify that every referenced evidence file is included. Deliver a five-minute handover to the class.

**Expected result:** The recipient can read the report, find evidence and understand residual risk.

**If it differs:** Missing evidence should be marked missing, not replaced with invented output.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Is “monitor more” an actionable recommendation?
2. Can an RCA be useful when some uncertainty remains?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-08` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] handover.md — shift-ready incident summary
- [ ] improvements.md — three owned, measurable actions
- [ ] script-test-index.md — paths to scripts and their test evidence

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Confirm with the instructor that simulation faults and open transactions are cleared. Remove only your exercise cron entries if still active; retain reviewed artifacts for assessment.

## Completion criteria

- [ ] Next shift can reproduce checks and locate evidence.
- [ ] Final report distinguishes confirmed facts from probable explanations.

[Previous exercise](07-war-room.md) · [Module agenda](../README.md) · [Next exercise](09-automation-extension.md)
