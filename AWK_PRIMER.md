# awk primer for the assessment

This guide builds from printing a line to extracting fields, matching exact values,
and associating slow-log statements with their timing headers. Use it alongside
[ASSESSMENT.md](ASSESSMENT.md). Examples use small practice inputs so you can learn
the techniques before assembling your own `report-utility.sh`.

Run the examples in **Bash**. They use simple awk with no explicit `for`, `while`,
or `do` loops. awk automatically processes each input line. The assessment also
requires grep, tail, Bash, and MySQL; awk alone does not replace those requirements.

## 1. The basic form: pattern and action

```bash
awk 'pattern { action }' input-file
```

For each line, awk checks the pattern and runs the action when it matches.
Omit the pattern to run the action for every line. `$0` means the whole line.

```bash
awk '{print $0}' <<'EOF_INPUT'
alpha 10
beta 20
EOF_INPUT
```

Output:

```text
alpha 10
beta 20
```

`{print}` is shorthand for `{print $0}`. Keep the awk program in single quotes:
otherwise Bash may expand `$0`, `$1`, and other awk field references itself.

## 2. Print fields instead of whole lines

By default, awk splits each line on whitespace. Repeated spaces and tabs act as
separators. `$1` is the first field, `$2` the second, and `$NF` the last.
`NF` is the number of fields; `NR` is the input line number.

```bash
awk '{print NR, $1, $2, NF}' <<'EOF_INPUT'
alpha 10
beta 20
EOF_INPUT
```

Output:

```text
1 alpha 10 2
2 beta 20 2
```

Commas in `print` separate output values with a space by default.

**Quotes inside input do not group fields.** In the assessment application logs,
`message="statement timeout"` occupies two whitespace-separated fields. The fields
before the message still have fixed positions:

| Application field | awk reference |
|---|---|
| Timestamp | `$1` |
| Level | `$3` |
| Environment | `$4` |
| Service | `$5` |
| Host | `$6` |
| Path | `$7` |
| Status | `$8` |
| Duration | `$9` |
| Client | `$10` |
| Request | `$11` |
| Code | `$12` |

Splitting into fields does **not** validate the original spacing or complete record
format. Validate the original application line before extracting from it.

## 3. Read a file into a Bash variable, then feed awk

For assessment work, load each of the five files using its own direct `cat`
command substitution before processing it. From the repository root, for example:

```bash
LOG_DIR='shared/fixtures/okada-assessment'
older=$(cat "$LOG_DIR/application.log.1")
newer=$(cat "$LOG_DIR/application.log")
payments=$(cat "$LOG_DIR/payments.log")
baseline_slow=$(cat "$LOG_DIR/baseline-slow.log")
detail_slow=$(cat "$LOG_DIR/detail-slow.log")

awk '{print $11}' <<< "$older"
```

`$(...)` captures command output. `<<< "$older"` is a Bash here-string: it sends
the variable's contents to standard input. Quote variables to preserve spaces and
line breaks. In the final script, assign `LOG_DIR` from `"$1"` instead.

Preserve the specified rotation order with a literal newline between variables:

```bash
applications="$older
$newer"
```

Command substitution removes trailing newlines; the newline between these two
variables keeps their adjoining records separate. Do not rely on glob order.

## 4. Select lines using a condition

An exact comparison uses `==`; assignment uses `=`.

```bash
awk '$2 == "ERROR" {print $1}' <<'EOF_INPUT'
req-0101 INFO
req-0102 ERROR
req-01020 ERROR
EOF_INPUT
```

Output:

```text
req-0102
req-01020
```

Combine conditions with `&&` (and) or `||` (or):

```bash
awk '$1 == "req-0102" && $2 == "ERROR" {print $0}' <<'EOF_INPUT'
req-0102 ERROR
req-01020 ERROR
req-0102 INFO
EOF_INPUT
```

Only `req-0102 ERROR` is printed. Exact field comparisons avoid accidentally
matching a longer identifier.

## 5. Match regular expressions

`/expression/` searches the whole line. `$2 ~ /expression/` searches one field.
`!~` means the field must not match. `^` anchors the start and `$` the end.

```bash
awk '$1 ~ /^req-[0-9]{4}$/ {print $1}' <<'EOF_INPUT'
req-0102 ERROR
req-01020 ERROR
prefix-req-0102 ERROR
EOF_INPUT
```

On the course GNU awk environment, this prints only `req-0102`.

Useful extended regular expression building blocks for Question 1:

| Expression | Meaning |
|---|---|
| `(WARN|ERROR)` | Either exact alternative, when bounded by surrounding fields |
| `[^ ]+` | One or more non-space characters |
| `5[0-9]{2}` | Three-digit 5xx status |
| `203\.0\.113\.8` | Literal client address; unescaped dots mean any character |
| `([2-9][0-9]{3}|[1-9][0-9]{4,})` | Integer at least 2,000, with no leading zeroes |
| `2026-10-21T10:1[5-9]:[0-5][0-9]Z` | The assessment's inclusive UTC time interval |

