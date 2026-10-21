#!/usr/bin/env bash
# Usage: collect-evidence.sh [output-parent] [since]; exit 1 means a partial bundle.
set -u
umask 077
out=${1:-./evidence}; since=${2:-'15 minutes ago'}
mkdir -p -- "$out" || exit 2
folder=$(mktemp -d "$out/incident-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX") || exit 2
partial=0
mask() { sed -E 's/((password|token|secret|authorization)[=:][[:space:]]*)[^[:space:]]+/\1[REDACTED]/Ig'; }
capture() {
 local name=$1 rc; shift
 timeout 15 "$@" > "$folder/.raw" 2>&1; rc=$?
 mask < "$folder/.raw" > "$folder/$name.txt"
 rm -f "$folder/.raw"
 printf '%s\t%s\n' "$name" "$rc" >> "$folder/manifest.tsv"
 ((rc==0)) || partial=1
}
printf 'capture\texit_code\n' > "$folder/manifest.tsv"
capture timestamp date -u +%FT%TZ
capture identity id
capture uptime uptime
capture memory free -h
capture disk df -hT
capture inodes df -i
# Do not capture process arguments or environment; either can contain secrets.
capture processes ps -eo pid,ppid,user,comm,pcpu,pmem --sort=-pcpu
capture sockets ss -lnt
capture service systemctl status support-tomcat --no-pager
capture journal journalctl -u support-tomcat --since "$since" --utc --no-pager -n 1000
printf 'Review all files for sensitive data before sharing. Regex masking is not a security guarantee.\n' > "$folder/REVIEW.txt"
archive="$folder.tar.gz"
tar -czf "$archive" -C "$(dirname -- "$folder")" "$(basename -- "$folder")" || exit 2
printf 'bundle=%s partial=%s\n' "$archive" "$partial"
exit "$partial"
