import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=next((ROOT/'scripts').glob('*.sh'))
BASH=shutil.which('bash')

class Diagnostics(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)
        self.env=dict(os.environ)
        self.env['PATH']=str(self.path)+os.pathsep+os.environ['PATH']

    def mock(self,name,body):
        path=self.path/name
        path.write_text('#!/bin/sh\n'+body+'\n')
        path.chmod(0o755)
        return str(path)

    def run_script(self):
        return subprocess.run([BASH,str(SCRIPT)],env=self.env,capture_output=True,text=True,timeout=10)

    def prepare(self,log):
        entry=self.path/'moodle root/admin/cli/cron.php'
        entry.parent.mkdir(parents=True)
        entry.write_text('DO NOT EXECUTE')
        self.env['MOODLE_ROOT']=str(entry.parents[2])
        self.env['PHP_BIN']=self.mock('php', '[ "$1" = "--version" ] || exit 99; echo "PHP synthetic"')
        logpath=self.path/'cron.txt'
        logpath.write_text(log)
        self.env['LOG_FILE']=str(logpath)

    def test_counts_without_executing_cron_or_leaking_log(self):
        self.prepare("Cron run completed correctly\nCron run completed correctly\nInvalid get_string() identifier: private detail\n")
        result=self.run_script()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Successful completion markers: 2',result.stdout)
        self.assertIn('Custom language-string warnings: 1',result.stdout)
        self.assertNotIn('private detail',result.stdout)

    def test_no_markers_means_zero_not_a_business_success(self):
        self.prepare('unrelated synthetic line')
        result=self.run_script()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Successful completion markers: 0',result.stdout)

    def test_missing_entry_is_refused(self):
        self.env['MOODLE_ROOT']=str(self.path)
        self.assertEqual(self.run_script().returncode,2)

    def test_missing_log_is_refused(self):
        self.prepare('')
        self.env['LOG_FILE']=str(self.path/'absent')
        self.assertEqual(self.run_script().returncode,2)

if __name__ == "__main__": unittest.main()
