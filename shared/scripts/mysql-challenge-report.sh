#!/usr/bin/env bash
# Instructor reference solution: offline evidence only.
set -euo pipefail
umask 077
export LC_ALL=C
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
[[ $# == 2 ]] || fail "Usage: $0 INPUT_DIR OUTPUT_PARENT"
input=$1
parent=$2
files=(provenance.txt baseline.log detail.log original-workload.sql capture-workload.sql plan-before.txt)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail 'Cannot create output parent.'
bundle=$(mktemp -d -- "$parent/mysql-challenge-XXXXXX") || fail 'Cannot create report directory.'
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
if [[ -f $input/plan-after.txt ]]; then
    cp -- "$input/plan-after.txt" "$bundle/plan-after.txt"
fi
for file in baseline.log detail.log; do
    awk '/^# Query_time:/ {
        if(NF!=9 || $3 !~ /^[0-9]+([.][0-9]+)?$/ || $5 !~ /^[0-9]+([.][0-9]+)?$/ || $7 !~ /^[0-9]+$/ || $9 !~ /^[0-9]+$/) exit 2
    }' "$bundle/$file" || fail "Malformed timing header: $file"
done
summarize() {
    local file=$1
    # Match the single-line query forms in THIS supplied workload only.
    awk '
    /^# Time:/ {ready=0}
    /^# Query_time:/ {ready=1; q=$3; lock=$5; rows=$9; headers++; total+=q}
    ready && /^SELECT SLEEP[(]8[)] AS heartbeat_probe;/ {
        probes++; probe_time+=q; probe_rows+=rows; ready=0
    }
    ready && /^SELECT COUNT.*SUM.*FROM ticket_sales WHERE event_id=/ {
        calls++; call_time+=q; examined+=rows; lock_time+=lock; ready=0
    }
    END {
        printf "timing_headers=%d total_logged_seconds=%.6f\n",headers,total
        printf "captured_report_calls=%d report_seconds=%.6f report_rows_examined=%.0f report_lock_seconds=%.6f\n",calls,call_time,examined,lock_time
        printf "captured_probe_calls=%d probe_seconds=%.6f probe_rows_examined=%.0f\n",probes,probe_time,probe_rows
        if(!headers) print "UNKNOWN: no timing evidence; verify capture before interpreting zero counts"
        if(calls!=8 || probes!=1) print "INCOMPLETE_OR_MIXED: expected one probe and eight reports for one full run"
    }' "$file"
}
{
    printf 'MYSQL CHALLENGE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"
    for file in original-workload.sql capture-workload.sql; do
        printf '\nWORKLOAD CONFIGURATION: %s\n' "$file"
        if grep -nE 'long_query_time|min_examined_row_limit|SLEEP' "$bundle/$file"; then :; else
            rc=$?; (( rc == 1 )) || fail 'Cannot read workload copy.'
            printf 'UNKNOWN: no matching settings or probe text\n'
        fi
    done
    for file in baseline.log detail.log; do
        printf '\nCAPTURE: %s\n' "$file"
        summarize "$bundle/$file"
        if command -v mysqldumpslow >/dev/null 2>&1; then
            for order in c at t; do
                printf '\nmysqldumpslow sort=%s\n' "$order"
                mysqldumpslow -s "$order" "$bundle/$file"
            done
        else
            printf 'UNKNOWN: mysqldumpslow unavailable; grouped rankings omitted\n'
        fi
    done
    printf '\nPLAN AND RESULT BEFORE CHANGE\n'
    cat -- "$bundle/plan-before.txt"
    if [[ -f $bundle/plan-after.txt ]]; then
        printf '\nPLAN AND RESULT AFTER CHANGE\n'
        cat -- "$bundle/plan-after.txt"
    else
        printf '\nUNKNOWN: no post-change plan supplied; improvement is not demonstrated\n'
    fi
    printf '\nINTERPRETATION TO COMPLETE\nFacts: ...\nCatch and evidence: ...\nHypothesis: ...\nNext check: ...\nCleanup verified: ...\n'
    printf '\nLimits: recognizes the supplied single-line workload only, not arbitrary SQL.\n'
    printf 'Counts describe logged statements, not all application calls. Low thresholds include otherwise fast work.\n'
    printf 'No CPU diagnosis or speedup is inferred. Capture success is not a health verdict.\n'
    printf 'Review every copied file before sharing; no automatic redaction is performed.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
