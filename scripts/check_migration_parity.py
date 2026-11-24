#!/usr/bin/env python3
"""Compare a candidate with the exact 29 October published 0.2 archive."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ARCHIVE_SHA256 = 'da822774bcf48c3514324cbdd8aa68b8e5231a496f7f10169b827df4a4b4e8be'
SOURCE_SHA256 = 'f7e776c0245d698c62ce7211beaa0d8e90c13f2f431ca82e8a6eb26705bc5bac'
SKOS = 'http://www.w3.org/2004/02/skos/core#'
ROUTE = 'urn:okf:xgov:route'


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def read_member(archive: tarfile.TarFile, name: str) -> bytes:
    member = archive.getmember(name)
    if not member.isreg() or member.size > 30_000_000:
        raise ValueError('Reference member is not a bounded regular file: ' + name)
    handle = archive.extractfile(member)
    if handle is None:
        raise ValueError('Reference member cannot be read: ' + name)
    raw = handle.read(member.size + 1)
    if len(raw) != member.size:
        raise ValueError('Reference member length differs: ' + name)
    return raw


def assertion_map(rows: list[dict]) -> dict[str, dict]:
    output = {}
    for row in rows:
        identity = row.get('id')
        if not isinstance(identity, str) or identity in output:
            raise ValueError('Candidate contains a missing or duplicate assertion ID')
        output[identity] = row
    return output


def load_old_assertions(archive: tarfile.TarFile) -> dict[str, dict]:
    paths = sorted(member.name for member in archive.getmembers()
                   if member.name.startswith('xgov-okf/generated/data/assertions-')
                   and member.name.endswith('.json.gz'))
    if not paths:
        raise ValueError('Reference archive has no assertion chunks')
    all_rows = []
    for name in paths:
        value = json.loads(gzip.decompress(read_member(archive, name)))
        if not isinstance(value, list):
            raise ValueError('Reference assertion chunk is not a JSON array')
        all_rows.extend(value)
    return assertion_map(all_rows)


def load_current_assertions(generated: Path) -> dict[str, dict]:
    paths = sorted((generated / 'data').glob('assertions-*.json.gz'))
    if not paths:
        raise ValueError('Candidate has no assertion chunks')
    return assertion_map([row for path in paths for row in json.loads(gzip.decompress(path.read_bytes()))])


def vocabulary_pairs(raw: bytes) -> set[tuple[str, str]]:
    document = json.loads(gzip.decompress(raw))
    return {(node['@id'], node[ROUTE]) for node in document['@graph']
            if node.get('@type') == SKOS + 'Concept' and isinstance(node.get(ROUTE), str)}


def check(reference_archive: Path, generated: Path) -> dict:
    archive_sha = sha256(reference_archive)
    if archive_sha != REFERENCE_ARCHIVE_SHA256:
        raise ValueError('Reference archive does not match the pinned 29 October published candidate')
    with tarfile.open(reference_archive, mode='r:gz') as archive:
        old_records = json.loads(read_member(archive, 'xgov-okf/generated/record-hashes.json'))
        old_vocabulary = vocabulary_pairs(read_member(archive, 'xgov-okf/generated/semantic/vocabulary.jsonld.gz'))
        old_assertions = load_old_assertions(archive)
    new_records = json.loads((generated / 'record-hashes.json').read_bytes())
    new_assertions = load_current_assertions(generated)
    new_vocabulary = vocabulary_pairs((generated / 'semantic/vocabulary.jsonld.gz').read_bytes())
    if set(old_records) != set(new_records):
        raise ValueError('Repository record identity set changed across same-input migration')
    if old_vocabulary != new_vocabulary:
        raise ValueError('Existing semantic taxonomy identities or routes changed')
    if set(old_assertions) != set(new_assertions):
        raise ValueError('Assertion identity set changed across same-input migration')
    for identity in old_assertions:
        if old_assertions[identity] != new_assertions[identity]:
            raise ValueError('Source assertion or evidence changed during core migration: ' + identity)
    triples = sorted((row['source_iri'], row['predicate'], row['target_iri']) for row in new_assertions.values())
    triple_digest = hashlib.sha256(json.dumps(triples, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    return {'status': 'passed', 'reference_archive_sha256': archive_sha,
            'source_snapshot_sha256': SOURCE_SHA256, 'repository_record_ids_preserved': len(old_records),
            'semantic_taxonomy_id_route_pairs_preserved': len(old_vocabulary),
            'assertion_objects_preserved': len(old_assertions), 'directed_assertion_triples_preserved': len(triples),
            'directed_triples_sha256': triple_digest,
            'comparison': 'same 29 October archived inputs; record payload fields may gain the declared OKF 0.3 extension role'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-archive', type=Path, required=True)
    parser.add_argument('--generated', type=Path, default=ROOT / 'generated')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.reference_archive, args.generated)
        encoded = json.dumps(result, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded)
        print(encoded, end='')
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError, tarfile.TarError) as error:
        raise SystemExit(f'Migration parity check failed: {error}') from error


if __name__ == '__main__':
    main()
