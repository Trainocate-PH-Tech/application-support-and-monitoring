#!/usr/bin/env bash
# Instructor only; run on a dedicated Ubuntu training host.
set -euo pipefail
[[ ${EUID} -eq 0 ]] || { echo 'Run with sudo'; exit 1; }
[[ ${1:-} == --training-host ]] || { echo 'Usage: sudo ./setup-ubuntu.sh --training-host'; exit 2; }
# shellcheck source=/dev/null
source /etc/os-release
[[ $(uname -m) == x86_64 ]] || { echo "This setup expects x86_64 Ubuntu"; exit 1; }
[[ $ID == ubuntu ]] || { echo 'Ubuntu only'; exit 1; }
base=$(cd -- "$(dirname -- "$0")/.." && pwd)
apt-get update
apt-get install -y openjdk-17-jdk maven python3 openssl mysql-server curl netcat-openbsd dnsutils traceroute sysstat lsof jq quota cloud-guest-utils xfsprogs unzip
# Download a tested Tomcat 10.1 release; verify upstream checksum before extraction.
version=10.1.61
archive="apache-tomcat-${version}.tar.gz"
work=$(mktemp -d); trap 'rm -rf -- "$work"' EXIT
curl --fail --location "https://archive.apache.org/dist/tomcat/tomcat-10/v${version}/bin/${archive}" -o "$work/$archive"
curl --fail --location "https://archive.apache.org/dist/tomcat/tomcat-10/v${version}/bin/${archive}.sha512" -o "$work/$archive.sha512"
(cd "$work"; sha512sum -c "$archive.sha512")
id supportapp >/dev/null 2>&1 || useradd --system --home-dir /opt/support-lab/tomcat --shell /usr/sbin/nologin supportapp
install -d /opt/support-lab /etc/support-lab
if [[ ! -d /opt/support-lab/tomcat ]]; then
 tar -xzf "$work/$archive" -C /opt/support-lab
 mv "/opt/support-lab/apache-tomcat-${version}" /opt/support-lab/tomcat
fi
# Bind HTTP to loopback; students reach it through SSH forwarding.
python3 - <<'PY'
from pathlib import Path
p=Path('/opt/support-lab/tomcat/conf/server.xml')
s=p.read_text(); s=s.replace('<Connector port="8080"', '<Connector address="127.0.0.1" port="8080"'); p.write_text(s)
PY
systemctl enable --now mysql
mysql < "$base/sql/mysql/seed.sql"
if [[ ! -f /etc/support-lab/app.properties ]]; then
 password=$(openssl rand -hex 24)
 mysql <<SQL
CREATE USER IF NOT EXISTS 'support_app'@'127.0.0.1' IDENTIFIED BY '$password';
ALTER USER 'support_app'@'127.0.0.1' IDENTIFIED BY '$password';
GRANT SELECT ON support_lab.* TO 'support_app'@'127.0.0.1';
SQL
 cat > /etc/support-lab/app.properties <<CFG
db.url=jdbc:mysql://127.0.0.1:3306/support_lab?connectTimeout=2000&socketTimeout=5000
db.user=support_app
db.password=$password
delay.ms=0
payment.fail=false
CFG
fi
chown root:supportapp /etc/support-lab/app.properties
chmod 640 /etc/support-lab/app.properties
(cd "$base/app"; mvn -B clean package)
install -m 644 "$base/app/target/loyalty.war" /opt/support-lab/tomcat/webapps/loyalty.war
chown -R supportapp:supportapp /opt/support-lab/tomcat
cat > /etc/systemd/system/support-tomcat.service <<'UNIT'
[Unit]
Description=Training loyalty Tomcat
After=network.target mysql.service
[Service]
Type=simple
User=supportapp
Group=supportapp
Environment=JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
Environment=LAB_CONFIG=/etc/support-lab/app.properties
Environment="CATALINA_OPTS=-Xms128m -Xmx384m"
ExecStart=/opt/support-lab/tomcat/bin/catalina.sh run
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
UMask=0027
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now support-tomcat
for _attempt in {1..30}; do
 if curl --fail --silent http://127.0.0.1:8080/loyalty/health; then exit 0; fi
 sleep 2
done
echo 'Health check failed; inspect journalctl -u support-tomcat'; exit 1
