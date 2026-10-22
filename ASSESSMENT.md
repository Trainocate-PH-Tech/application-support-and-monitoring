# Okada Application Support and MySQL Performance Assessment

## Objectives

Demonstrate the ability to investigate a casino loyalty-statement incident by correlating application and payment logs, distinguishing slow-log visibility from query execution, and correcting inefficient database access. Produce reproducible evidence through a single Bash script without loops.

On completion, candidates must be able to:

- Match complete records while rejecting malformed and near-matching entries.
- Correlate exact request identifiers across files and distinguish a line window from a time interval.
- Capture MySQL results in shell variables and distinguish actual counts from EXPLAIN estimates.
- Reset a specified index, collect a baseline, create the supplied index, and verify the selected access path and unchanged business results.

**Scenario:** The casino's loyalty-statement service reports timeouts. Support must identify the most recent qualifying incident, locate the associated player, and investigate that player's settled buy-in transactions for the specified reporting period. PHP amounts are transaction values, not net casino revenue or player profit.

## Expected Output

Submit `report-utility.sh` and the `evidence.txt` it generates. Leave both files in your respective directories in the sandbox EC2 server.

### Environment and supplied materials

Use Bash, GNU grep, tail, awk, cat, and the MySQL client on the course EC2 host. The instructor imports [okada_assessment.sql](okada_assessment.sql) once, without `--force`, into the new `okada_assessment` database. It contains 10,000 players, 200 terminals, and 1,000,000 transactions. Only primary keys exist initially. Related ID columns deliberately have neither secondary indexes nor enforced foreign-key constraints: MySQL otherwise creates supporting foreign-key indexes automatically. See the [MySQL reference](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html).

The instructor supplies a protected, absolute-path MySQL client configuration file containing the connection credentials. Do not embed a password in the script or evidence. Pass the file using `--defaults-extra-file` as the first MySQL option. The existing training `developer` account has the needed privileges; do not change accounts or server configuration.

Use the five log files in [shared/fixtures/okada-assessment](shared/fixtures/okada-assessment/):

| File | Purpose |
|---|---|
| `application.log.1` | Older 360 application lines |
| `application.log` | Newer 360 application lines |
| `payments.log` | Request-to-player context and payment-service query outcomes |
| `baseline-slow.log` | Original synthetic capture, session `long_query_time=1.0` |
| `detail-slow.log` | Fuller synthetic capture, session `long_query_time=0.1` |

Read the older application file **before** the newer one. Together they form one chronological 720-line stream. Do not use glob order or alphabetical sorting. All timestamps, including database `created_at`, are **UTC**; do not convert them to Philippine time for filtering. Use complete logs unless a question explicitly specifies a line window. The logs are fixed evidence, not captures from the live database used in your attempt.

Eligible application records have exactly this field order, single spaces, and no embedded quotes in the final message:

```text
TIMESTAMP id=ID level=LEVEL env=ENV service=SERVICE host=HOST path=PATH status=STATUS duration_ms=DURATION client=CLIENT request=REQUEST code=CODE message="MESSAGE"
```

Payment records use:

```text
TIMESTAMP id=ID level=LEVEL env=ENV service=SERVICE request=REQUEST player_id=PLAYER event=EVENT outcome=OUTCOME code=CODE
```

Treat JSON, pipe-separated entries, and malformed application records as ineligible. Valid application durations are nonnegative integers without leading zeroes. The qualifying request used for correlation has the form `req-` followed by four digits; it is safe to interpolate as literal ERE text. Player IDs are positive decimal integers. The supplied payment log has exactly one production `CONTEXT` / `ACCEPTED` row for the qualifying request.

### Example: using `--defaults-extra-file`

On EC2, the instructor can create the following connection file using the supplied training credentials. These are one-time setup commands, outside `report-utility.sh`; `umask` and `chmod` are not additions to the permitted report-processing commands.

```bash
MYSQL_DEFAULTS_FILE="$HOME/okada-client.cnf"
umask 077
cat > "$MYSQL_DEFAULTS_FILE" <<'EOF'
[client]
user=developer
password=password
host=localhost
EOF
chmod 600 "$MYSQL_DEFAULTS_FILE"
```

