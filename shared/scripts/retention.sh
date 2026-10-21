#!/usr/bin/env bash
# Fixed training path, regular evidence archives only, dry-run by default.
set -euo pipefail
mode=${1:---dry-run}
[[ $mode == --dry-run || $mode == --apply ]] || exit 2
root="$HOME/support-lab/evidence"
[[ -d $root && ! -L $root ]] || { echo 'Expected real directory ~/support-lab/evidence'; exit 2; }
if [[ $mode == --apply ]]; then
 find "$root" -xdev -maxdepth 1 -type f -name 'incident-*.tar.gz' -mtime +7 -print -delete
else
 find "$root" -xdev -maxdepth 1 -type f -name 'incident-*.tar.gz' -mtime +7 -print
fi
