#!/usr/bin/env bash
# Safe read-only MySQL checks. MYSQL_CNF must refer to a chmod 600 client file.
set -u
file=${MYSQL_CNF:-$HOME/.support-lab.cnf}
[[ -r $file ]] || { echo 'Set MYSQL_CNF to a readable protected mysql client config'; exit 2; }
[[ $(stat -c '%a' "$file") == 600 ]] || { echo 'Client config must be mode 600'; exit 2; }
date -u +%FT%TZ
timeout 10 mysql --defaults-extra-file="$file" --batch --connect-timeout=3 <<'SQL'
SELECT UTC_TIMESTAMP(),VERSION();
SELECT 1 AS connectivity;
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Max_used_connections';
SHOW VARIABLES LIKE 'max_connections';
SQL
