# MySQL Support Diagnostics Exercise: Log Investigation and Bash Reporting

Build a reusable Bash utility that reads MySQL error and slow-query logs, extracts evidence with `tail` and `grep`, and writes a report. Allow 60–90 minutes. Run all commands in **Bash**, not at the `mysql>` prompt.

This exercise follows [MySQL Support Diagnostics](MYSQL_SUPPORT_DIAGNOSTICS.md). The supplied logs use the `mysql_support_demo` database and order `1001` from that guide. They are **synthetic text fixtures**, not observations from your EC2 instance. No running MySQL server or database load is needed for the fixture exercises. The slow report deliberately includes an invented 1.5-second aggregation; six rows alone do not explain that duration.

**Deliverables:** your executable `mysql-log-report.sh`, a generated report directory containing two saved log windows and `report.txt`, and your completed interpretation. The [reference utility](shared/scripts/mysql-log-report.sh) is also provided.

## Section: Prepare your workspace and sample logs

1. In your EC2 or local Linux Bash terminal, enter the actual repository path:

   ```bash
   read -r -p 'Absolute repository directory: ' COURSE_ROOT
   cd "$COURSE_ROOT"
   ```

   Stop if `cd` fails. Use Ubuntu/GNU tools for these examples.

2. Create a private exercise workspace and copy the two fixtures:

   ```bash
   umask 077
   WORK_DIR="$HOME/support-lab/mysql-log-exercise"
   mkdir -p "$WORK_DIR/logs" "$WORK_DIR/reports"
   cp -n shared/fixtures/mysql-diagnostics-error.log "$WORK_DIR/logs/error.log"
   cp -n shared/fixtures/mysql-diagnostics-slow.log "$WORK_DIR/logs/slow.log"
   cd "$WORK_DIR"
   ls -l logs
   ```

   `cp -n` preserves existing practice copies on repeat runs. Expected sizes are eight error-log lines and eighteen slow-log lines. Keep originals unchanged; use separate files for experiments. If you start another shell, set `WORK_DIR` again and `cd` into it.

## Section: Select a bounded window with tail

1. Read the last five error-log lines:

   ```bash
   tail -n 5 logs/error.log
   ```

   Find the access-denied event, connection-limit event, and slow-log-path failure. The timestamps describe the fixture, not the current time.

2. Save a larger window from each file:

   ```bash
   tail -n 200 logs/error.log > error-window.log
   tail -n 200 logs/slow.log > slow-window.log
   wc -l error-window.log slow-window.log
   ```

   Expect 8 and 18 lines. Asking for 200 lines from a shorter file returns the whole file. `>` creates or replaces a file; `>>` appends. Neither redirects text back into the source logs here.

3. Compare `tail -n 5 slow-window.log` with the complete slow window. Notice that the five-line tail loses the last entry's `# Time:` line. Slow-query records span multiple lines; a line window is neither a complete-record parser nor a time interval.

4. Optional live-reading demonstration:

   ```bash
   tail -n 5 -f logs/error.log
   ```

   `-f` waits for appended lines; an unchanged fixture produces no new output. Press Ctrl-C to stop. The report script will use `tail -n`, without `-f`, so it can finish. For rotating live files, GNU `tail -F` follows the filename, but still runs continuously.

## Section: Find messages with grep

1. Display error and warning lines, ignoring case:

   ```bash
   grep -Ein '\[ERROR\]|\[Warning\]' error-window.log
   ```

   `-E` enables extended expressions, `|` means either pattern, `-i` ignores case, and `-n` prints line numbers. The escaped brackets match literal severity brackets. Expect four matching lines. These numbers refer to the saved window, not the full original file.

2. Search a specific message with surrounding context:

   ```bash
   grep -n -C 1 'Too many connections' error-window.log
   ```

   `-C 1` includes one surrounding line on each side. Context is evidence, not proof of a causal relationship.

3. Count matching lines and examine the command's exit status immediately:

   ```bash
   grep -Eic '\[ERROR\]' error-window.log
   printf 'grep exit=%s\n' "$?"
   grep -Eic 'deadlock' error-window.log
   printf 'grep exit=%s\n' "$?"
   ```

   Expect `2` with exit `0`, then `0` with exit `1`. For grep, exit `1` means no matches; exit `2` indicates an error, such as an unreadable input. Do not treat all nonzero results as the same condition.

