import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLITests(unittest.TestCase):
    def test_all_demos_create_reviewable_outputs_without_api_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'result'
            run=subprocess.run([sys.executable,'-m','portfolio','demo','--output',str(output)],
                               capture_output=True,text=True,timeout=15)
            self.assertEqual(run.returncode,0,run.stderr)
            report=json.loads((output/'report.json').read_text())
            self.assertTrue(report['synthetic'])
            self.assertEqual(report['crm']['outcomes'],['review','applied','duplicate','review'])
            self.assertEqual(report['crm']['audit_events'],3)
            self.assertEqual(report['transcript']['turn_count'],3)
            self.assertEqual(report['voice']['final_state'],'closed')
            self.assertEqual(report['voice']['transport_frames'],2)
            self.assertIn('CUSTOMER',(output/'transcript.txt').read_text())
            self.assertTrue((output/'stereo-test.wav').exists())

    def test_rerun_does_not_overwrite_previous_database_or_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'result';output.mkdir();(output/'marker').write_text('keep')
            run=subprocess.run([sys.executable,'-m','portfolio','demo','--output',str(output)],
                               capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            self.assertEqual((output/'marker').read_text(),'keep')
