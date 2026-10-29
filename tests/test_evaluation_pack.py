import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import archive as packager
import catalogue as c
import evaluation_pack as pack
import verify_bundle as verifier
from test_report_regressions import candidate


def frozen_archive(root):
    candidate(root)
    m=c.read(root/'generated/build-manifest.json');path=root/'xgov-okf.tar.gz'
    with tarfile.open(path,'w:gz') as tar:
        for name in packager.archive_members(m):
            data=(root/name.removeprefix('xgov-okf/')).read_bytes();info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
    return path


class EvaluationPackTests(unittest.TestCase):
    def test_rejects_unsafe_and_duplicate_members(self):
        for names in [('../escape',),('xgov-okf/same','xgov-okf/same')]:
            with self.subTest(names=names),tempfile.TemporaryDirectory() as td:
                path=Path(td)/'a.tar.gz'
                with tarfile.open(path,'w:gz') as tar:
                    for name in names:
                        info=tarfile.TarInfo(name);info.size=1;tar.addfile(info,io.BytesIO(b'x'))
                with self.assertRaisesRegex(ValueError,'[Uu]nsafe|Duplicate'):pack.read_archive(path)

    def test_complete_pack_is_deterministic_and_archive_pinned(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);arc=frozen_archive(root);one=root/'one.zip';two=root/'two.zip'
            pack.create_test_pack(root,arc,one);pack.create_test_pack(root,arc,two)
            self.assertEqual(one.read_bytes(),two.read_bytes())
            with zipfile.ZipFile(one) as z:
                manifest=json.loads(z.read('manifest.json'));expected=json.loads(z.read('expected-results.json'))
                self.assertEqual(expected['status'],'passed');self.assertEqual(expected['facts']['catalogue_records'],6)
                self.assertEqual(expected['facts']['available_profiles_checked'],1)
                self.assertEqual(len(expected['checks']),10)
                self.assertEqual(expected['facts']['history_state_counts']['not-collected'],2)
                self.assertEqual(verifier.digest(z.read('verify_bundle.py')),manifest['verifier_sha256'])
            pin=root/'manifest.json';manifest['archive_sha256']='0'*64;c.write(pin,manifest)
            with self.assertRaisesRegex(ValueError,'paired test pack'):verifier.run(arc,pack_manifest=pin)

    def test_modified_bytes_and_external_checksum_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);arc=frozen_archive(root);data=pack.read_archive(arc)
            data['xgov-okf/generated/index.md']+=b'Changed'
            with self.assertRaisesRegex(ValueError,'checksum differs'):pack.verify(data,'0'*64,arc.stat().st_size)
            sums=root/'SHA256SUMS';sums.write_text('0'*64+'  xgov-okf.tar.gz\n')
            with self.assertRaisesRegex(ValueError,'External SHA256SUMS'):verifier.run(arc,sums)

    def test_semantic_metadata_loss_fails_even_after_rebinding_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);arc=frozen_archive(root);data=pack.read_archive(arc)
            path='semantic/assertions-000.jsonld.gz';key='xgov-okf/generated/'+path
            graph=json.loads(gzip.decompress(data[key]));graph['@graph'][0].pop(c.NS+'authority');data[key]=gzip.compress(c.encoded(graph),mtime=0)
            sem_key='xgov-okf/generated/semantic/manifest.json';sem=json.loads(data[sem_key])
            for row in sem['shards']:
                if row['path']==path:row.update(sha256=c.digest(data[key]),bytes=len(data[key]))
            data[sem_key]=c.encoded(sem)
            manifest_key='xgov-okf/generated/build-manifest.json';manifest=json.loads(data[manifest_key]);manifest['outputs'][path]=c.digest(data[key]);manifest['outputs']['semantic/manifest.json']=c.digest(data[sem_key]);data[manifest_key]=c.encoded(manifest)
            with self.assertRaisesRegex(ValueError,'Runtime/RDF metadata differs'):pack.verify(data,'0'*64,arc.stat().st_size)
