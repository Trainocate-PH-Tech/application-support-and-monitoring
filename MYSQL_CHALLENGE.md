# MySQL Challenge: The Slow Ticket-Sales Batch

**Audience:** participants who completed [support diagnostics](MYSQL_SUPPORT_DIAGNOSTICS.md), [log reporting](MYSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md), and [slow-query analysis](MYSQL_SLOW_QUERY_ANALYSIS_EXERCISE.md).

**Time:** 60–90 minutes. **Environment:** Ubuntu Bash, MySQL 8.0/8.4, and a dedicated training instance. The instructor provides logging administration and readable captures. No new diagnostic tools are required.

## Section: Incident brief

A ticket-sales team says its reporting batch takes several seconds. Someone proposes: “Find the longest query in the slow log and add an index to fix it.”

Your job is to investigate that claim, identify the work performed by the batch, and produce an evidence-based report with your own Bash script. There is a catch: do not assume that the first slow-log capture gives a complete or correctly prioritized account of the workload.

Do not consult the instructor solution until you submit your findings.

## Section: Dataset and supplied process

The new database is `mysql_ticket_challenge`, separate from previous labs. Its `ticket_sales` table has:

| Column | Meaning |
|---|---|
| `sale_id` | Unique sale identifier; primary key |
| `event_id` | Event being reported |
| `amount` | Sale amount in synthetic currency units |

There are 100000 sales across 100 event IDs. Each event has 1000 sales totalling 25000.00. These fixed results let you detect accidental changes to the business query.

The instructor imports [challenge-setup.sql](shared/sql/mysql/challenge-setup.sql) once and provides database access. On the EC2 training host, use `developer` and enter `password` at each `-p` prompt after connecting over SSH. You receive two process files:

- [challenge-workload.sql](shared/sql/mysql/challenge-workload.sql): a finite read-only batch to execute.
- [challenge-inspect.sql](shared/sql/mysql/challenge-inspect.sql): identity, index, plan, and result checks.

The batch ends by itself. Run it once for the baseline and once for the fuller capture; do not turn it into a stress test. Timing varies by machine, so conclusions must follow your evidence.

## Section: Prepare your workspace

1. In Bash on the host containing the repository:

   ```bash
   read -r -p 'Absolute repository directory: ' COURSE_ROOT
   cd "$COURSE_ROOT"
   ```

   Stop if `cd` fails.

2. Create a private workspace and preserve both an original and a working copy:

   ```bash
   umask 077
   mkdir -p "$HOME/support-lab"
   WORK_DIR=$(mktemp -d "$HOME/support-lab/mysql-challenge-XXXXXX")
   mkdir -p "$WORK_DIR/input" "$WORK_DIR/reports"
   cp shared/sql/mysql/challenge-workload.sql "$WORK_DIR/input/original-workload.sql"
   cp shared/sql/mysql/challenge-workload.sql "$WORK_DIR/input/capture-workload.sql"
   printf '%s\n' "$WORK_DIR"
   ```

3. Give the workspace path to the instructor for the two log exports. Record the server, account, MySQL version, UTC capture windows, and whether the evidence is live in `input/provenance.txt` using `nano`. Do not include the password.
4. If you open another Bash terminal, set `WORK_DIR` to that same path. The commands below use the EC2 training account `developer`.

## Section: Run the baseline and observe it

1. Confirm the instructor has enabled the dedicated **baseline** slow-log file. The instructor must keep unrelated activity out of this capture.
2. In Bash, run the original process once:

   ```bash
   mysql -u developer -p mysql_ticket_challenge \
     < "$WORK_DIR/input/original-workload.sql" \
     > "$WORK_DIR/baseline-output.txt"
   batch_rc=$?
   printf 'batch exit=%s\n' "$batch_rc"
   ```

3. During execution, use a second terminal and the same database account:

   ```bash
   mysql -u developer -p mysql_ticket_challenge
   ```

   At `mysql>`:

   ```sql
   SELECT UTC_TIMESTAMP();
   SHOW FULL PROCESSLIST;
   ```

   Record what is running and what it is doing. An idle `Sleep` command state and a SQL call to `SLEEP()` are different things. If you miss the observation window, use the completed capture; do not fabricate a process-list result.

4. After the process exits, read its output with `cat`. Verify eight sales summaries, each with count 1000 and amount 25000.00. Report any mismatch before proceeding.
5. The instructor stops capture and supplies the complete file as `input/baseline.log`. Keep it intact; a tail fragment can split a slow-query record.

## Section: Investigate what the log does and does not show

1. Inspect the bounded capture and workload with familiar commands:

   ```bash
   tail -n 80 "$WORK_DIR/input/baseline.log"
   grep -n '^# Query_time:' "$WORK_DIR/input/baseline.log"
   cat "$WORK_DIR/input/original-workload.sql"
   ```

   If grep exits 1, that means no matching lines. It does not prove no queries ran.

