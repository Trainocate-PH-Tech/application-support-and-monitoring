"""Offline checks for topic reports and documentation. Run from any directory."""
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SPECS = [
    ('MYSQL_SLOW_QUERY_ANALYSIS', 'mysql-slow', 'mysql-slow-report', ['entries=4', 'total_query_seconds=6.60', 'rows_examined=300000']),
    ('MYSQL_CONTENTION_RELIABILITY', 'mysql-contention', 'mysql-contention-report', ['lag_seconds=UNKNOWN', 'gap seconds=410', 'age seconds=420']),
    ('MSSQL_SUPPORT_DIAGNOSTICS', 'mssql-diagnostics', 'mssql-diagnostics-report', ['avg_elapsed_ms=800.00', 'failed_steps=1 failed_job_outcomes=1']),
    ('MSSQL_BLOCKING_PLAN_REGRESSION', 'mssql-regression', 'mssql-regression-report', ['63 -> 62 -> 61 head=61', 'LCK_M_X delta_ms=12000', 'duration_ms=60.00', 'reads=220.00']),
    ('APP_DB_CORRELATION', 'app-db', 'app-db-correlation-report', ['requests=4 error_requests=2 error_percent=50.00', 'explicit_db_match=q101']),
]

def run(script, source, output):
    return subprocess.run([str(script), str(source), str(output)], capture_output=True, text=True)

def report(result):
    assert result.returncode == 0, result.stderr
    path = Path(result.stdout.strip().removeprefix('Report: '))
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    return path

def main():
    for stem, topic, utility, expected in SPECS:
        script = ROOT / 'shared/scripts' / (utility + '.sh')
        for suffix in ['', '_EXERCISE']:
            doc = ROOT / (stem + suffix + '.md')
            text = doc.read_text()
            assert text.count('```') % 2 == 0, doc
            assert not re.search(r'^## Task ', text, re.M), doc
            for block in re.findall(r'```bash\n(.*?)```', text, re.S):
                r = subprocess.run(['bash', '-n'], input=block, text=True, capture_output=True)
                assert r.returncode == 0, (doc, r.stderr)
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if not link.startswith(('https://', '#')):
                    assert (doc.parent / link.split('#')[0]).exists(), (doc, link)
            if suffix:
                assert '```bash\n' + script.read_text() + '```' in text, doc
        with tempfile.TemporaryDirectory(prefix='db-topic-test-') as tmp:
            work = Path(tmp)
            source = work / 'input with spaces'
            shutil.copytree(ROOT / 'shared/fixtures/db-topics' / topic, source)
            output = work / 'reports with spaces'
            first = report(run(script, source, output))
            for value in expected:
                assert value in first.read_text(), (topic, value)
            assert first != report(run(script, source, output))
            assert run(script, work / 'missing', output).returncode == 2
            assert run(script, source, source / 'provenance.txt').returncode == 2
            # Missing required files cannot masquerade as empty observations.
            provenance = (source / 'provenance.txt').read_text()
            (source / 'provenance.txt').unlink()
            assert run(script, source, output).returncode == 2
            (source / 'provenance.txt').write_text(provenance)
            tables = list(source.glob('*.tsv'))
            if tables:
                table = tables[0]
                original = table.read_text()
                table.write_text(original.splitlines()[0] + '\n')
                report(run(script, source, output))
                table.write_text('wrong header\n')
                assert run(script, source, output).returncode == 2
                table.write_text(original)
            if topic == 'mysql-slow':
                log = source / 'slow.log'
                original = log.read_text()
                log.write_text('')
                assert 'UNKNOWN: no timing headers' in report(run(script, source, output)).read_text()
                log.write_text(original.replace('1.200000', 'invalid', 1))
                assert run(script, source, output).returncode == 2
            if topic == 'mysql-contention':
                (source / 'replica.json').write_text('{broken')
                assert run(script, source, output).returncode == 2
            if topic == 'mssql-diagnostics':
                p = source / 'expensive.tsv'
                p.write_text(p.read_text().replace('17\t100\t', '17\t0\t'))
                assert 'UNKNOWN: zero executions' in report(run(script, source, output)).read_text()
            if topic == 'mssql-regression':
                p = source / 'waits-after.tsv'
                p.write_text(p.read_text().replace('112000', '1'))
                assert 'UNKNOWN: missing baseline, reset, or invalid interval' in report(run(script, source, output)).read_text()
                p = source / 'sessions.tsv'
                original = p.read_text()
                p.write_text(original.replace('61\t0\tsleeping\t1\n', ''))
                assert 'UNKNOWN: blocker not captured' in report(run(script, source, output)).read_text()
                p.write_text(original.replace('61\t0\t', '61\t63\t'))
                assert 'UNKNOWN: cycle' in report(run(script, source, output)).read_text()
                p.write_text(original.replace('61\t0\t', '61\t-2\t'))
                assert 'UNKNOWN: special blocker' in report(run(script, source, output)).read_text()
            if topic == 'app-db':
                p = source / 'db.tsv'
                p.write_text('\n'.join(line for line in p.read_text().splitlines() if not line.startswith('q101\t')) + '\n')
                assert 'UNKNOWN: no explicit database-operation match' in report(run(script, source, output)).read_text()
        print('PASS', topic)
    print('PASS documentation links, Bash syntax, and embedded/reference script consistency')

if __name__ == '__main__':
    main()
