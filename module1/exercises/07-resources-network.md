# Resource and network troubleshooting

**Time:** 25 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core: process, listener and endpoint checks; platform cards: choose one; remaining cards: extension | Application-server Bash; workstation only where labeled |

**Deliverables:** resource-baseline.txt — interval observations; connectivity-table.md — layer, evidence, limitation and next check

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Healthy application; sysstat/lsof/network utilities installed; instructor available for privileged observations and a brief fault.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Users report intermittent errors. Determine whether CPU, memory, DNS, TCP, TLS or database authentication evidence supports the complaint.

## Learning goals

- High load is not the same measurement as CPU utilization; memory available differs from free.
- A listening port and successful TCP connection do not prove database authentication.
- Ubuntu firewall checks differ from Red Hat SELinux indicators; do not disable controls as a diagnostic shortcut.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-07" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Measure resources over an interval

**Where and who:** Learner · application server · Bash terminal

Capture a baseline. Explain available versus free memory and load versus CPU percentage.

```bash
uptime
free -h
ps -eo pid,ppid,user,comm,pcpu,pmem --sort=-pcpu | head
top -b -n 1 | head -n 20
pidstat 1 3
```

**Expected result:** Measurements vary with the host; there is no fixed “correct” CPU value.

**If it differs:** If pidstat is missing, ask for sysstat installation. A single sample is insufficient for root-cause claims.

### Step 2 — Observe bounded CPU and file handles

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The synthetic loop ends after 15 seconds; timeout normally returns 124.

**If it differs:** If the service PID is 0, inspect service state instead of passing that PID to lsof.

### Step 3 — Test network layers in order

**Where and who:** Learner · application server · Bash terminal

Keep the target local for these probes. Record what each check establishes.

```bash
getent hosts localhost
dig localhost
nslookup localhost
ping -c 2 127.0.0.1
traceroute -m 3 127.0.0.1
ss -lnt
nc -vz -w 2 127.0.0.1 3306
curl --max-time 5 -i http://127.0.0.1:8080/loyalty/health
```

**Expected result:** DNS, ICMP, listeners, TCP and HTTP provide different evidence; health should be 200 before injection.

**If it differs:** A DNS resolver may treat localhost differently from getent; explain the lookup path rather than inventing an outage.

### Step 4 — Compare TCP with authenticated readiness

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** TCP still connects while application readiness returns 503; reset restores the credentials.

**If it differs:** If TCP also fails, investigate that separate observation instead of assuming all symptoms match the intended scenario.

### Step 5 — Analyze platform evidence

**Where and who:** Learner · Markdown evidence review

Choose one [platform incident card](../../shared/fixtures/platform-incidents.md). State facts, a competing explanation and a discriminating check. Other cards are optional extensions. The instructor may demonstrate read-only firewall inspection.

**Expected result:** You distinguish Ubuntu live observations from Red Hat/Windows synthetic evidence.

**If it differs:** Do not run platform-specific commands blindly or disable security controls as a shortcut.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does failed ping prove the host is down?
2. Is low free memory alone proof of memory pressure?
3. Does curl -k repair an expired certificate?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-07` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] resource-baseline.txt — interval observations
- [ ] connectivity-table.md — layer, evidence, limitation and next check

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Instructor verifies the active fault is reset and /health returns 200. The bounded CPU worker should already have exited; retain observations, not an active load generator.

## Completion criteria

- [ ] Student differentiates TCP reachability from successful authenticated queries.
- [ ] Diagnosis cites interval evidence and acknowledges ICMP/filtering limitations.

[Previous exercise](06-service-log-triage.md) · [Module agenda](../README.md) · [Next exercise](08-first-script-capstone.md)
