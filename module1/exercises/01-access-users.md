# Access, identity and user creation

**Time:** 40 minutes  
**Working mode:** Guided walkthrough

| Difficulty | Delivery | Sessions |
|---|---|---|
| Foundation | Core practice | Application-server Bash; workstation only where labeled |

**Deliverables:** identity.txt — learner identity and UTC timestamp; access-notes.md — permission results and answers to the challenge questions

[Walkthrough](#step-by-step-walkthrough) · [Submit](#submission-checklist) · [Recovery](#cleanup-and-recovery)

## Before you start

Instructor access through the supplied key; a unique learner account name and team name assigned by the instructor; a workstation with OpenSSH. No existing learner login is required.

Read the [Learner setup and terminal guide](../../shared/learner-start.md). It explains the local workstation, application-server SSH shell and database-client prompts. Set `COURSE_ROOT` in each Bash session that uses course files; an SSH session does not inherit workstation variables.

## Situation

You are the new support team. Establish individual identities before changing the shared loyalty server.

## Learning goals

- The SSH key authenticates a login; it does not make the login root.
- A user, primary group, supplementary groups and home-directory permissions are separate controls.
- Use sudo only for the supervised administrative step; keep routine investigation unprivileged.

**Repeat run:** Keep earlier submissions. Reopen existing scripts; back up edited files before replacing them. Recheck the baseline and confirm the shared-stack slot before repeating instructor demonstrations.

## Step-by-step walkthrough

### Step 1 — Generate your own SSH key

**Where and who:** Learner · local workstation · Bash terminal

Run this only if this course-specific key does not already exist. Accept a passphrase and keep the private file on your workstation. Send only the displayed public key to the instructor.

```bash
ssh-keygen -t ed25519 -f "$HOME/.ssh/support_lab_ed25519"
cat "$HOME/.ssh/support_lab_ed25519.pub"
```

**Expected result:** Two key files exist; only the .pub file is shared.

**If it differs:** If asked to overwrite a key, answer no and ask the instructor to confirm which existing key to use.

### Step 2 — Open the instructor session

**Where and who:** Instructor · local workstation → application server

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** whoami reports ubuntu, not root. Hostname and timestamp depend on the server.

**If it differs:** If SSH fails, check the key path, network access and host identity with the instructor; do not change the key permissions on a shared copy.

### Step 3 — Create the learner and team

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** The account and home directory exist; no unrestricted sudo grant is added.

**If it differs:** If the account already exists, stop and inspect id ACCOUNT rather than recreating or replacing its files.

### Step 4 — Install the public key

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Directory mode is 700 and key-file mode is 600; both belong to the learner.

**If it differs:** Stop if the pasted text starts with BEGIN PRIVATE KEY or contains multiple lines. Never install a private key here.

### Step 5 — Connect with your own account

**Where and who:** Learner · local workstation · Bash terminal

Open a second workstation terminal. Enter your assigned account name; leave the instructor session open.

```bash
read -r -p 'Your assigned learner account: ' learner
ssh -i "$HOME/.ssh/support_lab_ed25519" "$learner@47.131.221.162"
whoami
id
printf 'HOME=%s\n' "$HOME"
```

**Expected result:** The new SSH session identifies your learner account and team group.

**If it differs:** If a recently added group is missing, reconnect. If authentication fails, the instructor checks the public key, ownership and SSH server logs.

### Step 6 — Create private evidence and confirm access

**Where and who:** Learner · application server · Bash terminal

You are now in your learner SSH session. Run the checks, then ask the instructor to test access from a different learner account.

```bash
mkdir -p ~/support-lab/evidence/m1-01
umask 077
printf 'private lab note\n' > ~/support-lab/private.txt
stat -c '%U %G %a %n' ~/support-lab/private.txt
id > ~/support-lab/evidence/m1-01/identity.txt
date -u +%FT%TZ >> ~/support-lab/evidence/m1-01/identity.txt
```

**Expected result:** The private file is mode 600; an unrelated learner cannot read it.

**If it differs:** If mode differs, set chmod 600 on this file and inspect umask. Changing permission does not change disk capacity.

### Step 7 — Perform the second-user check

**Where and who:** Instructor · application server · Bash terminal

Observe the instructor demonstration. Before the change, predict the result; after it, record the evidence and explain the verification. Execution commands are in the instructor guide. 

**Expected result:** Permission denied is the intended result. Record it; do not loosen permissions to make this check succeed.

**If it differs:** If contents are readable, inspect both the directory modes and file ownership before continuing.

### Step 8 — Transfer the method without copying

**Where and who:** Learner · individual review

Choose one input, path, service name or evidence assumption from this exercise and predict how a changed value would affect the result. Use only learner-owned files or permitted read-only checks. Choose the command yourself, run it, then explain the observed difference to a partner. If only synthetic evidence is available, request a changed capture and label the result simulated.

**Expected result:** An individual prediction, a chosen check and an evidence-based explanation are recorded in the exercise notes.

**If it differs:** A changed input must not mutate shared services or another learner’s files. Ask for a fixture variant when necessary.

## Check your understanding

1. Does a # character inside a command prove you are root?
2. Why might id in an old shell omit a newly granted group?
3. Does chmod 777 fix a missing filesystem quota?

## Submission checklist

Save the following under `~/support-lab/evidence/m1-01` or reference a reviewed artifact stored elsewhere. Record UTC time and distinguish live output from synthetic fixtures.

- [ ] identity.txt — learner identity and UTC timestamp
- [ ] access-notes.md — permission results and answers to the challenge questions

- [ ] Include interpretation, expected failures, unavailable evidence and remaining uncertainty.
- [ ] Review copies for credentials before sharing; never submit your private key or client password file.

## Cleanup and recovery

Leave learner accounts and keys in place for subsequent exercises. Close only redundant sessions with exit. Do not delete accounts or remove SSH access during class.

## Completion criteria

- [ ] Learner logs in using their own key and has a writable home.
- [ ] Private file has mode 600; team membership appears after a new login.

[Module agenda](../README.md) · [Next exercise](02-files-packages.md)