4. Inspect slow-query timing lines and the sample order query:

   ```bash
   grep -nE '^# (Time:|Query_time:)' slow-window.log
   grep -n -B 5 'order_id = 1001' slow-window.log
   ```

   `^` anchors a pattern at the start of a line. `-B 5` adds preceding context suitable for these fixtures; real SQL can span more lines. There are three `Query_time` headers and two queries for order `1001`. The two `SLEEP()` calls intentionally manufacture delay.

5. Try a direct pipeline, then explain why the utility saves a snapshot first:

   ```bash
   tail -n 200 logs/error.log | grep -Ei '\[ERROR\]|\[Warning\]'
   ```

   A pipe sends one command's standard output to another. Repeating this pipeline against a changing file can produce different windows. Saving one window lets the report count and display the same evidence.

## Section: Build a report manually

1. Group commands and redirect their combined output:

   ```bash
   {
       printf 'MYSQL MANUAL LOG REPORT\n'
       date -u
       printf '\nError and warning evidence\n'
       grep -Ein '\[ERROR\]|\[Warning\]' error-window.log
       printf '\nSlow-query timings\n'
       grep -n '^# Query_time:' slow-window.log
   } > manual-report.txt
   cat manual-report.txt
   ```

2. Add three sentences using `nano manual-report.txt`: observed facts, one possible explanation, and one next read-only check. For example, the fixture contains a connection-limit message; check current connection counts against `max_connections` before concluding the limit is still exhausted.

3. Explain why the warning containing `Access denied` belongs to two categories. Adding category totals would double-count that line.

## Section: Turn the commands into a Bash utility

1. Confirm you are in your exercise workspace. Open an editor:

   ```bash
   nano mysql-log-report.sh
   ```

   If this file exists from an earlier attempt, preserve your work before replacing it. Paste the complete script below. Save with Ctrl-O, Enter; exit with Ctrl-X. The first line must be the shebang, with no Markdown fences in the file.

