#!/usr/bin/env python3
"""Restore only the JSON inputs pinned from one immutable public release."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'source/published-inputs-2026-10-29.json'
ARCHIVE_PREFIX = 'xgov-okf/'
MAX_ARCHIVE_BYTES = 80_000_000
ALLOWED_DOWNLOAD_HOSTS = {'github.com', 'release-assets.githubusercontent.com'}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(path: Path = MANIFEST) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    release = value['source_release']
    if (value.get('schema') != 'xgov-pinned-published-inputs.v1'
            or release.get('archive_sha256') != 'da822774bcf48c3514324cbdd8aa68b8e5231a496f7f10169b827df4a4b4e8be'
            or release.get('archive_bytes') != 70_468_434
            or release.get('source_commit') != '58eb97ad52c50f9e3c869a57797a1d53e96636b4'):
        raise ValueError('Pinned published-input manifest identity is not recognised')
    rows = value.get('files')
    if not isinstance(rows, list) or len(rows) != 3356 or len(rows) != value.get('source_files_retained'):
        raise ValueError('Pinned published-input inventory is incomplete')
    seen = set()
    for row in rows:
        path_value = row.get('path')
        path = PurePosixPath(path_value) if isinstance(path_value, str) else None
        if (path is None or path.is_absolute() or path.as_posix() != path_value
                or not path_value.startswith('source/')
                or any(part in ('', '.', '..') for part in path.parts)
                or path_value in seen or path.suffix != '.json'
                or type(row.get('bytes')) is not int or row['bytes'] < 0
                or not isinstance(row.get('sha256'), str) or len(row['sha256']) != 64):
            raise ValueError('Pinned input inventory contains an unsafe or malformed entry')
        seen.add(path_value)
    if not {'source/current.json', 'source/history/index.json'}.issubset(seen):
        raise ValueError('Pinned input inventory lacks required source indexes')
    return value


def read_archive(archive_path: Path | None, release: dict) -> bytes:
    if archive_path is not None:
        raw = archive_path.read_bytes()
    else:
        url = release['url']
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname != 'github.com' or parsed.username or parsed.password:
            raise ValueError('Pinned release URL must be credential-free GitHub HTTPS')
        request = urllib.request.Request(url, headers={'User-Agent': 'xgov-okf-pinned-input-restore/1', 'Accept': 'application/octet-stream'})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                final = urllib.parse.urlsplit(response.geturl())
                if final.scheme != 'https' or final.hostname not in ALLOWED_DOWNLOAD_HOSTS:
                    raise ValueError('Release download redirected to an unapproved host')
                raw = response.read(MAX_ARCHIVE_BYTES + 1)
        except urllib.error.URLError as exc:
            raise ValueError('Pinned release archive could not be downloaded') from exc
    if len(raw) > MAX_ARCHIVE_BYTES or len(raw) != release['archive_bytes']:
        raise ValueError('Pinned release archive byte length differs')
    if sha256(raw) != release['archive_sha256']:
        raise ValueError('Pinned release archive SHA-256 differs')
    return raw


def copy_verified_archive(path: Path, raw: bytes, expected_sha256: str) -> None:
    path = Path(path).absolute()
    if path.exists() or path.is_symlink():
        raise ValueError('Archive copy path already exists; select a new private path')
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    if parent.resolve(strict=True) != parent or parent.is_symlink():
        raise ValueError('Archive copy parent must not contain symbolic links')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    if path.is_symlink() or path.stat().st_size != len(raw) or sha256(path.read_bytes()) != expected_sha256:
        path.unlink(missing_ok=True)
        raise ValueError('Copied reference archive failed its exact byte or SHA-256 check')


def restore(archive_path: Path | None, output: Path, manifest_path: Path = MANIFEST,
            archive_copy: Path | None = None) -> dict:
    manifest = load_manifest(manifest_path)
    release = manifest['source_release']
    if output.exists():
        raise ValueError('Output path already exists; select a new private staging path')
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = read_archive(archive_path, release)
    if archive_copy is not None:
        copy_verified_archive(archive_copy, raw, release['archive_sha256'])
    expected = {ARCHIVE_PREFIX + row['path']: row for row in manifest['files']}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.xgov-pinned-inputs-', dir=output.parent))
    seen = set()
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as bundle:
            for member in bundle:
                if member.name in seen:
                    raise ValueError('Pinned archive contains a duplicate source member')
                row = expected.get(member.name)
                if row is None:
                    continue
                if not member.isreg() or member.size != row['bytes']:
                    raise ValueError('Pinned source member is not a regular file of the declared size')
                handle = bundle.extractfile(member)
                if handle is None:
                    raise ValueError('Pinned source member could not be read')
                data = handle.read(row['bytes'] + 1)
                if len(data) != row['bytes'] or sha256(data) != row['sha256']:
                    raise ValueError('Pinned source member differs from its SHA-256 manifest')
                relative = PurePosixPath(row['path'])
                destination = temporary.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                seen.add(member.name)
        if seen != set(expected):
            missing = sorted(set(expected) - seen)
            raise ValueError(f'Pinned archive member coverage is incomplete ({len(missing)} missing)')
        shutil.copyfile(manifest_path, temporary / 'source/published-inputs-2026-10-29.json')
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary.rename(output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {'status': 'passed', 'archive_sha256': release['archive_sha256'],
            'archive_bytes': len(raw), 'source_files': len(seen),
            'history_packages': manifest['history_packages'],
            'output': str(output.resolve()), 'manifest_sha256': sha256(manifest_path.read_bytes())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='Use a previously retained exact release archive')
    parser.add_argument('--output', type=Path, required=True, help='New isolated output directory; existing paths are refused')
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--copy-archive-to', type=Path,
                        help='Optionally retain the checksum-verified archive at a new private path')
    args = parser.parse_args()
    try:
        print(json.dumps(restore(args.archive, args.output, args.manifest, args.copy_archive_to), indent=2))
    except (OSError, KeyError, TypeError, json.JSONDecodeError, tarfile.TarError, ValueError) as exc:
        raise SystemExit(f'Pinned-input hydration failed: {exc}') from exc


if __name__ == '__main__':
    main()
