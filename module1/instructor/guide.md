# Module 1 instructor guide

Keep this answer key separate from student handouts. Rehearse setup and fault reset before class. Speaker notes include the same reasoning for live delivery. Review [shared setup](../../shared/instructor/setup-and-delivery.md), [scenario cards/rubric](../../shared/instructor/scenarios.md) and [storage procedures](../../shared/instructor/storage.md).

## Access, identity and user creation

Slides 5–9. Time: 40.

**Expected reasoning:** Use id -u to establish identity. A new login refreshes supplementary groups. Directory traversal requires execute permission; read permission alone is insufficient. chmod changes access, not capacity. Keep ~/.ssh owned by its account and never place a private key in the course repository.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Learner logs in using their own key and has a writable home. Private file has mode 600; team membership appears after a new login.

**Submission:** Identity baseline, permission evidence and a short access checklist.

**Guided walkthrough checkpoints:**

1. Generate your own SSH key — Two key files exist; only the .pub file is shared.
2. Open the instructor session — whoami reports ubuntu, not root. Hostname and timestamp depend on the server.
3. Create the learner and team — The account and home directory exist; no unrestricted sudo grant is added.
4. Install the public key — Directory mode is 700 and key-file mode is 600; both belong to the learner.
5. Connect with your own account — The new SSH session identifies your learner account and team group.
6. Create private evidence and confirm access — The private file is mode 600; an unrelated learner cannot read it.
7. Perform the second-user check — Permission denied is the intended result. Record it; do not loosen permissions to make this check succeed.
8. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Leave learner accounts and keys in place for subsequent exercises. Close only redundant sessions with exit. Do not delete accounts or remove SSH access during class.

**Instructor execution sheet:**

Open the instructor session

Using the instructor key at ~/pem/okada.pem, connect. The following steps run on the server after login.

```bash
chmod 600 ~/pem/okada.pem
ssh -i ~/pem/okada.pem ubuntu@47.131.221.162
whoami
id
hostname
date -u +%FT%TZ
```

Create the learner and team

The instructor enters the assigned names at the prompts. Keep these variables in this terminal for the next two steps. Use a new account for each learner.

```bash
read -r -p 'Assigned learner name: ' learner
read -r -p 'Assigned team group: ' team
sudo adduser --disabled-password --gecos '' "$learner"
sudo groupadd -f "$team"
sudo usermod -aG "$team" "$learner"
sudo chmod 750 "/home/$learner"
sudo install -d -m 700 -o "$learner" -g "$learner" "/home/$learner/.ssh"
```

Install the public key

Paste the learner’s single public-key line at the prompt. These instructions assume the newly created account has no existing authorized_keys file.

```bash
read -r -p 'Learner PUBLIC key (one line): ' learner_public_key
printf '%s\n' "$learner_public_key" | sudo tee "/home/$learner/.ssh/authorized_keys" >/dev/null
sudo chown "$learner:$learner" "/home/$learner/.ssh/authorized_keys"
sudo chmod 600 "/home/$learner/.ssh/authorized_keys"
sudo stat -c '%U %G %a %n' "/home/$learner/.ssh" "/home/$learner/.ssh/authorized_keys"
```

Perform the second-user check

Use the account variables retained in the instructor session. Enter a different learner account that exists.

```bash
read -r -p 'A different learner account: ' other
sudo -u "$other" cat "/home/$learner/support-lab/private.txt"
```
## Navigation, files and package installation

Slides 10–14. Time: 60.

**Expected reasoning:** The shell performs redirection before sudo runs echo. Use a deliberately approved destination and sudo tee when needed. cd changes the current process environment. A symlink stores a path and does not keep its target alive. Use -- before filenames when the tool supports it.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Student explains why the symlink breaks after its target is removed. Commands are found through PATH; package installation is verified rather than assumed.

**Submission:** A directory tree, package verification table and safe file-handling notes.

**Guided walkthrough checkpoints:**

1. Create and navigate your workspace — You return to ~/support-lab/files-practice. cd - prints the previous directory.
2. Create, copy and rename a file — head prints alpha; latest points to status.txt.
3. Inspect packages and command lookup — Installation completes or reports the packages already installed; package ownership is printed.
4. Check the tools as a learner — Tool paths print; the archive contains application.log, latency.csv and filenames/.
5. Compress a copy and observe a broken link — gzip prints compress me; the final cat fails because the link’s target was removed. That failure is expected.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Keep ~/support-lab/fixtures for later exercises. Leave the broken link as evidence or remove that link only with rm -i; retain the original incoming file.

**Instructor execution sheet:**

Inspect packages and command lookup

Learners observe this shared-host package change. Explain that apt-get update refreshes package metadata, then install the named diagnostic packages.

