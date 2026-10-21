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
