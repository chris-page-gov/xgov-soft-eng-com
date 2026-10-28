import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import private_starter as p


class PrivateStarterTests(unittest.TestCase):
    def test_first_build_is_offline_empty_and_reads_no_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'private';p.create(root)
            (root/'unadmitted-source.py').write_text('Synthetic unread source canary')
            subprocess.run([sys.executable,str(root/'build.py')],check=True,capture_output=True)
            receipt=json.loads((root/'generated/build-receipt.json').read_text())
            self.assertEqual(receipt['records'],0);self.assertEqual(receipt['source_code_files_read'],0);self.assertEqual(receipt['network_calls'],0)
            self.assertNotIn('Synthetic unread source canary',(root/'generated/okf-bundle.json').read_text())

    def test_existing_destination_and_weakened_policy_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'private';p.create(root)
            with self.assertRaises(ValueError):p.create(root)
            policy=json.loads((root/'okf.private.json').read_text());policy['publication']='enabled';(root/'okf.private.json').write_text(json.dumps(policy))
            run=subprocess.run([sys.executable,str(root/'build.py')],capture_output=True)
            self.assertNotEqual(run.returncode,0)


if __name__=='__main__':unittest.main()