These are fragments, not complete record validators. For Question 1, assemble
**one anchored extended regular expression** covering every field in order,
single spaces, and the complete quoted message. Use `grep -E` on the original
records. A field-based awk numeric check would accept some malformed records and
does not satisfy that question's requirement. Treat code and message alternatives
independently; do not restrict them to paired combinations.

## 6. Strip a prefix with `sub`

`sub(regex, replacement, target)` replaces the first matching part of the target.
An anchored prefix only matches at the start.

```bash
awk '{sub(/^request=/, "", $2); print $2}' <<'EOF_INPUT'
INFO request=req-0102
EOF_INPUT
```

Output: `req-0102`.

Once you have selected a complete qualifying application record:

```bash
latest_incident_request=$(awk '{sub(/^request=/, "", $11); print $11}' <<< "$selected_record")
```

Changing a field can cause awk to rebuild `$0` with normalized separators. Use
prefix removal for extraction **after** validating the original record.

## 7. Pass Bash values into awk with `-v`

Do not splice shell variables into awk source code. Pass their values with `-v`:

```bash
wanted_request='req-0102'
awk -v wanted="$wanted_request" '$1 == "request=" wanted {print $2}' <<'EOF_INPUT'
request=req-0102 player_id=73
request=req-01020 player_id=99
EOF_INPUT
```

Output: `player_id=73`. In awk, `"request=" wanted` concatenates two strings.

Payment fields differ from application fields: request is `$6`, player is `$7`,
event is `$8`, and outcome is `$9`. This extraction illustrates Question 3 on
the supplied payment format:

```bash
affected_player_id=$(awk -v wanted="$latest_incident_request" '
  NF == 10 && $4 == "env=prod" && $5 == "service=casino-payments" &&
  $6 == "request=" wanted && $7 ~ /^player_id=[1-9][0-9]*$/ &&
  $8 == "event=CONTEXT" && $9 == "outcome=ACCEPTED" {
    sub(/^player_id=/, "", $7)
    print $7
  }
' <<< "$payments")
```

The assessment guarantees one qualifying context row. For Question 4, pass both
the request and discovered player with `-v`, compare their full fields, and count
only production `casino-payments` rows with `event=QUERY` and `outcome=FAILED`.
Do not reuse the application field positions or count the context row.

## 8. Count and sum with `END`

Variables begin with an empty/zero value. `count++` adds one. `total += $2` adds
the second field to a running total. `END` runs once after all input is read.

```bash
awk '$1 == "FAILED" {count++; total += $2}
     END {print count+0, total+0}' <<'EOF_INPUT'
FAILED 12
OK 99
FAILED 8
EOF_INPUT
```

Output: `2 20`. The `+0` ensures that no matches produce numeric `0`, not an
empty string. Without `END`, printing inside the action would emit intermediate
values for each matching line.

For grep counts in the assessment, use:

```bash
count=$(grep -Ec '^FAILED [0-9]+$' <<< "$text" | cat)
```

Here `text` must already contain successfully loaded input. `grep -Ec` prints
zero but returns status 1 for no matches. The final `cat` permits a valid zero
under `set -e`. Follow the assessment's instruction **not to enable `pipefail`**;
check regex syntax during development and investigate stderr because this pipeline
also hides grep failures.

## 9. Put `tail` on the correct side of filtering

After constructing your complete Question 1 regex in `incident_regex`:

```bash
# Question 2: last matching original record.
selected_record=$(grep -E "$incident_regex" <<< "$applications" | tail -n 1)

# Question 5: matches within the last 200 original records.
recent_incident_count=$(tail -n 200 <<< "$applications" |
  grep -Ec "$incident_regex" | cat)
```

Filtering before `tail -n 200` would select the last 200 *matches*, a different
population. A line window is also different from a time interval. Retain the UTC
time condition inside the regex even when processing the recent-line window.

## 10. Parse MySQL columns using literal tabs

With the assessment's `--batch --raw --skip-column-names` options, use `-F '\t'`
to make the field separator a tab. Do not split SQL output on general whitespace.

This practice result uses Bash `$'...'` to create an actual tab:

```bash
result=$'7\t12345.60'
count=$(awk -F '\t' '{print $1}' <<< "$result")
amount=$(awk -F '\t' '{print $2}' <<< "$result")
```

`count` is `7`; `amount` is `12345.60`. Extracting the DECIMAL text directly
preserves its fractional digits. For general practice, formatting works like this:

```bash
awk 'BEGIN {printf "%.2f\n", 12.5}'
```

