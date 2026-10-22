"""Offline verification: python3 tools/test_mysql_challenge.py."""
from pathlib import Path
from unittest import mock
import importlib.util
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT.parent / 'module2_challenge_checker.py'
SOLUTION = ROOT.parent / 'MYSQL_CHALLENGE_SOLUTION.md'
SCRIPT = ROOT / 'shared/scripts/mysql-challenge-report.sh'
FIXTURES = ROOT / 'shared/fixtures/mysql-challenge'
spec = importlib.util.spec_from_file_location('module2_checker', CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
ANSWER = ''.join(f'{key}={value}\n' for key, value in checker.EXPECTED.items())


def run(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, **kwargs)


class ChallengeTests(unittest.TestCase):
    def test_checker_cases(self):
        cases = [
            (ANSWER, 20, False),
            (ANSWER.replace('\n', '\r\n'), 20, False),
            (ANSWER.rstrip('\n'), 20, False),
            (ANSWER.replace('8.200000', '8.20'), 20, False),
            (ANSWER.replace('submitted_report_calls=8', 'submitted_report_calls=8.0'), 20, False),
            (ANSWER.replace('baseline_report_calls=0', 'baseline_report_calls=8'), 19, False),
            (ANSWER.replace('evidence_source=SYNTHETIC\n', ''), 19, True),
            (ANSWER + 'evidence_source=SYNTHETIC\n', 19, True),
            ('evidence_source=LIVE\n' + ANSWER, 19, True),
            (ANSWER + 'extra=1\n', 20, True),
            (ANSWER + '\n', 20, True),
            (ANSWER + 'malformed\n', 20, True),
            (ANSWER + 'bad=x=y\n', 20, True),
            ('\n'.join(reversed(ANSWER.splitlines())), 20, True),
            ('', 0, True),
            (ANSWER.replace('SYNTHETIC', 'synthetic'), 19, False),
            (ANSWER.replace('SYNTHETIC', 'SYNTHETIC '), 19, False),
        ]
        for bad in ['NaN', 'Infinity', '-1', '8e0', '8,0', ' 8', '８']:
            cases.append((ANSWER.replace('submitted_report_calls=8', f'submitted_report_calls={bad}'), 19, False))
        for text, correct, format_failure in cases:
            with self.subTest(text=text):
                result = checker.evaluate(text)
                self.assertEqual(result[0], correct)
                self.assertEqual(sum(result[:3]), 20)
                self.assertEqual(bool(result[3]), format_failure)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'evidence with spaces.txt'
            for content, status in [(ANSWER, 0), ('', 1), (ANSWER + 'extra=1\n', 1)]:
                path.write_text(content)
                result = run(['python3', str(CHECKER), str(path)])
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn('Score:', result.stdout)
            path.write_bytes(b'\xff')
            self.assertEqual(run(['python3', str(CHECKER), str(path)]).returncode, 2)
            self.assertEqual(run(['python3', str(CHECKER), tmp]).returncode, 2)
            self.assertEqual(run(['python3', str(CHECKER), str(path)+'-missing']).returncode, 2)
            self.assertEqual(run(['python3', str(CHECKER)]).returncode, 2)
            with mock.patch.object(Path, 'open', side_effect=PermissionError('Access denied')):
                self.assertEqual(checker.main([str(path)]), 2)

    def test_reference(self):
        self.assertEqual(run(['bash', '-n', str(SCRIPT)]).returncode, 0)
        with tempfile.TemporaryDirectory(prefix='module2 test ') as tmp:
            work = Path(tmp)
            source = work / 'input with spaces'
            shutil.copytree(FIXTURES, source)
            output = work / 'module2-evidence.txt'
            for _ in range(2):
                result = run(['bash', str(SCRIPT), str(source)], cwd=work)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(output.read_text(), ANSWER)
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(run(['python3', str(CHECKER), str(output)]).returncode, 0)
            for name in ['baseline.log', 'detail.log', 'results.tsv']:
                original = (source/name).read_text()
                (source/name).write_text('')
                self.assertNotEqual(run(['bash', str(SCRIPT), str(source)], cwd=work).returncode, 0)
                self.assertEqual(output.read_text(), ANSWER)
                (source/name).unlink()
                self.assertNotEqual(run(['bash', str(SCRIPT), str(source)], cwd=work).returncode, 0)
                self.assertEqual(output.read_text(), ANSWER)
                (source/name).write_text(original)
            detail = source / 'detail.log'
            original = detail.read_text()
            detail.write_text(original.replace('0.025000', 'invalid', 1))
            self.assertNotEqual(run(['bash', str(SCRIPT), str(source)], cwd=work).returncode, 0)
            self.assertEqual(output.read_text(), ANSWER)
            detail.write_text(original.replace('0.025000', '0.050000'))
            self.assertEqual(run(['bash', str(SCRIPT), str(source)], cwd=work).returncode, 0)
            self.assertIn('detail_query_seconds=8.400000', output.read_text())
            self.assertNotEqual(run(['bash', str(SCRIPT)], cwd=work).returncode, 0)

    def test_docs_and_fixtures(self):
        self.assertIn(SCRIPT.read_text(), SOLUTION.read_text())
        self.assertIn(ANSWER, SOLUTION.read_text())
        for path in [ROOT/'MYSQL_CHALLENGE.md', SOLUTION]:
            text = path.read_text()
            self.assertEqual(text.count('```') % 2, 0)
            for block in re.findall(r'```bash\n(.*?)```', text, re.S):
                result = run(['bash', '-n'], input=block)
                self.assertEqual(result.returncode, 0, result.stderr)
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if not link.startswith(('http', '#')):
                    self.assertTrue((path.parent/link.split('#')[0]).exists(), link)
        original = (FIXTURES/'original-workload.sql').read_text()
        self.assertEqual(original, (ROOT/'shared/sql/mysql/challenge-workload.sql').read_text())
        self.assertEqual((FIXTURES/'capture-workload.sql').read_text(), original.replace('long_query_time = 1;', 'long_query_time = 0;'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
