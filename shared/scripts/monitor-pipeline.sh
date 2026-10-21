#!/usr/bin/env bash
# Usage: monitor-pipeline.sh WINDOW_LOG [output-parent] [MYSQL_SLOW_LOG]
# 0 healthy, 1 alert, 2 incomplete/invalid. Caller supplies a current bounded window.
set -u
[[ $# -ge 1 && $# -le 3 ]] || { echo 'Usage: monitor-pipeline.sh WINDOW_LOG [output-parent] [MYSQL_SLOW_LOG]'; exit 2; }
source_log=$1; parent=${2:-$HOME/support-lab/monitoring}; slow=${3:-}
[[ -r $source_log ]] || exit 2
umask 077
mkdir -p -- "$parent" || exit 2
out=$(mktemp -d "$parent/window-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX") || exit 2
base=$(cd -- "$(dirname -- "$0")" && pwd)
"$base/monitor-log.sh" "$source_log" > "$out/application.csv"
state=$?
printf 'captured_at=%s\ninput=%s\napplication_exit=%s\n' "$(date -u +%FT%TZ)" "$source_log" "$state" > "$out/manifest.txt"
if [[ -n $slow ]]; then
 if [[ -r $slow ]] && command -v mysqldumpslow >/dev/null; then
  timeout 15 mysqldumpslow -s t -t 5 "$slow" > "$out/slow-time.txt" 2>&1
  rc=$?
  printf 'slow_summary_exit=%s\n' "$rc" >> "$out/manifest.txt"
  if ((rc!=0)); then state=2; fi
 else
  printf 'slow_summary=UNAVAILABLE\n' >> "$out/manifest.txt"; state=2
 fi
fi
printf 'output=%s state=%s\n' "$out" "$state"
exit "$state"
