# Advanced Linux command challenge bank

**Time:** Optional extension  
**Working mode:** Guided setup; independent diagnosis

| Difficulty | Delivery | Sessions |
|---|---|---|
| Independent assessment | Optional extension | Application-server Bash; workstation only where labeled |

**Deliverables:** command-notebook.md — 18 numbered answers and counterexamples; peer-review.md — reproduction result and corrections

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Complete the command investigations in Module 1 exercise 04. Use copies of synthetic files. This is optional extension work, not part of the 390-minute core day.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

You must produce defensible answers from awkward input without changing source evidence.

## Learning goals

- Predict command behavior before running it.
- Preserve evidence and explain assumptions about input format.
- Robust pipelines handle empty input, malformed records and unusual filenames.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-09" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Create an isolated challenge workspace

**Where and who:** Learner · application server · Bash terminal

Copy fixtures into a new directory and record the path. Use that directory for the tasks.

```bash
mkdir -p ~/support-lab/challenges
challenge_dir=$(mktemp -d "$HOME/support-lab/challenges/commands-XXXXXX")
cp -a "$COURSE_ROOT/shared/fixtures/." "$challenge_dir/"
cd "$challenge_dir"
pwd
```

**Expected result:** All challenge mutations stay inside your new copy.

**If it differs:** Do not work directly in the shared fixture directory.

### Step 2 — Prepare an answer notebook

**Where and who:** Learner · Markdown editor

For each of the 18 tasks in [Command challenges](../../shared/fixtures/command-challenges.md), record prediction, command, observed output, interpretation and one limitation. Work in groups of six tasks, reviewing after each group.

**Expected result:** The notebook has numbered sections 1–18 before you begin solving.

**If it differs:** Do not open the instructor answer key during the attempt.

### Step 3 — Solve and test counterexamples

**Where and who:** Learner · Bash in the challenge directory

Follow the command bank step by step. Explain why a naive version fails before proposing a correction. Preserve source evidence and do not bypass an error without interpreting it.

**Expected result:** Each completed task includes a runnable approach and evidence supporting its behavior.

**If it differs:** When stuck, use the optional hints below and the Linux desk reference. A prediction can be wrong; record what the observation taught you.

### Step 4 — Review with another learner

**Where and who:** Peer review

Exchange notebooks. Your reviewer runs one safe pipeline and checks one edge case, then flags missing assumptions or evidence.

**Expected result:** A second person can reproduce your result from the written steps.

**If it differs:** Record a limitation if a command depends on GNU options or a particular log format.

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

1. Is line count always record count?
2. When does tail -f miss a replacement log file?
3. Can grep ERROR count HTTP failures accurately?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-09` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] command-notebook.md — 18 numbered answers and counterexamples
- [ ] peer-review.md — reproduction result and corrections

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Keep the copied challenge workspace until review completes. Close any tail-following process with Ctrl-C. Remove only temporary files you created in that copy; leave originals untouched.

## Completion criteria

- [ ] Each answer includes an explanation and a counterexample where appropriate.
- [ ] No command mutates original evidence or uses blanket deletion.

[Previous exercise](08-first-script-capstone.md) · [Module agenda](../README.md)
