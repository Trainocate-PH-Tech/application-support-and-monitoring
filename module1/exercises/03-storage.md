# Allocate space and diagnose disk limits

**Time:** 45 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Foundation | Core: diagnose and compare growth; demonstration: quota; extensions: deleted-open files and inodes | Application-server Bash; workstation only where labeled |

**Deliverables:** storage-before-after.txt — observed capacities and quota results; storage-decision-tree.md — diagnosis sequence and EBS explanation

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Instructor has installed parted, quota and cloud-guest-utils. Reserve the shared storage lab; no other team may use its disposable mounts at the same time.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

A learner reports “my EC2 user is capped.” Determine which layer is limiting writes before selecting a fix.

## Learning goals

- EBS volume → partition → filesystem → directory/account; growing one layer does not automatically grow all layers.
- Compare byte capacity, inode capacity, quotas, permissions and deleted-open files.
- The observed host already has an expanded root filesystem; reproduce growth on a disposable disk.

## Prepare this exercise workspace

**Where and who:** Learner · Bash on the host where the course files are installed. For SQL-client exercises, repeat this preparation on that client host if it is separate.

Enter the actual absolute course directory if it has not been set in this shell. Do not paste a path copied from the authoring workstation.

```bash
if [[ -z ${COURSE_ROOT:-} ]]; then
    read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
    export COURSE_ROOT
fi
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    mkdir -p "$HOME/support-lab/evidence/m1-03" && printf 'Workspace ready\n'
else
    printf 'STOP: confirm the course directory before continuing.\n' >&2
fi
```

**Expected result:** Workspace ready is printed only after the course directory and fixture are confirmed and the evidence directory is prepared.

**If it differs:** Stop if `cd` or `test` fails. Confirm the instructor-provided path before running relative commands.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Record the actual limiting layer

**Where and who:** Learner · application server · Bash terminal

Capture your identity and filesystem inventory before accepting the phrase “user disk cap” as a diagnosis.

```bash
id
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
findmnt -T "$HOME"
df -hT "$HOME"
df -i "$HOME"
quota -s
```

**Expected result:** You can identify the device, filesystem, byte usage and inode usage. quota may report no configured limit or a missing tool.

**If it differs:** Missing quota output is not proof that every filesystem is quota-free. Ask the instructor to inspect quota configuration.

### Step 2 — Inspect privileged storage evidence

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Results may be empty on a healthy host; deleted-open files, if present, have link count below one.

**If it differs:** If permission or tooling prevents a check, record it as unavailable, not as a healthy result.

### Step 3 — Create the disposable partition lab

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** A roughly 192 MiB image is mounted at the lab path; root storage remains separate.

**If it differs:** If the lab already exists, stop and check whether another team owns it. Never substitute a root-disk device.

### Step 4 — Grow and compare capacity

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The disposable image is 320 MiB and its filesystem capacity increases; df is smaller than raw device size because of metadata.

**If it differs:** If growth fails, keep the device mounted for inspection and record the failing stage; do not rerun commands against another device.

### Step 5 — Observe quota allocation; compare additional storage symptoms

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Quota enforcement can reject a learner write despite free filesystem space. Deleted-open data can consume space after its filename disappears.

**If it differs:** If the instructor cannot reproduce the required condition, record the limitation. Do not claim the demonstration succeeded.

### Step 6 — Explain the real EBS sequence

**Where and who:** Team discussion; no AWS changes

Using the [storage worksheet](../../shared/storage-worksheet.md), draw volume → partition → filesystem. Treat quota and permissions as separate checks. EBS administration is an instructor demonstration; no AWS changes are required.

**Expected result:** Your decision tree chooses a fix only after identifying the limiting layer.

**If it differs:** Do not infer the historical EC2 problem from today’s expanded filesystem alone.

### Step 7 — Choose the limiting layer independently

**Where and who:** Learner · storage worksheet

Case A: device 120 GiB, partition 8 GiB, filesystem 7.7 GiB, no quota. Case B: filesystem 70% free, quota usage equals hard limit. Case C: bytes available but inodes 100% used. For each, choose the next observation, propose one scoped correction and state what must be verified.

**Expected result:** Three separate diagnoses; no blanket repartitioning recommendation.

**If it differs:** A lack of permission is not proof of a full disk.

### Step 8 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. df says full but du is small: name three explanations.
2. Will adding a user allocate a new partition?
3. Why can root sometimes write when an ordinary user cannot, even without quotas?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-03` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] storage-before-after.txt — observed capacities and quota results
- [ ] storage-decision-tree.md — diagnosis sequence and EBS explanation

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

The growth lab is removed before demonstrations C/D; each demonstration then performs its own cleanup. Confirm no lab image remains mounted. If interrupted with a growth lab still active, the instructor runs its cleanup helper after closing open handles. Do not rerun cleanup against an already removed lab or delete a mounted image.

## Completion criteria

- [ ] Student identifies the limiting layer from evidence, not the wording of the complaint.
- [ ] Disposable filesystem grows and can be cleaned up; root partition is untouched.

[Previous exercise](02-files-packages.md) · [Module agenda](../README.md) · [Next exercise](04-command-investigations.md)
