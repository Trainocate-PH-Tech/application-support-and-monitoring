# MySQL Challenge — Instructor Solution

Instructor-only material: withhold this solution, the reference script, and the checker answer key until submission. The required challenge now uses fixed synthetic fixtures; live investigation is optional and not graded by the fixed-answer checker.

## Section: Teaching intent and evidence

The original workload sets its own one-second session threshold. The baseline fixture records the intentional eight-second heartbeat sleep, but omits eight faster sales reports. The revised workload changes only that threshold to zero. The detail fixture records the same probe plus all eight reports, each taking 0.025 seconds. The verified business results are identical in both runs.

Absence from a slow log does not establish absence of execution. Changing only a global threshold would not override the workload's explicit session assignment. The detail capture improves visibility, not query performance.

The detail reports total 0.2 seconds and examine 800000 rows. The complete detail capture totals 8.2 seconds, so the probe remains the dominant elapsed cost. The eight aggregates return eight result rows; each represents 1000 sales totalling 25000.00. Do not confuse rows sent, sales counted, rows examined, and EXPLAIN estimates.

The synthetic before-index plan uses ALL with no chosen key and an estimate of 100000 rows. This supports investigating an event_id index for selective row access. It does not prove a speedup, a business latency breach, CPU usage, or a missing-index explanation for deliberate sleep. Indexes incur storage and write maintenance costs.

## Section: Prepare and run

Use the repository's `shared/fixtures/mysql-challenge` directory. The student-facing instructions describe each required field without exposing the completed answer. Students need Bash, coreutils, grep, and awk; no live server is needed. `mysqldumpslow` is optional and its rounded output is not used for exact totals.

From a private output workspace, run the reference script with absolute paths:

```bash
read -r -p 'Absolute repository directory: ' COURSE_ROOT
bash -n "$COURSE_ROOT/shared/scripts/mysql-challenge-report.sh"
bash "$COURSE_ROOT/shared/scripts/mysql-challenge-report.sh" "$COURSE_ROOT/shared/fixtures/mysql-challenge"
python3 ~/Desktop/module2_challenge_checker.py module2-evidence.txt
```

Expected output from the checker: Correct 20, Incorrect 0, Missing 0, Format PASS, Score 100/100, exit 0.

## Section: Expected evidence

```text
evidence_source=SYNTHETIC
submitted_report_calls=8
original_session_long_query_time=1
capture_session_long_query_time=0
baseline_probe_calls=1
baseline_report_calls=0
detail_probe_calls=1
detail_report_calls=8
baseline_query_seconds=8.000000
detail_query_seconds=8.200000
detail_lock_seconds=0.000000
detail_report_rows_examined=800000
detail_report_rows_sent=8
event_42_sales_count=1000
event_42_sales_total=25000.00
plan_before_access_type=ALL
plan_before_key=NONE
plan_before_estimated_rows=100000
capture_cause=SESSION_THRESHOLD
index_cannot_remove=DELIBERATE_SLEEP
```

Numeric precision may differ if the decimal value is identical. Text values are exact and case-sensitive. The output must use the documented order, with no extra lines. CRLF and an optional final newline are accepted.

## Section: Reference Bash solution

This reference recognizes only the supplied single-line query and TSV formats. It checks required inputs before opening the output, handles grep's zero-match exit status, and derives all measurements from files. The final two codes encode an instructor interpretation of this specific scenario; they are not a general diagnostic algorithm.

