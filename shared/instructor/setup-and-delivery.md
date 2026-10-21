# Instructor setup and delivery

## Infrastructure and version policy

The inspected EC2 host was Ubuntu 26.04, approximately 2 GB RAM, with a 120 GB disk and expanded ext4 root partition. This is an observation, not a guarantee of future state. Run preflight again before delivery. Use an 8 GB RAM Linux application host and a separate 8 GB RAM SQL Server host as the classroom baseline; exact concurrent capacity must be rehearsed. The current 2 GB host is for one bounded demonstration at a time until resized. No infrastructure changes were made while authoring this package.

Use x86_64 Ubuntu for the supplied Java path. Tomcat is pinned to 10.1.61, Java to major 17, and Connector/J to 8.4.0. Ubuntu installs its repository MySQL/Maven versions; record `mysql --version`, `mvn -version`, `java -version` and `dpkg-query -W` after provisioning. Do not label those OS package versions as already tested on the EC2 server. Rehearse before class and retain the exact package inventory. SQL Server uses 2022 Developer on Ubuntu 22.04; record the installed cumulative update with `@@VERSION`.

## Preparation sequence

1. Back up training data; confirm this is a dedicated training host. Restrict SSH ingress to training networks. Do not publicly expose MySQL, SQL Server or Tomcat. Use SSH tunnels/private networking.
2. Resize/provision the classroom hosts before class. Upload the repository WITHOUT private keys. Run `shared/scripts/preflight.sh` and review its output.
3. On the application host, run `sudo shared/scripts/setup-ubuntu.sh --training-host`. It installs packages, builds the WAR and deploys the service. Re-running preserves existing application configuration and seeds missing fixture rows; it is not a full reset of arbitrary changes.
4. Run `shared/scripts/health-check.sh`, request player 1 and `/report`, and verify 100,000 synthetic transactions. Capture installed versions. Setup is instructor-controlled; students observe and explain each installation stage.
5. Create unique learner accounts/public keys and team groups. Grant journal access with `sudo usermod -aG systemd-journal learner01` only on this dedicated training host; learners reconnect. This group can read other system journals, so explain its scope. Shared service changes remain instructor-operated; do not hand out unrestricted sudo to every learner.
6. Create database training accounts below. Keep instructor answers outside the student handout distribution. Read-only app credentials are separate from lab writers.
7. Install the separate SQL Server host using `shared/instructor/sqlserver-setup.md`. Run the live SQL exercises and the intentional job failure once before delivery.
8. Rehearse inject → observe → reset → verify for every fault. Confirm no fault state remains and no learner transaction stays open.
9. Copy fixtures into learner workspaces and confirm every team can run the parser. Allocate one shared-stack change slot per team; other teams use evidence exercises while waiting.

## MySQL diagnostic and writer accounts

Create a unique user per team; replace the placeholder with a generated password entered in a protected administrator session. Do not commit the resulting SQL or client file.

```sql
CREATE USER 'team01'@'localhost' IDENTIFIED BY 'REPLACE_WITH_GENERATED_PASSWORD';
GRANT SELECT, UPDATE ON support_lab.* TO 'team01'@'localhost';
GRANT SELECT ON performance_schema.* TO 'team01'@'localhost';
GRANT PROCESS, REPLICATION CLIENT ON *.* TO 'team01'@'localhost';
```

These privileges expose cross-session diagnostics on a dedicated training instance. UPDATE supports the transaction labs; it is not a production read-only support role. Index creation, global log settings and user creation stay with the instructor. Learners use a mode-600 `~/.support-lab.cnf` with `[client]`, `user=team01`, `password=...`, and `host=localhost`; avoid `-pPASSWORD`. For TCP labs create the deliberate matching host account instead of assuming localhost and 127.0.0.1 account matching are identical.

## Reset and recovery

