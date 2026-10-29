#!/usr/bin/env python3
"""Package one independent verifier and one shared prompt for a frozen archive."""
import hashlib
import json
from pathlib import Path
import zipfile
import verify_bundle

read_archive=verify_bundle.read_archive
verify=verify_bundle.verify

PROMPT='''# Shared Claude and Gemini evaluation\n\nUse only the accompanying frozen xgov-okf.tar.gz and this test pack. Read manifest.json first. Check the archive SHA-256, byte length, complete build ID and source hash; stop if any differ. Never substitute a live descriptor, a different release or an earlier local copy.\n\nIf you can execute this reviewed helper, run `python verify_bundle.py --archive xgov-okf.tar.gz --checksums SHA256SUMS --output verification-result.json`. It reads data without extracting or executing archive code. If your environment cannot run Python, mark automated verification UNTESTED and perform the same read-only checks with your own tools. Supply the exact verification code you used and its machine-readable result. Never claim a script was run unless it was.\n\nIndependently find 111Online/nhs111-resources, three Python repositories with reported SBOM paths, and three security helpers. Give complete counts for Python AND SBOM, preserve OR within facets and AND across facets, and distinguish bounded examples from all matches. Separate SBOM references, inspected inventory, quality summaries and vulnerability evidence.\n\nFollow one contributor and one inferred concept relationship. Quote exact assertion IDs, source/target IRIs and routes, predicate, preferred/inverse labels, authority, derivation, status/scope, observation, evidence and rights. Compare runtime and RDF representations. Follow incoming adjacency back to the repository; do not invent an inverse triple. Logical routes need not equal Markdown storage paths.\n\nFor available history, recompute historical/recent commits, additions, deletions and active weeks from the captured observation and its exact window. Explain provider and default-branch limitations. Inspect pending, unavailable and not-collected examples if present. Unknown history is not zero. Report coverage for the full catalogue. A contributor account is not an owner or scan authority.\n\nCompare your computed facts with expected-results.json. For each discrepancy, show test ID, expected value, observed value and exact source path or assertion ID. Correct your own interpretation when the source contradicts it. Report automated PASS/FAIL, manual interpretations and UNTESTED items separately. State archive/source/output/observation counts separately. Do not infer defects merely from network restrictions, deliberate result caps or different snapshot versions.\n\nDo not execute producer or catalogued repository code, scan repositories, contact maintainers, fetch private material or use paid services. Browser and live HTTP checks remain UNTESTED unless you actually perform them; the offline verifier does not establish browser acceptance or exhaustive classification accuracy.\n'''


def create_test_pack(root,archive,destination):
    archive,destination=Path(archive),Path(destination)
    result=verify_bundle.run(archive)
    script=Path(__file__).with_name('verify_bundle.py').read_bytes()
    sha=lambda value:hashlib.sha256(value).hexdigest()
    manifest={'schema':'xgov-ai-test-pack.v1','archive_filename':'xgov-okf.tar.gz','archive_sha256':result['archive_sha256'],'archive_bytes':result['archive_bytes'],'build_id':result['build_id'],'source_sha256':result['source_sha256'],'verifier_sha256':sha(script),'test_case_ids':verify_bundle.CASE_IDS,'expected_result_comparison':'Compare facts and identities; external-checksum and pin statuses depend on supplied companion files.'}
    files={'verify_bundle.py':script,'PROMPT.md':PROMPT.encode(),'manifest.json':verify_bundle.encoded(manifest),'expected-results.json':verify_bundle.encoded(result),'README.md':b'# Frozen AI evaluation pack\n\nGive Claude and Gemini this same pack, xgov-okf.tar.gz and SHA256SUMS from the same release. Check SHA256SUMS before running the helper. The manifest pins the archive and verifier bytes. The helper automatically uses the adjacent manifest.json.\n\nRun: `python verify_bundle.py --archive xgov-okf.tar.gz --checksums SHA256SUMS --output verification-result.json`\n\nThe helper uses Python 3.12 or later and the standard library. It makes no network requests and never executes archive code. Results identify exactly which automated checks passed; browser, live HTTP and broader classification accuracy remain separate. PROMPT.md applies unchanged to both models. Preserve each model\'s verification script and JSON result alongside its narrative.\n'}
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for name,value in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            output.writestr(info,value)
    return {'path':str(destination),'sha256':sha(destination.read_bytes()),'bytes':destination.stat().st_size,'build_id':result['build_id'],'checks':len(result['checks'])}
