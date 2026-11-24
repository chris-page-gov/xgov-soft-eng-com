import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import hydrate_published_inputs as hydration


class VerifiedArchiveCopyTests(unittest.TestCase):
    def test_copies_only_to_a_new_private_path_and_verifies_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = b'pinned archive bytes'
            target = root / 'retained.tar.gz'
            hydration.copy_verified_archive(target, raw, hashlib.sha256(raw).hexdigest())
            self.assertEqual(target.read_bytes(), raw)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                hydration.copy_verified_archive(target, raw, hashlib.sha256(raw).hexdigest())

    def test_rejects_digest_mismatch_and_removes_partial_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'retained.tar.gz'
            with self.assertRaisesRegex(ValueError, 'SHA-256 check'):
                hydration.copy_verified_archive(target, b'wrong', '0' * 64)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
