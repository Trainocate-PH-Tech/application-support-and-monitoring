# Automated evidence collection

**Time:** 55 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** evidence-index.md — bundle path, UTC window, capture statuses and redaction review; reviewed-bundle.tar.gz — a reviewed copy of the generated archive

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Journal access and the reference collector are available. Use only synthetic secrets in masking tests; never copy real credentials into sample input.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

An escalation needs a portable evidence bundle even when some commands fail or lack permission.

## Learning goals

- Use restrictive permissions, unique timestamped directories and a manifest.
- Capture stdout, stderr and exit status for each check.
- Redaction needs review; a regex cannot guarantee removal of every secret.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-02" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Collect a bounded evidence bundle

**Where and who:** Learner · application server · Bash terminal

Capture the status immediately, then copy the printed bundle path into your notes.

```bash
cd "$COURSE_ROOT"
shared/scripts/collect-evidence.sh "$HOME/support-lab/evidence/m3-02/bundles" '20 minutes ago'
collector_rc=$?
printf 'collector_exit=%s\n' "$collector_rc"
```

**Expected result:** Exit 0 means all capture commands succeeded; 1 means a useful partial bundle; 2 means creation/packaging failed.

**If it differs:** Read the per-command manifest before treating exit 1 as an unusable bundle.

### Step 2 — Inspect the exact bundle

**Where and who:** Learner · application server · Bash terminal

At the prompt, paste the archive path printed by the collector, without the bundle= prefix. Do not choose an unrelated archive.

```bash
read -r -p 'Printed archive path: ' bundle
stat -c '%a %n' "$bundle"
tar -tzf "$bundle"
review_dir=$(mktemp -d "$HOME/support-lab/evidence/m3-02/review-XXXXXX")
tar -xzf "$bundle" -C "$review_dir"
find "$review_dir" -name manifest.tsv -exec cat {} \;
```

**Expected result:** The archive is private to your account; the manifest lists each capture’s exit code.

**If it differs:** If extraction fails, verify the exact printed path and archive listing before retrying.

### Step 3 — Interpret missing permissions

**Where and who:** Learner and instructor · compare existing captures

Identify a nonzero capture status or ask the instructor to provide a capture from an account without journal access. Compare denied output with a genuinely empty window. Do not remove groups from the shared account just to create a test.

**Expected result:** Your evidence index labels inaccessible data and empty data differently.

**If it differs:** If every capture succeeded, use the provided local test harness as the partial-failure demonstration; do not invent a failed capture.

### Step 4 — Inspect and exercise masking with synthetic input

**Where and who:** Learner · application server · Bash terminal

This mirrors the collector’s simple filter. Explain why it is only a teaching example and still needs manual review.

```bash
printf 'password=synthetic-only token=dummy-token\n' | sed -E 's/((password|token|secret|authorization)[=:][[:space:]]*)[^[:space:]]+/\1[REDACTED]/Ig'
```

**Expected result:** Both synthetic values become [REDACTED].

**If it differs:** Values with spaces, alternate formats or secrets inside SQL may evade this pattern. Never assume the regex guarantees safe sharing.

### Step 5 — Write an evidence index

**Where and who:** Learner · editor

List every useful file, its UTC window, successful/partial status and why it matters. Review extracted content before submission and leave real credentials out.

**Expected result:** A reviewer can locate evidence and understand gaps without rerunning the incident.

**If it differs:** If sensitive content appears, redact a submission copy and retain the original only under the instructor’s evidence policy.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Can a timestamp alone prevent simultaneous filename collisions?
2. Should permission denied be silently converted to an empty success file?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-02` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] evidence-index.md — bundle path, UTC window, capture statuses and redaction review
- [ ] reviewed-bundle.tar.gz — a reviewed copy of the generated archive

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Keep the reviewed bundle and index. The extraction directory contains copies and may be removed after review; do not delete the only incident archive or broadly clean other evidence.

## Completion criteria

- [ ] Failed checks remain visible in the manifest.
- [ ] Bundle contains no credentials or environment dumps and is reviewed before sharing.

[Previous exercise](01-bash.md) · [Module agenda](../README.md) · [Next exercise](03-monitoring.md)
