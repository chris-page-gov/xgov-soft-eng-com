#!/usr/bin/env python3
"""Package only admitted public material, with deterministic archive metadata."""
import gzip
import hashlib
import io
from pathlib import Path
import shutil
import tarfile

import catalogue as c


def main():
    root=c.ROOT
    c.check_output(root/"generated")
    manifest=c.read(root/"generated/build-manifest.json")
    if manifest["controlled_inputs"]!=c.controlled_inputs(root):
        raise ValueError("Controlled inputs changed after build; rebuild and assure first")
    dist=root/"dist";dist.mkdir(exist_ok=True)
    selected=[]
    for pattern in ("*.md","LICENSE","pyproject.toml","uv.lock",".python-version","requirements-assurance.txt","okf.*.json","config/**/*","schemas/**/*","scripts/*.py","tests/*.py","docs/**/*","source/**/*","generated/**/*",".github/workflows/*"):
        selected.extend(p for p in root.glob(pattern) if p.is_file() and "__pycache__" not in p.parts and p.name!=".DS_Store")
    archive=dist/"xgov-okf.tar.gz"
    with archive.open("wb") as raw, gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped, tarfile.open(mode="w|",fileobj=zipped,format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(set(selected)):
            name="xgov-okf/"+path.relative_to(root).as_posix()
            data=path.read_bytes()
            info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644
            tar.addfile(info,io.BytesIO(data))
    for name in ("record-hashes.json","build-manifest.json","quality.json"):
        shutil.copyfile(root/"generated"/name,dist/name)
    names=["xgov-okf.tar.gz","record-hashes.json","build-manifest.json","quality.json"]
    (dist/"SHA256SUMS").write_text("".join(hashlib.sha256((dist/name).read_bytes()).hexdigest()+"  "+name+"\n" for name in names))
    (dist/"release-notes.md").write_text("Experimental cross-government software discovery pack.\n\nSource SHA-256: "+manifest["source"]["sha256"]+"\n\nBuild identity: "+manifest["build_id"]+"\n\nUnreviewed classification rules; no vulnerability scan or complete Explorer consumer acceptance. See the included evidence and documentation.\n")
    print(archive)


if __name__=="__main__":main()
