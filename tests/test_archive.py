import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import catalogue as c
import archive


class ArchiveTests(unittest.TestCase):
    def candidate(self,destination,omit=None,private=False):
        files={".gitignore":b"generated/\n","source/raw.json":b"[]\n","generated/index.md":b"# Public pack\n"}
        manifest={"controlled_inputs":{".gitignore":c.digest(files['.gitignore'])},"source":{"path":"source/raw.json","sha256":c.digest(files['source/raw.json'])},"outputs":{"index.md":c.digest(files['generated/index.md'])}}
        files['generated/build-manifest.json']=c.encoded(manifest)
        files['source/current.json']=c.encoded(manifest['source'])
        if private:files['.consent/request.md']=b'Synthetic private request fixture'
        with tarfile.open(destination,'w:gz') as tar:
            for name,value in files.items():
                if name==omit:continue
                info=tarfile.TarInfo('xgov-okf/'+name);info.size=len(value);tar.addfile(info,io.BytesIO(value))
        return manifest

    def test_all_declared_inputs_and_outputs_travel_with_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pack.tar.gz';manifest=self.candidate(path)
            self.assertEqual(archive.verify_archive(path,manifest),5)

    def test_omitted_hidden_build_input_blocks_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pack.tar.gz';manifest=self.candidate(path,omit='.gitignore')
            with self.assertRaisesRegex(ValueError,'missing declared'):archive.verify_archive(path,manifest)

    def test_private_permission_material_blocks_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pack.tar.gz';manifest=self.candidate(path,private=True)
            with self.assertRaisesRegex(ValueError,'Private or local-only'):archive.verify_archive(path,manifest)

    def test_undeclared_source_file_blocks_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pack.tar.gz';manifest=self.candidate(path)
            with tarfile.open(path,'r:gz') as old:contents={m.name:old.extractfile(m).read() for m in old}
            contents['xgov-okf/source/unadmitted.txt']=b'Synthetic unadmitted material'
            with tarfile.open(path,'w:gz') as tar:
                for name,value in contents.items():
                    info=tarfile.TarInfo(name);info.size=len(value);tar.addfile(info,io.BytesIO(value))
            with self.assertRaisesRegex(ValueError,'Undeclared content'):archive.verify_archive(path,manifest)


if __name__=='__main__':unittest.main()
