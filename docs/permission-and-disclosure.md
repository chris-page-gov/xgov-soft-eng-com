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
requires an explicitly reviewed approval record for owner-scoped testing rather
than inferring consent.

## Public SBOM data analysis

The `public-sbom-data-analysis` mode is separately authorised for reading
already-published public SBOM documents and matching their package identities
locally against a pinned advisory database. It does not require individual
repository-owner consent for that limited data-analysis activity. This is not
owner approval, security-testing permission or permission to reuse every
element of a published SBOM. Before admitting a source, record its exact URL,
retrieval date, digest and any stated licence or reuse terms; assess document
access and reuse rights separately. Public accessibility alone is not a reuse
grant. Where the basis is unclear or restricted, exclude the document pending
review. Do not represent this operational scope as a legal determination.

The mode is limited to anonymous retrieval through normal published URLs or
official public SBOM APIs and local matching of that data. Dry-run makes no
requests; implementation tests did not fetch catalogue SBOMs. It does not
inspect repository source or code, resolve dependencies,
probe images or services, contact owners, or use AI. Candidate advisory matches
and reports remain private in `.sbom-pilot/`; they are not vulnerability
findings or permission to disclose. The existing `.consent/` workflow remains
in force for separately scoped source analysis, testing or disclosure work.
See the [runner guide](public-sbom-pilot.md) for admission, pins, bounds and
private outputs. No approval record is required or created for this mode.

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
These commands are for an expressly owner-agreed engagement. They are not a
prerequisite for the separate public-data mode and must not be used to imply
that a published document's owner approved its analysis.

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

The public-data matcher is invoked with the explicit `public-sbom-data-analysis`
mode and uses a pinned scanner and advisory database in an offline, network-
isolated run. Preview the small manifest with:

```sh
uv run --locked python scripts/sbom_pilot.py run \
  --manifest examples/public-sbom-pilot.json --dry-run
```

An actual local match requires the explicit `--execute` option. Its runner is
limited to supplied public SBOM inputs and local advisory data; it does not
replace or approve the existing consent workflow. Candidate results stay
private, and no public finding, email, issue or advisory is automatically sent
or published. Owner-scoped work continues to require the separate approval
record, checked immediately before work and before preparing a private report.
Revocation or changed scope must stop that work.