```bash
sudo apt-get update
apt-cache search '^lsof$'
sudo apt-get install -y curl netcat-openbsd dnsutils lsof sysstat
dpkg-query -S /usr/bin/lsof
```
## Allocate space and diagnose disk limits

Slides 15–19. Time: 45.

**Expected reasoning:** Possible causes include deleted-open files, hidden data under mounts, inaccessible paths during du, reserved ext4 blocks, inode exhaustion, quotas, or permissions. Normal user creation does not create a per-user EBS disk. Show inode and quota evidence before diagnosing a cap. EBS growth requires appropriate AWS access and a snapshot; grow the partition only if present, then the matching filesystem.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Student identifies the limiting layer from evidence, not the wording of the complaint. Disposable filesystem grows and can be cleaned up; root partition is untouched.

**Submission:** A storage decision tree and before/after capacity evidence.

**Guided walkthrough checkpoints:**

1. Record the actual limiting layer — You can identify the device, filesystem, byte usage and inode usage. quota may report no configured limit or a missing tool.
2. Inspect privileged storage evidence — Results may be empty on a healthy host; deleted-open files, if present, have link count below one.
3. Create the disposable partition lab — A roughly 192 MiB image is mounted at the lab path; root storage remains separate.
4. Grow and compare capacity — The disposable image is 320 MiB and its filesystem capacity increases; df is smaller than raw device size because of metadata.
5. Observe quota allocation; compare additional storage symptoms — Quota enforcement can reject a learner write despite free filesystem space. Deleted-open data can consume space after its filename disappears.
6. Explain the real EBS sequence — Your decision tree chooses a fix only after identifying the limiting layer.
7. Choose the limiting layer independently — Three separate diagnoses; no blanket repartitioning recommendation.
8. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** The growth lab is removed before demonstrations C/D; each demonstration then performs its own cleanup. Confirm no lab image remains mounted. If interrupted with a growth lab still active, the instructor runs its cleanup helper after closing open handles. Do not rerun cleanup against an already removed lab or delete a mounted image.

**Instructor execution sheet:**

Inspect privileged storage evidence

Do not change the root filesystem. Explain what each result can and cannot establish.

```bash
sudo repquota -a
sudo lsof +L1
```

Create the disposable partition lab

From COURSE_ROOT, read the helper and run its create operation. Record the loop device printed by the script.

```bash
cd "$COURSE_ROOT"
less shared/scripts/storage-lab.sh
sudo shared/scripts/storage-lab.sh create
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo df -hT /var/lib/support-storage-lab/mount
```

Grow and compare capacity

Read the grow branch aloud: image/device capacity, partition growth, then ext4 growth. The helper runs these stages consecutively; it does not pause interactively.

```bash
sudo shared/scripts/storage-lab.sh grow
sudo lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo df -hT /var/lib/support-storage-lab/mount
```

Observe quota allocation; compare additional storage symptoms

After the growth demonstration, the instructor cleans up its image. Observe the quota demonstration and complete the [storage worksheet](../../shared/storage-worksheet.md). Deleted-open-file and inode demonstrations are optional extensions with their own cleanup.

```bash
sudo shared/scripts/storage-lab.sh cleanup
```
## Command investigations and first Bash script

Slides 20–24. Time: 75.

**Expected reasoning:** grep exits 1 for no matches, 2 for an error. uniq removes adjacent duplicates only. Basic cut is not a full CSV parser. A pipeline usually reports its last command status; pipefail changes this. Use NUL separators for arbitrary filenames. The fixture contains six valid requests, two 5xx errors, two slow requests at >=1000 ms, and one malformed row.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Counts match parsed fixture records; malformed rows are reported separately. All unusual filenames survive the archive round trip. Run triage.sh with two service arguments and explain the captured statuses.

**Submission:** Pipelines, archive check and triage.sh with two-input test evidence.

**Guided walkthrough checkpoints:**

1. Inspect the evidence without editing it — Seven lines exist: six requests and one malformed record.
2. Compare a naive search with parsed status — ERROR matches three lines, but status=5xx matches two. /player appears three times.
3. Extract and transform fields — Numeric latencies are 5, 25, 30, 80, 1500 and 2100. tee writes to screen and file.
4. Handle unusual filenames safely — diff prints nothing and returns 0 when names and contents match.
5. Observe an expected nonzero pipeline result — wc prints 0 and pipeline_exit is 1: grep found no matches, rather than a command error.
6. Build your first evidence script — An executable script and timestamped evidence exist before the incident challenge. Syntax checking completes before execution.
7. Inspect and execute your saved script — The collector runs from another directory and reports the service check separately.
8. Change the input, then choose your own check — Your notes include the prediction, observed status and a justified additional command.
9. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Leave original fixtures unchanged. Keep your archive and evidence; you may remove only the newly created verification directory after recording its contents. Restore pipefail as shown.

