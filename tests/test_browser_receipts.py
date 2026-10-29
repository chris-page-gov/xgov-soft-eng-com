import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import collect_browser_receipts as b


class BrowserReceiptTests(unittest.TestCase):
    def fixture(self,root):
        quality=b'{"counts":{"records":2}}\n';(root/'quality.json').write_bytes(quality)
        manifest={'build_id':'a'*64,'outputs':{'okf-explorer.json':'b'*64,'quality.json':hashlib.sha256(quality).hexdigest()}}
        (root/'build-manifest.json').write_text(json.dumps(manifest))
        receipts={name:{'schema':'xgov-browser-acceptance.v1','status':'passed','descriptor_url':b.DESCRIPTOR,'snapshot_id':'a'*64,'descriptor_sha256':'b'*64,'records':2,'consumer_commit':'c'*40,'consumer_app_tree_sha256':'d'*64,'browser':'156.0.8078.48','checks':[{'id':key,'passed':True} for key in sorted(ids)],'console_errors':[],'page_errors':[],'failed_requests':[]} for name,ids in b.expected_checks().items()}
        return receipts

    def write(self,root,receipts):
        for name,receipt in receipts.items():(root/(name+'.txt')).write_text('### Result\n'+json.dumps(receipt)+'\n### Ran Playwright code\n')

    def test_accepts_complete_consistent_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);r=self.fixture(root);self.write(root,r)
            self.assertEqual(b.collect(root/'build-manifest.json',root)['checks'],38)

    def test_rejects_false_success_missing_checks_and_mixed_snapshots(self):
        for mutation in ('status','check','snapshot','consumer','consumer-format','request'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);receipts=self.fixture(root);r=receipts['facets']
                if mutation=='status':r['status']='failed'
                elif mutation=='check':r['checks'].pop()
                elif mutation=='snapshot':r['snapshot_id']='e'*64
                elif mutation=='consumer':r['consumer_commit']='f'*40
                elif mutation=='consumer-format':r['consumer_commit']='unknown'
                else:r['failed_requests']=[{'error':'failed'}]
                self.write(root,receipts)
                with self.assertRaises(ValueError):b.collect(root/'build-manifest.json',root)

    def test_cli_errors_and_quality_tampering_fail_even_with_zero_cli_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);r=self.fixture(root);self.write(root,r)
            (root/'facets.txt').write_text('### Error\nTimeout')
            with self.assertRaises(ValueError):b.collect(root/'build-manifest.json',root)
            self.write(root,r);(root/'quality.json').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'checksum'):b.collect(root/'build-manifest.json',root)


if __name__=='__main__':unittest.main()
