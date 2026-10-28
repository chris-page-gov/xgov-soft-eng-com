#!/usr/bin/env python3
"""Discover public reporting routes and prepare private, unsent permission requests.

This module never sends messages, starts a scanner or decides legal authority.
An operator must review the owner's response and authority before recording it.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

import catalogue as c

MODES=("published-sbom-advisory-match","repository-static-analysis")


def target(value):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",value):
        raise ValueError("Use a GitHub owner/repository identifier")
    if any(p in (".","..") for p in value.split("/")):raise ValueError("Invalid repository identity")
    return value.casefold()


def vault(root,repository):
    base=Path(root)/".consent"
    if base.is_symlink():raise ValueError("Private consent directory must not be a symbolic link")
    base.mkdir(mode=0o700,exist_ok=True);os.chmod(base,0o700)
    folder=base/target(repository).replace("/","__")
    if folder.is_symlink():raise ValueError("Private repository directory must not be a symbolic link")
    folder.mkdir(mode=0o700,exist_ok=True);os.chmod(folder,0o700)
    return folder


def private_write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
    if path.is_symlink():raise ValueError("Private output must not be a symbolic link")
    raw=value if isinstance(value,bytes) else value.encode() if isinstance(value,str) else c.encoded(value)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        f.write(raw);temporary=Path(f.name)
    os.chmod(temporary,0o600);os.replace(temporary,path)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def github_get(path):
    url="https://api.github.com"+path
    request=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":"xgov-okf-permission-route-discovery"})
    try:
        with urllib.request.build_opener(NoRedirect).open(request,timeout=20) as response:
            raw=response.read(262145)
            if len(raw)>262144:raise ValueError("Route discovery response exceeds 256 KiB")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        if exc.code==404:return None
        raise ValueError(f"Public route lookup returned HTTP {exc.code}; review manually") from None


def discover(root,repository):
    repository=target(repository);owner=repository.split("/")[0]
    metadata=github_get("/repos/"+repository)
    if not metadata:raise ValueError("Public repository not found")
    if metadata.get("private") or metadata.get("full_name","").casefold()!=repository:
        raise ValueError("Repository identity or public visibility requires review")
    policies=[]
    # Explicit candidates: do not infer service domains or guess email addresses.
    for repo,scope in ((repository,"repository"),(owner+"/.github","owner-default-candidate")):
        for name in (".github/SECURITY.md","SECURITY.md","docs/SECURITY.md"):
            result=github_get("/repos/"+repo+"/contents/"+name)
            if not result:continue
            if result.get("type")!="file" or result.get("encoding")!="base64" or result.get("size",0)>65536:
                raise ValueError("Published security policy is oversized or unsupported")
            raw=base64.b64decode(result["content"],validate=False)
            if len(raw)>65536:raise ValueError("Published security policy exceeds 64 KiB")
            policies.append({"scope":scope,"url":result["html_url"],"blob_sha":result["sha"],"content_sha256":hashlib.sha256(raw).hexdigest(),"text":raw.decode("utf-8")})
        if policies:break
    enabled=github_get("/repos/"+repository+"/private-vulnerability-reporting")
    routes={"schema":"xgov-security-routes.v1","repository":repository,"checked_at":c.now(),"security_policy_page":"https://github.com/"+repository+"/security/policy","policies":policies,"private_reporting_status":"enabled" if enabled and enabled.get("enabled") is True else "disabled" if enabled and enabled.get("enabled") is False else "unknown","private_reporting_url":"https://github.com/"+repository+"/security/advisories/new" if enabled and enabled.get("enabled") is True else None,"permission_status":"not-requested","authority":"published-contact-information-only"}
    private_write(vault(root,repository)/"routes.json",routes)
    return {"repository":repository,"policies_found":len(policies),"private_reporting_status":routes["private_reporting_status"],"saved_to":str(vault(root,repository)/"routes.json"),"permission_granted":False}


def request(root,repository,mode,fingerprint):
    repository=target(repository)
    validate_fingerprint(mode,fingerprint)
    folder=vault(root,repository)
    if (folder/"request.md").exists():raise ValueError("A private request draft already exists; review it rather than overwrite it")
    route_data=c.read(folder/"routes.json") if (folder/"routes.json").exists() else {}
    policy=route_data.get("security_policy_page") or "https://github.com/"+repository+"/security/policy"
    description="Compare the exact published SBOM's package versions with vulnerability advisories." if mode==MODES[0] else "Read the exact public source revision using static analysis."
    content=f"""# Unsent permission request: {repository}

