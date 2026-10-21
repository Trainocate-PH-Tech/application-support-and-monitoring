# Separate SQL Server lab

Use a dedicated x86_64 Ubuntu 22.04 VM, 8 GB RAM recommended for training, with SQL Server 2022 Developer Edition (nonproduction). Keep port 1433 private or accessible only through approved tunnels. This package does not provision cloud resources.

## Install and initialize

Follow the [Microsoft Ubuntu installation guide](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-ubuntu?view=sql-server-ver16) for the 2022/Ubuntu 22.04 repository. The core sequence is below; verify the repository instructions before delivery if Microsoft changes packaging.

```bash
sudo apt-get update
sudo apt-get install -y curl gnupg
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/microsoft.gpg
sudo install -m 644 /tmp/microsoft.gpg /usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/config/ubuntu/22.04/mssql-server-2022.list -o /tmp/mssql-server-2022.list
sudo install -m 644 /tmp/mssql-server-2022.list /etc/apt/sources.list.d/mssql-server-2022.list
sudo apt-get update
sudo apt-get install -y mssql-server
sudo /opt/mssql/bin/mssql-conf setup
# Select Developer Edition; enter a generated administrator password interactively.
sudo /opt/mssql/bin/mssql-conf set sqlagent.enabled true
sudo systemctl restart mssql-server
sudo systemctl status mssql-server --no-pager
```

Install the current Microsoft `mssql-tools18`/ODBC client using the same official guide's client section and package-license prompts. Use `/opt/mssql-tools18/bin/sqlcmd`; inspect `sqlcmd -?` because Go and ODBC sqlcmd variants differ. Use a valid trusted server certificate for training connections. If a disposable lab uses a self-signed certificate, explain the trust limitation before explicitly using ODBC sqlcmd `-C`; do not present that as certificate remediation.

Enter a password locally with `read -rs SQLCMDPASSWORD; export SQLCMDPASSWORD`, then invoke sqlcmd with `-U` and no `-P`. Unset it after the session. This environment variable is not appropriate for evidence collection.

```bash
sqlcmd -S tcp:SQL_HOST,1433 -U sa -i shared/sql/sqlserver/setup.sql
sqlcmd -S tcp:SQL_HOST,1433 -U sa -Q 'SELECT @@VERSION;'
```

## Team logins and permissions

Run as instructor, replacing the password in a protected session. Do not save real credentials with the course.

```sql
USE master;
CREATE LOGIN team01 WITH PASSWORD='REPLACE_WITH_GENERATED_STRONG_PASSWORD';
GRANT VIEW SERVER PERFORMANCE STATE TO team01;
GRANT VIEW SERVER STATE TO team01;
GO
USE SupportLab;
CREATE USER team01 FOR LOGIN team01;
GRANT SELECT, UPDATE TO team01;
GRANT VIEW DATABASE STATE TO team01;
GRANT VIEW DATABASE PERFORMANCE STATE TO team01;
GO
USE msdb;
CREATE USER team01 FOR LOGIN team01;
ALTER ROLE SQLAgentReaderRole ADD MEMBER team01;
GO
```

These are training-wide diagnostics, not a production least-privilege blueprint. The instructor creates indexes, flushes Query Store and starts the synthetic job. Team sessions inspect and perform bounded updates in SupportLab. Verify visibility with `diagnostics.sql` as the learner, not only as sa. SQL Server 2022 requires [VIEW SERVER PERFORMANCE STATE for requests](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-requests-transact-sql?view=sql-server-ver16).

## Rehearsal

1. SQL Agent readiness can lag engine readiness. If setup reports error 14258 (Agent starting), wait and rerun; the job, step and server association are created independently so an interrupted setup can resume. Run setup, workload, diagnostics and the two-session blocking sequence.
2. Verify Query Store is READ_WRITE. Execute queries more than once, flush as instructor, and allow the runtime interval to populate; data is not guaranteed to appear immediately.
3. Start `SupportLab-IntentionalFailure`; verify failed step history. SQL Agent must be running.
4. Rehearse the index before/after comparison. A changed plan is observable; dramatic CPU/latency differences are not guaranteed on every VM. Use the synthetic plan-regression and high-CPU evidence when live timing is inconclusive.
5. Roll back every open writer transaction, remove the training index and verify normal selects.

IIS is not installed on Linux. Use `platform-incidents.md` for the Windows/IIS scenario and clearly distinguish it from live Linux services.
