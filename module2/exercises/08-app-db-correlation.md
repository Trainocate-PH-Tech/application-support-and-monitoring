# Application/database correlation

**Time:** 50 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Bash plus labeled MySQL or SQL Server query windows |

**Deliverables:** correlation-timeline.md — arithmetic, IDs, live before/during/after timings and next measurement

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Healthy application and readable correlation.csv; an instructor-controlled delay-fault slot. The live app has no connection pool: pooled-app evidence is synthetic.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

An HTTP request took five seconds, but its database query took 40 milliseconds. Determine where the rest of the time went.

## Learning goals

- Application latency includes pool waits, SQL time, retries and downstream work.
- Correlate IDs and UTC windows; acknowledge clock skew and missing instrumentation.
- Request IDs in app logs do not automatically appear in database logs.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m2-08" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Read and reconcile the synthetic request timing

**Where and who:** Learner · application server · Bash terminal

For each request, add pool wait, SQL time and other time. Compare the sum with total HTTP time.

```bash
cd "$COURSE_ROOT"
cat shared/fixtures/correlation.csv
```

**Expected result:** For r900, 4000 + 40 + 960 = 5000 ms. Retries and pooled connection wait are supplied evidence, not live app features.

**If it differs:** Do not infer an exact request-to-query join from coincident timestamps alone.

### Step 2 — Measure the healthy live baseline

**Where and who:** Learner · application server · Bash terminal

Generate only five sequential requests and record their HTTP codes and seconds.

```bash
shared/scripts/traffic.sh http://127.0.0.1:8080/loyalty 5
```

**Expected result:** A healthy baseline has successful responses; times depend on the host.

**If it differs:** If already failing, resolve that condition before comparing with an injected delay.

### Step 3 — Introduce application-side delay

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The app now adds 1500 ms during the request path.

**If it differs:** Do not stack this fault with another saved fault.

### Step 4 — Compare latency with application evidence

**Where and who:** Learner · application server · Bash terminal

Repeat the same five requests and inspect the same time window.

```bash
shared/scripts/traffic.sh http://127.0.0.1:8080/loyalty 5
journalctl -u support-tomcat --since '5 minutes ago' --utc --no-pager
```

**Expected result:** Responses are roughly 1.5 seconds slower; logs provide request IDs and latency_ms.

**If it differs:** This is not proof of slow SQL. Separate measured facts from where you suspect time was spent.

### Step 5 — Reset and confirm the comparison

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The added delay disappears; compare equivalent routes and sample counts.

**If it differs:** If delay persists, inspect remaining load/configuration before declaring recovery.

### Step 6 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does slow HTTP prove slow SQL?
2. Can retries amplify a partial outage?

## Submission checklist

Save the following under `~/support-lab/evidence/m2-08` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] correlation-timeline.md — arithmetic, IDs, live before/during/after timings and next measurement

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Instructor confirms reset. Keep the synthetic pooled-app timeline and live delay experiment in separate sections of the report.

## Completion criteria

- [ ] Timeline accounts for measured time without inventing an exact database-request-ID join.
- [ ] Learner distinguishes the sample app’s behavior from the supplied pooled-app evidence.

[Previous exercise](07-sqlserver-blocking-plans-jobs.md) · [Module agenda](../README.md) · [Next exercise](09-database-capstone.md)
