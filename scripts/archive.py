#!/usr/bin/env python3
"""Package only admitted public material, with deterministic archive metadata."""
import gzip
import hashlib
import io
from pathlib import Path
import shutil
import tarfile

import catalogue as c


def archive_members(manifest):
    expected={"xgov-okf/"+p:sha for p,sha in manifest["controlled_inputs"].items()}
    expected.update({"xgov-okf/generated/"+p:sha for p,sha in manifest["outputs"].items()})
    expected["xgov-okf/"+manifest["source"]["path"]]=manifest["source"]["sha256"]
    expected.update({"xgov-okf/"+r["path"]:r["sha256"] for r in manifest["source"].get("supplements",{}).values()})
    expected["xgov-okf/generated/build-manifest.json"]=c.digest(manifest)
    expected["xgov-okf/source/current.json"]=c.digest(manifest["source"])
    if manifest["source"].get("baseline_summary"):
        row=manifest["source"]["baseline_summary"];expected["xgov-okf/"+row["path"]]=row["sha256"]
    if manifest["source"].get("baseline_path"):
        expected["xgov-okf/"+manifest["source"]["baseline_path"]]=manifest["baseline_sha256"]
    for row in manifest.get("history_sources",[]):expected["xgov-okf/"+row["path"]]=row["sha256"]
    return expected


def verify_archive(archive,manifest):
    expected=archive_members(manifest)
    found=set()
    with tarfile.open(archive,mode="r|gz") as tar:
        for member in tar:
            if any(part in (".consent",".git",".venv","__pycache__",".DS_Store") for part in Path(member.name).parts):
                raise ValueError("Private or local-only material cannot enter a release archive")
            if member.name not in expected:raise ValueError("Undeclared content cannot enter a release archive: "+member.name)
            if member.name in found:raise ValueError("Duplicate declared archive member")
            stream=tar.extractfile(member)
            if stream is None:raise ValueError("Declared archive input is not a file")
            value=hashlib.sha256()
            while chunk:=stream.read(1024*1024):value.update(chunk)
            if value.hexdigest()!=expected[member.name]:raise ValueError("Archive checksum mismatch: "+member.name)
            found.add(member.name)
    missing=set(expected)-found
    if missing:raise ValueError("Archive is missing declared inputs or outputs: "+", ".join(sorted(missing)))
    return len(found)


def main():
    root=c.ROOT
    c.check_output(root/"generated")
    manifest=c.read(root/"generated/build-manifest.json")
    if manifest["controlled_inputs"]!=c.controlled_inputs(root):
        raise ValueError("Controlled inputs changed after build; rebuild and assure first")
    dist=root/"dist";dist.mkdir(exist_ok=True)
    selected=[root/Path(name).relative_to('xgov-okf') for name in archive_members(manifest)]
    archive=dist/"xgov-okf.tar.gz"
    with archive.open("wb") as raw, gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped, tarfile.open(mode="w|",fileobj=zipped,format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(set(selected)):
            name="xgov-okf/"+path.relative_to(root).as_posix()
            data=path.read_bytes()
            info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644
            tar.addfile(info,io.BytesIO(data))
    verify_archive(archive,manifest)
    for name in ("record-hashes.json","record-summary.json","build-manifest.json","quality.json"):
        shutil.copyfile(root/"generated"/name,dist/name)
    names=["xgov-okf.tar.gz","record-hashes.json","record-summary.json","build-manifest.json","quality.json"]
    (dist/"SHA256SUMS").write_text("".join(hashlib.sha256((dist/name).read_bytes()).hexdigest()+"  "+name+"\n" for name in names))
    (dist/"release-notes.md").write_text("Experimental cross-government software discovery pack.\n\nSource SHA-256: "+manifest["source"]["sha256"]+"\n\nBuild identity: "+manifest["build_id"]+"\n\nUnreviewed classification rules; no vulnerability scan or complete Explorer consumer acceptance. See the included evidence and documentation.\n")
    print(archive)


if __name__=="__main__":main()
