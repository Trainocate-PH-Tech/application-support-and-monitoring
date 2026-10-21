"""Opt-in integration test on disposable local Docker containers; cleans up on exit.
Requires a built WAR and pre-pulled mysql:8.4 and tomcat:10.1.61-jdk17-temurin.
Does not connect to the training EC2 host.
"""
import concurrent.futures, json, os, secrets, subprocess, tempfile, time, urllib.request, urllib.error, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def cmd(args,input=None,check=True):
    r=subprocess.run(args,input=input,capture_output=True,text=True)
    if check and r.returncode:raise RuntimeError(r.stderr[-1200:])
    return r

def main():
    tag='support-course-test-'+uuid.uuid4().hex[:8];db=tag+'-db';app=tag+'-app';pw=secrets.token_hex(16)
    results=[]
    def record(name,passed,detail=''):
        results.append(dict(test=name,passed=bool(passed),detail=detail));print(name, 'PASS' if passed else 'FAIL',flush=True)
        if not passed:raise AssertionError(name+': '+detail)
    try:
        cmd(['docker','network','create',tag])
        with tempfile.TemporaryDirectory(prefix='support-course-') as temp:
            temp=Path(temp);env=temp/'db.env';env.write_text('MYSQL_ROOT_PASSWORD='+pw+'\n');env.chmod(0o600)
            cmd(['docker','run','-d','--name',db,'--network',tag,'--env-file',str(env),'mysql:8.4'])
            def sql(text,check=True):return cmd(['docker','exec','-i','-e','MYSQL_PWD='+pw,db,'mysql','-uroot','--batch','--skip-column-names'],text,check)
            for _ in range(90):
                if sql('SELECT 1;',False).returncode==0:break
                time.sleep(1)
            else:raise RuntimeError('MySQL startup timed out')
            record('mysql seed',sql((ROOT/'shared/sql/mysql/seed.sql').read_text()).returncode==0)
            record('seed row count',sql('SELECT COUNT(*) FROM support_lab.transactions;').stdout.strip()=='100000')
            sql("CREATE USER 'app'@'%' IDENTIFIED BY '"+pw+"'; GRANT SELECT ON support_lab.* TO 'app'@'%';")
            config=temp/'app.properties'
            base=f'db.url=jdbc:mysql://{db}:3306/support_lab?connectTimeout=2000&socketTimeout=5000\ndb.user=app\ndb.password={pw}\ndelay.ms=0\npayment.fail=false\n'
            config.write_text(base)
            cmd(['docker','run','-d','--name',app,'--network',tag,'-p','127.0.0.1::8080','-e','LAB_CONFIG=/lab/app.properties','-v',str(temp)+':/lab:ro','-v',str(ROOT/'shared/app/target/loyalty.war')+':/usr/local/tomcat/webapps/loyalty.war:ro','tomcat:10.1.61-jdk17-temurin'])
            port=cmd(['docker','port',app,'8080/tcp']).stdout.strip().split(':')[-1]
            def get(path):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:'+port+'/loyalty'+path,timeout=10) as r:return r.status,r.read().decode(),r.headers
                except urllib.error.HTTPError as e:return e.code,e.read().decode(),e.headers
            for _ in range(60):
                try:
                    if get('/health')[0]==200:break
                except (OSError,urllib.error.URLError):pass
                time.sleep(1)
            else:raise RuntimeError('Tomcat readiness timeout: '+cmd(['docker','logs',app],check=False).stdout[-1000:])
            record('readiness and JDBC',get('/health')[0]==200)
            status,body,headers=get('/player?id=1')
            record('player and request ID',status==200 and body=='1,Synthetic Player One,100\n' and bool(headers.get('X-Request-ID')))
            record('report total',get('/report')[1]=='transactions=1000 total=10000.00\n')
            record('invalid ID',get('/player?id=invalid')[0]==400)
            record('missing player',get('/player?id=9999')[0]==404)
            config.write_text(base.replace('payment.fail=false','payment.fail=true'))
            record('payment fault with green readiness',get('/payment')[0]==502 and get('/health')[0]==200)
            config.write_text(base.replace('db.password='+pw,'db.password=WRONG'))
            record('DB auth fault with green liveness',get('/health')[0]==503 and get('/live')[0]==200)
            config.write_text(base.replace('delay.ms=0','delay.ms=1500'))
            before=time.monotonic();status=get('/player?id=1')[0];duration=time.monotonic()-before
            record('bounded latency fault',status==200 and 1.4<=duration<5, f'{duration:.2f}s')
            config.write_text(base);record('config reset recovery',get('/health')[0]==200 and get('/payment')[0]==200)
            before=sql('EXPLAIN SELECT COUNT(*),SUM(amount) FROM support_lab.transactions WHERE player_id=42;').stdout
            sql('CREATE INDEX idx_transactions_player ON support_lab.transactions(player_id);')
            after=sql('EXPLAIN SELECT COUNT(*),SUM(amount) FROM support_lab.transactions WHERE player_id=42;').stdout
            record('index plan comparison',before!=after and 'idx_transactions_player' in after)
            sql('DROP INDEX idx_transactions_player ON support_lab.transactions;')
            record('MySQL diagnostics',sql((ROOT/'shared/sql/mysql/diagnostics.sql').read_text()).returncode==0)
            with concurrent.futures.ThreadPoolExecutor(2) as pool:
                a=pool.submit(sql,'USE support_lab; START TRANSACTION; UPDATE players SET points=points+1 WHERE id=1; SELECT SLEEP(2); UPDATE players SET points=points+1 WHERE id=2; ROLLBACK;',False)
                b=pool.submit(sql,'USE support_lab; START TRANSACTION; UPDATE players SET points=points+1 WHERE id=2; SELECT SLEEP(2); UPDATE players SET points=points+1 WHERE id=1; ROLLBACK;',False)
                outputs=[a.result(),b.result()]
            record('deadlock reproduction',sum(r.returncode!=0 for r in outputs)==1 and any('Deadlock' in r.stderr for r in outputs))
            record('deadlock cleanup',sql('SELECT SUM(points) FROM support_lab.players;').stdout.strip()=='600')
            log=cmd(['docker','logs',app]).stdout
            record('logs omit generated password',pw not in log and 'request_id=' in log)
            version=sql('SELECT VERSION();').stdout.strip()
            print('MySQL version:',version,flush=True)
    finally:
        cmd(['docker','rm','-f','-v',app,db],check=False)
        cmd(['docker','network','rm',tag],check=False)
        (ROOT/'.build/app-integration-results.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
