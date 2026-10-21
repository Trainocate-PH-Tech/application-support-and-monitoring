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
files=(provenance.txt requests.tsv db.tsv context.txt)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/app-db-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/requests.tsv" $'request_id\tstart_utc\toperation\thttp_status\thttp_ms\tpool_ms\tsql_ms\tdownstream_ms\tother_ms\tattempts\tdb_operation_id' '4,5,6,7,8,9,10'
validate_tsv "$bundle/db.tsv" $'db_operation_id\trequest_id\tduration_ms\tendpoint' '3'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'REQUEST RECONCILIATION (sequential fixture buckets, all attempts included)\n'
awk -F '\t' 'FNR==1 {next} FILENAME==ARGV[1] {key=$1 SUBSEP $2;duration[key]=$3;next}
{n++; errors+=($4>=400);sum=$6+$7+$8+$9;key=$11 SUBSEP $1;
printf "request=%s operation=%s status=%s http_ms=%s component_ms=%.0f residual_ms=%.0f attempts=%s\n",$1,$3,$4,$5,sum,$5-sum,$10;
if(key in duration) printf "  explicit_db_match=%s sql_difference_ms=%.0f\n",$11,$7-duration[key];else print "  UNKNOWN: no explicit database-operation match";
print "  pool_ms=" $6,"sql_ms=" $7,"downstream_ms=" $8,"other_ms=" $9}
END {if(n) printf "requests=%d error_requests=%d error_percent=%.2f\n",n,errors,100*errors/n; else print "UNKNOWN: no requests"}' "$bundle/db.tsv" "$bundle/requests.tsv"
printf '\nCONTEXT\n'
cat -- "$bundle/context.txt"

    printf '\nINTERPRETATION TO COMPLETE\nObserved facts: ...\nUncertainty: ...\nNext read-only check: ...\n'
    printf 'Collector success is not a database-health verdict. Review copied evidence before sharing.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
