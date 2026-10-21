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
files=(provenance.txt requests.tsv expensive.tsv plans.tsv jobs.tsv)
for file in "${files[@]}"; do
    [[ -f $input/$file && -r $input/$file ]] || fail "Missing or unreadable input: $file"
done
mkdir -p -- "$parent" || fail "Cannot create output parent."
bundle=$(mktemp -d -- "$parent/mssql-diagnostics-XXXXXX") || fail "Cannot create output directory."
for file in "${files[@]}"; do cp -- "$input/$file" "$bundle/$file"; done
validate_tsv "$bundle/requests.tsv" $'captured_utc\tsession_id\tblocking_session_id\twait_type\telapsed_ms' '2,5'
validate_tsv "$bundle/expensive.tsv" $'query_id\texecutions\ttotal_elapsed_us\ttotal_cpu_us\ttotal_reads' '1,2,3,4,5'
validate_tsv "$bundle/plans.tsv" $'interval_utc\tquery_id\tplan_id\texecutions\tavg_duration_us\tavg_cpu_us\tavg_reads' '2,3,4,5,6,7'
validate_tsv "$bundle/jobs.tsv" $'job\tstep_id\trun_status\tmessage' '2,3'
awk -F '\t' 'NR>1 && $3 !~ /^-?[0-9]+$/ {exit 2}' "$bundle/requests.tsv" || fail 'Invalid blocking session identifier.'
{
    printf 'DATABASE SUPPORT EVIDENCE REPORT\nCaptured UTC: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    cat -- "$bundle/provenance.txt"

printf 'ACTIVE REQUEST SNAPSHOT\n'
awk -F '\t' 'NR>1 {printf "session=%s blocker=%s wait=%s elapsed_ms=%s\n",$2,$3,$4,$5} END {if(NR==1) print "UNKNOWN: no requests supplied"}' "$bundle/requests.tsv"
printf '\nCACHED QUERY TOTALS AND AVERAGES\n'
awk -F '\t' 'NR>1 {if($2>0) printf "query=%s executions=%s avg_elapsed_ms=%.2f avg_cpu_ms=%.2f total_reads=%.0f\n",$1,$2,$3/$2/1000,$4/$2/1000,$5; else print "UNKNOWN: zero executions for query",$1} END {if(NR==1) print "UNKNOWN: no cached queries"}' "$bundle/expensive.tsv"
printf '\nJOB FAILURES (step 0 is the job outcome, not another failed step)\n'
awk -F '\t' 'NR>1 && $3==0 {if($2==0) jobs++; else steps++; print $1,"step=" $2,$4}
END {if(NR==1) print "UNKNOWN: no job history"; else printf "failed_steps=%d failed_job_outcomes=%d\n",steps,jobs}' "$bundle/jobs.tsv"

printf '\nQUERY STORE (execution-weighted; only comparable supplied intervals)\n'
awk -F '\t' 'NR>1 {key=$1 " query=" $2 " plan=" $3; n[key]+=$4; d[key]+=$4*$5; c[key]+=$4*$6; r[key]+=$4*$7}
END {if(NR==1) print "UNKNOWN: no Query Store rows";
for(k in n) if(n[k]>0) printf "%s executions=%d duration_ms=%.2f cpu_ms=%.2f reads=%.2f\n",k,n[k],d[k]/n[k]/1000,c[k]/n[k]/1000,r[k]/n[k]; else print k,"UNKNOWN: zero executions"}' "$bundle/plans.tsv" | sort

    printf '\nINTERPRETATION TO COMPLETE\nObserved facts: ...\nUncertainty: ...\nNext read-only check: ...\n'
    printf 'Collector success is not a database-health verdict. Review copied evidence before sharing.\n'
} > "$bundle/report.txt"
printf 'Report: %s/report.txt\n' "$bundle"
