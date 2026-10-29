from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import report_pages as r

ROOT=Path(__file__).resolve().parents[1]


class ReportPagesTests(unittest.TestCase):
    def test_public_sources_have_consistent_provenance_and_no_private_paths(self):
        folder=ROOT/r.SOURCE;manifest=json.loads((folder/'publication-manifest.json').read_text())
        for name,checksum in manifest['supporting_files'].items():
            self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),checksum,name)
        for report in manifest['reports']:
            self.assertEqual(hashlib.sha256((folder/report['public_report']).read_bytes()).hexdigest(),report['public_sha256'])
        for name in r.FILES:
            text=(folder/name).read_text()
            self.assertNotRegex(text,r'(?:file://|/Users/|/home/claude|/root/\.claude|access_token=|gh[pousr]_[A-Za-z0-9]{20})',name)
        capture=json.loads((folder/'claude-capture-review.json').read_text())
        self.assertFalse(capture['raw_capture_published']);self.assertEqual(len(capture['records']),35)
        self.assertEqual(sum(row['ui_outcome_label']=='Error' for row in capture['records']),5)
        self.assertEqual(sum(row['explicit_exit_code'] is not None for row in capture['records']),5)

    def test_every_authored_report_link_resolves_to_public_destination(self):
        for name in r.MARKDOWN:
            source=ROOT/r.SOURCE/name
            for label,target in re.findall(r'\[([^\]\n]+)\]\(([^)\n]+)\)',source.read_text()):
                self.assertIsNotNone(r.link_target(target,source,ROOT),(name,label,target))

    def test_renders_readable_structure_and_escapes_model_supplied_html(self):
        source=ROOT/r.SOURCE/'claude.md'
        text='# Review\n\n> **Scope:** bounded\n\n| Claim | Evidence |\n| --- | --- |\n| <script>alert(1)</script> | `code` |\n\n- First\n  continued\n- Second\n\n```html\n<img src=x onerror=alert(1)>\n```\n'
        page=r.render_markdown(text,source,ROOT)
        for marker in ['id="review"','<blockquote>','<table>','scope="col"','<ul>','First continued','<pre><code>']:
            self.assertIn(marker,page)
        self.assertNotIn('<script>',page);self.assertNotIn('<img',page)
        self.assertIn('&lt;script&gt;',page)

    def test_unsafe_links_never_become_anchors(self):
        source=ROOT/r.SOURCE/'claude.md'
        for target in ['javascript:alert(1)','data:text/html,x','file:///tmp/private','//example.test/x','https://user:pass@example.test/','https://example.test:0/','https://example.test:99999/','https://example.test/%zz','https://example.test/a b','../../../../private.md']:
            self.assertIsNone(r.link_target(target,source,ROOT),target)
        self.assertNotIn('<a ',r.inline('[run](javascript:alert(1)) <img src=x>',source,ROOT))

    def test_local_reports_and_fragment_links_use_html_routes(self):
        source=ROOT/r.SOURCE/'claude.md'
        self.assertEqual(r.link_target('README.md',source,ROOT),'index.html')
        self.assertEqual(r.link_target('corrections.md#claude-report',source,ROOT),'corrections.html#claude-report')
        self.assertEqual(r.link_target('publication-manifest.json',source,ROOT),'publication-manifest.json')
        self.assertEqual(r.link_target('../../ai-evaluation.md',source,ROOT),r.REPOSITORY+'docs/ai-evaluation.md')

    def test_generation_is_deterministic_and_admits_only_reviewed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out1,out2=Path(tmp)/'one',Path(tmp)/'two'
            self.assertEqual(r.generate(ROOT,out1),r.generate(ROOT,out2))
            names={p.relative_to(out1).as_posix() for p in out1.rglob('*') if p.is_file()}
            self.assertEqual(names,{'reports/'+name for name in (*r.FILES,*r.PAGES.values())})
            for name in names:self.assertEqual((out1/name).read_bytes(),(out2/name).read_bytes())
            page=(out1/'reports/claude.html').read_text()
            self.assertIn('claude-capture-review.html',page);self.assertIn('corrections.html#claude-report',page)
            self.assertIn('lang="en-GB"',page);self.assertIn('Skip to content',page)

    def test_tampered_public_source_fails_before_writing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';folder=root/r.SOURCE;shutil.copytree(ROOT/r.SOURCE,folder)
            (folder/'claude.md').write_text('changed')
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):
                r.generate(root,Path(tmp)/'output')
            self.assertFalse((Path(tmp)/'output').exists())

    def test_missing_public_collection_keeps_other_build_fixtures_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(r.generate(Path(tmp),Path(tmp)/'output'),[])
