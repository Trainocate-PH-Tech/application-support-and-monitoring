#!/usr/bin/env bash
# Offline teaching collector: no database connections or remediation.
set -euo pipefail
umask 077
export LC_ALL=C
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
[[ $# == 2 ]] || fail "Usage: $0 INPUT_DIR OUTPUT_PARENT"
input=$1
parent=$2
[[ -d $input ]] || fail "Not an input directory: $input"
# Validate a deliberately simple TSV contract: header, nonempty cells, numbers.
validate_tsv() {
    local file=$1 header=$2 numeric=$3
    awk -F '\t' -v header="$header" -v numeric="$numeric" '
    BEGIN { n=split(header,h,"\t"); k=split(numeric,cols,",") }
    NR==1 { if ($0!=header) exit 2; next }
    { if(NF!=n) exit 2
      for(i=1;i<=NF;i++) if($i=="" || $i ~ /\r/) exit 2
      for(i=1;i<=k;i++) if(cols[i]!="" && $(cols[i]) !~ /^[0-9]+([.][0-9]+)?$/) exit 2 }
    END { if(NR==0) exit 2 }' "$file" || fail "Malformed TSV: $file"
}
files=(provenance.txt slow.log)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mysql-slow-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
# Recognize the conventional timing header; do not claim this parses arbitrary SQL.
awk '/^# Query_time:/ {if(NF!=9 || $3 !~ /^[0-9]+([.][0-9]+)?$/ || $5 !~ /^[0-9]+([.][0-9]+)?$/ || $7 !~ /^[0-9]+$/ || $9 !~ /^[0-9]+$/) exit 2}' "$bundle/slow.log" || fail 'Malformed slow-log timing header.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'SLOW LOG SUMMARY\n'
awk '/^# Query_time:/ {n++;seconds+=$3;locks+=$5;examined+=$9}
END {if(n) printf "entries=%d total_query_seconds=%.2f total_lock_seconds=%.6f rows_examined=%.0f\n",n,seconds,locks,examined; else print "UNKNOWN: no timing headers"}' "$bundle/slow.log"
if command -v mysqldumpslow >/dev/null 2>&1; then
    for ranking in c at t; do
        printf '\nmysqldumpslow sort=%s\n' "$ranking"
        mysqldumpslow -s "$ranking" "$bundle/slow.log"
    done
else
    printf 'UNKNOWN: mysqldumpslow unavailable; grouped rankings not generated. Install the matching MySQL utility, then rerun.\n'
fi
printf 'Timing-header totals are observations, not CPU usage or unique incidents.\n'

    printf '\nINTERPRETATION TO COMPLETE\nObserved facts: ...\nUncertainty: ...\nNext read-only check: ...\n'
    printf 'Collector success is not a database-health verdict. Review copied evidence before sharing.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
