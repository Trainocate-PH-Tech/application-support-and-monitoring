#!/usr/bin/env bash
# Usage: monitor-log.sh LOG [error-percent=10] [latency-ms=1000]
# Input is one bounded, current time window, not a perpetually accumulated log.
set -euo pipefail
[[ $# -ge 1 && $# -le 3 ]] || { echo 'Usage: monitor-log.sh LOG [error-percent] [latency-ms]' >&2; exit 2; }
file=$1; errors=${2:-10}; latency=${3:-1000}
[[ -r $file && $errors =~ ^[0-9]+$ && $latency =~ ^[0-9]+$ ]] && ((errors<=100)) || exit 2
awk -v threshold="$errors" -v latency="$latency" '
BEGIN {print "requests,errors,error_percent,slow_requests,malformed,state"}
{
 status=""; ms=""
 for(i=1;i<=NF;i++) {
  if($i ~ /^status=[0-9][0-9][0-9]$/) {split($i,a,"=");status=a[2]}
  if($i ~ /^latency_ms=[0-9]+$/) {split($i,a,"=");ms=a[2]}
 }
 if(status=="" || ms=="") {bad++; next}
 n++; if(status>=500) e++; if(ms>=latency) slow++
}
END {
 if(n==0) {printf "0,0,0,0,%d,NO_DATA\n",bad; exit 2}
 rate=100*e/n; alert=(rate>=threshold || slow>0)
 printf "%d,%d,%.2f,%d,%d,%s\n",n,e,rate,slow,bad,alert?"ALERT":"OK"
 exit (alert?1:0)
}' "$file"