**Instructor execution sheet:**


## Install and inspect the application stack

Slides 25–29. Time: 50.

**Expected reasoning:** enable configures boot behavior; --now also starts. /live intentionally avoids the database. /health opens a connection and executes SELECT 1. Restart can destroy transient evidence and temporarily hide a fault. systemctl cat reveals drop-ins as well as the main unit.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Readiness returns 200 and player 1 returns synthetic data. Student explains why Tomcat runs as supportapp and MySQL is not exposed publicly.

**Submission:** A component diagram and a healthy baseline evidence bundle.

**Guided walkthrough checkpoints:**

1. Inspect the setup stages — The host matches the setup assumptions. Learners can explain which operations need sudo.
2. Install the shared stack — Exit 0 is printed only after application readiness succeeds.
3. Repair a copied service configuration — Each learner submits an annotated corrected unit and a readiness test proposal.
4. Inspect service identity and logs — The unit runs as supportapp and the HTTP listener is bound to loopback port 8080.
5. Verify readiness and business data — Healthy requests return 200. Player 1 is Synthetic Player One with 100 points; report count is 1000 and total is 10000.00.
6. Open a browser through SSH forwarding — Open http://127.0.0.1:18080/loyalty/health on your workstation; the tunnel command normally shows no output.
7. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Press Ctrl-C in the tunnel terminal to close forwarding. Leave Tomcat/MySQL running for the following exercises; do not uninstall shared packages.

**Instructor execution sheet:**

Inspect the setup stages

Display the setup script before running it. Identify package installation, checksum verification, app account creation, WAR build and systemd setup.

```bash
cd "$COURSE_ROOT"
less shared/scripts/setup-ubuntu.sh
shared/scripts/preflight.sh
```

Install the shared stack

Run once for the class. Downloads may take several minutes; do not launch another installer while it runs.

```bash
sudo shared/scripts/setup-ubuntu.sh --training-host
setup_rc=$?
printf 'setup_exit=%s\n' "$setup_rc"
```
## Service failures and application log diagnosis

Slides 30–34. Time: 35.

**Expected reasoning:** The startup drop-in overrides ExecStart; inspect both unit and drop-in. The permissions fault leaves root owning a mode-600 config, so supportapp cannot read it. Correct access is root:supportapp mode 640. Repeated restarts cannot fix either cause. Preserve the failure evidence before using reset.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Evidence names the actual failed executable or unreadable file. Recovery includes HTTP and business checks, not only active service status.

**Submission:** A timeline with failing and recovered request IDs.

**Guided walkthrough checkpoints:**

1. Capture the healthy baseline — HTTP 200 establishes the before-state.
2. Introduce and observe a startup fault — A deliberate service-start error is expected; the instructor announces that the investigation can begin.
3. Locate the failing startup configuration — status may return nonzero. The training drop-in points to a nonexistent executable.
4. Reset, then introduce a different failure — Readiness is healthy between faults; the permission fault affects configuration readability.
5. Inspect runtime symptoms and file access — HTTP 503 accompanies a file-access error even though Tomcat can be active.
6. Verify permissions, restore and retest — Before reset the root-owned config is 600; restored access is root:supportapp mode 640. HTTP checks recover.
7. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Instructor confirms fault reset and healthy business requests. Keep the two fault timelines separate; leave the shared services running.

**Instructor execution sheet:**

Introduce and observe a startup fault

This guided exercise names the fault; final assessments will not. Tell learners when injection is complete.

```bash
cd "$COURSE_ROOT"
sudo shared/scripts/fault.sh startup
```

Reset, then introduce a different failure

Reset the startup fault before injecting permissions. Wait for health to return before the next injection.

```bash
sudo shared/scripts/fault.sh reset
curl --fail -i http://127.0.0.1:8080/loyalty/health && sudo shared/scripts/fault.sh permissions
```

Verify permissions, restore and retest

Compare the service identity with file ownership, then restore the saved configuration.

```bash
sudo namei -l /etc/support-lab/app.properties
sudo stat -c '%U %G %a %n' /etc/support-lab/app.properties
sudo shared/scripts/fault.sh reset
curl -i http://127.0.0.1:8080/loyalty/health
curl -i 'http://127.0.0.1:8080/loyalty/player?id=1'
```
## Resource and network troubleshooting

Slides 35–39. Time: 25.

**Expected reasoning:** ICMP can be blocked while TCP works. Inspect available memory, swap/OOM evidence and workload behavior. curl -k bypasses validation and does not repair certificates. A MySQL listener can accept TCP while rejecting credentials. Red Hat AVC evidence requires policy/path investigation; do not teach disabling SELinux as the fix.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Student differentiates TCP reachability from successful authenticated queries. Diagnosis cites interval evidence and acknowledges ICMP/filtering limitations.

