#!/usr/bin/env bash
set -euo pipefail
url=${1:-http://127.0.0.1:8080/loyalty}
count=${2:-20}
if [[ ! $count =~ ^[0-9]{1,3}$ ]]; then echo 'count must be 1..100'; exit 2; fi
count=$((10#$count))
if ((count<1 || count>100)); then echo 'count must be 1..100'; exit 2; fi
for ((i=0;i<count;i++)); do
 curl --silent --show-error --max-time 8 -o /dev/null -w '%{http_code},%{time_total}\n' "$url/player?id=1" || true
 sleep 0.2
done
