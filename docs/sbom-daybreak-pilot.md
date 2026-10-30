# A bounded SBOM and Daybreak Blue pilot

Policy and pilot scope updated on 30 October 2026. The public-data matching
runner is implemented with synthetic regression checks and verified tooling
preparation. No real SBOM matching has run. This document is not an
authorisation record, a vulnerability finding or human acceptance.

The current step is reproducible inventory and advisory matching. A later,
separate decision could use Daybreak Blue to investigate a small candidate
queue and review remediation; this runner does not invoke AI. The present
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

For `public-sbom-data-analysis`, use only already-published public SBOM
documents whose access and reuse basis has been reviewed and recorded. This
limited local matching mode does not require individual repository-owner
consent; it does not amount to owner approval for testing. Include resolved
package versions, unresolved versions, an older document and different
dependency contexts. Any subsequent source review or testing needs its own
scope and genuine owner approval.

| Stage | Deliverable | Evidence boundary |
| --- | --- | --- |
| Inventory quality | Exact SBOM bytes/hash, document date, generator, source revision where supplied, package identities and version coverage | Keep missing, stale and unresolved information explicit; do not guess versions |
| Advisory matching | Pinned scanner and advisory database; package/version matches; full and runtime-view comparison | Candidate advisory matches, with coverage and errors; no inference of deployed exposure |
| Blue investigation | A private, evidence-linked disposition for each candidate, with relevant source/configuration at an approved commit | Static reachability and applicability reasoning retain unknowns and require review |
| Remediation | Reviewed upgrade/configuration proposal, regression evidence and owner reporting | No automatic fixes, public vulnerability labels or disclosure |

Use the bounded [public-data runner](public-sbom-pilot.md) as the reproducible matcher to extend the earlier
pilot. It accepts supplied SPDX and CycloneDX SBOMs. Pin the scanner and
advisory database, then perform matching offline in a network-isolated
environment without uploading package identities. Keep the database age and
digest with results. Dry-run does not fetch SBOMs; a later explicit execution
can retrieve admitted documents from their existing public URLs. The bounded dry-run
preview is:

```sh
uv run --locked python scripts/sbom_pilot.py run \
  --manifest examples/public-sbom-pilot.json --dry-run
```

Actual matching requires the explicit `--execute` option. Inputs and candidate
matches are retained only under the private `.sbom-pilot/` root. The runner
does not probe repositories, dependencies, images or services, inspect source
or code, and does not invoke AI. OS-level network isolation is part of the run boundary;
the application's offline configuration alone is not a substitute.

Grype accepts existing SPDX and CycloneDX SBOMs. Keep its database age and
digest with results.
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

## Separately scoped model-assisted review

The public-data matching mode does not invoke Daybreak Blue or any other AI.
Any later model-assisted review is separate work: it needs a defined scope,
appropriate authority for the evidence supplied, privacy review and a distinct
decision to use the model. A model's availability does not grant permission to
send it SBOMs, source, candidate findings or private evidence.

An advisory match cannot repair missing versions or infer a deployed
environment from an SBOM. Preserve the progression: advisory match, affected
package, reachable code, then demonstrated deployed exposure. An owner or
reviewer confirms each disposition.

Record applicability decisions in a VEX-compatible design with product scope,
evidence, issuer, observation time and review status. Do not publish a
not-affected assertion on unreviewed model output. CycloneDX
[VEX](https://cyclonedx.org/capabilities/vex/) provides a format for communicating
product-specific applicability; conformance would need schema validation.

## Permission, privacy and cost

Follow the [permission and reporting policy](permission-and-disclosure.md).
The public-data mode is limited to local matching of already-published SBOMs
and is not owner-approved testing. Any separately scoped source analysis,
external source transfer or live service testing still requires genuine,
reviewed owner approval recorded through `.consent/`. The runner does not
enforce or manufacture that approval, and no AI or model gateway is part of
this pilot.

Do not install dependencies or execute repository code as part of this pilot;
keep any later source excerpts, candidate findings, approval evidence and
reports private. Use the agreed owner route for any later communication.

Success means reproducible matches, documented coverage gaps, a traceable
review decision for every candidate, useful remediation and measured review
effort. It does not certify the catalogue as secure. Do not turn the pilot into
a recurring service or publish candidate matches. Public catalogue exports
should contain only reviewed coverage and capability metadata, with disclosure
decisions kept separate from raw private results.
