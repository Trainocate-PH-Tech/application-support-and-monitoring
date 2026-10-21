"""Opt-in SQL Server lab checks on a disposable local container, never EC2."""
import concurrent.futures,json,secrets,subprocess,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    name='support-course-sqltest-'+uuid.uuid4().hex[:8];password='Train!'+secrets.token_hex(16);results=[]
    def run(args,text=None,check=True):
        r=subprocess.run(args,input=text,capture_output=True,text=True)
        if check and r.returncode:raise RuntimeError((r.stdout+r.stderr)[-2000:])
        return r
    def sql(text,check=True,user="sa"):
        return run(['docker','exec','-i','-e','SQLCMDPASSWORD='+password,name,'/opt/mssql-tools18/bin/sqlcmd','-S','localhost','-U',user,'-C','-b','-h','-1','-W'],text,check)
    def record(test,ok):
        results.append(dict(test=test,passed=bool(ok)));print(test,'PASS' if ok else 'FAIL',flush=True)
        if not ok:raise AssertionError(test)
    try:
        with tempfile.TemporaryDirectory() as d:
            env=Path(d)/'sql.env';env.write_text('ACCEPT_EULA=Y\nMSSQL_PID=Developer\nMSSQL_AGENT_ENABLED=true\nMSSQL_SA_PASSWORD='+password+'\n');env.chmod(0o600)
            run(['docker','run','-d','--name',name,'--env-file',str(env),'mcr.microsoft.com/mssql/server:2022-latest'])
            for _ in range(120):
                if sql('SELECT 1;\nGO\n',False).returncode==0:break
                time.sleep(1)
            else:raise RuntimeError('SQL Server did not become ready')
            for _ in range(30):
                if sql('EXEC msdb.dbo.sp_is_sqlagent_starting;\nGO\n',False).returncode==0:break
                time.sleep(1)
            record('schema, Query Store and job setup',sql((ROOT/'shared/sql/sqlserver/setup.sql').read_text()).returncode==0)
            record('SQL Server row count','100000' in sql('SELECT COUNT(*) FROM SupportLab.dbo.Transactions;\nGO\n').stdout)
            record('bounded workload',sql((ROOT/'shared/sql/sqlserver/workload.sql').read_text()).returncode==0)
            record('DMV, plans, waits, statistics and Query Store diagnostics',sql((ROOT/'shared/sql/sqlserver/diagnostics.sql').read_text()).returncode==0)
            permissions="""USE master;
CREATE LOGIN teamtest WITH PASSWORD='"""+password+"""';
GRANT VIEW SERVER PERFORMANCE STATE TO teamtest;
GRANT VIEW SERVER STATE TO teamtest;
GO
USE SupportLab;
CREATE USER teamtest FOR LOGIN teamtest;
GRANT SELECT, UPDATE TO teamtest;
GRANT VIEW DATABASE STATE TO teamtest;
GRANT VIEW DATABASE PERFORMANCE STATE TO teamtest;
GO
USE msdb;
CREATE USER teamtest FOR LOGIN teamtest;
ALTER ROLE SQLAgentReaderRole ADD MEMBER teamtest;
GO
"""
            sql(permissions)
            record('learner diagnostic permissions',sql((ROOT/'shared/sql/sqlserver/diagnostics.sql').read_text(),user='teamtest').returncode==0)
            sql('USE SupportLab; EXEC sys.sp_query_store_flush_db;\nGO\n')
            record('Query Store captured plans','CAPTURED' in sql("USE SupportLab; IF EXISTS(SELECT 1 FROM sys.query_store_plan) SELECT 'CAPTURED';\nGO\n").stdout)
            sql("EXEC msdb.dbo.sp_start_job @job_name=N'SupportLab-IntentionalFailure';\nGO\n")
            time.sleep(3)
            record('intentional SQL Agent job failure','EXPECTED_FAILURE' in sql("SELECT 'EXPECTED_FAILURE' FROM msdb.dbo.sysjobhistory h JOIN msdb.dbo.sysjobs j ON j.job_id=h.job_id WHERE j.name=N'SupportLab-IntentionalFailure' AND h.run_status=0;\nGO\n").stdout)
            with concurrent.futures.ThreadPoolExecutor(2) as p:
                a=p.submit(sql,"USE SupportLab; BEGIN TRAN; UPDATE dbo.Players SET points=points+1 WHERE id=1; WAITFOR DELAY '00:00:05'; ROLLBACK;\nGO\n")
                time.sleep(1)
                b=p.submit(sql,"USE SupportLab; SET LOCK_TIMEOUT 2000; UPDATE dbo.Players SET points=points+1 WHERE id=1;\nGO\n",False)
                time.sleep(.5)
                evidence=sql("SELECT 'BLOCKED' FROM sys.dm_exec_requests WHERE blocking_session_id>0;\nGO\n").stdout
                br=b.result();a.result()
            record('blocking observed and timeout bounded','BLOCKED' in evidence and br.returncode!=0 and 'Lock request time out' in br.stdout)
            record('rollback recovery','300' in sql('SELECT SUM(points) FROM SupportLab.dbo.Players;\nGO\n').stdout)
            print(sql('SELECT @@VERSION;\nGO\n').stdout,flush=True)
    finally:
        run(['docker','rm','-f','-v',name],check=False)
        (ROOT/'.build/sqlserver-integration-results.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
