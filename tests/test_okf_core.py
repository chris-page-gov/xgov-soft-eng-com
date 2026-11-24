import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import okf_core
import notification_walkthrough
import core_walkthrough
import hydrate_published_inputs


class CoreProjectionTests(unittest.TestCase):
    def test_export_preserves_source_frontmatter_body_path_and_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.md').write_text('# Index\n')
            (root / 'concepts/index.md').parent.mkdir(parents=True, exist_ok=True)
            (root / 'concepts/index.md').write_text('# Concepts\n')
            source = root / 'concepts/domains/notifications.md'
            source.parent.mkdir(parents=True)
            metadata = {'@context': {'title': 'http://www.w3.org/2004/02/skos/core#prefLabel'},
                        '@id': 'https://example.test/concept/notifications', 'okf_version': '0.3',
                        'type': 'Concept', 'title': 'Notifications'}
            text = okf_core.markdown(metadata, 3, ['notify'])
            source.write_text(text)
            row = {'source_path': 'concepts/domains/notifications.md',
                   'semantic_route': 'domains/notifications.md', 'frontmatter': metadata,
                   'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            result = okf_core.export(root, [row], '0.6.0', 'a' * 64)
            node = result['nodes']['domains/notifications.md']
            self.assertEqual(node['core_role'], 'concept')
            self.assertEqual(node['semantic_id'], metadata['@id'])
            self.assertEqual(node['source_path'], row['source_path'])
            self.assertEqual(node['frontmatter'], metadata)
            self.assertTrue(node['body'].startswith('# Notifications'))
            self.assertEqual(node['source_sha256'], row['source_sha256'])
            self.assertEqual(result['edges'], [])

    def test_core_walkthrough_binds_taxonomy_markdown_descriptor_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source').mkdir()
            (root / 'concepts/capabilities').mkdir(parents=True)
            rule = {'id': 'notifications', 'label': 'Send notifications and messages',
                    'terms': ['notify', 'notifications', 'email', 'sms']}
            taxonomy = {'status': 'experimental-unreviewed',
                        'policy': 'Whole-token or whole-phrase matching against repository name and description only.',
                        'capabilities': [rule]}
            taxonomy_raw = (json.dumps(taxonomy, indent=2) + '\n').encode()
            (root / 'source/taxonomy.json').write_bytes(taxonomy_raw)
            metadata = {'@id': 'urn:example:notifications', 'okf_version': '0.3',
                        'type': 'Concept', 'title': rule['label'], 'taxonomy_record': rule}
            md_raw = (okf_core.markdown(metadata, 334, rule['terms'])).encode()
            (root / 'concepts/capabilities/notifications.md').write_bytes(md_raw)
            node = {'semantic_id': metadata['@id'], 'source_path': 'concepts/capabilities/notifications.md',
                    'source_sha256': hashlib.sha256(md_raw).hexdigest(), 'body': md_raw.decode().split('---\n', 2)[-1],
                    'taxonomy_record': rule}
            descriptor = {'schema': 'okf-explorer-bundle.v0', 'bundle_id': 'https://example.test/core.json',
                          'version': '0.6.0', 'snapshot': 'a' * 64,
                          'nodes': {'capabilities/notifications.md': node}, 'edges': []}
            (root / 'okf-core-explorer.json').write_text(json.dumps(descriptor, sort_keys=True) + '\n')
            result = core_walkthrough.generate(root, descriptor)
            page = (root / result['path']).read_text()
            svg = (root / result['diagram']).read_text()
            mobile_svg = (root / result['mobile_diagram']).read_text()
            evidence = json.loads((root / result['evidence']).read_text())
            self.assertIn('334 repositories matching experimental name and description rules', page)
            self.assertIn('zero authored concept-to-concept edges', page)
            self.assertIn('zero match count does not establish that no relevant software exists', page)
            self.assertIn('config/taxonomy.json', page)
            self.assertIn('config/taxonomy.json', svg)
            self.assertIn('core-taxonomy-mobile.svg', page)
            self.assertIn('fill:#f0f4f8', svg)
            self.assertIn('viewBox="0 0 420 700"', mobile_svg)
            self.assertIn('0 authored core edges', mobile_svg)
            self.assertEqual(evidence['diagrams']['desktop']['sha256'], hashlib.sha256(svg.encode()).hexdigest())
            self.assertEqual(evidence['diagrams']['mobile']['sha256'], hashlib.sha256(mobile_svg.encode()).hexdigest())
            self.assertEqual(evidence['taxonomy_source']['sha256'], hashlib.sha256(taxonomy_raw).hexdigest())
            self.assertEqual(evidence['concept']['source_sha256'], hashlib.sha256(md_raw).hexdigest())
            self.assertEqual(evidence['concept']['core_edges_in_bundle'], 0)
            self.assertEqual(result['source_count'], 2)

    def test_export_rejects_duplicate_routes_and_post_projection_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.md').write_text('# Index\n')
            (root / 'concepts/index.md').parent.mkdir(parents=True, exist_ok=True)
            (root / 'concepts/index.md').write_text('# Concepts\n')
            source = root / 'concepts/domains/notifications.md'
            source.parent.mkdir(parents=True)
            metadata = {'@id': 'https://example.test/notifications', 'okf_version': '0.3',
                        'type': 'Concept', 'title': 'Notifications'}
            source.write_text(okf_core.markdown(metadata, 0, ['notify']))
            item = {'source_path': 'concepts/domains/notifications.md',
                    'semantic_route': 'domains/notifications.md', 'frontmatter': metadata,
                    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(ValueError, 'Duplicate or missing'):
                okf_core.export(root, [item, item], '0.6.0', 'a' * 64)
            source.write_text(source.read_text() + 'changed\n')
            with self.assertRaisesRegex(ValueError, 'bytes changed'):
                okf_core.export(root, [item], '0.6.0', 'a' * 64)

    def test_frontmatter_source_pointer_is_bundle_relative(self):
        metadata = okf_core.frontmatter('domains', {'id': 'notification-services', 'label': 'Notification services'},
                                        'urn:example:notification-services', 'f' * 64, 0)
        self.assertEqual(metadata['sources']['path'], '../../source/taxonomy.json')
        self.assertEqual(metadata['sources']['field'], '/domains/0')


class WalkthroughTests(unittest.TestCase):
    def test_walkthrough_uses_pinned_rows_and_keeps_missing_fields_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = root / 'inputs'
            (inputs / 'source/snapshots').mkdir(parents=True)
            (inputs / 'source/history/observations').mkdir(parents=True)
            feed = []
            records = []
            for index, name in enumerate(('notifications-api', 'notifications-local', 'notifications-release')):
                row = {'owner': 'alphagov', 'name': name, 'url': f'https://github.com/alphagov/{name}',
                       'license': {'spdxId': 'MIT'} if index == 0 else None,
                       'sbom': f'sbom/alphagov/{name}.json.gz' if index < 2 else None}
                feed.append(row)
                observation_raw = json.dumps({'history': 'pending'}).encode()
                observation_path = f'source/history/observations/{index}.json'
                (inputs / observation_path).write_bytes(observation_raw)
                observation_hash = hashlib.sha256(observation_raw).hexdigest()
                records.append({'name': f'alphagov/{name}', 'source_rows': [index],
                                'route': f'repositories/alphagov/{name}.md',
                                'history_coverage': 'pending-provider-statistics',
                                'history_observation': {'path': observation_path, 'sha256': observation_hash},
                                'provenance': {'source_sha256': 'b' * 64},
                                'classification_evidence': {'domains': [], 'capabilities': [], 'content_types': []}})
            feed_raw = json.dumps(feed).encode()
            feed_path = 'source/snapshots/feed.json'
            (inputs / feed_path).write_bytes(feed_raw)
            (inputs / 'source/current.json').write_text(json.dumps({'path': feed_path,
                'sha256': hashlib.sha256(feed_raw).hexdigest(), 'bytes': len(feed_raw)}))
            output = root / 'generated'
            result = notification_walkthrough.generate(output, records, inputs)
            page = (output / result['path']).read_text()
            evidence = json.loads((output / result['evidence_path']).read_text())
            desktop_diagram = (output / result['diagram_path']).read_bytes()
            mobile_diagram = (output / result['mobile_diagram_path']).read_bytes()
            self.assertIn('Source-reported licence:</strong> MIT', page)
            self.assertIn('No SBOM reference reported', page)
            self.assertIn('pending-provider-statistics', page)
            self.assertIn('notification-software-mobile.svg', page)
            self.assertIn('Licence: MIT', mobile_diagram.decode())
            self.assertIn('History: pending-provider-statistics', mobile_diagram.decode())
            self.assertEqual(evidence['diagrams']['desktop']['sha256'], hashlib.sha256(desktop_diagram).hexdigest())
            self.assertEqual(evidence['diagrams']['mobile']['sha256'], hashlib.sha256(mobile_diagram).hexdigest())
            self.assertEqual(len(evidence['records']), 3)
            self.assertEqual(len(evidence['history_observations']), 3)
            self.assertIn('not represented as a byte slice', evidence['extraction_note'])


class PinnedInputManifestTests(unittest.TestCase):
    def test_public_manifest_has_exact_historical_identity_and_file_inventory(self):
        manifest = hydrate_published_inputs.load_manifest()
        self.assertEqual(manifest['source_release']['tag'], 'snapshot-40941783959-1')
        self.assertEqual(len(manifest['files']), 3356)
        self.assertEqual(manifest['history_packages'], 3350)

    def test_manifest_rejects_escape_paths_and_duplicates(self):
        import copy
        manifest = hydrate_published_inputs.load_manifest()
        for mutation in ('../outside.json', 'source/../../outside.json'):
            changed = copy.deepcopy(manifest)
            changed['files'][0]['path'] = mutation
            with self.subTest(path=mutation), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'manifest.json'
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'unsafe or malformed'):
                    hydrate_published_inputs.load_manifest(path)
        changed = copy.deepcopy(manifest)
        changed['files'][1]['path'] = changed['files'][0]['path']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.json'
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'unsafe or malformed'):
                hydrate_published_inputs.load_manifest(path)


if __name__ == '__main__':
    unittest.main()
