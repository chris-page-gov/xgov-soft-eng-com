# A bounded SBOM and Daybreak Blue pilot

Recommendation prepared on 29 October 2026. This is a proposed next step, not a
scanner implementation, an authorisation record or a new vulnerability finding.

Start with reproducible inventory and advisory matching. Then use Daybreak Blue
to investigate a small candidate queue and review remediation. The present
catalogue is a discovery and evidence layer; it does not establish which
software is deployed or vulnerable.

## What the existing work supports

The [earlier review](security-and-sbom-review.md) found upstream scheduled SBOM
collection, SPDX/CycloneDX publication, normalisation and quality counters.
CodeQL and Dependabot configuration for the scraper do not cover every
catalogued repository. The historical ten-repository Grype A/B pilot in
[PR #40](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/pull/40)
is maintainer-reported; this project has not independently reproduced it.

The frozen [v0.5.0 input](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/v0.5.0)
contains 24,019 repositories and 14,309 SBOM references. Those references do not
prove fresh or complete documents. The older package-resolution counters in
the review are dated observations, not a current vulnerability inventory.
The sample document's creation date and its later served-file modification
date differ substantially, so freshness must be checked per document.

## Suggested first pilot

Choose ten named repositories with owners who agree to the relevant scope.
Include resolved package versions, unresolved versions, an older document and
different dependency contexts. Prefer systems where the team can also explain
the deployed build; that makes applicability review useful.

| Stage | Deliverable | Evidence boundary |
| --- | --- | --- |
| Inventory quality | Exact SBOM bytes/hash, document date, generator, source revision where supplied, package identities and version coverage | Keep missing, stale and unresolved information explicit; do not guess versions |
| Advisory matching | Pinned scanner and advisory database; package/version matches; full and runtime-view comparison | Candidate advisory matches, with coverage and errors; no inference of deployed exposure |
| Blue investigation | A private, evidence-linked disposition for each candidate, with relevant source/configuration at an approved commit | Static reachability and applicability reasoning retain unknowns and require review |
| Remediation | Reviewed upgrade/configuration proposal, regression evidence and owner reporting | No automatic fixes, public vulnerability labels or disclosure |

Use Grype as the initial reproducible matcher to extend the earlier pilot.
It accepts existing SPDX and CycloneDX SBOMs. Download and pin the advisory
database, then perform the matching locally in an isolated environment without
uploading package identities. Keep its database age and digest with results.
See [supported targets](https://oss.anchore.com/docs/guides/vulnerability/scan-targets/)
and [offline operation](https://oss.anchore.com/docs/guides/vulnerability/getting-started/).
OSV-Scanner can provide a comparison on a subset; its
[offline mode](https://google.github.io/osv-scanner/usage/) needs explicit
configuration and cached databases. A second scanner is useful for examining
disagreements, not for converting agreement into proof of exploitability.

Keep build, test and CI components visible. A runtime-filter heuristic can
reduce noise, but excluding a build tool does not establish that it creates no
supply-chain risk. Count unresolved identities and version ranges as coverage
gaps rather than name-only vulnerability findings.

## Where Blue adds most value

Official [OpenAI documentation](https://learn.chatgpt.com/docs/cyber-safety#choose-the-right-model)
places Blue in authorised defensive discovery, triage, secure code review and
patch validation. For this pilot, use it to reconcile advisory aliases and
fixed ranges, inspect the relevant approved code/configuration, explain likely
applicability and review a proposed fix. It can also find code-level weaknesses
that an inventory matcher cannot see, as a separately scoped source review.

Blue cannot repair missing versions, infer a deployed environment from an SBOM,
or turn model confidence into a verified finding. Preserve the progression:
advisory match, affected package, reachable code, then demonstrated deployed
exposure. An owner or reviewer confirms each disposition.

Record applicability decisions in a VEX-compatible design with product scope,
evidence, issuer, observation time and review status. Do not publish a
not-affected assertion on model output alone. CycloneDX
[VEX](https://cyclonedx.org/capabilities/vex/) provides a format for communicating
product-specific applicability; conformance would need schema validation.

## Permission, privacy and cost

Use the existing [permission and reporting workflow](permission-and-disclosure.md).
An approval for matching one published SBOM does not authorise source analysis
at another commit, external source transfer or live service testing. The tool
creates unsent drafts and checks private records; there is no scanner runner
or model gateway enforcing those checks yet.

Use only the approved Daybreak account/project/surface. Confirm its current
access and applicable costs before starting. Access is not a spending budget.
Do not install dependencies or execute repository code as part of this pilot;
keep source excerpts, candidate findings, approval evidence and reports private.
Use the agreed owner route for any later communication.

Success means reproducible matches, documented coverage gaps, a traceable
review decision for every candidate, useful remediation and measured review
effort. It does not certify the catalogue as secure. Once that small pilot is
useful, add a permission-checking runner, private report retention and only
then a bounded recurring service. Public catalogue exports should initially
contain coverage and capability metadata, with reviewed disclosure decisions
kept separate from raw findings.
