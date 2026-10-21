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
files=(provenance.txt sessions.tsv waits-before.tsv waits-after.tsv plans.tsv context.txt)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mssql-regression-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/sessions.tsv" $'session_id\tblocking_session_id\tstatus\topen_transactions' '1,4'
validate_tsv "$bundle/waits-before.tsv" $'captured_utc\tserver_start_utc\twait_type\twait_ms' '4'
validate_tsv "$bundle/waits-after.tsv" $'captured_utc\tserver_start_utc\twait_type\twait_ms' '4'
validate_tsv "$bundle/plans.tsv" $'interval_utc\tquery_id\tplan_id\texecutions\tavg_duration_us\tavg_cpu_us\tavg_reads' '2,3,4,5,6,7'
awk -F '\t' 'NR>1 && $2 !~ /^-?[0-9]+$/ {exit 2}' "$bundle/sessions.tsv" || fail 'Invalid blocking session identifier.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'BLOCKING CHAIN SNAPSHOT\n'
awk -F '\t' 'NR>1 {b[$1]=$2;s[$1]=$3;t[$1]=$4}
END {if(NR==1) print "UNKNOWN: no sessions supplied";
for(id in b) if(b[id]>0) {delete seen; x=id; chain=id;
while((x in b) && b[x]>0 && !seen[x]) {seen[x]=1;x=b[x];chain=chain " -> " x}
if(seen[x]) print chain,"UNKNOWN: cycle";
else if(!(x in b)) print chain,"UNKNOWN: blocker not captured";
else if(b[x]<0) print chain,"UNKNOWN: special blocker",b[x];
else print chain,"head=" x,"status=" s[x],"open_transactions=" t[x]}
for(id in b) if(b[id]<0) print "session=" id,"UNKNOWN: special blocker",b[id]}' "$bundle/sessions.tsv" | sort
printf '\nWAIT DELTAS (separate blocking case)\n'
awk -F '\t' 'FNR==1 {next} FILENAME==ARGV[1] {v[$3]=$4;start[$3]=$2;stamp[$3]=$1;next}
{n++; if(!($3 in v)||$2!=start[$3]||$4<v[$3]||$1<=stamp[$3]) print $3,"UNKNOWN: missing baseline, reset, or invalid interval";
else printf "%s delta_ms=%.0f\n",$3,$4-v[$3]}
END {if(!n) print "UNKNOWN: no after snapshot"}' "$bundle/waits-before.tsv" "$bundle/waits-after.tsv" | sort

printf '\nQUERY STORE (execution-weighted; only comparable supplied intervals)\n'
awk -F '\t' 'NR>1 {key=$1 " query=" $2 " plan=" $3; n[key]+=$4; d[key]+=$4*$5; c[key]+=$4*$6; r[key]+=$4*$7}
END {if(NR==1) print "UNKNOWN: no Query Store rows";
for(k in n) if(n[k]>0) printf "%s executions=%d duration_ms=%.2f cpu_ms=%.2f reads=%.2f\n",k,n[k],d[k]/n[k]/1000,c[k]/n[k]/1000,r[k]/n[k]; else print k,"UNKNOWN: zero executions"}' "$bundle/plans.tsv" | sort

printf '\nCASE BOUNDARIES AND DEPLOYMENT CONTEXT\n'
cat -- "$bundle/context.txt"

    printf '\nINTERPRETATION TO COMPLETE\nObserved facts: ...\nUncertainty: ...\nNext read-only check: ...\n'
    printf 'Collector success is not a database-health verdict. Review copied evidence before sharing.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