- Run `sudo shared/scripts/fault.sh reset`; then check `/health`, `/player?id=1` and `/payment`.
- End all lab writer transactions with ROLLBACK. Drop only the named lab indexes if created.
- Restore recorded slow-log settings and session thresholds; do not hard-code presumed defaults.
- For a complete MySQL synthetic-data reset, instructor verifies the database name, then runs `DROP DATABASE support_lab;` and imports `shared/sql/mysql/seed.sql`. This destroys only training data; learner evidence remains elsewhere.
- For SQL Server reset, roll back sessions, drop the named training index, and rerun setup to ensure objects exist. A full database reset is instructor-only after confirming no active class sessions.
- Storage cleanup must unmount successfully before detaching/deleting its backing image. Do not remove an active mount's directory.

## Bounded CPU demonstration

Instructor runs `timeout 15s bash -c 'while :; do :; done' &` on the training host, then learners use `pidstat 1 3`, `top`, `ps` and `uptime`. One process only; timeout ends it. The process is synthetic and unrelated to real JVM profiling. Do not use fork bombs or unbounded traffic generators.

## Class timing

Each day is 09:00–17:00 with lunch 12:00–13:00 and two 15-minute breaks, leaving 390 instructional minutes. Pause blocks at break boundaries and resume afterward. The module agenda gives instructional minutes; extensions are optional homework. Account setup and package downloads are rehearsed in advance; class installation is an instructor demonstration with learner checkpoints. Use pairs within teams for the foundations and rotate the incident roles.

## Scope of the app

The app opens a database connection per request and supports reads; it does not implement a connection pool, payment gateway, authentication system or production observability. Pool exhaustion, transaction retries, real payment integration, replication and IIS are taught with clearly labeled synthetic evidence. The MySQL/SQL Server transaction labs perform controlled writes directly in SQL. Do not present simulated behavior as a complete production architecture.

## Delivery revision: pacing and shared-stack rotation

Each agenda schedules 370 minutes plus two 10-minute checkpoints (390 total). Place the first checkpoint before the application/database practical block and the second before the final assessment. Use them for evidence review, interrupted-step recovery and prerequisites. Do not spend them on optional extensions before core learners are ready.

At enrollment, divide learners into teams of 3–4. For a shared fault exercise use 12-minute slots: 2 minutes baseline and owner handoff, 6 minutes operator work, 2 minutes recovery verification, 2 minutes reset and handoff. Publish team names against slots before class. Only the current team requests a shared mutation. Waiting teams investigate their own copies of evidence, annotate a copied service unit or perform individual checks; they must not diagnose another team's live fault as their own.

For more teams than fit the exercise's live window, the instructor demonstrates one live case; remaining teams use a released evidence capture and label recovery simulated. Do not shorten rollback or silently claim every team performed a live repair. Parallel hands-on fault repairs require additional isolated application stacks. Installation occurs once on the shared host; learners independently prepare a corrected unit and explain installation and readiness stages.

Rotate investigator, operator and reviewer each block. With four learners, the fourth is incident lead; merge lead/reviewer with three. Keep a roster with individual command, interpretation and rollback checks. Prepare public evidence copies before the class; keep this master directory and instructor files inaccessible to learner accounts. Upload only the student package to the learner-readable course directory. Keep setup/fault scripts in a separate instructor-owned directory and run them there.

For Module 2 SQL Server, blocking is core live practice. Query Store and job history use supplied evidence during the core block; live plan changes and Agent execution are optional extensions. Finish both session rollbacks before changing activities.

## Timed beginner pilot checklist

- Record actual start/end and minutes spent on access, command entry, interpretation, waiting and cleanup for each block.
- At each checkpoint, sample one learner per team: can they explain their last status and next check without copying?
- Record hints and individual remediation separately from team scores.
- Stop extensions if any core team has not reached the prerequisite checkpoint.
- Preserve final-assessment time. Record any unfinished required task rather than marking it complete.
- After the pilot, move tasks that consistently overrun to demonstrations/extensions and repeat the affected timing measurement.

Automated checks validate artifacts and selected command behavior. They do not validate beginner pacing or teaching effectiveness.
