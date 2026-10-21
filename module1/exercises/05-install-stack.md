# Install and inspect the application stack

**Time:** 50 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Guided application | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** baseline.txt — service state, listeners and HTTP results; components.md — application/database diagram and request-ID explanation; corrected-unit.md — copied unit, correction evidence and verification proposal

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Instructor has rehearsed setup on a dedicated Ubuntu x86_64 training host with adequate capacity. Installation is one shared operation; learners need read access to the course and service journal.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

Deploy the loyalty application, establish a healthy baseline and understand the service before introducing failures.

## Learning goals

- A Java runtime, servlet container, database and application configuration are separate dependencies.
- systemd unit configuration defines process identity, environment, startup and restart behavior.
- A live process is weaker evidence than an authenticated business request.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-05" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Inspect the setup stages

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The host matches the setup assumptions. Learners can explain which operations need sudo.

**If it differs:** If host capacity or platform differs, stop and use the instructor preparation guide; do not force the installer.

### Step 2 — Install the shared stack

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Exit 0 is printed only after application readiness succeeds.

**If it differs:** On failure, preserve the output and inspect the reported stage. Do not continue as though deployment succeeded.

### Step 3 — Repair a copied service configuration

**Where and who:** Learner · application server · Bash terminal

Work on this intentionally broken training unit only. Before editing, annotate the service user, Java dependency, startup path and restart policy. Replace /missing/startup.sh using the effective installed unit as evidence; do not install the copy. Explain which installer stages create the service user, deploy the WAR and configure database access.

```bash
practice_dir=$(mktemp -d "$HOME/support-lab/unit-practice-XXXXXX")
cp "$COURSE_ROOT/shared/templates/service-practice.service" "$practice_dir/support-tomcat.service"
systemctl cat support-tomcat
nano "$practice_dir/support-tomcat.service"
cat "$practice_dir/support-tomcat.service"
```

**Expected result:** Each learner submits an annotated corrected unit and a readiness test proposal.

**If it differs:** If the live unit is unavailable, the instructor supplies its rehearsed capture. Do not guess a production path.

### Step 4 — Inspect service identity and logs

**Where and who:** Learner · application server · Bash terminal

Use these read-only checks after the instructor confirms setup success.

```bash
systemctl cat support-tomcat
systemctl status support-tomcat --no-pager
journalctl -u support-tomcat --since '10 minutes ago' --utc --no-pager
ss -lnt
```

**Expected result:** The unit runs as supportapp and the HTTP listener is bound to loopback port 8080.

**If it differs:** If journal access is denied, ask for the training journal group and reconnect; do not use blanket sudo.

### Step 5 — Verify readiness and business data

**Where and who:** Learner · application server · Bash terminal

Save the responses including the request-ID header.

```bash
curl -i http://127.0.0.1:8080/loyalty/live
curl -i http://127.0.0.1:8080/loyalty/health
curl -i 'http://127.0.0.1:8080/loyalty/player?id=1'
curl -i http://127.0.0.1:8080/loyalty/report
```

**Expected result:** Healthy requests return 200. Player 1 is Synthetic Player One with 100 points; report count is 1000 and total is 10000.00.

**If it differs:** If /live works but /health fails, investigate the authenticated database path before restarting Tomcat.

### Step 6 — Open a browser through SSH forwarding

**Where and who:** Learner · local workstation · Bash terminal

Use a new workstation terminal and your own key. Local port 18080 avoids conflict with a local development server. Keep this session open while browsing.

```bash
read -r -p 'Assigned learner account: ' learner
ssh -N -L 18080:127.0.0.1:8080 -i "$HOME/.ssh/support_lab_ed25519" "$learner@47.131.221.162"
```

**Expected result:** Open http://127.0.0.1:18080/loyalty/health on your workstation; the tunnel command normally shows no output.

**If it differs:** If local port 18080 is occupied, choose a free local port and change the browser URL to match.

### Step 7 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does systemctl enable start a stopped service?
2. Can /live return 200 while the database password is wrong?
3. Why should you collect the journal before restart?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-05` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] baseline.txt — service state, listeners and HTTP results
- [ ] components.md — application/database diagram and request-ID explanation
- [ ] corrected-unit.md — copied unit, correction evidence and verification proposal

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Press Ctrl-C in the tunnel terminal to close forwarding. Leave Tomcat/MySQL running for the following exercises; do not uninstall shared packages.

## Completion criteria

- [ ] Readiness returns 200 and player 1 returns synthetic data.
- [ ] Student explains why Tomcat runs as supportapp and MySQL is not exposed publicly.

[Previous exercise](04-command-investigations.md) · [Module agenda](../README.md) · [Next exercise](06-service-log-triage.md)
