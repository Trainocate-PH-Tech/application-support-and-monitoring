#!/usr/bin/env bash
# Exit 0 healthy, 1 unhealthy, 2 usage/dependency error. No credentials in arguments.
set -u
service=${SERVICE:-support-tomcat}
url=${URL:-http://127.0.0.1:8080/loyalty/health}
limit=${DISK_LIMIT:-85}
path=${DISK_PATH:-/}
if [[ ! $limit =~ ^[0-9]{1,3}$ ]]; then echo 'DISK_LIMIT must be 1..100'; exit 2; fi
limit=$((10#$limit))
if ((limit<1 || limit>100)); then echo 'DISK_LIMIT must be 1..100'; exit 2; fi
for command in curl df systemctl awk; do command -v "$command" >/dev/null || exit 2; done
status=0
emit() { printf '%s check=%s state=%s detail=%s\n' "$(date -u +%FT%TZ)" "$1" "$2" "$3"; }
if systemctl is-active --quiet "$service"; then emit service OK "$service"; else emit service FAIL "$service"; status=1; fi
if code=$(curl --silent --show-error --max-time 5 -o /dev/null -w '%{http_code}' "$url") && [[ $code == 200 ]]; then
 emit endpoint OK "$code"
else emit endpoint FAIL "${code:-unreachable}"; status=1; fi
if usage=$(df -P -- "$path" 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}') && [[ $usage =~ ^[0-9]+$ ]]; then
 if ((usage>=limit)); then emit disk FAIL "$usage"; status=1; else emit disk OK "$usage"; fi
else emit disk FAIL unknown; status=1; fi
exit "$status"