`[client]` identifies settings read by the MySQL client. `$HOME` expands to an absolute path (for example, `/home/ubuntu/okada-client.cnf`). Keep the password in this file rather than in your report script. If the instructor has already supplied a file, assign its absolute path to `MYSQL_DEFAULTS_FILE` instead of recreating it.

Test the connection with a read-only query:

```bash
mysql --defaults-extra-file="$MYSQL_DEFAULTS_FILE" \
  --batch --raw --skip-column-names \
  --database=okada_assessment \
  --execute='SELECT CURRENT_USER(), DATABASE();'
```

The result should identify `developer@localhost` and `okada_assessment`, separated by a tab. Put `--defaults-extra-file` immediately after `mysql`, before the other options. MySQL reads the connection settings from the file, so no `-p` option or password prompt is needed.

During your assigned execution slot, run your script from your submission directory, passing the same file as its second argument:

```bash
LOG_DIR="/home/ubuntu/okada-assessment-validation/input"
bash report-utility.sh "$LOG_DIR" "$MYSQL_DEFAULTS_FILE"
```

The log directory above is the validated EC2 fixture location; use the instructor's replacement path if the files have been moved. Inside the script, `MYSQL_DEFAULTS_FILE` is assigned from `$2`, then passed to each `mysql` invocation as shown above.

### Script contract

```bash
bash report-utility.sh LOG_DIR MYSQL_DEFAULTS_FILE
```

Both arguments may contain spaces and must be quoted wherever used. Run from your own submission directory. Write `evidence.txt` there, replacing its contents on a successful full run. The script must calculate all values; fixed output labels and the incident criteria may be literal strings.

Use only these processing commands: **`cat`, `grep` (including `-E` and `-Ec`), `tail`, simple `awk`, and `mysql`**. Bash assignments, quoted variable expansion, command substitution, pipes, here-strings, here-documents, and redirection are permitted.

Read each input into a variable with a direct `cat` command substitution before processing. Derive every value before the final output here-document so ordinary read/database failures preserve previous evidence.

`grep -Ec` prints `0` but exits with status 1 when no lines match. For a valid zero count, use `grep -Ec ... | cat` in command substitution. Do **not** enable `pipefail` for this exercise: the final `cat` intentionally makes a no-match count usable with `set -e`. Since this also hides upstream grep errors, check regex syntax during development and use only successfully loaded fixture variables. Investigate any stderr output; a zero count is not proof that a command was valid.

**Shared-database rule:** Develop and test log extraction first. Run the complete script only when the instructor assigns your exclusive execution slot. Every complete run must drop the named assessment index if present and recreate it later. Concurrent attempts would invalidate one another's baselines. A run has no interactive pause: be ready for the entire reset/query/index sequence before launching it. Do not drop tables, reload the dump, or modify transaction data. After an interrupted run, the instructor confirms that no other attempt is active before authorizing your next full run.

The final file must contain exactly these 15 keys in this order, one `KEY=value` per line, with no headings, blank lines, spaces around `=`, or additional output:

```text
incident_error_count=<integer>
latest_incident_request=<request identifier>
affected_player_id=<integer>
matching_payment_failures=<integer>
recent_incident_count=<integer>
baseline_report_calls=<integer>
detail_report_calls=<integer>
detail_report_rows_examined=<integer>
player_transaction_count=<integer>
player_transaction_total_php=<decimal with two fractional digits>
before_access_type=<MySQL access type>
before_estimated_rows=<integer>
after_access_type=<MySQL access type>
after_selected_index=<index name or NULL>
result_unchanged=<YES or NO>
```

### Supplied SQL and extraction examples

Use this reset **before** collecting live baseline results. It only drops the named index when present; SQL conditional logic is supplied and does not violate the Bash restriction. Run it in one MySQL session, redirecting its normal output away from `evidence.txt`.

