"""Challenge checks. Offline: python3 tools/test_mysql_challenge.py
Optional isolated MySQL 8.4 rehearsal: add --docker. No learner Python required.
"""
from pathlib import Path
import json
import re
import stat
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'shared/scripts/mysql-challenge-report.sh'
WORKLOAD = ROOT / 'shared/sql/mysql/challenge-workload.sql'

def run(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, **kwargs)

def invoke(source, parent):
    return run([str(SCRIPT), str(source), str(parent)])

def report(result):
    assert result.returncode == 0, result.stderr
    p = Path(result.stdout.strip().removeprefix('Report: '))
    assert stat.S_IMODE(p.stat().st_mode) == 0o600
    assert stat.S_IMODE(p.parent.stat().st_mode) == 0o700
    return p

def prepare(source):
    source.mkdir()
    (source/'provenance.txt').write_text('SYNTHETIC automated-test evidence, not production.\n')
    (source/'original-workload.sql').write_text(WORKLOAD.read_text())
    (source/'capture-workload.sql').write_text(WORKLOAD.read_text().replace('long_query_time = 1;', 'long_query_time = 0;'))
    (source/'plan-before.txt').write_text('SYNTHETIC plan placeholder for collector test.\n')

def entry(query, seconds, rows):
    return ('# Time: 2026-10-21T08:00:00.000000Z\n'
            '# User@Host: ticket_reader[ticket_reader] @ localhost [] Id: 10\n'
            f'# Query_time: {seconds:.6f} Lock_time: 0.000000 Rows_sent: 1 Rows_examined: {rows}\n'
            'use mysql_ticket_challenge;\nSET timestamp=1792569600;\n'+query+'\n')

def offline():
    for name in ['MYSQL_CHALLENGE.md', 'MYSQL_CHALLENGE_SOLUTION.md']:
        p = ROOT/name
        text = p.read_text()
        assert text.count('```') % 2 == 0
        for block in re.findall(r'```bash\n(.*?)```', text, re.S):
            r = run(['bash', '-n'], input=block)
            assert r.returncode == 0, (name, r.stderr)
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if not link.startswith(('http', '#')):
                assert (p.parent/link.split('#')[0]).exists(), (name, link)
    assert SCRIPT.read_text() in (ROOT/'MYSQL_CHALLENGE_SOLUTION.md').read_text()
    with tempfile.TemporaryDirectory(prefix='mysql-challenge-test-') as tmp:
        work = Path(tmp); source = work/'input with spaces'; prepare(source)
        probe = entry('SELECT SLEEP(8) AS heartbeat_probe;', 8.0001, 0)
        detail = probe + ''.join(entry(q, .025, 100000) for q in WORKLOAD.read_text().splitlines() if q.startswith('SELECT COUNT'))
        (source/'baseline.log').write_text(probe)
        (source/'detail.log').write_text(detail)
        first = report(invoke(source, work/'reports with spaces'))
        text = first.read_text()
        assert 'captured_report_calls=0' in text
        assert 'captured_report_calls=8 report_seconds=0.200000 report_rows_examined=800000' in text
        assert 'INCOMPLETE_OR_MIXED' in text
        assert 'UNKNOWN: no post-change plan' in text
        assert first != report(invoke(source, work/'reports with spaces'))
        (source/'plan-after.txt').write_text('SYNTHETIC index plan\n')
        assert 'PLAN AND RESULT AFTER CHANGE' in report(invoke(source, work/'reports')).read_text()
        (source/'detail.log').write_text('')
        assert 'UNKNOWN: no timing evidence' in report(invoke(source, work/'reports')).read_text()
        (source/'detail.log').write_text(detail.replace('0.025000', 'invalid', 1))
        assert invoke(source, work/'reports').returncode == 2
        (source/'detail.log').unlink()
        assert invoke(source, work/'reports').returncode == 2
    print('PASS offline report counts, unknown/malformed inputs, private output, repeated runs, spaces, and documentation', flush=True)

