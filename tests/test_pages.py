from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import catalogue as c
import pages


class PagesTests(unittest.TestCase):
    def fixture(self, root):
        generated = root / "generated"
        generated.mkdir(parents=True)
        payloads = {
            "okf-explorer.json": c.encoded({"counts": {}, "title": "Experimental"}),
            "record-summary.json": c.encoded({"one": {"title": "Public"}, "two": {"title": "Public"}}),
            "data/index.json": b'{"public":true}\n',
            "walkthrough/core-taxonomy.html": b'<h1>Core taxonomy</h1>\n',
            "walkthrough/notification-software.html": b'<h1>Notification evidence</h1>\n',
        }
        for name, data in payloads.items():
            target = generated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        manifest = {"build_id": "fixture-build", "outputs": {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}}
        (generated / "build-manifest.json").write_bytes(c.encoded(manifest))
        return generated, manifest

    def test_copies_only_manifest_outputs_and_records_receipt_and_landing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            generated, _ = self.fixture(root)
            (generated / "unlisted.json").write_text("not copied")
            destination = Path(tmp) / "pages"
            result = pages.create_candidate(root, destination, check=False)
            self.assertEqual(result["records"], 2)
            self.assertTrue((destination / "data/index.json").is_file())
            self.assertFalse((destination / "unlisted.json").exists())
            landing = (destination / "index.html").read_text()
            self.assertIn("2 repository records", landing)
            self.assertIn("Open in OKF Explorer", landing)
            self.assertIn('href="walkthrough/core-taxonomy.html"', landing)
            self.assertIn('href="walkthrough/notification-software.html"', landing)
            receipt = json.loads((destination / "publication-receipt.json").read_bytes())
            self.assertEqual(receipt["build_id"], "fixture-build")
            self.assertEqual(receipt["descriptor_sha256"], result["descriptor_sha256"])

    def test_rejects_manifest_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            generated, _ = self.fixture(root)
            (generated / "data/index.json").write_text("changed")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                pages.create_candidate(root, Path(tmp) / "pages", check=False)

    def test_rejects_private_component_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            generated, _ = self.fixture(root)
            secret = generated / ".consent" / "grant.json"
            secret.parent.mkdir()
            secret.write_text("private")
            with self.assertRaisesRegex(ValueError, "Private or local-only"):
                pages._safe_relative(".consent/grant.json")
            target = Path(tmp) / "outside.json"
            target.write_text("outside")
            (generated / "data/link.json").symlink_to(target)
            manifest = c.read(generated / "build-manifest.json")
            manifest["outputs"]["data/link.json"] = hashlib.sha256(b"outside").hexdigest()
            c.write(generated / "build-manifest.json", manifest)
            with self.assertRaisesRegex(ValueError, "symlink"):
                pages.create_candidate(root, Path(tmp) / "pages", check=False)

    def test_report_navigation_appears_only_for_manifest_bound_report_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';root.mkdir();generated,manifest=self.fixture(root)
            first=Path(tmp)/'without-reports'
            pages.create_candidate(root,first,check=False)
            self.assertNotIn('reports/',(first/'index.html').read_text())
            report=generated/'reports/index.html';report.parent.mkdir();report.write_bytes(b'<h1>Reviewed reports</h1>')
            manifest['outputs']['reports/index.html']=hashlib.sha256(report.read_bytes()).hexdigest()
            c.write(generated/'build-manifest.json',manifest)
            second=Path(tmp)/'with-reports';pages.create_candidate(root,second,check=False)
            self.assertIn('Early AI evaluation examples',(second/'index.html').read_text())
            self.assertEqual((second/'reports/index.html').read_bytes(),report.read_bytes())

    def test_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            self.fixture(root)
            destination = Path(tmp) / "pages"
            destination.mkdir()
            with self.assertRaises(FileExistsError):
                pages.create_candidate(root, destination, check=False)

    def test_declared_private_files_and_reserved_delivery_names_are_rejected(self):
        for name in ('.consent/grant.json','index.html','publication-receipt.json'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)/'repo';root.mkdir();generated,manifest=self.fixture(root)
                path=generated/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'private fixture')
                manifest['outputs'][name]=hashlib.sha256(path.read_bytes()).hexdigest();c.write(generated/'build-manifest.json',manifest)
                with self.assertRaises(ValueError):pages.create_candidate(root,Path(tmp)/'pages',check=False)

    def test_size_boundary_fails_before_candidate_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';root.mkdir();self.fixture(root);destination=Path(tmp)/'pages'
            with patch.object(pages,'MAX_BYTES',10),self.assertRaisesRegex(ValueError,'size limit'):
                pages.create_candidate(root,destination,check=False)
            self.assertFalse(destination.exists())

    def test_release_checksum_paths_cannot_escape_download_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'SHA256SUMS').write_text('a'*64+'  ../outside\n')
            with self.assertRaisesRegex(ValueError,'Unexpected release checksum entry'):
                pages.prepare_release(root,root,root/'pages')

    def pinned_release_fixture(self, root):
        inventory = {'schema': 'xgov-pinned-published-inputs.v1',
                     'source_release': {'tag': 'frozen-source', 'archive_sha256': 'a'*64},
                     'files': [{'path': 'source/current.json', 'sha256': 'b'*64},
                               {'path': 'source/history/frozen.json', 'sha256': 'c'*64}]}
        name = 'source/published-inputs-2026-10-29.json'
        c.write(root/name, inventory)
        controlled = {'scripts/pages.py': 'd'*64, 'source/current.json': 'e'*64,
                      name: c.digest((root/name).read_bytes())}
        manifest = {'published_input_set': inventory['source_release'],
                    'controlled_inputs': {'scripts/pages.py': 'd'*64,
                                         name: controlled[name],
                                         **{row['path']: row['sha256'] for row in inventory['files']}}}
        return controlled, manifest

    def test_frozen_release_uses_reviewed_source_inventory_and_current_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);controlled,manifest=self.pinned_release_fixture(root)
            with patch.object(c, 'controlled_inputs', return_value=controlled):
                pages.check_release_inputs(root, manifest)
                controlled['scripts/pages.py']='f'*64
                with self.assertRaisesRegex(ValueError, 'build inputs differ'):
                    pages.check_release_inputs(root, manifest)

    def test_frozen_release_rejects_changed_missing_and_extra_source_hashes(self):
        for change in ('changed', 'missing', 'extra'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);controlled,manifest=self.pinned_release_fixture(root)
                if change=='changed': manifest['controlled_inputs']['source/current.json']='e'*64
                elif change=='missing': del manifest['controlled_inputs']['source/history/frozen.json']
                else: manifest['controlled_inputs']['source/unlisted.json']='f'*64
                with patch.object(c, 'controlled_inputs', return_value=controlled), self.assertRaisesRegex(ValueError, 'build inputs differ'):
                    pages.check_release_inputs(root, manifest)

    def test_frozen_release_rejects_a_different_source_release_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);controlled,manifest=self.pinned_release_fixture(root)
            manifest['published_input_set']={**manifest['published_input_set'], 'tag': 'different'}
            with patch.object(c, 'controlled_inputs', return_value=controlled), self.assertRaisesRegex(ValueError, 'source identity differs'):
                pages.check_release_inputs(root, manifest)


if __name__ == "__main__":
    unittest.main()
