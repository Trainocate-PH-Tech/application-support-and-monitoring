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
