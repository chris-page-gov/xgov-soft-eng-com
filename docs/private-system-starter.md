# A beginner path for private codebases

Start with a small private metadata inventory. Keep source code, credentials,
personal information and security findings out of the first pack. You can learn
the format and validate the workflow without granting a tool access to a
private system or uploading anything.

This guide is for someone who manages a closed-source codebase. Open-source
licensing is not required to describe your own system in an internal OKF+;
your organisation must decide authority, permitted use and access. This
starter is a local experiment, not an accreditation or complete security model.

## First local build

1. Agree a named owner, intended users, permitted purpose, classification and
   approved storage location. Include the service/security owner where code
   or vulnerability information will be involved.
2. In an approved local Python environment, create a new folder outside this
   public repository:

   ```sh
   uv run --locked python scripts/private_starter.py /absolute/approved/private-okf
   ```

   The command creates no Git repository, remote, CI workflow or account. It
   does not read your codebase. Existing destinations are never overwritten.
3. Review the fictional inventory/components.example.json, then manually add
   a few approved metadata records to inventory/components.json. Use a local
   component identifier, short title, type, service area and content type.
   Optional fields include team, language, lifecycle and an internal reference.
   Use unknown where appropriate. Do not paste secrets or access-bearing URLs.
4. Run python build.py from the new folder. The trusted starter script reads
   only that inventory, creates a small OKF 0.2 JSON bundle, facets and a build
   receipt, and makes no network or model calls. The initial empty inventory
   builds zero records; that is a scaffold, not evidence about your system.
5. Inspect generated/okf-bundle.json, generated/facets.json and the receipt in
   approved local tools. Check that only intended metadata appears. Keep these
   files private: names, architecture and hashes can themselves be sensitive.

The default policy disables publication, source-code ingestion, model calls
and scanning. The builder stops if those defaults are weakened. It does not
walk directories, install dependencies or execute code from the target system.
It is not a data-loss-prevention system: a person must review admitted values.

## Add capability in controlled steps

| Next need | Efficient starting point | Review before enabling |
| --- | --- | --- |
| Better navigation | Add team, service area, content type, language and lifecycle facets to the metadata inventory | Terminology, unknown values and intended audience |
| Read documents | Admit a small explicit allowlist of approved documents | Secrets/personal data, extraction scope, logging and retention |
| Read source code | Pin an exact repository revision and paths; keep original bytes in approved private storage | Owner authority, code execution restrictions and supply-chain access |
| Check dependencies | Generate an SBOM in an approved build environment and preserve exact versions/source revision | Permission, tool provenance, advisory source and whether anything leaves the environment |
| Assess vulnerabilities | Use the separate permission/reporting workflow; keep candidate matches separate from applicability | Private route, owner response, disclosure terms, expiry and revocation |
| Share with colleagues | Use approved private Git, internal hosting or managed storage | Membership, inherited access, authentication, backups and removal of access |
| Add a Reader | Evaluate a pinned, locally deployed or approved internal Reader | Actual data flows, external requests, caching, browser storage and access controls |
| Add AI assistance | Start only after approval for the exact service, model and data | Retention, training settings, geography, credentials, logging, budget and human review |

A public Reader, browser-only implementation, private Git repository or
localhost URL alone does not prove privacy. Do not load private bundles into a
public site or hosted assistant before its actual data flows are approved.
The local starter has not established private Explorer browser acceptance.

## Keep the work maintainable

Record admitted files/versions, checksums, classifications, owner decisions and
known gaps. Keep authored inputs, generated outputs and documentation separate.
Review changes and rebuild them together. Store permission evidence separately
from broad team-facing knowledge. Agree retention and removal, including caches,
exports, backups, CI artefacts and browser storage.

When moving beyond metadata, use the standard repository contracts and the
project’s lockstep checks with explicit private publication boundaries. Avoid
turning on the public catalogue’s Actions workflow in a private project: it
publishes releases. The starter intentionally provides a smaller local path.
