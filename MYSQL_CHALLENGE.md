# MySQL Challenge: The Slow Ticket-Sales Batch

**Audience:** participants who completed [support diagnostics](MYSQL_SUPPORT_DIAGNOSTICS.md), [the diagnostics exercise](MYSQL_SUPPORT_DIAGNOSTICS_EXERCISE.md), [slow-query analysis](MYSQL_SLOW_QUERY_ANALYSIS.md), and [the slow-query exercise](MYSQL_SLOW_QUERY_ANALYSIS_EXERCISE.md).

**Time:** 60–90 minutes. **Required environment:** Bash, GNU coreutils, grep, and awk. No running database or Python programming is required. `mysqldumpslow` is optional for exploration.

## Section: Incident and evidence

A ticket-sales team reports that its batch takes several seconds. Someone proposes: “Find the longest query in the slow log and add an index to fix it.” Investigate that claim and write your own Bash script to produce a precisely formatted evidence file.

Use only the [supplied synthetic evidence](shared/fixtures/mysql-challenge). It represents two completed runs of the same business workload, with different capture settings. It is invented teaching data, not a capture from your host. Timing, counts, and plan estimates are fixed for grading; real servers can produce different values. Do not consult the instructor reference script or solution before submitting.

| File | Purpose |
|---|---|
| `provenance.txt` | Source label and capture assumptions |
| `original-workload.sql` | Original session setting, probe, and business queries |
| `capture-workload.sql` | Revised capture setting with the same queries |
| `baseline.log` | Complete original slow-log capture |
| `detail.log` | Complete fuller slow-log capture |
| `results.tsv` | Verified business results, identical for both completed runs |
| `plan-before.tsv` | Selected fields from a synthetic before-index EXPLAIN plan |

The tab-separated files have one header line and literal tab separators. Their cells contain no embedded tabs or newlines. Each SQL statement in the workload and logs occupies one line. The conventional slow-log timing headers contain query seconds, lock seconds, rows sent, and rows examined. These are deliberately bounded formats, not arbitrary SQL or log formats.

## Section: Prepare and investigate

From Bash on the host containing the repository:

```bash
read -r -p 'Absolute repository directory: ' COURSE_ROOT
cd "$COURSE_ROOT"
```

Stop if `cd` fails. Then create your workspace:

```bash
umask 077
mkdir -p "$HOME/support-lab"
WORK_DIR=$(mktemp -d "$HOME/support-lab/module2-XXXXXX")
cp -R "$COURSE_ROOT/shared/fixtures/mysql-challenge" "$WORK_DIR/input"
cd "$WORK_DIR"
cat input/provenance.txt
```

Inspect the evidence before writing the script:

```bash
tail -n 80 input/baseline.log
grep -n '^# Query_time:' input/detail.log
cat input/original-workload.sql input/capture-workload.sql
cat input/results.tsv input/plan-before.tsv
```

Use complete logs for totals. A tail can split a slow-query record, and its line limit is not a time interval. When available, compare `mysqldumpslow -s c`, `-s at`, and `-s t` against `input/detail.log`; calculate precise required seconds from raw headers, not rounded rankings.

Investigate these questions:

1. What does the longest recorded query actually do?
2. Does absence from the baseline log mean a business query did not execute?
3. Which connection's capture setting changed? Why does that matter?
4. How many rows does an aggregate return versus examine or count?
5. What could an event-ID index improve, and what delay can it not remove?

## Section: Required output contract

Create `module2-report.sh` with this interface:

```text
bash module2-report.sh INPUT_DIR
```

It must write **`module2-evidence.txt` in the current directory**, replacing its previous contents on a successful rerun. Submit both files. Do not manually edit the generated evidence.

The file must contain exactly 20 `KEY=value` lines in the order below. Replace descriptions with values; do not print headings, comments, blank lines, spaces around `=`, Markdown fences, or extra keys. Keys and text values are case-sensitive. Numeric values use nonnegative decimal notation without units, commas, signs, or exponents. Equivalent decimal precision is accepted. A final newline is recommended; LF and CRLF are accepted.

