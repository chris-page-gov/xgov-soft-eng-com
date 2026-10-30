import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
import check_npm_lock


class NpmLockTests(unittest.TestCase):
    def test_checked_in_npm_toolchain_is_locked(self):
        with patch.object(check_npm_lock.subprocess, 'check_output', side_effect=AssertionError('Static checks must not execute Node/npm')):
            self.assertTrue(check_npm_lock.validate(ROOT))

    def test_runtime_verification_is_explicit_and_rejects_version_drift(self):
        for versions in (['v25.0.0\n'], ['v26.7.0\n', '11.0.0\n']):
            with patch.object(check_npm_lock.subprocess, 'check_output', side_effect=versions), self.assertRaises(ValueError):
                check_npm_lock.validate(ROOT, check_runtime=True)

    def test_transitive_lock_requires_registry_integrity_and_credential_free_urls(self):
        for change in (
                lambda lock: lock['packages']['node_modules/playwright'].update(integrity='sha512-invalid'),
                lambda lock: lock['packages']['node_modules/playwright'].update(resolved='https://user:secret@registry.npmjs.org/playwright/-/playwright.tgz'),
                lambda lock: lock['packages']['node_modules/playwright'].update(resolved='https://example.invalid/playwright.tgz'),
                lambda lock: lock['packages']['node_modules/playwright'].update(resolved='https://registry.npmjs.org/unrelated/-/unrelated-1.0.0.tgz'),
                lambda lock: lock['packages'].pop('node_modules/playwright-core'),
                lambda lock: lock['packages']['node_modules/playwright'].update(link=True),
                lambda lock: lock['packages']['node_modules/playwright'].pop('integrity')):
            with self.subTest(change=change):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    for name in ('package.json', '.npmrc', '.github/workflows/pages.yml', '.github/workflows/validate.yml'):
                        target = root / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes((ROOT / name).read_bytes())
                    lock = json.loads((ROOT / 'package-lock.json').read_text())
                    change(lock)
                    (root / 'package-lock.json').write_text(json.dumps(lock))
                    with self.assertRaises(ValueError):
                        check_npm_lock.validate(root)

    def test_manifest_changes_are_rejected_as_lock_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('package.json', 'package-lock.json', '.npmrc', '.github/workflows/pages.yml', '.github/workflows/validate.yml'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            package = json.loads((root / 'package.json').read_text())
            package['devDependencies']['@playwright/cli'] = '0.1.18'
            (root / 'package.json').write_text(json.dumps(package))
            with self.assertRaises(ValueError):
                check_npm_lock.validate(root)

    def test_scripts_and_remote_cli_resolution_are_disabled(self):
        for path, old, new in (
                ('.npmrc', 'ignore-scripts=true', 'ignore-scripts=false'),
                ('.npmrc', 'ignore-scripts=true', 'ignore-scripts=true\nignore-scripts=false'),
                ('.github/workflows/pages.yml', 'npm ci --ignore-scripts --no-audit --no-fund', 'npm install'),
                ('.github/workflows/pages.yml', './node_modules/.bin/playwright-cli', 'npx --yes playwright-cli')):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in ('package.json', 'package-lock.json', '.npmrc', '.github/workflows/pages.yml', '.github/workflows/validate.yml'):
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / name).read_bytes())
                target = root / path
                target.write_text(target.read_text().replace(old, new))
                with self.assertRaises(ValueError):
                    check_npm_lock.validate(root)


if __name__ == '__main__':
    unittest.main()