Please confirm that you own this repository or are authorised to approve this
work, and whether you permit the following independent experimental analysis.

- Repository: https://github.com/{repository}
- Proposed activity: {description}
- Exact input fingerprint: {fingerprint}
- Tool and version: to agree before work starts.
- Start/end dates, rate limits and stop contact: please confirm.
- Builds, package installation, code execution, exploitation and testing live
  services are outside this request.
- Any transfer of package identities or source material to an external service
  must be identified and agreed before it occurs.

Please identify a private reporting route, any encryption requirements, what
to include in reports, acknowledgement expectations and agreed disclosure terms.
Candidate reporting policy: {policy}
Private GitHub reporting status at last lookup: {route_data.get('private_reporting_status','not checked')}.

If you decline, withdraw approval or need us to stop, we will stop the proposed
analysis. This draft contains no vulnerability claim. No request has been sent.
"""
    scope={"repository":repository,"mode":mode,"input_sha256":fingerprint if mode==MODES[0] else None,"commit_sha":fingerprint if mode==MODES[1] else None,"execute_code":False,"active_service_testing":False,"external_service_transfer":"not-approved"}
    template={"schema":"xgov-scan-permission.v1","status":"pending","scope":scope,"owner_or_delegate":None,"authority_review":{"confirmed":False,"reviewed_by":None,"basis":None},"response_received_at":None,"valid_from":None,"expires_at":None,"reporting":{"route":None,"private_initial_report":True,"disclosure_terms":None},"tool_and_version":None,"conditions":None}
    private_write(folder/"request.md",content)
    private_write(folder/"approval-template.json",template)
    private_write(folder/"report-template.md","# Private candidate vulnerability report\n\nRepository and exact input:\nScanner/version and advisory database date:\nPackage/version and advisory identifier:\nEvidence and reproduction boundaries:\nApplicability: unreviewed / affected / not affected / unknown (with justification)\nSuggested remediation and fixed version, if supported:\nCoverage gaps and unresolved versions:\nAgreed private route and disclosure terms:\n\nKeep this draft private; a scanner match alone is not a confirmed affected deployment.\n")
    return {"repository":repository,"status":"draft-unsent","draft":str(folder/"request.md"),"approval_template":str(folder/"approval-template.json")}


def validate_fingerprint(mode,value):
    if mode not in MODES:raise ValueError("Unsupported scan scope; active service testing is excluded")
    length=64 if mode==MODES[0] else 40
    if not isinstance(value,str) or not re.fullmatch("[0-9a-f]{"+str(length)+"}",value):raise ValueError(f"This scope needs an exact {length}-character lowercase hexadecimal input fingerprint")


def validate_grant(grant,repository,mode,fingerprint,at=None,require_current=True):
    repository=target(repository);validate_fingerprint(mode,fingerprint)
    if grant.get("schema")!="xgov-scan-permission.v1" or grant.get("status")!="approved":raise ValueError("No recorded owner approval for this operation")
    scope=grant.get("scope",{})
    if scope.get("repository")!=repository or scope.get("mode")!=mode:raise ValueError("Approval does not cover this repository and scan mode")
    expected=scope.get("input_sha256") if mode==MODES[0] else scope.get("commit_sha")
    if expected!=fingerprint:raise ValueError("Approval does not cover this exact input")
    if scope.get("execute_code") is not False or scope.get("active_service_testing") is not False or scope.get("external_service_transfer")!="not-approved":raise ValueError("This workflow only supports local non-executing analysis")
    review=grant.get("authority_review",{})
    for value in (grant.get("owner_or_delegate"),review.get("reviewed_by"),review.get("basis"),grant.get("tool_and_version"),grant.get("conditions")):
        if not isinstance(value,str) or not value.strip():raise ValueError("Owner authority, operator review and agreed conditions are required")
    if review.get("confirmed") is not True:raise ValueError("An operator must explicitly confirm the approver's authority")
    start,end,received=(c.parse_date(grant.get(k) or "") for k in ("valid_from","expires_at","response_received_at"))
    current=at or dt.datetime.now(dt.timezone.utc)
    if end<=start or received>current:raise ValueError("Invalid approval dates")
    if require_current and not start<=current<end:raise ValueError("Approval has not started or has expired")
    reporting=grant.get("reporting",{});uri=urllib.parse.urlsplit(reporting.get("route") or "")
    if not ((uri.scheme=="https" and uri.hostname and not uri.username and not uri.password) or (uri.scheme=="mailto" and re.fullmatch(r"[^\s@?]+@[^\s@?]+",uri.path) and not uri.query)):
        raise ValueError("An agreed HTTPS or mailto reporting route is required")
    if reporting.get("private_initial_report") is not True or not str(reporting.get("disclosure_terms") or "").strip():raise ValueError("Private reporting and explicit disclosure terms are required")
    if not re.fullmatch(r"[0-9a-f]{64}",grant.get("approval_evidence_sha256","")):raise ValueError("Approval evidence is required")
    return True


def save_grant(folder,grant):
    name=c.digest(grant)+".json"
    private_write(folder/"grants"/name,grant)
    private_write(folder/"current.json",{"grant":name})


def record(root,repository,approval_file,evidence_file):
    repository=target(repository);folder=vault(root,repository)
    evidence=Path(evidence_file).read_bytes()
    if not evidence or len(evidence)>1048576:raise ValueError("Approval evidence must be non-empty and at most 1 MiB")
    if Path(approval_file).stat().st_size>65536:raise ValueError("Approval record is too large")
    grant=c.read(approval_file);scope=grant.get("scope",{});mode=scope.get("mode")
    fingerprint=scope.get("input_sha256") if mode==MODES[0] else scope.get("commit_sha")
    grant["approval_evidence_sha256"]=hashlib.sha256(evidence).hexdigest()
    validate_grant(grant,repository,mode,fingerprint)
    private_write(folder/"evidence"/(grant["approval_evidence_sha256"]+".bin"),evidence)
    save_grant(folder,grant)
    return {"repository":repository,"status":"owner-approval-recorded-by-operator","scope":mode,"private_record":str(folder/"current.json"),"legal_authority":"operator-reviewed-not-independently-verified"}


def check(root,repository,mode,fingerprint):
    folder=vault(root,repository)
    pointer=c.read(folder/"current.json");name=pointer.get("grant","")
    if not re.fullmatch(r"[0-9a-f]{64}\.json",name):raise ValueError("Invalid private approval pointer")
    raw=(folder/"grants"/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()+".json"!=name:raise ValueError("Approval record checksum mismatch")
    grant=json.loads(raw);validate_grant(grant,repository,mode,fingerprint)
    evidence=folder/"evidence"/(grant["approval_evidence_sha256"]+".bin")
    if hashlib.sha256(evidence.read_bytes()).hexdigest()!=grant["approval_evidence_sha256"]:raise ValueError("Approval evidence checksum mismatch")
    return {"repository":target(repository),"permission_record":"current-for-exact-local-scope","expires_at":grant["expires_at"],"scan_started":False,"report_sent":False}


def revoke(root,repository):
    folder=vault(root,repository);pointer=c.read(folder/"current.json")
    if not re.fullmatch(r"[0-9a-f]{64}\.json",pointer.get("grant","")):raise ValueError("Invalid approval pointer")
    grant=c.read(folder/"grants"/pointer["grant"]);grant["status"]="revoked";grant["revoked_at"]=c.now();save_grant(folder,grant)
    return {"repository":target(repository),"status":"revoked"}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest="command",required=True)
    for command in ("discover","draft","record","check","revoke"):
        p=sub.add_parser(command);p.add_argument("repository")
        if command in ("draft","check"):
            p.add_argument("--mode",choices=MODES,required=True);p.add_argument("--fingerprint",required=True)
        if command=="record":p.add_argument("--approval",type=Path,required=True);p.add_argument("--evidence",type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=="discover":result=discover(c.ROOT,args.repository)
        elif args.command=="draft":result=request(c.ROOT,args.repository,args.mode,args.fingerprint)
        elif args.command=="record":result=record(c.ROOT,args.repository,args.approval,args.evidence)
        elif args.command=="check":result=check(c.ROOT,args.repository,args.mode,args.fingerprint)
        else:result=revoke(c.ROOT,args.repository)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print("Permission workflow stopped: "+str(exc),file=sys.stderr);sys.exit(1)


if __name__=="__main__":main()
