# Synthetic loyalty application

Java 17 / Jakarta Servlet 6 WAR for Tomcat 10.1, with Connector/J 8.4.0. Source and Maven build are included. This is deliberately small training software, not a production payment or gaming application.

## Build and deploy

`mvn -B clean package` from this directory creates `target/loyalty.war`. The instructor setup script installs Java/Maven/MySQL, downloads verified Tomcat 10.1.61, creates a read-only app account, seeds 100,000 transactions and deploys the WAR. It assumes x86_64 Ubuntu. Use `shared/scripts/setup-ubuntu.sh --training-host` with sudo only on the intended training host.

Configuration is read from `LAB_CONFIG`, default `/etc/support-lab/app.properties`, on every request. Required properties: `db.url`, `db.user`, `db.password`. Optional training controls: `delay.ms` (clamped to 0–2000) and `payment.fail` (true/false). Configuration is root:supportapp mode 640. Do not print it in evidence bundles.

| HTTP GET route under /loyalty | Result |
|---|---|
| `/live` | Process/config readability check; no database query |
| `/health` | Authenticated connection and SELECT 1 |
| `/player?id=1` | Parameterized player lookup; invalid integer 400, missing player 404 |
| `/report` | Count and sum for player 42; intentionally no initial player index |
| `/payment` | Synthetic dependency status, 200 or deliberate 502; no actual payment |

Each response includes X-Request-ID. Logs contain UTC timestamp, level, request_id, sanitized path, status, latency_ms and safe error category. Credentials and full SQL exception messages are not logged. This is an educational tradeoff: production diagnostics may need richer securely handled error detail.

The app opens one DB connection per request; pooling and retry incidents are separate synthetic evidence exercises. SQL transaction exercises use database clients. All endpoints are reads. Build/HTTP verification and unexecuted database checks are recorded in the root VALIDATION.md.
