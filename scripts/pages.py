#!/usr/bin/env python3
"""Create a deterministic, static GitHub Pages candidate from checked outputs."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import tarfile
from urllib.parse import quote

import catalogue as c

MAX_BYTES = 1024 * 1024 * 1024
PRIVATE_PARTS = {".consent", ".git", ".venv", "__pycache__", ".ds_store"}
EXPLORER = "https://chris-page-gov.github.io/okf-explorer/explore/?bundle="
DESCRIPTOR_URL = "https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json"


def _safe_relative(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or "\\" in name or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError("Unsafe generated output path: " + name)
    if any(part.casefold() in PRIVATE_PARTS for part in path.parts):
        raise ValueError("Private or local-only material cannot enter a Pages candidate: " + name)
    return path


def _landing(count):
    explorer_url = EXPLORER + quote(DESCRIPTOR_URL, safe="")
    return ("<!doctype html>\n<html lang=\"en-GB\">\n<head>\n"
            "  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "  <title>Experimental cross-government software catalogue</title>\n</head>\n<body>\n"
            "  <main>\n    <h1>Experimental cross-government software catalogue</h1>\n"
            f"    <p>This experimental catalogue contains {count} repository records.</p>\n"
            "    <p>It presents source-reported metadata. Suggested classifications are unreviewed; coverage is limited to the admitted sources and recorded collection period. Repository rights and reported licences are not independently verified. This is not a security assessment.</p>\n"
            f"    <p><a href=\"{html.escape(DESCRIPTOR_URL, quote=True)}\">View the OKF Explorer descriptor</a></p>\n"
            f"    <p><a href=\"{html.escape(explorer_url, quote=True)}\">Open in OKF Explorer</a></p>\n"
            "    <p><a href=\"publication-receipt.json\">Publication receipt and checksums</a> · <a href=\"semantic/manifest.json\">Semantic graph</a> · <a href=\"https://github.com/chris-page-gov/xgov-soft-eng-com\">Source code, documentation and credits</a></p>\n"
            "  </main>\n</body>\n</html>\n").encode("utf-8")


def create_candidate(root, destination, *, check=True):
    """Stage and promote an exact Pages copy of the declared generated outputs."""
    root, destination = Path(root).resolve(), Path(destination).absolute()
    generated = root / "generated"
    if check:
        c.check_output(generated)
    manifest_path = generated / "build-manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Missing or unsafe generated build manifest")
    manifest = c.read(manifest_path)
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("Build manifest has no declared generated outputs")
    selected = dict(outputs)
    if any(name in outputs for name in ('index.html','publication-receipt.json')):
        raise ValueError('Generated outputs collide with Pages delivery files')
    selected["build-manifest.json"] = c.digest(manifest)
    total = 0
    sources = {}
    for name, checksum in selected.items():
        rel = _safe_relative(name)
        source = generated.joinpath(*rel.parts)
        if any(part.is_symlink() for part in (generated, *[generated.joinpath(*rel.parts[:i]) for i in range(1, len(rel.parts) + 1)])) or not source.is_file():
            raise ValueError("Declared generated output is missing or is a symlink: " + name)
        if not source.resolve().is_relative_to(generated.resolve()):
            raise ValueError("Generated output escapes its directory: " + name)
        total += source.stat().st_size
        if total > MAX_BYTES:
            raise ValueError("Pages candidate exceeds the 1 GiB size limit")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != checksum:
            raise ValueError("Generated output checksum mismatch: " + name)
        sources[name] = data
    descriptor_name = "okf-explorer.json"
    if descriptor_name not in outputs:
        raise ValueError("Declared outputs do not include the OKF Explorer descriptor")
    descriptor = json.loads(sources[descriptor_name])
    summary = json.loads(sources["record-summary.json"]) if "record-summary.json" in sources else None
    record_count = len(summary) if isinstance(summary, dict) else None
    if type(record_count) is not int:
        raise ValueError("Declared outputs have no valid repository record summary")
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(sources.items())}
    receipt = {"schema": "xgov-pages-candidate.v1", "build_id": manifest.get("build_id"),
               "descriptor_sha256": hashes[descriptor_name], "generated_files": hashes,
               "records": record_count, "checks": ["manifest-bound generated output hashes verified"]}
    sources["index.html"] = _landing(record_count)
    sources["publication-receipt.json"] = c.encoded(receipt)
    if sum(map(len,sources.values())) > MAX_BYTES:
        raise ValueError('Pages candidate exceeds the 1 GiB size limit including delivery files')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Pages candidate destination already exists: " + str(destination))
    stage = Path(tempfile.mkdtemp(prefix="." + destination.name + ".staging-", dir=destination.parent))
    try:
        for name, data in sorted(sources.items()):
            target = stage.joinpath(*_safe_relative(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            if hashlib.sha256(target.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
                raise ValueError("Staged Pages candidate checksum mismatch: " + name)
        if destination.exists() or destination.is_symlink():
            raise FileExistsError("Pages candidate destination already exists: " + str(destination))
        os.replace(stage, destination)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return receipt


def prepare_release(root, release, destination):
    """Verify an assured release; extract only generated data, never its code."""
    import archive as packager
    root,release=Path(root),Path(release)
    expected={'xgov-okf.tar.gz','xgov-ai-test-pack.zip','verification-result.json','build-manifest.json','record-hashes.json','record-summary.json','quality.json'}
    checked=set()
    for line in (release/'SHA256SUMS').read_text().splitlines():
        checksum,name=line.split('  ',1)
        if name not in expected or name in checked or len(checksum)!=64 or any(ch not in '0123456789abcdef' for ch in checksum):raise ValueError('Unexpected release checksum entry')
        value=hashlib.sha256()
        with (release/name).open('rb') as stream:
            while chunk:=stream.read(1024*1024):value.update(chunk)
        if value.hexdigest()!=checksum:raise ValueError('Release asset checksum mismatch: '+name)
        checked.add(name)
    if checked!=expected:raise ValueError('Release checksum list is incomplete')
    manifest=c.read(release/'build-manifest.json')
    controlled={name:sha for name,sha in c.controlled_inputs(root).items() if name!='source/history/index.json'}
    if any(manifest['controlled_inputs'].get(name)!=sha for name,sha in controlled.items()):raise ValueError('Release build inputs differ from the checked-out producer')
    if set(manifest['controlled_inputs'])-set(controlled)-{'source/history/index.json'}:raise ValueError('Release has undeclared additional producer inputs')
    packager.verify_archive(release/'xgov-okf.tar.gz',manifest)
    with tempfile.TemporaryDirectory(prefix='xgov-pages-release-') as directory:
        extracted=Path(directory)/'xgov-okf'
        with tarfile.open(release/'xgov-okf.tar.gz','r|gz') as archive:
            for member in archive:
                prefix='xgov-okf/generated/'
                if not member.name.startswith(prefix):continue
                if not member.isfile():raise ValueError('Generated release member is not a regular file')
                name=member.name[len(prefix):]
                rel=_safe_relative(name)
                if name!='build-manifest.json' and name not in manifest['outputs']:raise ValueError('Undeclared generated release member')
                target=extracted/'generated'/Path(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True)
                with archive.extractfile(member) as source,target.open('wb') as output:shutil.copyfileobj(source,output)
        return create_candidate(extracted,destination)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, help="new destination directory (default: dist/pages)")
    parser.add_argument('--release',type=Path,help='directory containing all assets from one assured snapshot release')
    args = parser.parse_args(argv)
    destination = args.output or c.ROOT / "dist/pages"
    receipt = prepare_release(c.ROOT,args.release,destination) if args.release else create_candidate(c.ROOT,destination)
    print(json.dumps({key:value for key,value in receipt.items() if key!='generated_files'}, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