**Submission:** A layered connectivity table with evidence and remaining unknowns.

**Guided walkthrough checkpoints:**

1. Measure resources over an interval — Measurements vary with the host; there is no fixed “correct” CPU value.
2. Observe bounded CPU and file handles — The synthetic loop ends after 15 seconds; timeout normally returns 124.
3. Test network layers in order — DNS, ICMP, listeners, TCP and HTTP provide different evidence; health should be 200 before injection.
4. Compare TCP with authenticated readiness — TCP still connects while application readiness returns 503; reset restores the credentials.
5. Analyze platform evidence — You distinguish Ubuntu live observations from Red Hat/Windows synthetic evidence.
6. Transfer the method without copying — An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**Exercise-specific recovery:** Instructor verifies the active fault is reset and /health returns 200. The bounded CPU worker should already have exited; retain observations, not an active load generator.

**Instructor execution sheet:**

Observe bounded CPU and file handles

Start one bounded worker while learners repeat pidstat. Then inspect Tomcat handles; do not start multiple workers.

```bash
timeout 15s bash -c 'while :; do :; done' &
worker_pid=$!
sudo lsof -p "$(systemctl show -p MainPID --value support-tomcat)" | head
wait "$worker_pid"
worker_rc=$?
printf 'worker_exit=%s\n' "$worker_rc"
```

Compare TCP with authenticated readiness

Inject only after the previous checks finish. Learners repeat nc and curl while the fault is active.

```bash
sudo shared/scripts/fault.sh db-auth
nc -vz -w 2 127.0.0.1 3306
curl -i http://127.0.0.1:8080/loyalty/health
sudo shared/scripts/fault.sh reset
```
## Linux incident challenge with your evidence script

Slides 40–44. Time: 40.

**Expected reasoning:** A partial bundle may contain a failed service-status check or a permission-denied log capture. Record those statuses instead of suppressing them. The interpreter in the shebang must exist; use Bash explicitly for Bash syntax. Grade reasoning and verified recovery above speed.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Script runs without interactive input and records UTC timestamps. Incident report includes evidence, probable cause, mitigation and recovery validation.

**Submission:** Executable triage script, checklist, evidence bundle and incident report.

**Guided walkthrough checkpoints:**

1. Prepare your submission workspace — A report exists before the fault is introduced; roles and start time are recorded.
2. Extend your existing evidence script — Your script runs and captures observations without silently treating failures as healthy.
3. Receive the incident and assign roles — You know the business symptom, allowed targets, time budget and required deliverables, but not the root cause.
4. Investigate within the time budget — Your timeline contains evidence-linked observations rather than a list of guesses.
5. Collect and inspect evidence — A full or partial bundle is available. Exit 1 can be valid partial evidence; inspect the manifest.
6. Propose one mitigation and define recovery — The instructor can review a concrete action; the report distinguishes diagnosis from speculation.
7. Verify and hand over — Recovery is supported by the affected business function and a clear observation window.

**Exercise-specific recovery:** After saving evidence, the instructor resets the assigned fault. Roll back any transactions opened during investigation in their owning sessions, close database clients and unset SQLCMDPASSWORD where used. Verify the affected business route again. Keep evidence and scripts; do not reset another team’s active scenario.

**Instructor execution sheet:**


## Advanced Linux command challenge bank

Slides 45–49. Time: Extension.

**Expected reasoning:** Use tail -F for following a filename across rotation when appropriate. wc -l counts newline characters. Parse explicit status fields rather than unstructured words. See instructor command-answer key for all 18 explanations.

**Hint ladder:** First ask which layer the evidence describes. Next ask for a discriminating command from the worksheet. Finally point to the relevant fixture or reference script; do not reveal the hidden fault immediately.

**Acceptance:** Each answer includes an explanation and a counterexample where appropriate. No command mutates original evidence or uses blanket deletion.

**Submission:** A reviewed command notebook; extensions do not displace required class activities.

**Guided walkthrough checkpoints:**

1. Create an isolated challenge workspace — All challenge mutations stay inside your new copy.
2. Prepare an answer notebook — The notebook has numbered sections 1–18 before you begin solving.
3. Solve and test counterexamples — Each completed task includes a runnable approach and evidence supporting its behavior.
4. Review with another learner — A second person can reproduce your result from the written steps.

**Exercise-specific recovery:** Keep the copied challenge workspace until review completes. Close any tail-following process with Ctrl-C. Remove only temporary files you created in that copy; leave originals untouched.

**Instructor execution sheet:**
