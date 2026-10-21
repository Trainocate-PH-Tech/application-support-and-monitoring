"""Checks for the guided Markdown revision; never touches EC2 or privileged state."""
import os,re,subprocess,tempfile,unittest
from pathlib import Path
import build_course
from guided_exercises import GUIDES,render_exercise
ROOT=Path(__file__).resolve().parents[1]
class GuidedMaterialTests(unittest.TestCase):
    def test_all_guides_match_authoring_source(self):
        self.assertEqual(len(GUIDES),27)
        for m,labs in build_course.MODULES.items():
            self.assertEqual(sum(x['minutes'] for x in labs if isinstance(x['minutes'],int)),370)
            for n,lab in enumerate(labs,1):
                path=ROOT/f'module{m}/exercises/{lab["slug"]}.md'
                text=path.read_text()
                self.assertEqual(text.strip(),render_exercise(m,n,lab).strip(),path)
                nums=list(map(int,re.findall(r'^### Step (\d+) —',text,re.M)))
                self.assertEqual(nums,list(range(1,len(GUIDES[m,n]['steps'])+1)))
                for part in re.split(r'^### Step \d+ —.*$',text,flags=re.M)[1:]:
                    for label in ('**Where and who:**','**Expected result:**','**If it differs:**'):
                        self.assertIn(label,part,path)
                self.assertIn('## Cleanup and recovery',text)
                self.assertIn('## Submission checklist',text)
                self.assertNotIn('## Command worksheet',text)
                self.assertNotIn('Complete the preceding required exercises and the module setup.',text)
    def test_fences_syntax_and_control_characters(self):
        paths=list(ROOT.glob('module*/exercises/*.md'))+[ROOT/'shared/instructor/storage.md',ROOT/'shared/learner-start.md']
        checked=0
        for p in paths:
            text=p.read_text()
            self.assertEqual(sum(line.startswith('```') for line in text.splitlines())%2,0,p)
            self.assertFalse(any(ord(c)<32 and c not in '\n\t\r' for c in text),p)
            for lang,code in re.findall(r'```(\w+)\n(.*?)\n```',text,re.S):
                if lang=='bash':
                    self.assertNotRegex(code,r"(?m)^'\s*(?:$|[\"$])",p)
                    r=subprocess.run(['bash','-n'],input=code,capture_output=True,text=True)
                    self.assertEqual(r.returncode,0,(p,r.stderr));checked+=1
                elif lang=='sql':
                    self.assertFalse(re.search(r'^#\s*(SELECT|SHOW|ROLLBACK)',code,re.M),p)
        self.assertGreater(checked,100)
    def test_challenges_keep_independent_diagnosis(self):
        for key in [(1,8),(1,9),(2,9),(3,7),(3,9)]:
            g=GUIDES[key];self.assertTrue(g['challenge'])
            all_code='\n'.join(s['code'] for s in g['steps'])
            self.assertNotRegex(all_code,r'fault\.sh (db-auth|startup|permissions|latency|payment)')
        bank=(ROOT/'shared/fixtures/command-challenges.md').read_text()
        self.assertEqual(list(map(int,re.findall(r'^## Task (\d+)',bank,re.M))),list(range(1,19)))
    def execute(self,code,home,input=''):
        # The code being exercised here is explicitly selected nonprivileged learner work.
        return subprocess.run(['bash','-c',code],input=input,text=True,capture_output=True,cwd=ROOT,
            env={**os.environ,'HOME':str(home),'COURSE_ROOT':str(ROOT),'TMPDIR':str(home)})
    def test_file_walkthrough_directory_flow(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            steps=GUIDES[1,2]['steps']
            # Commands execute together so cd transitions match the written session.
            code='\n'.join(steps[i]['code'] for i in (0,1,3,4))
            r=self.execute(code,home,'y\n')
            self.assertEqual(r.returncode,1,r.stderr) # final cat of broken link is intentional
            self.assertTrue((home/'support-lab/fixtures/application.log').exists())
            self.assertTrue((home/'support-lab/files-practice/work/compression.txt.gz').exists())
            link=home/'support-lab/files-practice/work/latest'
            self.assertTrue(link.is_symlink());self.assertFalse(link.exists())
    def test_pipeline_walkthrough_preserves_names(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            (home/'support-lab/evidence/m1-04').mkdir(parents=True)
            prep='mkdir -p ~/support-lab/fixtures\ntar -xzf "$COURSE_ROOT/shared/fixtures/support-fixtures.tar.gz" -C ~/support-lab/fixtures\ncd ~/support-lab/fixtures\n'
            r=self.execute(prep+'\n'.join(GUIDES[1,4]['steps'][i]['code'] for i in (1,2,3,4)),home)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn('pipeline_exit=1',r.stdout)
            self.assertTrue((home/'support-lab/archive/selected.tar.gz').exists())
    def test_retention_walkthrough_isolated_home(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            r=self.execute('\n'.join(GUIDES[3,5]['steps'][i]['code'] for i in (3,4)),home)
            self.assertEqual(r.returncode,0,r.stderr)
            survivors=list(home.rglob('unrelated.txt'))
            self.assertEqual(len(survivors),1)
            self.assertFalse(list(home.rglob('incident-old.tar.gz')))
    def test_both_sql_blocking_sessions_rollback(self):
        g=GUIDES[2,7]
        step=next(s for s in g['steps'] if s['title']=='Create a bounded wait in B')
        self.assertIn('BEGIN TRAN;',step['code'])
        for title in ('Release A’s transaction','Release B and verify data'):
            release=next(s for s in g['steps'] if s['title']==title)
            self.assertIn('ROLLBACK;',release['code'])
if __name__=='__main__':unittest.main(verbosity=2)