```sql
SET @assessment_reset = IF(
 (SELECT COUNT(*) FROM information_schema.statistics
  WHERE table_schema='okada_assessment' AND table_name='transactions'
    AND index_name='idx_transactions_player_created') > 0,
 'DROP INDEX idx_transactions_player_created ON okada_assessment.transactions',
 'DO 0');
PREPARE assessment_reset FROM @assessment_reset;
EXECUTE assessment_reset;
DEALLOCATE PREPARE assessment_reset;
```

Assign the player ID discovered in Question 3 to `affected_player_id`, then use the following supplied query. Capture its result before and after index creation. Do not substitute a hard-coded player ID.

```bash
query="SELECT COUNT(*) AS transaction_count, COALESCE(SUM(amount_php),0.00) AS total_php FROM transactions WHERE player_id=${affected_player_id} AND created_at >= '2026-10-15 00:00:00' AND created_at < '2026-10-22 00:00:00' AND transaction_type='BUY_IN' AND status='SETTLED';"
result=$(mysql --defaults-extra-file="$MYSQL_DEFAULTS_FILE" --batch --raw --skip-column-names --database=okada_assessment --execute="$query")
plan=$(mysql --defaults-extra-file="$MYSQL_DEFAULTS_FILE" --batch --raw --skip-column-names --database=okada_assessment --execute="EXPLAIN FORMAT=TRADITIONAL $query")
```

After capturing the baseline, execute exactly:

```sql
CREATE INDEX idx_transactions_player_created
ON transactions (player_id, created_at);
```

Run the same query and EXPLAIN again. Do not force an index. To calculate the final comparison, extract numeric values into `before_count`, `after_count`, `before_total`, and `after_total`, then execute the supplied SQL through MySQL:

```bash
comparison_sql="SELECT IF(${before_count}=${after_count} AND ${before_total}=${after_total}, 'YES', 'NO');"
```

Simple awk examples are provided below. They illustrate extraction, not the complete solution. Here-strings supply a variable as command input; `sub` replaces a matching prefix; `$1`, `$2`, and so on identify fields.

```bash
# Read an input safely before filtering it.
older=$(cat "$LOG_DIR/application.log.1")
# Extract the request value from an already selected application record.
request=$(awk '{sub(/^request=/,"",$11); print $11}' <<< "$selected_record")
# Read columns of a headerless tab-separated aggregate result.
count=$(awk -F '\t' '{print $1}' <<< "$result")
amount=$(awk -F '\t' '{print $2}' <<< "$result")
# Select the table row in traditional EXPLAIN output.
access=$(awk -F '\t' '$3=="transactions" {print $5}' <<< "$plan")
# Add numeric fields without an explicit loop.
seconds=$(awk '/^# Query_time:/ {total+=$3} END {printf "%.6f\n",total+0}' <<< "$slow_log")
# Count zero or more matches in successfully loaded input.
count=$(grep -Ec '^EXAMPLE$' <<< "$text" | cat)
```

With the supplied MySQL options, traditional EXPLAIN columns are: `id`, `select_type`, `table`, `partitions`, `type`, `possible_keys`, `key`, `key_len`, `ref`, `rows`, `filtered`, `Extra`. Use literal-tab parsing; NULL fields still occupy columns. `rows` is an optimizer estimate, not a measured count. `possible_keys` is not the chosen `key`.

A slow-log timing header has this bounded format:

```text
# Query_time: 0.410000  Lock_time: 0.000010 Rows_sent: 1  Rows_examined: 1000000
```

Its ninth whitespace-separated field is rows examined. Remember that field in an awk variable, then add it only when the following SQL statement is a relevant business report. Reset record state at `# Time:`. There are no multiline SQL statements in these fixtures.

A final `cat > evidence.txt <<EOF` here-document can expand your 15 computed variables into the required format. Keep SQL diagnostics and exploratory output out of that file. Validate syntax with `bash -n report-utility.sh`, then run the complete script during your slot and inspect the generated evidence with `cat`.

## Questions

