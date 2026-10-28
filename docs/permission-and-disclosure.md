# Ask permission and agree a reporting route

The workflow prepares private drafts and records operator-reviewed owner
approval. It does not send a message, start a scanner or determine legal
authority. Reporting contacts, scan permission and permission to disclose
findings are separate decisions.

## Standards and conventions

| Reference | What it provides | What to check |
| --- | --- | --- |
| [RFC 9116 security.txt](https://www.rfc-editor.org/rfc/rfc9116.html) | A published contact, policy, expiry and optional encryption information at a domain’s /.well-known/security.txt | Section 5.5 explicitly says presence or absence does not grant or deny testing permission; establish that the domain and policy apply |
| [GitHub SECURITY.md](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy) | A repository’s reporting instructions | Check scope, supported versions and the actual private contact |
| [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately) | A private reporting form when the owner enables it | It is separate from SECURITY.md; an enabled form is not a scan grant |
| [ISO/IEC 29147:2018](https://www.iso.org/standard/72311.html) | Receiving and coordinating vulnerability disclosure | The public summary was reviewed; no claim of full ISO conformance is made |
| [ISO/IEC 30111:2019](https://www.iso.org/standard/69725.html) | Handling, investigating and remediating reported vulnerabilities | Agree an owner/team able to receive and act on reports |
| [NCSC disclosure toolkit](https://www.ncsc.gov.uk/information/vulnerability-disclosure-toolkit) | UK guidance and policy templates covering communication, policy and security.txt | Use the relevant owner’s policy and agreed framework |

There is no universal permission grant in these conventions. This project’s
JSON permission record is a custom administrative format, not an ISO or IETF
authorisation standard. A contributor list is not proof of approval authority.
Published policies can contain relevant permission, but this implementation
requires an explicitly reviewed approval record rather than inferring consent.

## Prepare a request

Run route discovery for one named public repository, using read-only GitHub
requests. It checks repository policy files, owner-default candidates and
private-reporting availability. It does not guess email addresses or service
domains, follow redirects or contact maintainers.

```sh
uv run --locked python scripts/permissions.py discover OWNER/REPOSITORY
uv run --locked python scripts/permissions.py draft OWNER/REPOSITORY \
  --mode published-sbom-advisory-match --fingerprint EXACT_SBOM_SHA256
```

Replace the fingerprint with the SHA-256 of the exact proposed SBOM. For
non-executing source analysis use mode repository-static-analysis and the
exact 40-character source commit SHA. These are alternative scopes; approval
for one does not cover the other. Live service testing is outside this tool.

Review the resulting .consent/OWNER__REPOSITORY/request.md. Ask the owner or
authorised delegate to confirm scope, tool/version, dates, conditions, a stop
contact, the private reporting route, acknowledgement expectations and
disclosure terms. Requests contain no vulnerability detail. Send only through
a route you have verified and only after a separate decision to send.

The proposed scope excludes executing repository/dependency code, installing
its dependencies, exploitation and active service tests. External transfer of
source or package identities is not approved by this local workflow. Downloading
a scanner’s public advisory database is distinct from uploading private input.

## Record an actual response

After reviewing a real response and the approver’s authority, complete the
private approval-template.json. Do not mark it approved merely because a policy,
public repository, open-source licence or private reporting form exists.

```sh
uv run --locked python scripts/permissions.py record OWNER/REPOSITORY \
  --approval /absolute/private/approval.json --evidence /absolute/private/response.eml
uv run --locked python scripts/permissions.py check OWNER/REPOSITORY \
  --mode published-sbom-advisory-match --fingerprint EXACT_SBOM_SHA256
uv run --locked python scripts/permissions.py revoke OWNER/REPOSITORY
```

The check rejects absent, pending, revoked, expired, future, mismatched or
tampered records/evidence. Approval is bound to one repository, mode and input.
Changing a source revision or SBOM requires a new appropriate grant. Evidence
hashes prove integrity relative to the record, not the sender’s identity.
The operator remains responsible for checking authority, conditions and scope.

All drafts, reporting templates, responses and grants stay in .consent/, with
restricted local file permissions. Git ignores the directory and release
packaging rejects it. Local file modes do not replace managed device security,
access control, encryption or your organisation’s retention policy.

There is no scanner runner yet. A future runner must call check immediately
before work and again before preparing a private report. Revocation or changed
scope must stop work; a check does not technically prevent someone invoking a
separate scanner themselves. No public finding, email, issue or advisory is
automatically sent or published by this feature.
