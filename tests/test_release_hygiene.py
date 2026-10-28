from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_release_hygiene as h


class ReleaseHygieneTests(unittest.TestCase):
    def test_conventional_types_scope_and_breaking_marker(self):
        for subject in ('feat(facets): add analysis dimensions','fix(release)!: require complete input archives','docs: explain private setup'):
            self.assertTrue(h.check_subject(subject))
        for subject in ('Update stuff','feat: ','fix: '+('x'*80),'fix: add a full stop.'):
            with self.assertRaises(ValueError):h.check_subject(subject)

    def test_changelog_requires_release_structure_and_links(self):
        good='# Changelog\n\n## [Unreleased]\n\n### Added\n\n- A feature.\n\n## [0.1.0] - 2026-10-28\n\n[Unreleased]: https://example.invalid/compare\n[0.1.0]: https://example.invalid/release\n'
        self.assertTrue(h.check_changelog(good))
        with self.assertRaises(ValueError):h.check_changelog(good.replace('### Added','### Implementation notes'))


if __name__=='__main__':unittest.main()