1. **Determine the incident population — `incident_error_count`.** Across both application rotations, count original records satisfying every condition below using one anchored extended regular expression: timestamp from **2026-10-21 10:15:00 through 10:19:59 UTC**, inclusive; level exactly `WARN` or `ERROR`; environment `prod`; service `casino-report`; host `app-01` or `app-02`; path `/loyalty/statement`; valid three-digit 5xx status; duration at least 2,000 ms, including values above 9,999; client exactly `203.0.113.8`; code `DB_TIMEOUT` or `DB_SCAN`; and message exactly `statement timeout` or `scan limit exceeded`. Either allowed code may occur with either allowed message. Match the entire record. Accept any nonempty ID and request token without spaces; do not select particular IDs.

2. **Identify the latest qualifying request — `latest_incident_request`.** Reuse the complete Question 1 criteria, process the rotations in the stipulated order, and use `tail` to select the last qualifying original line. Extract only its request value. Do not take the last line before applying the criteria.

3. **Resolve the player identity — `affected_player_id`.** In `payments.log`, locate the production `casino-payments` record whose request exactly equals Question 2, whose event is `CONTEXT`, and whose outcome is `ACCEPTED`. Extract its numeric `player_id`. Reject longer request values and records from other environments. Use this result in subsequent live SQL.

4. **Correlate failed query attempts — `matching_payment_failures`.** Count production `casino-payments` records matching both the exact request and player from Questions 2–3, with event `QUERY` and outcome `FAILED`. Count records, not unique requests; exclude the context record, successful outcomes, and near-matches.

5. **Apply a bounded recent-line window — `recent_incident_count`.** Concatenate the application rotations in chronological order, take the last **200 original lines**, and only then apply all Question 1 criteria. Report the number of matching lines in this window. Taking the last 200 matching lines answers a different question.

6. **Measure original capture visibility — `baseline_report_calls`.** Count the business SELECT statements in `baseline-slow.log` marked `/* loyalty_statement */`. Count statement lines, not timing headers or occurrences in arbitrary text. A valid zero count must not terminate your script. Both captures represent the same submitted workload; absence from the original capture does not establish nonexecution.

7. **Measure fuller capture visibility — `detail_report_calls`.** Count the corresponding business SELECT statements in `detail-slow.log`, excluding the heartbeat probe and player-count query. The different session threshold explains the visibility difference; these fixed logs do not demonstrate an index improvement.

8. **Quantify examined rows — `detail_report_rows_examined`.** Add `Rows_examined` only for detail-capture records belonging to the business SELECTs counted in Question 7. Associate each statement with its preceding timing header. Do not sum every header or confuse rows examined with rows sent.

9. **Retrieve the live business count — `player_transaction_count`.** After running the supplied index reset, execute the supplied query using the correlated player. Report the count of settled buy-ins from October 15 inclusive to October 22 exclusive. This value must come from MySQL, not a fixture or EXPLAIN.

10. **Retrieve the live business amount — `player_transaction_total_php`.** Extract the amount from the same pre-index aggregate result used in Question 9. Preserve two decimal places and omit a currency symbol, grouping separators, and units.

11. **Identify baseline access — `before_access_type`.** Before creating the index, execute the supplied traditional EXPLAIN and extract the `transactions` row's `type`. Capture the actual server result; do not print a presumed access type.

12. **Record the baseline estimate — `before_estimated_rows`.** From that same pre-index EXPLAIN result, extract `rows`. Do not substitute the table row count or the synthetic slow-log rows examined. Optimizer estimates can vary between servers and runs.

13. **Apply remediation and inspect access — `after_access_type`.** Execute the supplied CREATE INDEX from within your script, then execute the same EXPLAIN again and report `type`. This must happen after Questions 9–12 have captured the baseline. A script that merely prints an expected answer does not satisfy the requirement.

14. **Verify index selection — `after_selected_index`.** From the same after-index EXPLAIN, extract the chosen `key`, not `possible_keys`. Preserve `NULL` if the optimizer selects no index, and report that outcome to the instructor rather than fabricating success.

15. **Verify business-result preservation — `result_unchanged`.** Run the identical aggregate again after indexing. Use the supplied numeric comparison SQL to compare both the pre/post count and the pre/post amount. Output `YES` only when both agree, otherwise `NO`. Index creation should improve selective access without changing business results. Neither EXPLAIN nor the fixed log timings prove a measured runtime speedup, and this index cannot remove a deliberate `SLEEP` delay.
