# Extend your Bash script into a health check

**Time:** 60 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** my-health.sh — submit a copy from your learner bin directory; script-tests.md — healthy, unreachable and invalid-input results plus remaining limitations

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Your Module 1 triage.sh and first-script notes; a healthy shared stack; Bash, curl, timeout, systemctl and an editor.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Turn yesterday’s commands into a script another engineer can run reliably.

## Learning goals

- Quote expansions; treat arguments as data; use arrays for command arguments.
- Exit codes are an interface: document healthy, unhealthy and usage outcomes.
- set -e is not a substitute for deliberate error handling.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m3-01" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Create a script you can edit

**Where and who:** Learner · application server · Bash terminal

Review your Module 1 collector. Extend its observations into a new health-check interface. Preserve an existing my-health.sh; edit only after inspecting it.

```bash
mkdir -p ~/support-lab/bin
cat "$HOME/support-lab/bin/triage.sh"
if [[ ! -e "$HOME/support-lab/bin/my-health.sh" ]]; then
    cp "$HOME/support-lab/bin/triage.sh" "$HOME/support-lab/bin/my-health.sh"
fi
nano "$HOME/support-lab/bin/my-health.sh"
```

**Expected result:** You have your own editable script; the shared original is unchanged.

**If it differs:** If my-health.sh already exists, copy it to a backup filename before replacing it.

### Step 2 — Implement the check interface

**Where and who:** Learner · editor for my-health.sh

Adapt your collector using this scaffold. Add available-memory and disk reporting yourself. Define 0 healthy, 1 failed probe, 2 invalid arguments or missing tools. Explain why the quoted probe_args array passes each option separately. Bounded probes prevent a missing service response from hanging your check.

```bash
#!/usr/bin/env bash
set -u
if (( $# > 2 )); then
    printf 'Usage: %s [service [http(s)-url]]\n' "$0" >&2
    exit 2
fi
service=${1-support-tomcat}
url=${2-http://127.0.0.1:8080/loyalty/health}
if [[ -z "$service" || "$service" == -* || "$service" == *[[:space:]]* ]]; then
    printf 'Invalid service\n' >&2; exit 2
fi
case "$url" in
    http://?*|https://?*) ;;
    *) printf 'Invalid URL\n' >&2; exit 2 ;;
esac
failed=0
log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$1"; }
for tool in systemctl curl timeout date; do
    command -v "$tool" >/dev/null || exit 2
done
probe_args=(--fail --silent --show-error --max-time 5)
if timeout 5 systemctl is-active --quiet "$service"; then
    log 'service=OK'
else
    log 'service=FAIL'; failed=1
fi
if curl "${probe_args[@]}" "$url" >/dev/null; then
    log 'endpoint=OK'
else
    log 'endpoint=FAIL'; failed=1
fi
exit "$failed"
```

**Expected result:** The script uses arguments, defaults, a function, a loop, conditions and a documented status.

**If it differs:** Keep quotes around expansions; do not paste the surrounding Markdown fences into the file.

### Step 3 — Check syntax before execution

**Where and who:** Learner · application server · Bash terminal

A syntax check does not run the script. Only execute it after bash -n succeeds.

```bash
bash -n ~/support-lab/bin/my-health.sh
chmod 750 ~/support-lab/bin/my-health.sh
~/support-lab/bin/my-health.sh
script_rc=$?
printf 'script_exit=%s\n' "$script_rc"
```

**Expected result:** Healthy checks return 0. Syntax success normally produces no output.

**If it differs:** If a line number is reported, fix that line and nearby quotes/keywords before continuing.

### Step 4 — Test an expected failure without changing services

**Where and who:** Learner · application server · Bash terminal

Use an unreachable loopback port. This is a failed probe, not a request to stop the shared application.

```bash
~/support-lab/bin/my-health.sh support-tomcat http://127.0.0.1:1
script_rc=$?
printf 'script_exit=%s\n' "$script_rc"
```

**Expected result:** The endpoint check fails promptly and the script returns 1.

**If it differs:** If it hangs, inspect whether your curl call still has a timeout.

### Step 5 — Test your own validation and array behavior

**Where and who:** Learner · application server · Bash terminal

Predict each status first. Invalid argument counts and unsupported URLs must return 2 before any network probe. Inspect the array expansion in your script; explain why an unquoted string is not equivalent.

```bash
~/support-lab/bin/my-health.sh support-tomcat http://127.0.0.1:8080/loyalty/health extra
printf 'extra_argument_exit=%s\n' "$?"
~/support-lab/bin/my-health.sh support-tomcat file:///etc/passwd
printf 'invalid_url_exit=%s\n' "$?"
~/support-lab/bin/my-health.sh '' http://127.0.0.1:8080/loyalty/health
printf 'empty_service_exit=%s\n' "$?"
```

**Expected result:** All three return 2. Your test transcript names your own script and observed result.

**If it differs:** Do not substitute reference-script results for your implementation.

### Step 6 — Compare with the reference implementation

**Where and who:** Learner · application server · Bash terminal

Read the reference, then test its input validation. Document what your script does and does not yet handle.

```bash
less "$COURSE_ROOT/shared/scripts/health-check.sh"
DISK_LIMIT=invalid "$COURSE_ROOT/shared/scripts/health-check.sh"
reference_rc=$?
printf 'reference_exit=%s\n' "$reference_rc"
```

**Expected result:** The reference returns 2 for invalid configuration. Your report distinguishes this from an unhealthy service.

**If it differs:** Do not claim your scaffold has every reference behavior until you implement and test it.

### Step 7 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. What happens to $? after echo runs?
2. Why can set -e behave differently inside conditionals?

## Submission checklist

Save the following under `~/support-lab/evidence/m3-01` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] my-health.sh — submit a copy from your learner bin directory
- [ ] script-tests.md — healthy, unreachable and invalid-input results plus remaining limitations

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Leave the shared service running. Keep your executable script and test transcript; remove no system files. Return to COURSE_ROOT before the next exercise.

## Completion criteria

- [ ] Your script returns 0 for healthy checks, 1 for an unreachable endpoint and 2 for invalid arguments or missing tools.
- [ ] Explain the quoted option array; submit actual results from your own script.

[Module agenda](../README.md) · [Next exercise](02-evidence.md)
