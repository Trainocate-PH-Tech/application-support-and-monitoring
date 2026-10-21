#!/usr/bin/env bash
# Instructor controls ONE global scenario at a time. Back up configuration first.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'sudo required'; exit 1; }
config=/etc/support-lab/app.properties
state=/var/lib/support-lab-fault
case ${1:-} in
 reset)
  [[ -d $state ]] || { echo 'No active fault'; exit 0; }
  cp -p "$state/app.properties" "$config"
  rm -f /etc/systemd/system/support-tomcat.service.d/training-fault.conf
  systemctl daemon-reload
  systemctl restart support-tomcat
  rm -rf -- "$state"
  echo 'Reset complete; run health-check.sh';;
 db-auth|latency|payment|permissions|startup)
  [[ ! -e $state ]] || { echo 'Reset the active fault first'; exit 1; }
  install -d -m 700 "$state"; cp -p "$config" "$state/app.properties"
  case $1 in
   db-auth) sed -i 's/^db.password=.*/db.password=INTENTIONALLY_WRONG/' "$config";;
   latency) sed -i 's/^delay.ms=.*/delay.ms=1500/' "$config";;
   payment) sed -i 's/^payment.fail=.*/payment.fail=true/' "$config";;
   permissions) chmod 600 "$config";;
   startup)
    install -d /etc/systemd/system/support-tomcat.service.d
    printf '[Service]\nExecStart=\nExecStart=/opt/support-lab/does-not-exist\n' > /etc/systemd/system/support-tomcat.service.d/training-fault.conf
    systemctl daemon-reload; systemctl restart support-tomcat || true;;
  esac
  echo "Injected $1; reset with sudo $0 reset";;
 *) echo 'Usage: fault.sh {db-auth|latency|payment|permissions|startup|reset}'; exit 2;;
esac
