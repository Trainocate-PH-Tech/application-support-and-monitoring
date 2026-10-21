# Linux command challenges — guided setup, independent solutions

Complete Module 1 exercise 09 setup first. Work inside its printed challenge_dir, never the shared original fixtures. Keep a numbered Markdown notebook. For each task, record prediction, command, observed output, interpretation and one limitation. Solutions remain in the instructor answer key.

## How to work through the bank

1. Complete tasks 1–6, then review your notebook with a peer.
2. Complete tasks 7–12 and repeat the review.
3. Complete tasks 13–18 and submit the final notebook.
4. Use the optional hints in exercise 09 if stuck; do not open the answer key during the attempt.

## Task 1 — Count valid requests, 5xx errors and malformed rows separately. Why does `grep ERROR` overcount?

**Where and input:** Learner Bash in your copied challenge workspace. application.log.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Compare a word-based search with explicit field parsing. Keep malformed records separate from the request denominator.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 2 — Rank paths by frequency and break ties alphabetically.

**Where and input:** Learner Bash in your copied challenge workspace. application.log.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Extract the path field, count groups and decide how to sort ties. State the order before testing.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 3 — Sort latency values numerically without including the CSV header.

**Where and input:** Learner Bash in your copied challenge workspace. latency.csv.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Exclude the header and compare lexical with numeric ordering. Explain why this simple CSV permits a delimiter-based tool.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 4 — Count unique request IDs. Explain why counting log lines is not always counting requests.

**Where and input:** Learner Bash in your copied challenge workspace. application.log.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Extract IDs, check uniqueness and explain when multiple log lines could belong to one request.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 5 — Find all files including hidden names, spaces, a leading dash and a newline. Pass them safely to another command.

**Where and input:** Learner Bash in your copied challenge workspace. filenames/.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Inspect every filename and choose a delimiter that survives spaces and newlines. Do not parse a human-readable ls listing.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 6 — Archive those files and verify that all names survive extraction into a new directory.

**Where and input:** Learner Bash in your copied challenge workspace. filenames/ and a new extraction folder.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Create an archive from your selected files, list its members, extract into a fresh directory and compare with the source copy.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 7 — Read `-dangerous-name.txt` without having it interpreted as an option.

**Where and input:** Learner Bash in your copied challenge workspace. filenames/-dangerous-name.txt.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Choose a way to distinguish a filename from an option. Read this copied file without renaming it.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 8 — Compare `grep no_match application.log | wc -l` with and without pipefail. Explain all relevant exit codes.

**Where and input:** Learner Bash in your copied challenge workspace. application.log and a search term that is absent.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Run the pipeline twice with different pipefail settings. Capture its exit status immediately each time, then restore your original setting.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 9 — Predict `printf 'one\ntwo' | wc -l`. Explain a robust record-counting alternative.

**Where and input:** Learner Bash in your copied challenge workspace. The printf example in the question; no file needed.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Predict the count before execution. Compare newline characters with logical records and state your definition.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 10 — Explain why `uniq -c` without sorting misses separated duplicates.

**Where and input:** Learner Bash in your copied challenge workspace. A small sequence containing a, b, a.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Create a temporary input with separated duplicates. Compare grouping with and without ordering first.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 11 — Follow a rotating log: compare `tail -f` and `tail -F`; describe a reproducible test in your workspace.

**Where and input:** Learner Bash in your copied challenge workspace. A disposable rotation-demo.log in your copied workspace; two terminals.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Create the disposable log in terminal A and start a follower. In terminal B rename it, create a replacement and append to both. Stop the follower with Ctrl-C, then repeat with the other follow mode.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 12 — Explain why `sudo echo value > restricted-file` can fail and propose a scoped alternative.

**Where and input:** Learner Bash in your copied challenge workspace. A written scenario only; no root-directory write required.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Draw which process opens the redirection target and which process receives sudo privileges. Propose an approved-path alternative in notes; do not try it against /root.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 13 — Find files changed recently without crossing filesystems; explain the difference between mtime and ctime.

**Where and input:** Learner Bash in your copied challenge workspace. Your copied workspace and a file you have just touched.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Create or touch a file inside your copy, select a recent time window and ensure the search does not cross filesystem boundaries.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 14 — Extract a log window with ISO UTC timestamps. Explain when lexical comparisons are valid and what timezone offsets break.

**Where and input:** Learner Bash in your copied challenge workspace. application.log, using its normalized UTC timestamps.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Choose an inclusive start and exclusive end. State assumptions about UTC normalization and timestamp precision before filtering.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 15 — A filesystem is full but `du` is small. Provide a diagnostic sequence that considers privilege, mount boundaries, deleted-open files and inodes.

**Where and input:** Learner Bash in your copied challenge workspace. The storage observations from exercise 03; read-only analysis.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Order checks to distinguish bytes, inodes, permissions, mount boundaries and open descriptors without deleting evidence.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 16 — A shell sees a command but cron does not. Diagnose PATH, working directory, environment, shebang and permissions.

**Where and input:** Learner Bash in your copied challenge workspace. Your own script and the minimal-environment test from exercise 3.05.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Compare working directory, PATH, interpreter and permission assumptions. Use only your learner-owned script in a minimal environment.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 17 — Explain why unquoted `$files` and `for f in $(find ...)` fail on arbitrary names; propose a safe loop.

**Where and input:** Learner Bash in your copied challenge workspace. The copied filenames/ tree.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Test a naive loop on the copied names, then design a loop that preserves each filename as one value. Explain which features require Bash.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Task 18 — Create a pipeline that emits a report to screen and a file, preserves failure status and does not overwrite original evidence.

**Where and input:** Learner Bash in your copied challenge workspace. A simple read-only check and a new output file.

### Step 1 — Predict

Write the expected behavior and the assumption most likely to break it.

### Step 2 — Investigate

Send output to both screen and a new file. Introduce a harmless no-match/failure condition and verify that your wrapper preserves it.

### Step 3 — Verify and record

**Completion check:** Your notebook contains the actual command/result, an explanation, and a counterexample or limitation. A peer can reproduce the result using your stated input.

**If stuck:** Inspect the exact input and tool help, then narrow the test to one assumption. Do not modify shared evidence or suppress an error without recording it.

## Cleanup and submission

Stop any follower with Ctrl-C and restore pipefail if you changed it. Keep only your own copied files/archives for review; leave shared fixtures unchanged. Submit command-notebook.md with sections 1–18 and peer-review.md.

## Optional discussion

Explain tar packaging versus gzip compression; distinguish a curl exit code from HTTP status; compare ping, nc, ss and authenticated SQL as evidence.
