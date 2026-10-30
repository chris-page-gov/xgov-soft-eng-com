"""Synthetic account-review metadata must remain outside public artefacts."""
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import archive
import catalogue
import pages
import verify_bundle
import check_release_hygiene as hygiene


class PrivateAccountBoundaryTests(unittest.TestCase):
    def test_every_publication_plane_rejects_private_account_and_install_paths(self):
        for part in ('.account-security', '.ACCOUNT-SECURITY', 'node_modules', 'NODE_MODULES'):
            name = 'xgov-okf/' + part + '/fixture.json'
            self.assertFalse(verify_bundle.safe(name))
            with self.assertRaisesRegex(ValueError, 'Private'):
                pages._safe_relative(part + '/fixture.json')
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'fixture.tar.gz'
                with tarfile.open(path, 'w:gz') as output:
                    member = tarfile.TarInfo(name); member.size = 2
                    output.addfile(member, io.BytesIO(b'{}'))
                manifest = {'controlled_inputs': {}, 'source': {'path': 'public.json', 'sha256': '0' * 64}, 'outputs': {}}
                with self.assertRaisesRegex(ValueError, 'Private'):
                    archive.verify_archive(path, manifest)
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    verify_bundle.read_archive(path)

    def test_public_symlinks_cannot_admit_private_review_or_installed_dependencies(self):
        for part in ('.account-security', '.ACCOUNT-SECURITY', 'node_modules'):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory); (root / part).mkdir(); (root / 'docs').mkdir()
                private = root / part / 'fixture.md'; private.write_text('Synthetic fixture only')
                (root / 'docs/leak.md').symlink_to(private)
                with self.assertRaisesRegex(ValueError, 'Private'):
                    catalogue.controlled_inputs(root)

    def test_forced_tracking_fails_and_git_ignores_case_variants(self):
        for part in ('.account-security', '.ACCOUNT-SECURITY', 'node_modules'):
            with patch.object(hygiene.subprocess, 'check_output', return_value=(part + '/fixture.json\0').encode()):
                with self.assertRaisesRegex(ValueError, 'Private'):
                    hygiene.check_private_tracking(ROOT)
            subprocess.run(['git', 'check-ignore', '--no-index', '--quiet', part + '/fixture.json'], cwd=ROOT, check=True)

    def test_browser_lock_inputs_are_bound_without_installed_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'node_modules').mkdir()
            for name in ('package.json', 'package-lock.json', '.npmrc'):
                (root / name).write_text('Synthetic ' + name)
            (root / 'node_modules/fixture.json').write_text('Installed fixture')
            hashes = catalogue.controlled_inputs(root)
            self.assertTrue({'package.json', 'package-lock.json', '.npmrc'} <= hashes.keys())
            self.assertFalse(any('node_modules' in name for name in hashes))


if __name__ == '__main__':
    unittest.main()