Output: `12.50`. `BEGIN` runs before reading input; `printf` needs an explicit
`\n` for a newline. For the assessment's money comparison, use the supplied
MySQL numeric comparison instead of converting decimal amounts to awk floating
point numbers.

For traditional EXPLAIN, select the `transactions` row before extracting:

```bash
access=$(awk -F '\t' '$3 == "transactions" {print $5}' <<< "$plan")
estimated_rows=$(awk -F '\t' '$3 == "transactions" {print $10}' <<< "$plan")
selected_index=$(awk -F '\t' '$3 == "transactions" {print $7}' <<< "$plan")
```

| Column | Meaning |
|---|---|
| `$3` | Table |
| `$5` | Access type |
| `$6` | Possible indexes |
| `$7` | Chosen index (`key`) |
| `$10` | Estimated rows |

`NULL` still occupies a column. Preserve it when extracting the chosen index.
Estimated rows are neither the aggregate's actual transaction count nor slow-log
rows examined. Capture separate before/after results at the stages specified in
the assessment; do not assume the server will choose a particular plan.

## 11. Remember state across slow-log lines

A slow-log entry spans multiple lines. The timing header provides `Rows_examined`,
but the following SQL line tells you whether the value belongs in your total.
An awk variable can remember the header while intervening lines are read.

```bash
practice_slow=$(cat <<'EOF_INPUT'
# Time: 2026-10-21T10:19:00Z
# Query_time: 0.400000  Lock_time: 0.000010 Rows_sent: 1  Rows_examined: 120
SET timestamp=1792577940;
SELECT /* loyalty_statement */ COUNT(*) FROM transactions;
# Time: 2026-10-21T10:19:01Z
# Query_time: 0.200000  Lock_time: 0.000010 Rows_sent: 1  Rows_examined: 900
SELECT COUNT(*) FROM players;
# Time: 2026-10-21T10:19:02Z
# Query_time: 0.500000  Lock_time: 0.000010 Rows_sent: 1  Rows_examined: 80
SELECT /* loyalty_statement */ COUNT(*) FROM transactions;
EOF_INPUT
)

awk '
  /^# Time:/ {examined = 0}
  /^# Query_time:/ {examined = $9}
  /^SELECT \/\* loyalty_statement \*\// {calls++; total += examined}
  END {print calls+0, total+0}
' <<< "$practice_slow"
```

Output: `2 200`.

Each rule is checked for each input line, in order. At `# Time:`, reset the record
state. At the timing header, save field 9. At a business SELECT, add the saved
value. The `SET timestamp` line does not erase it. The player-count query's 900
examined rows are excluded.

The regex escapes `/` because it delimits awk regex literals, and `*` because it
is a regex operator. Anchoring at `SELECT` avoids counting the marker in arbitrary
text. This matcher fits the supplied single-line SQL fixtures; it is not a general
SQL parser. For Questions 6–7, count just these statement lines. For Question 8,
print just `total+0` from the detail capture. Do not sum all timing headers.

A zero business-statement count in the baseline capture means zero captured
statements, not proof that the workload did not execute. The two fixed captures
use different thresholds; they do not measure your live index improvement.

## 12. Assemble your assessment solution

| Questions | Techniques to apply |
|---|---|
| 1 | Complete anchored ERE, chronological input, zero-safe count |
| 2 | Same ERE, then `tail -n 1`, then `$11` prefix removal |
| 3–4 | Exact payment field comparisons, `-v`, prefix removal and counting |
| 5 | `tail -n 200` before filtering |
| 6–7 | Count marked business SELECT lines, including a valid zero |
| 8 | Save header state, add only for the marked statement, print at `END` |
| 9–10 | Capture the live aggregate and extract its tab-separated columns |
| 11–14 | Capture each live EXPLAIN and extract the table row's columns |
| 15 | Capture the aggregate again and execute the supplied numeric comparison SQL |

Practice log extraction first. The database sequence must remain: supplied index
reset, baseline aggregate and EXPLAIN, supplied CREATE INDEX, after-index
aggregate and EXPLAIN, then the supplied comparison. Run the full sequence only
during your instructor-assigned exclusive slot. Pass the protected connection
file as the first MySQL option, as shown in the assessment.

Calculate every value before the final output here-document. Then write exactly
the 15 required `KEY=value` lines to `evidence.txt`. Keep exploratory output out of
that file. Validate your finished script with `bash -n report-utility.sh` before
running it; syntax validation does not execute the script or verify its answers.

To check your understanding, change the practice request to a longer near-match,
remove all matching rows from a counting example, and change the unrelated
player-count header's rows examined. Exact correlation should reject the
near-match, an empty match set should produce zero, and unrelated slow-log rows
should not affect the business total.
