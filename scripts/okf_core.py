"""Portable OKF core concepts alongside the separately governed metadata graph."""

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

CORE_VERSION = '0.3'
NS = 'urn:okf:xgov:'
RDF_JSON = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#JSON'
SKOS = 'http://www.w3.org/2004/02/skos/core#'
OKF_CONTEXT = 'https://chris-page-gov.github.io/okf-explorer/ns#'
TAXONOMY_PATH = 'source/taxonomy.json'


def frontmatter(scheme, rule, identity, taxonomy_sha256, index):
    source_path = '../../' + TAXONOMY_PATH
    if scheme not in ('domains', 'capabilities', 'content_types') or type(index) is not int or index < 0:
        raise ValueError('Unknown taxonomy scheme')
    return {
        '@context': {
            'type': '@type', 'Concept': SKOS + 'Concept',
            'title': SKOS + 'prefLabel', 'route': OKF_CONTEXT + 'route',
            'classification_status': OKF_CONTEXT + 'classificationStatus',
            'taxonomy_record': {'@id': OKF_CONTEXT + 'taxonomyRecord', '@type': '@json'},
            'sources': {'@id': 'http://purl.org/dc/terms/source', '@type': '@json'},
        },
        '@id': identity, 'okf_version': CORE_VERSION, 'type': 'Concept', 'title': rule['label'],
        'route': scheme.replace('_', '-') + '/' + quote(rule['id'], safe='-._~') + '.md',
        'classification_status': 'experimental-unreviewed',
        'scheme': scheme, 'taxonomy_record': dict(rule), 'sources': {
            'path': source_path,
            'sha256': taxonomy_sha256,
            'field': f'/{scheme}/{index}',
        },
    }


def markdown(metadata, count, terms):
    fields = '\n'.join(
        json.dumps(key, ensure_ascii=False) + ': ' + json.dumps(value, ensure_ascii=False)
        for key, value in metadata.items()
    )
    body = (
        '# ' + metadata['title'] + f'\n\n{count:,} repositories match the experimental '
        'name/description rules.\n\nTerms: ' + ', '.join(terms) + '.\n\n'
        'Matches are suggestions, with evidence in each record. A zero count does not '
        'establish absence.\n\n[Inspect the exact classification rules](../../source/taxonomy.json).\n'
    )
    return '---\n' + fields + '\n---\n' + body


def export(output, documents, product_version, snapshot):
    """Keep complete source bytes and their inert metadata in a core Reader view."""
    output = Path(output)
    nodes = {}
    sources = []
    routes = set()
    identities = set()
    for item in sorted(documents, key=lambda row: row['source_path']):
        source_path = item['source_path']
        metadata = item['frontmatter']
        parts = source_path.split('/')
        if any(part in ('', '.', '..') for part in parts) or Path(source_path).is_absolute():
            raise ValueError('Unsafe core source path')
        path = output / source_path
        if path.is_symlink() or not path.resolve().is_relative_to(output.resolve()):
            raise ValueError('Core source must remain a regular bundle file')
        route = item['semantic_route']
        identity = metadata.get('@id')
        if not isinstance(route, str) or route in routes or not isinstance(identity, str) or identity in identities:
            raise ValueError('Duplicate or missing core route/semantic identity')
        routes.add(route)
        identities.add(identity)
        raw = path.read_bytes()
        # The generator emits JSON-valued YAML; the independent Reader parses it
        # separately during acceptance. No YAML context is fetched or executed.
        prefix = '---\n' + '\n'.join(
            json.dumps(key, ensure_ascii=False) + ': ' + json.dumps(value, ensure_ascii=False)
            for key, value in metadata.items()
        ) + '\n---\n'
        text = raw.decode('utf-8')
        if not text.startswith(prefix):
            raise ValueError('Core source frontmatter differs from the declared projection')
        if hashlib.sha256(raw).hexdigest() != item['source_sha256']:
            raise ValueError('Core source bytes changed after generation')
        body = text[len(prefix):]
        nodes[route] = {
            **metadata, 'id': route, 'route': route, 'semantic_id': identity,
            'core_role': 'concept', 'frontmatter': metadata,
            'body': body, 'source_path': source_path,
            'source_bytes': len(raw), 'source_sha256': hashlib.sha256(raw).hexdigest(),
            'section': source_path.split('/')[1],
        }
        sources.append({'route': route, 'semantic_id': identity, 'path': source_path,
                        'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    return {
        'schema': 'okf-explorer-bundle.v0', 'kind': 'okf-bundle', 'okf_version': CORE_VERSION,
        'bundle_id': 'https://chris-page-gov.github.io/xgov-soft-eng-com/okf-core-explorer.json',
        'version': product_version, 'snapshot': snapshot,
        'profile': 'https://github.com/chris-page-gov/xgov-soft-eng-com/blob/main/profiles/xgov-software/v2/index.md',
        'meta': {
            'title': 'Cross-government software discovery core concepts',
            'frontmatter': {'okf_version': CORE_VERSION},
            'navigation': [{'path': path, 'body': (output / path).read_text(),
                            'source_sha256': hashlib.sha256((output / path).read_bytes()).hexdigest()}
                           for path in ('index.md', 'concepts/index.md')],
            'scope': 'Complete typed Markdown concepts; repository metadata and its relationships '
                     'remain explicit custom-profile extensions in okf-explorer.json.',
            'source_documents': sources,
            'core_reference_pairs': 0,
        },
        'nodes': nodes, 'edges': [],
    }