2. When `mysqldumpslow` is available, rank the **complete capture** three ways:

   ```bash
   mysqldumpslow -s c "$WORK_DIR/input/baseline.log"
   mysqldumpslow -s at "$WORK_DIR/input/baseline.log"
   mysqldumpslow -s t "$WORK_DIR/input/baseline.log"
   ```

3. Compare submitted SQL, successful output, current/session/global logging settings, and captured statements. Explain any mismatch. A separately opened observer connection may have different session values from the batch connection.
4. Record which statements are visible, which may be missing, and what additional evidence is needed before recommending an index.

## Section: Obtain a fuller capture without changing the business workload

1. Propose a capture-only change using commands taught in the earlier exercises. Explain which connection it affects and why it should make the required statements visible. The instructor manages global logging; your working file may change session logging thresholds only.
2. Edit `input/capture-workload.sql` using `nano`. Preserve every query, event ID, and query count. Keep the original copy untouched. Do not add loops, enlarge the data, or remove inconvenient statements.
3. Have the instructor switch to a fresh **detail** log file. Then run the working copy once:

   ```bash
   mysql -u developer -p mysql_ticket_challenge \
     < "$WORK_DIR/input/capture-workload.sql" \
     > "$WORK_DIR/detail-output.txt"
   batch_rc=$?
   printf 'batch exit=%s\n' "$batch_rc"
   ```

4. Verify the same sales results. The instructor stops capture and supplies `input/detail.log`. Compare rankings and raw timing headers again. Do not mix records from different runs.
5. Explain whether the reports are actually slow in absolute terms on this host, merely frequent, or doing work that warrants a plan investigation. A lower threshold changes visibility; it does not make the database slower by definition.

## Section: Inspect query plans and propose a change

1. Capture the supplied read-only inspection:

   ```bash
   mysql -u developer -p mysql_ticket_challenge \
     < "$COURSE_ROOT/shared/sql/mysql/challenge-inspect.sql" \
     > "$WORK_DIR/input/plan-before.txt"
   cat "$WORK_DIR/input/plan-before.txt"
   ```

2. Explain `possible_keys`, `key`, estimated `rows`, and the relation between examined rows and the business result. Remember that the aggregation returns one result row representing many sales.
3. Propose one targeted change with its expected benefit, write/storage cost, and rollback. Do not claim it will fix a query it cannot affect.
4. If the instructor accepts an index experiment, repeat the same inspection into `input/plan-after.txt`, compare results/plans, and have the instructor remove only the newly created index. If no experiment is run, report post-change evidence as unavailable.

## Section: Build your Bash report utility

Create `challenge-report.sh` in your workspace. Adapt the Bash patterns from the preceding exercises; do not use the instructor's completed script.

The interface is:

```text
challenge-report.sh INPUT_DIR OUTPUT_PARENT
```

Requirements:

- Validate readable `provenance.txt`, `baseline.log`, `detail.log`, `original-workload.sql`, `capture-workload.sql`, and `plan-before.txt`.
- Create a unique private report directory; copy the evidence into it. Include `plan-after.txt` when available.
- Report both capture windows separately, including timing-header counts, query/lock time, rows examined, and frequency/average/total rankings when available.
- Compare the number of logged business queries with the eight submitted queries. Distinguish missing capture from absent execution.
- Include the original and revised logging settings, plan evidence, fixed business results, and missing evidence.
- Treat empty captures as unknown; handle grep's no-match status correctly. Label unavailable `mysqldumpslow` rankings rather than inventing them.
- Leave space for your conclusion: the catch, evidence for it, what an index could affect, uncertainty, and next check. No automatic tuning, service restarts, or credential collection.

Use only techniques already taught: Bash arguments, variables, quoting, functions, conditionals, loops, `umask`, `mkdir`, `mktemp`, `cp`, `cat`, `tail`, `grep`, `awk`, `printf`, `date`, redirection, and `mysqldumpslow`.

1. Create the script with `nano`, then validate and execute it:

   ```bash
   cd "$WORK_DIR"
   bash -n challenge-report.sh
   chmod u+x challenge-report.sh
   ./challenge-report.sh "$WORK_DIR/input" "$WORK_DIR/reports"
   report_rc=$?
   printf 'report exit=%s\n' "$report_rc"
   ```

2. Read the exact generated report path. Complete your interpretation using `nano` and review every copied file before sharing.
3. Test a missing input, an empty copied capture, and a path containing spaces. Keep original evidence intact and explain each result.

## Section: Submit your findings and verify cleanup

Submit your script, reviewed report/evidence bundle, original/revised workload copies, result checks, and test outcomes. Answer:

1. Which query has the highest observed duration, and what does its SQL actually do?
2. Did the first capture account for every submitted business query? Why or why not?
3. What changed in the second capture, and which connection received that change?
4. What does the plan suggest, and what does it not prove?
5. What should the team investigate or change next, and what remains uncertain?

The instructor restores exact logging settings, verifies any experimental index is removed, and retains the challenge dataset for repeat practice. Do not delete logs, drop the database, or clear counters as cleanup.
