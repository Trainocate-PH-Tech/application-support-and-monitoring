#!/usr/bin/env bash
set -u
printf 'UTC: '; date -u +%FT%TZ
cat /etc/os-release
id; free -h; df -hT; df -i; lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
for cmd in java mysql curl ss systemctl growpart resize2fs; do command -v "$cmd" || true; done
awk '/MemTotal/ {if ($2 < 7500000) print "CAPACITY: below 8 GB training baseline; run only bounded instructor demos until resized."}' /proc/meminfo
printf 'SSH user is not automatically root. Never share the instructor private key.\n'