def live():
    name = 'mysql-challenge-check-' + uuid.uuid4().hex[:8]
    checks = []
    def sql(query, user='root', tcp=False, check=True):
        args = ['docker', 'exec', '-i', name, 'mysql']
        if tcp: args += ['--protocol=TCP', '-h', '127.0.0.1']
        r = run(args + ['-u', user, '-N', '-B'], input=query)
        if check and r.returncode: raise RuntimeError(r.stderr)
        return r
    def record(message):
        checks.append(message); print('PASS', message, flush=True)
    try:
        r = run(['docker', 'run', '-d', '--rm', '--network', 'none', '--name', name,
                 '-e', 'MYSQL_ALLOW_EMPTY_PASSWORD=yes', 'mysql:8.4'])
        assert r.returncode == 0, r.stderr
        for _ in range(90):
            if sql('SELECT 1;', tcp=True, check=False).returncode == 0: break
            time.sleep(1)
        else: raise RuntimeError('MySQL startup timed out')
        setup = (ROOT/'shared/sql/mysql/challenge-setup.sql').read_text()
        r = sql(setup)
        assert '100000\t2500000.00' in r.stdout and '1000\t25000.00' in r.stdout
        assert sql(setup, check=False).returncode != 0
        sql("CREATE USER 'ticket_reader'@'localhost'; GRANT SELECT ON mysql_ticket_challenge.* TO 'ticket_reader'@'localhost';")
        assert sql('UPDATE mysql_ticket_challenge.ticket_sales SET amount=0 WHERE sale_id=1;',user='ticket_reader',check=False).returncode != 0
        record('new dataset, expected totals, no overwrite, SELECT-only reader')
        sql('SET GLOBAL min_examined_row_limit=7;')
        original = sql('SELECT @@GLOBAL.slow_query_log,@@GLOBAL.log_output,@@GLOBAL.slow_query_log_file,@@GLOBAL.min_examined_row_limit;').stdout.strip().split('\t')
        sql("SET GLOBAL slow_query_log=OFF; SET GLOBAL log_output='FILE'; SET GLOBAL slow_query_log_file='challenge-baseline.log'; SET GLOBAL min_examined_row_limit=0; SET GLOBAL slow_query_log=ON;")
        workload = WORKLOAD.read_text()
        r = sql(workload, user='ticket_reader')
        assert r.stdout.count('1000\t25000.00') == 8, r.stdout
        sql('SET GLOBAL slow_query_log=OFF;')
        baseline_path = sql('SELECT @@GLOBAL.slow_query_log_file;').stdout.strip()
        if not baseline_path.startswith('/'):
            baseline_path = str(Path(sql('SELECT @@datadir;').stdout.strip()) / baseline_path)
        baseline = run(['docker','exec',name,'cat',baseline_path]);assert baseline.returncode==0,baseline.stderr
        sql("SET GLOBAL slow_query_log_file='challenge-detail.log'; SET GLOBAL slow_query_log=ON;")
        r = sql(workload.replace('long_query_time = 1;', 'long_query_time = 0;'), user='ticket_reader')
        assert r.stdout.count('1000\t25000.00') == 8
        sql('SET GLOBAL slow_query_log=OFF;')
        detail_path = sql('SELECT @@GLOBAL.slow_query_log_file;').stdout.strip()
        if not detail_path.startswith('/'):
            detail_path = str(Path(sql('SELECT @@datadir;').stdout.strip()) / detail_path)
        detail = run(['docker','exec',name,'cat',detail_path]);assert detail.returncode==0,detail.stderr
        inspect = (ROOT/'shared/sql/mysql/challenge-inspect.sql').read_text()
        before = sql(inspect, user='ticket_reader').stdout
        sql('CREATE INDEX idx_ticket_event ON mysql_ticket_challenge.ticket_sales(event_id);')
        after = sql(inspect, user='ticket_reader').stdout
        assert 'idx_ticket_event' in after and '1000\t25000.00' in before and '1000\t25000.00' in after
        sql('DROP INDEX idx_ticket_event ON mysql_ticket_challenge.ticket_sales;')
        assert 'idx_ticket_event' not in sql('SHOW INDEX FROM mysql_ticket_challenge.ticket_sales;').stdout
        record('index experiment preserves results and removes its index')
        with tempfile.TemporaryDirectory(prefix='mysql-challenge-live-') as tmp:
            work = Path(tmp); source = work/'input';prepare(source)
            (source/'baseline.log').write_text(baseline.stdout)
            (source/'detail.log').write_text(detail.stdout)
            (source/'plan-before.txt').write_text(before)
            (source/'plan-after.txt').write_text(after)
            text = report(invoke(source, work/'reports')).read_text()
            assert 'captured_report_calls=8' in text, text
            assert text.count('captured_probe_calls=1') == 2, text
            baseline_count = baseline.stdout.count('SELECT COUNT(*) AS sales_count')
            assert 0 <= baseline_count <= 8
            print('Observed baseline report count:', baseline_count, flush=True)
            record('live detail capture accounts for eight reports and one deliberate probe; report parses live format')
        # Restore recorded original settings with SQL literals, not shell interpolation.
        def literal(v): return "'" + v.replace('\\', '\\\\').replace("'", "''") + "'"
        sql('SET GLOBAL slow_query_log=OFF; SET GLOBAL slow_query_log_file='+literal(original[2])+'; SET GLOBAL log_output='+literal(original[1])+'; SET GLOBAL min_examined_row_limit='+original[3]+'; SET GLOBAL slow_query_log='+original[0]+';')
        restored = sql('SELECT @@GLOBAL.slow_query_log,@@GLOBAL.log_output,@@GLOBAL.slow_query_log_file,@@GLOBAL.min_examined_row_limit;').stdout.strip().split('\t')
        assert restored == original
        record('exact original global logging settings restored')
    finally:
        run(['docker','rm','-f','-v',name])
        (ROOT/'.build').mkdir(exist_ok=True)
        (ROOT/'.build/mysql-challenge-validation.json').write_text(json.dumps(checks,indent=2))
        print('Disposable MySQL challenge container removed', flush=True)

if __name__ == '__main__':
    offline()
    if '--docker' in sys.argv: live()
