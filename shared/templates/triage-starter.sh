#!/usr/bin/env bash
# Learner starter: extend this in your own workspace, not the course originals.
set -u
service=${1:-support-tomcat}
printf 'UTC=%s service=%s\n' "$(date -u +%FT%TZ)" "$service"
if systemctl is-active --quiet "$service"; then
 printf 'service=ACTIVE\n'
else
 printf 'service=NOT_ACTIVE\n'
fi
df -h /
# TODO: add available memory, top processes and recent service errors.
# TODO: write output to a unique timestamped folder and preserve command statuses.
# TODO: explain how a permission failure differs from an empty error log.
