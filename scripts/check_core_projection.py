#!/usr/bin/env python3
"""Independently replay the generated 0.3 core Markdown projection."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue


def parse_generated_frontmatter(raw: bytes) -> tuple[dict, bytes]:
    text = raw.decode('utf-8')
    if not text.startswith('---\n'):
        raise ValueError('Typed concept has no YAML frontmatter')
    boundary = text.find('\n---\n', 4)
    if boundary < 0:
        raise ValueError('Typed concept frontmatter is not closed')
    metadata = {}
    for line in text[4:boundary].splitlines():
        key, separator, value = line.partition(': ')
        if not separator:
            raise ValueError('Frontmatter is not in the generator’s reviewed JSON-valued subset')
        name = json.loads(key)
        if name in metadata:
            raise ValueError('Duplicate frontmatter key')
        metadata[name] = json.loads(value)
    return metadata, text[boundary + len('\n---\n'):].encode('utf-8')


def check(root: Path = ROOT, output_path: Path | None = None) -> dict:
    output = Path(output_path) if output_path is not None else root / 'generated'
    taxonomy = catalogue.read(root / 'config/taxonomy.json')
    descriptor = catalogue.read(output / 'okf-explorer.json')
    projection = catalogue.read(output / descriptor['entrypoints']['okf_core_reader'])
    if descriptor.get('okf_version') != '0.3' or projection.get('okf_version') != '0.3':
        raise ValueError('Large-corpus descriptor and core projection must both declare OKF 0.3')
    if projection.get('bundle_id') != 'https://chris-page-gov.github.io/xgov-soft-eng-com/okf-core-explorer.json':
        raise ValueError('Core Reader projection identity changed')
    expected = {}
    for scheme in ('domains', 'capabilities', 'content_types'):
        for entry in taxonomy.get(scheme, []):
            route = scheme.replace('_', '-') + '/' + entry['id'] + '.md'
            expected[route] = entry
    nodes = projection.get('nodes')
    if not isinstance(nodes, dict) or set(nodes) != set(expected):
        raise ValueError('Core Reader projection does not cover the exact typed taxonomy route set')
    source_rows = {row['route']: row for row in projection['meta']['source_documents']}
    if set(source_rows) != set(nodes):
        raise ValueError('Core source inventory does not cover every projected route exactly once')
    for route, entry in expected.items():
        node = nodes[route]
        source = source_rows[route]
        path = source.get('path')
        if not isinstance(path, str) or not path.startswith('concepts/') or '..' in Path(path).parts:
            raise ValueError('Core source file path is unsafe or outside the typed concept tree')
        raw = (output / path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != source.get('sha256') or digest != node.get('source_sha256') or len(raw) != node.get('source_bytes'):
            raise ValueError('Core source digest or byte count differs from its Reader record')
        frontmatter, body = parse_generated_frontmatter(raw)
        if frontmatter != node.get('frontmatter') or node.get('frontmatter') != {key: value for key, value in node.items() if key in frontmatter}:
            raise ValueError('Reader frontmatter does not equal the actual Markdown source')
        if body.decode('utf-8') != node.get('body'):
            raise ValueError('Reader body does not equal the actual Markdown source')
        if frontmatter.get('type') != 'Concept' or frontmatter.get('okf_version') != '0.3':
            raise ValueError('Projected source is not a typed OKF 0.3 concept')
        if frontmatter.get('title') != entry['label'] or frontmatter.get('taxonomy_record') != entry:
            raise ValueError('Projected frontmatter differs from the authoritative taxonomy entry')
        if node.get('core_role') != 'concept' or node.get('route') != route:
            raise ValueError('Projected core role or semantic route is invalid')
        if source.get('semantic_id') != frontmatter.get('@id') or node.get('semantic_id') != frontmatter.get('@id'):
            raise ValueError('Semantic identity differs between Markdown and Reader projections')
    if projection.get('edges') != [] or projection['meta'].get('core_reference_pairs') != 0:
        raise ValueError('Generated taxonomy has no independently authored core edges')
    if projection['meta'].get('source_documents') is None:
        raise ValueError('Core source document inventory is absent')
    if projection['meta'].get('navigation') is None:
        raise ValueError('Reader navigation pages are absent')
    for page in projection['meta']['navigation']:
        raw = (output / page['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != page['source_sha256'] or raw.decode('utf-8') != page['body']:
            raise ValueError('Reader navigation differs from the generated Markdown page')

    records = catalogue.records_from(output)
    if any(record.get('core_role') != 'extension' for record in records):
        raise ValueError('Source-backed repository metadata rows must remain profile extensions')
    semantic_manifest = catalogue.read(output / 'semantic/manifest.json')
    semantic_concepts = {}
    repositories = {}
    vocabulary = output / 'semantic/vocabulary.jsonld.gz'
    if vocabulary.exists():
        for node in json.loads(gzip.decompress(vocabulary.read_bytes()))['@graph']:
            if node.get('@type') == 'http://www.w3.org/2004/02/skos/core#Concept':
                semantic_concepts[node['@id']] = node
    for item in semantic_manifest['shards']:
        raw = (output / item['path']).read_bytes()
        decoded = gzip.decompress(raw) if item['path'].endswith('.gz') else raw
        for node in json.loads(decoded)['@graph']:
            if node.get('@type') == 'http://www.w3.org/2004/02/skos/core#Concept':
                semantic_concepts[node['@id']] = node
            elif node.get('@type') == 'urn:okf:xgov:Repository':
                repositories[node['@id']] = node
    concepts = {identity: node for identity, node in semantic_concepts.items()
                if node.get('urn:okf:xgov:coreRole') == 'concept'}
    if len(concepts) != sum(len(taxonomy.get(scheme, [])) for scheme in ('domains', 'capabilities', 'content_types')):
        raise ValueError(f'Large-corpus semantic graph core taxonomy count differs: {len(concepts)} versus {sum(len(taxonomy.get(scheme, [])) for scheme in ("domains", "capabilities", "content_types"))}')
    if any(node.get('urn:okf:xgov:coreRole') != 'concept' for node in concepts.values()):
        raise ValueError('Typed taxonomy concepts lack their core concept role')
    if any(node.get('urn:okf:xgov:coreRole') != 'extension'
           for identity, node in semantic_concepts.items() if identity not in concepts):
        raise ValueError('Non-core semantic concept rows must be explicit profile extensions')
    if any(node.get('urn:okf:xgov:coreRole') != 'extension' for node in repositories.values()):
        raise ValueError('Repository metadata graph rows must remain profile extensions')
    counts = descriptor.get('extensions', {}).get('okf-core.v0.3', {})
    if counts.get('typed_markdown_concepts') != len(nodes) or counts.get('metadata_extension_records') != len(records):
        raise ValueError('Descriptor coverage counts differ from actual core and extension rows')
    return {'status': 'passed', 'typed_markdown_concepts': len(nodes),
            'core_reference_pairs': 0, 'metadata_extension_records': len(records),
            'metadata_graph_taxonomy_concepts': len(concepts),
            'metadata_graph_repository_nodes': len(repositories),
            'reader_projection_sha256': hashlib.sha256((output / descriptor['entrypoints']['okf_core_reader']).read_bytes()).hexdigest()}


if __name__ == '__main__':
    try:
        print(json.dumps(check(), indent=2))
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'Core projection check failed: {error}') from error
