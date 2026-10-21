-- Instructor only, dedicated nonproduction SQL Server 2022 Developer instance.
USE master;
GO
IF DB_ID(N'SupportLab') IS NULL CREATE DATABASE SupportLab;
GO
ALTER DATABASE SupportLab SET QUERY_STORE = ON;
ALTER DATABASE SupportLab SET QUERY_STORE (OPERATION_MODE = READ_WRITE, QUERY_CAPTURE_MODE = ALL);
GO
USE SupportLab;
GO
IF OBJECT_ID(N'dbo.Players') IS NULL
 CREATE TABLE dbo.Players(id int NOT NULL PRIMARY KEY, points int NOT NULL);
IF NOT EXISTS(SELECT 1 FROM dbo.Players) INSERT dbo.Players VALUES(1,100),(2,200);
IF OBJECT_ID(N'dbo.Transactions') IS NULL BEGIN
 CREATE TABLE dbo.Transactions(id int NOT NULL PRIMARY KEY,player_id int NOT NULL,amount decimal(10,2));
 ;WITH n AS (SELECT TOP (100000) ROW_NUMBER() OVER(ORDER BY (SELECT NULL)) AS id
 FROM sys.all_objects a CROSS JOIN sys.all_objects b)
 INSERT dbo.Transactions SELECT id,id%100+1,10.00 FROM n;
END;
GO
USE msdb;
GO
-- Agent readiness can lag engine readiness. If error 14258 appears, wait and rerun.
EXEC dbo.sp_is_sqlagent_starting;
GO
IF NOT EXISTS(SELECT 1 FROM dbo.sysjobs WHERE name=N'SupportLab-IntentionalFailure')
 EXEC dbo.sp_add_job @job_name=N'SupportLab-IntentionalFailure',@enabled=1;
GO
IF NOT EXISTS(SELECT 1 FROM dbo.sysjobsteps s JOIN dbo.sysjobs j ON j.job_id=s.job_id
 WHERE j.name=N'SupportLab-IntentionalFailure' AND s.step_name=N'Training failure')
 EXEC dbo.sp_add_jobstep @job_name=N'SupportLab-IntentionalFailure',@step_name=N'Training failure',
 @subsystem=N'TSQL',@database_name=N'SupportLab',@command=N'THROW 51000, ''Synthetic training job failure'', 1;';
GO
IF NOT EXISTS(SELECT 1 FROM dbo.sysjobservers s JOIN dbo.sysjobs j ON j.job_id=s.job_id
 WHERE j.name=N'SupportLab-IntentionalFailure')
 EXEC dbo.sp_add_jobserver @job_name=N'SupportLab-IntentionalFailure';
GO
