from pathlib import Path
import sys
import subprocess
import tempfile
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

    def test_only_the_temporary_merge_is_exempt(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            def git(*args):return subprocess.check_output(['git','-C',directory,'-c','user.name=Test fixture','-c','user.email=fixture@example.invalid',*args],stderr=subprocess.STDOUT,text=True).strip()
            git('init','--initial-branch=main');git('commit','--allow-empty','-m','chore: initialise fixture');baseline=git('rev-parse','HEAD')
            git('switch','-c','feature');(root/'feature.txt').write_text('Synthetic test data');git('add','feature.txt');git('commit','-m','feat: add fixture')
            git('switch','main');git('commit','--allow-empty','-m','docs: update fixture')
            git('merge','--no-ff','--no-edit','feature')
            h.check_history(root,baseline,True)
            with self.assertRaises(ValueError):h.check_history(root,baseline,False)
            git('commit','--allow-empty','-m','Invalid authored subject')
            with self.assertRaises(ValueError):h.check_history(root,baseline,True)


if __name__=='__main__':unittest.main()