```bash
#!/usr/bin/env bash
# Inspect readable MySQL text logs; never change a service or database.
set -euo pipefail
umask 077

usage() {
    printf 'Usage: %s ERROR_LOG SLOW_LOG OUTPUT_PARENT [LINES=200]\n' "$0" >&2
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

if (( $# < 3 || $# > 4 )); then
    usage
    exit 2
fi

error_log=$1
slow_log=$2
output_parent=$3
lines=${4:-200}

[[ $lines =~ ^[1-9][0-9]{0,5}$ ]] || fail 'LINES must be an integer from 1 to 100000.'
(( lines <= 100000 )) || fail 'LINES must be an integer from 1 to 100000.'
for log in "$error_log" "$slow_log"; do
    [[ -f $log && -r $log ]] || fail "Not a readable regular file: $log"
done

mkdir -p -- "$output_parent" || fail 'Cannot create output parent.'
bundle=$(mktemp -d -- "$output_parent/mysql-report-XXXXXX") || fail 'Cannot create report directory.'
captured_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Save each window once so all counts and excerpts use the same input.
tail -n "$lines" -- "$error_log" > "$bundle/error-window.log" || fail 'Cannot read error log.'
tail -n "$lines" -- "$slow_log" > "$bundle/slow-window.log" || fail 'Cannot read slow log.'

# grep returns 1 for no matches; this is valid evidence, not a read failure.
count_matches() {
    local count rc
    if count=$(grep -Eic -- "$1" "$2"); then
        printf '%s' "$count"
    else
        rc=$?
        if (( rc == 1 )); then
            printf '0'
        else
            fail "grep failed while counting: $2"
        fi
    fi
}

show_matches() {
    local rc
    if grep -Ein -- "$1" "$2"; then
        :
    else
        rc=$?
        if (( rc == 1 )); then
            printf '(no matching lines in this window)\n'
        else
            fail "grep failed while reading: $2"
        fi
    fi
}

error_count=$(count_matches '\[ERROR\]' "$bundle/error-window.log")
warning_count=$(count_matches '\[Warning\]' "$bundle/error-window.log")
denied_count=$(count_matches 'Access denied' "$bundle/error-window.log")
capacity_count=$(count_matches 'Too many connections' "$bundle/error-window.log")
slow_count=$(count_matches '^# Query_time:' "$bundle/slow-window.log")

{
    printf 'MYSQL LOG DIAGNOSTIC REPORT\n'
    printf 'Captured UTC: %s\nHost running collector: %s\n' "$captured_utc" "$(hostname)"
    printf 'Error source: %s\nSlow source: %s\n' "$error_log" "$slow_log"
    printf 'Window: last %s lines of EACH file; not a time interval\n\n' "$lines"
    printf 'ERROR lines: %s\nWarning lines: %s\n' "$error_count" "$warning_count"
    printf 'Access denied lines: %s\nToo many connections lines: %s\n' "$denied_count" "$capacity_count"
    printf 'Slow-query timing headers: %s\n\n' "$slow_count"
    printf 'ERROR-LOG MATCHES (line numbers refer to saved window)\n'
    show_matches '\[ERROR\]|\[Warning\]|Access denied|Too many connections' "$bundle/error-window.log"
    printf '\nSLOW-LOG TIMING HEADERS (line numbers refer to saved window)\n'
    show_matches '^# (Time:|Query_time:)' "$bundle/slow-window.log"
    printf '\nINTERPRETATION TO COMPLETE\n'
    printf 'Observed facts: ...\nPossible explanation: ...\nNext read-only check: ...\n'
    printf '\nLIMITS\nCounts are matching lines, not unique incidents. Categories can overlap.\n'
    printf 'A tail window can split a multiline slow-query entry. Inspect the saved context.\n'
    printf 'Zero matches do not prove server health. Rotation and separate capture times can affect evidence.\n'
    printf 'This collector does not redact data. Review all files before sharing.\n'
} > "$bundle/report.txt"

printf 'Report: %s/report.txt\n' "$bundle"
```

2. Read the script in small pieces and explain them to a partner:

   | Construct | Purpose |
   |---|---|
   | `#!/usr/bin/env bash` | Selects Bash when executed directly. |
   | `set -euo pipefail` | Stops on many unhandled command failures, rejects unset variables, and propagates pipeline failures; expected grep failures are handled explicitly. |
   | `umask 077` | Makes newly created report files private to the account. |
   | `$#`, `$1`, `${4:-200}` | Argument count, first argument, and a default for the optional fourth argument. |
   | `"$variable"`, `--` | Keeps paths containing spaces together and ends option parsing for supporting commands. |
   | `[[ ... ]]` and `(( ... ))` | Validate files/text and numeric conditions. |
   | `$(...)` | Captures command output into a variable. |
   | Functions | Reuse validation, counting, and display logic. |
   | `mktemp -d` | Creates a unique directory so a new run does not overwrite an earlier report. |
   | `{ ...; } > file` | Writes a group of command outputs into one report. |

3. Explain the interface before running it:

   ```text
   mysql-log-report.sh ERROR_LOG SLOW_LOG OUTPUT_PARENT [LINES=200]
   ```

   Both logs must be readable regular files. The line limit applies separately to each file and must be 1–100000. Output contains `error-window.log`, `slow-window.log`, and `report.txt`. A successful collection exits `0` even when errors are found: this is a collector, not a health verdict. Invalid arguments or unreadable inputs exit `2`; other unhandled tool failures can also exit nonzero. Do not treat an incomplete directory from a failed run as a completed report.

## Section: Check syntax and execute the script

1. Check Bash syntax before executing:

   ```bash
   bash -n mysql-log-report.sh
   ```

   No output and exit `0` means syntax passed; it does not prove the logic is correct.

2. Run explicitly with Bash:

   ```bash
   bash mysql-log-report.sh logs/error.log logs/slow.log reports 200
   report_rc=$?
   printf 'collector exit=%s\n' "$report_rc"
   ```

   Expect exit `0` and a printed report path in a unique `reports/mysql-report-...` directory.

