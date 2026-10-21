# Learner setup and terminal guide

Use this guide before your first exercise and whenever you open a new terminal. Complete account creation in Module 1 exercise 01 before attempting learner SSH access.

## Step 1 — Identify where you are working

| Label in an exercise | Where to type | Typical prompt / purpose |
|---|---|---|
| Local workstation | Your own computer | Holds your private SSH key and opens SSH tunnels |
| Application server · Bash | SSH terminal after login | Linux commands and course scripts |
| MySQL client | A mysql session opened from Bash | `mysql>`; SQL statements end with `;` or `\G` |
| SQL client host · Bash | Host with sqlcmd and course files | Launches sqlcmd or executes SQL files |
| T-SQL query session | sqlcmd or instructor-approved query editor | sqlcmd uses `GO` on its own line to send a batch |
| Instructor | Instructor's own authorized session | Account creation, installation, faults and administrative changes |

**Expected result:** You can identify which machine, account and interpreter each step needs.

**If unsure:** Run `whoami`, `hostname` and `pwd` only at a Bash prompt. Do not paste Bash commands at `mysql>` or SQL statements into Bash.

## Step 2 — Connect with your learner account

**Where:** Your workstation. The instructor supplies your account name; this key is created in Module 1 exercise 01.

```bash
read -r -p 'Assigned learner account: ' learner
ssh -i "$HOME/.ssh/support_lab_ed25519" "$learner@47.131.221.162"
```

**Expected result:** After authentication, your prompt belongs to the remote learner account. A key passphrase prompt is normal if you protected the key.

**If it differs:** Ask the instructor to confirm the account, host and installed public key. Keep the private key on your workstation. Do not use the instructor's key for learner work.

## Step 3 — Set the course location in this shell

**Where:** Learner Bash on the server/client host where the course files are installed. Ask the instructor for the absolute directory on that host. It may differ from the authoring workstation's path.

```bash
read -r -p 'Absolute course directory on this host: ' COURSE_ROOT
export COURSE_ROOT
if cd "$COURSE_ROOT" && test -f shared/fixtures/application.log; then
    pwd
    printf 'Course directory confirmed\n'
else
    printf 'STOP: ask the instructor to confirm the course location.\n' >&2
fi
```

**Expected result:** `pwd` shows the supplied course directory and Course directory confirmed is printed.

**If it differs:** Stop if `cd` or `test` fails. Confirm the path and read permission; do not continue from an unrelated directory. The environment variable belongs to this shell. Repeat this step in new SSH or SQL-client Bash terminals.

## Step 4 — Prepare your own work area

```bash
mkdir -p "$HOME/support-lab"/{bin,evidence,logs}
umask 077
```

**Expected result:** Your work area exists. Each exercise creates its own evidence subdirectory, such as `~/support-lab/evidence/m1-04`.

**If it differs:** Check `id`, home-directory ownership and filesystem capacity. Do not fix every write problem with chmod 777.

## Step 5 — Read a command block before running it

Run one numbered step at a time. Do not paste the entire document. Copy the contents of a code block, not its triple-backtick fence or a displayed prompt. Read any instruction to wait, switch sessions or verify a result before proceeding.

- `bash` blocks contain shell commands; `sql` blocks contain database statements; `ini` blocks are file contents to enter in an editor.
- Replace explicitly named placeholders before using a configuration file. Prompts using `read` ask you to supply the value without editing the command.
- When a step changes directory, keep using that same terminal until instructed otherwise.
- Capture an exit status immediately with `rc=$?`. Another command replaces `$?`.
- Nonzero can be expected: grep no match is 1; the monitor ALERT is 1; collector partial evidence is 1; NO_DATA/input errors are 2; timeout normally returns 124. The step explains what the specific result means.
- Leave scripts and fixtures in the shared course directory unchanged. Edit copies under your own home.

## Step 6 — Use the editor and clients

For the supplied examples, `nano FILE` opens an editor. Ctrl-O then Enter saves; Ctrl-X exits. If nano is unavailable, ask the instructor to provide an editor or demonstrate the installed alternative; do not perform your own shared-host package installation.

For MySQL, the course uses a mode-600 `~/.support-lab.cnf`; exercise 2.01 guides its creation. Type `exit` at `mysql>` to return to Bash.

For ODBC sqlcmd, follow exercise 2.06 to set credentials and certificate behavior. In interactive mode, enter SQL, then `GO` on its own line. Type `EXIT` to return to Bash. Open independent sessions for lock exercises; each connection owns its own transactions. Never rely on another session's ROLLBACK to release your locks.

## Step 7 — Keep the evidence useful

For each step record the UTC time, command/check, relevant result, interpretation and remaining uncertainty in a Markdown notebook. Preserve expected failures too. Label synthetic fixture analysis separately from live observations. Do not export full shell history, passwords, private keys or database client configuration files.

Each exercise ends with its own submission checklist and cleanup. Finish cleanup with the instructor before another team uses the shared fault slot.