| Position | Key | Required value or derivation |
|---|---|---|
| 1 | `evidence_source` | Source label from `provenance.txt` |
| 2 | `submitted_report_calls` | Number of sales aggregate SELECT statements in the original workload; exclude the probe |
| 3 | `original_session_long_query_time` | Session threshold from the original workload, in seconds |
| 4 | `capture_session_long_query_time` | Session threshold from the revised workload, in seconds |
| 5 | `baseline_probe_calls` | Number of logged heartbeat probe statements in baseline |
| 6 | `baseline_report_calls` | Number of logged sales report statements in baseline |
| 7 | `detail_probe_calls` | Number of logged heartbeat probe statements in detail |
| 8 | `detail_report_calls` | Number of logged sales report statements in detail |
| 9 | `baseline_query_seconds` | Sum of every baseline `Query_time`, including the probe |
| 10 | `detail_query_seconds` | Sum of every detail `Query_time`, including the probe |
| 11 | `detail_lock_seconds` | Sum of every detail `Lock_time`, including the probe |
| 12 | `detail_report_rows_examined` | Sum of `Rows_examined` for detail sales reports only |
| 13 | `detail_report_rows_sent` | Sum of `Rows_sent` for detail sales reports only |
| 14 | `event_42_sales_count` | Event 42 sales count from `results.tsv` |
| 15 | `event_42_sales_total` | Event 42 total amount from `results.tsv` |
| 16 | `plan_before_access_type` | `type` from `plan-before.tsv` |
| 17 | `plan_before_key` | Chosen `key` from the plan; print `NONE` when the cell is `NULL` |
| 18 | `plan_before_estimated_rows` | Estimated `rows` from the plan, not a measured row count |
| 19 | `capture_cause` | Choose `SESSION_THRESHOLD`, `QUERY_NOT_EXECUTED`, or `INDEX_CHANGED` to explain the visibility change |
| 20 | `index_cannot_remove` | Choose `DELIBERATE_SLEEP`, `SELECTIVE_ROW_ACCESS`, or `NO_LIMITATION` for the proposed index's limitation |

Calculate measurements from the input files; do not hard-code them. Fixed key labels and the two conclusion codes may be literals. Use the Bash constructs and commands taught in the linked lessons, including arguments, variables, quoting, functions, conditionals, loops, `printf`, `cat`, `tail`, `grep`, `awk`, and redirection. No Python, Perl, jq, or new diagnostic tool is needed in the student solution.

Validate that all seven files are readable and nonempty before replacing an existing output. Report missing or empty evidence as an error on stderr and exit nonzero. A valid log with zero matching business statements is different from an empty log: handle grep exit 1 as zero matches, not a read error. Do not modify the input fixtures. Keep newly created output private with `umask 077`.

## Section: Run, verify, and submit

```bash
bash -n module2-report.sh
bash module2-report.sh "$WORK_DIR/input"
report_rc=$?
printf 'report exit=%s\n' "$report_rc"
cat module2-evidence.txt
```

Require exit 0 for a successful report. Check a repeat run, an input directory containing spaces, a missing file, and an empty copied log. Use separate copies for failure tests; retain original evidence. Failed input checks must preserve a previous successful report.

Submit `module2-report.sh` and `module2-evidence.txt`. The instructor grades the text using:

```bash
python3 ~/Desktop/module2_challenge_checker.py module2-evidence.txt
```

Each correct field earns 5 points, for 100 total. Missing, incorrect, or duplicated keys earn no credit for that field. Extra or malformed lines and wrong ordering fail format validation; they do not add points. Full acceptance requires 100/100 **and** format PASS. The checker reports field feedback and exits 0 for full acceptance, 1 for a grading failure, or 2 for a usage/read error. The instructor separately reviews your script to confirm it computes the evidence and uses the permitted commands; a correct text file alone cannot prove this.

## Section: Optional live investigation

Live work is separate from fixed-answer grading. With instructor supervision, use the existing [dataset setup](shared/sql/mysql/challenge-setup.sql), [workload](shared/sql/mysql/challenge-workload.sql), and [inspection SQL](shared/sql/mysql/challenge-inspect.sql), following the linked lessons' capture and restoration procedures. Keep real measurements in separate notes, never substitute them into the graded fixture output.

A global threshold does not override an explicit session setting in the workload. Plain EXPLAIN estimates access; it does not measure elapsed time. An index can help selective row access but adds write/storage cost. Do not infer CPU usage, production health, or demonstrated speedup from these fixtures. Have the instructor restore logging settings and remove only an index created for the experiment; do not delete logs or drop the dataset as routine cleanup.