```bash
#!/usr/bin/env bash
# Instructor reference: fixed fixture format only; no database access.
set -euo pipefail
umask 077
export LC_ALL=C
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
[[ $# == 1 ]] || fail "Usage: $0 INPUT_DIR"
input=$1
for file in provenance.txt original-workload.sql capture-workload.sql baseline.log detail.log results.tsv plan-before.tsv; do
    [[ -f $input/$file && -r $input/$file && -s $input/$file ]] || fail "Missing, unreadable, or empty input: $file"
done
for file in baseline.log detail.log; do
    awk '/^# Query_time:/ {
        n++
        if (NF!=9 || $3 !~ /^[0-9]+([.][0-9]+)?$/ || $5 !~ /^[0-9]+([.][0-9]+)?$/ || $7 !~ /^[0-9]+$/ || $9 !~ /^[0-9]+$/) bad=1
    } END {if (!n || bad) exit 2}' "$input/$file" || fail "Invalid timing evidence: $file"
done
count_matches() {
    local count rc
    if count=$(grep -Ec -- "$1" "$2"); then
        printf '%s' "$count"
    else
        rc=$?
        if (( rc == 1 )); then printf '0'; else fail "Cannot read: $2"; fi
    fi
}
threshold() {
    awk '/^SET SESSION long_query_time = / {value=$5; sub(/;$/, "", value); print value}' "$1"
}
# Calculate before opening the output: missing inputs never truncate an old report.
report=$(
    set -e
    grep '^evidence_source=' "$input/provenance.txt"
    printf 'submitted_report_calls=%s\n' "$(count_matches '^SELECT COUNT.*FROM ticket_sales WHERE event_id=' "$input/original-workload.sql")"
    printf 'original_session_long_query_time=%s\n' "$(threshold "$input/original-workload.sql")"
    printf 'capture_session_long_query_time=%s\n' "$(threshold "$input/capture-workload.sql")"
    for capture in baseline detail; do
        printf '%s_probe_calls=%s\n' "$capture" "$(count_matches '^SELECT SLEEP[(]8[)] AS heartbeat_probe;' "$input/$capture.log")"
        printf '%s_report_calls=%s\n' "$capture" "$(count_matches '^SELECT COUNT.*FROM ticket_sales WHERE event_id=' "$input/$capture.log")"
    done
    for capture in baseline detail; do
        awk -v capture="$capture" '/^# Query_time:/ {seconds+=$3}
            END {printf "%s_query_seconds=%.6f\n",capture,seconds}' "$input/$capture.log"
    done
    awk '/^# Query_time:/ {locks+=$5}
        END {printf "detail_lock_seconds=%.6f\n",locks}' "$input/detail.log"
    # Associate each single-line report with its own preceding timing header.
    awk '
        /^# Time:/ {ready=0}
        /^# Query_time:/ {ready=1; sent=$7; examined=$9}
        ready && /^SELECT COUNT.*FROM ticket_sales WHERE event_id=/ {
            total_sent+=sent; total_examined+=examined; ready=0
        }
        END {printf "detail_report_rows_examined=%.0f\ndetail_report_rows_sent=%.0f\n", total_examined,total_sent}
    ' "$input/detail.log"
    awk -F '\t' '$1==42 {printf "event_42_sales_count=%s\nevent_42_sales_total=%s\n",$2,$3}' "$input/results.tsv"
    awk -F '\t' 'NR==2 {
        printf "plan_before_access_type=%s\nplan_before_key=%s\nplan_before_estimated_rows=%s\n",$2,($4=="NULL" ? "NONE" : $4),$5
    }' "$input/plan-before.tsv"
    # Human conclusions for this specific scenario; not an automated diagnosis.
    printf 'capture_cause=SESSION_THRESHOLD\nindex_cannot_remove=DELIBERATE_SLEEP\n'
)
printf '%s\n' "$report" > module2-evidence.txt
printf 'Report: module2-evidence.txt\n'
```

## Section: Grading and limitations

Award five points per correct required field. A duplicated key earns zero even if one occurrence is correct. Missing and incorrect fields earn zero. Unexpected keys, malformed/blank lines, and incorrect order fail format validation separately; they never earn points. A numeric score of 100 with extra lines still fails full acceptance. Exit codes are 0 for full acceptance, 1 for grading failure, and 2 for usage or reading failure.

The checker uses only Python's standard library and never runs the submitted script. Review the script separately for calculated rather than hard-coded measurements, allowed tooling, quoted paths, private output, and preservation of prior evidence on missing/empty-input errors. Require both the .sh and .txt submissions. Do not interpret a passing text file as proof of authorship or correct implementation.

Run `python3 tools/test_mysql_challenge.py` from the repository to exercise the reference output, grading failures, decimal equivalence, line endings, duplicate keys, input errors, and documentation. The checker and this solution are intentionally located beside the repository on the Desktop.

## Section: Optional live extension

The existing challenge SQL setup, workload, and inspection files remain unchanged. Use a dedicated training instance and follow MYSQL_SUPPORT_DIAGNOSTICS.md and MYSQL_SLOW_QUERY_ANALYSIS.md for administration, saved logging settings, fresh captures, bounded index experiments, and exact restoration. Confirm business results before comparing plans. Restore settings even after capture failure, and remove only an index created for the experiment.

Real baseline logs may include zero through eight business reports, and real times and plan estimates can differ. Keep those observations separate from the fixed-answer submission. Never change real evidence to match the synthetic answer key. No live server, restart, or database cleanup is part of the required grading workflow.
