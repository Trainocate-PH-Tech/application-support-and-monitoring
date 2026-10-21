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
files=(provenance.txt locks.tsv innodb.txt replica.json)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mysql-contention-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/locks.tsv" $'captured_utc\twaiting_session\tblocking_session\tobject_name' '2,3'
command -v jq >/dev/null || fail 'Install jq before using this collector.'
jq -e 'type=="object" and (.Replica_IO_Running|type=="string") and (.Replica_SQL_Running|type=="string") and has("Seconds_Behind_Source") and (.Seconds_Behind_Source==null or (.Seconds_Behind_Source|type=="number")) and (.Last_SQL_Errno|type=="number") and (.Relay_Log_File|type=="string") and (.report_route|type=="string") and ([.captured_at,.primary_last_write,.replica_last_visible_write]|all(.[]; type=="string" and (try fromdateiso8601 catch null)!=null))' "$bundle/replica.json" >/dev/null || fail 'Malformed replication evidence.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'CURRENT LOCK SNAPSHOT\n'
awk -F '\t' 'NR>1 {printf "%s waiting=%s blocking=%s object=%s\n",$1,$2,$3,$4} END {if(NR==1) print "UNKNOWN: no supplied waits"}' "$bundle/locks.tsv"
printf '\nHISTORICAL DEADLOCK EXCERPT\n'
if grep -nE 'DEADLOCK|Transaction|ROLL BACK' "$bundle/innodb.txt"; then :; else
    rc=$?; (( rc == 1 )) || fail 'Cannot search InnoDB evidence.'
    printf 'UNKNOWN: no matching deadlock evidence\n'
fi
printf '\nSEPARATE REPLICATION CASE\n'
jq -r '"receiver=\(.Replica_IO_Running) applier=\(.Replica_SQL_Running) lag_seconds=\(if .Seconds_Behind_Source == null then "UNKNOWN" else .Seconds_Behind_Source end)",
"route=\(.report_route) relay_log=\(.Relay_Log_File) error=\(.Last_SQL_Errno)",
"capture=\(.captured_at) primary_last_write=\(.primary_last_write) replica_visible=\(.replica_last_visible_write)",
"Latest-write gap seconds=\((.primary_last_write|fromdateiso8601)-(.replica_last_visible_write|fromdateiso8601))",
"Replica visible-write age seconds=\((.captured_at|fromdateiso8601)-(.replica_last_visible_write|fromdateiso8601))"' "$bundle/replica.json"
printf 'Write timestamps are application evidence, not a replacement for replication metrics.\n'

    printf '\nINTERPRETATION TO COMPLETE\nObserved facts: ...\nUncertainty: ...\nNext read-only check: ...\n'
    printf 'Collector success is not a database-health verdict. Review copied evidence before sharing.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