3. Make it executable and run directly:

   ```bash
   chmod u+x mysql-log-report.sh
   ./mysql-log-report.sh logs/error.log logs/slow.log reports 200
   ```

   `./` identifies the current directory; it is not normally searched as part of `PATH`. Do not use `sh mysql-log-report.sh`: this script uses Bash syntax. Each run produces a separate report directory.

4. Read the exact path printed by your run:

   ```bash
   read -r -p 'Printed report path (without Report: prefix): ' REPORT_FILE
   cat -- "$REPORT_FILE"
   ```

   Expected fixture counts:

   | Metric | Expected value |
   |---|---|
   | ERROR lines | 2 |
   | Warning lines | 2 |
   | Access denied lines | 1 |
   | Too many connections lines | 1 |
   | Slow-query timing headers | 3 |

5. Open `nano "$REPORT_FILE"` and complete the interpretation placeholders. Explicitly label these inputs synthetic. The collector's host and capture time describe your collection, not where or when the original events occurred.

## Section: Test missing data and invalid inputs

1. Create empty practice logs and collect them:

   ```bash
   touch logs/empty-error.log logs/empty-slow.log
   ./mysql-log-report.sh logs/empty-error.log logs/empty-slow.log reports 200
   ```

   Expect exit `0`, zero counts, and “no matching lines” messages. Empty inputs are not proof of healthy MySQL.

2. Try a nonexistent input, then an invalid line limit:

   ```bash
   ./mysql-log-report.sh logs/not-present.log logs/slow.log reports 200
   printf 'missing input exit=%s\n' "$?"
   ./mysql-log-report.sh logs/error.log logs/slow.log reports zero
   printf 'invalid limit exit=%s\n' "$?"
   ```

   Each should report an error and exit `2`. Do not change permissions on live logs to simulate an error.

3. Run with a five-line window and compare counts to the full fixture report. Explain why the smaller window loses earlier warnings and slow-query records; this is a scope change, not recovery of the database.

## Section: Use real MySQL logs when available

1. Follow the error-log discovery and slow-log inspection sections in [the diagnostics guide](MYSQL_SUPPORT_DIAGNOSTICS.md). Identify the actual `log_error`, `slow_query_log_file`, and `log_output` values. Do not assume a fixed path or enable slow logging simply to complete this exercise.

2. Have the administrator provide readable, bounded text-log exports in your private workspace if you lack file access. For a journal destination, an administrator can export an appropriate window with `journalctl -u mysql --since '15 minutes ago' --utc --no-pager`; journal prefixes may not match the bracketed severity patterns. Table-only slow logging, JSON error logs, and compressed rotations require a suitable export or another parser. This utility expects conventional MySQL text logs.

3. Run as your normal Linux user with the confirmed readable paths:

   ```bash
   read -r -p 'Readable error-log file or export: ' ERROR_LOG
   read -r -p 'Readable slow-log file or export: ' SLOW_LOG
   ./mysql-log-report.sh "$ERROR_LOG" "$SLOW_LOG" reports 200
   ```

4. Inspect the saved windows as well as the report. Last 200 lines does not mean last 15 minutes, and the two files are captured separately. A rotated file can omit the incident entirely. Counting `Query_time` headers is not ranking queries or measuring all workload; use `mysqldumpslow` as taught in the diagnostics guide when appropriate.

5. Review all three files for sensitive SQL, accounts, and host details before sharing. Keep private originals and share reviewed copies. The utility reads source logs and writes evidence only; it does not restart MySQL, change logging, or delete logs.

## Section: Submit and explain your findings

- Submit your script and a reviewed report bundle with both saved windows.
- Include the fixture counts and results of the empty-input and invalid-input checks.
- Explain `tail -n`, `grep -E`, `-i`, `-n`, `-c`, pipes, redirection, quoting, permissions, and exit codes.
- Complete the report with facts, uncertainty, and one next read-only check per suspected issue.
- Explain why slow fixture queries containing `SLEEP()` and historical error lines cannot establish a current production fault.

Optional extension: add a separate count for `Aborted connection`, then verify that the supplied fixture produces `1`. Keep it separate from warnings because the categories overlap.
