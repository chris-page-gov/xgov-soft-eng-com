# Existing security helpers, SBOMs and open issues

Review date: 28 October 2026. Scope: all nine public repositories in the
uk-x-gov-software-community organisation, their complete default-branch trees,
workflow/manifests and focused code searches. This is a read-only inventory,
not a security audit or proof that no other tooling or private reports exist.
Machine-readable evidence is in source/security-helper-inventory.json.

## Existing implementation

| Location | What exists | Boundary |
| --- | --- | --- |
| [Scraper SBOM workflow](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/blob/master/.github/workflows/sbom.yml) | Hourly scheduled incremental GitHub SBOM collection, caching, individual SPDX and consolidated CycloneDX publication | Inventory collection and publication; schedules can be delayed |
| [SBOM normalisation](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/blob/master/sbom-normalize.js) | Version-resolution checks, package scope heuristics and per-repository quality counts | Inferred build/runtime classification; not deployment evidence |
| [Scraper security workflow](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/blob/master/.github/workflows/security.yml) | Reuses a shared CodeQL workflow on pushes and pull requests | Analyses the scraper repository, not every catalogued repository |
| [Scraper Dependabot](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/blob/master/.github/dependabot.yml) | Daily npm and GitHub Actions version-update configuration | Version-update configuration does not prove vulnerability alerts are enabled or resolved |
| [Lean Coffee Dependabot](https://github.com/uk-x-gov-software-community/lean-coffee-hackmd-generator/blob/main/.github/dependabot.yml) | Weekly GitHub Actions version updates | Repository maintenance, not an estate-wide scanner |
| [Open source guide](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/blob/main/guides-open-source.md) | Links Microsoft SBOM tooling, GitHub SBOMs, Dependabot and Snyk | A draft resource list; links do not establish deployed integration |
| [Learning pathways security resources](https://github.com/uk-x-gov-software-community/software-developer-learning-pathways/blob/main/resources/other/security.html.md) | Security training, OWASP, exercises and books | Its review metadata dates to November 2018; linked resources were not all revalidated |
| [Repository query experiment](https://github.com/uk-x-gov-software-community/uk-x-gov-repo-query) | Metadata filters, tests and CI | Useful discovery reuse; no SBOM advisory-matching implementation found |

The other reviewed repositories are community websites, the archived pathways
pointer and the Eleventy table-of-contents plugin. Their inspected workflows
and manifests did not reveal another cyber scanner or SBOM advisory pipeline.
Code search can miss unindexed material; the tree and file review supplements it.

The latest inspected [scheduled SBOM run](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/actions/runs/40697967591)
completed successfully on 28 October 2026 at 14:37 UTC. Its workflow configuration
requests hourly runs. Successful collection does not verify the freshness of
each document: the sampled sds-addresses SPDX document declares creation on
19 April 2026, although the public file was last modified on 28 October.

## Published SBOM material

The publisher exposes [full CycloneDX inventory](https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom.json.gz),
[a filtered runtime inventory](https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom-runtime.json.gz),
[a quality summary](https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom-quality.json)
and per-repository compressed SPDX files. The uncompressed consolidated JSON
paths are stubs; the gzip files are the inventory artefacts.

The inspected feed has 14,326 distinct repositories with SBOM paths. A path is
not a fresh-fetch or completeness check. The quality summary reports 2,613,161
package observations and 61,792 unresolved versions. These are publisher
observations, not distinct packages, affected repositories or vulnerability
counts. No historical trend or independent estate reconciliation is claimed.

## Vulnerability checking opportunity

The inspected workflows collect and prepare inventory. No step matching this
whole inventory against OSV or another advisory database was found. This does
not establish that nobody runs separate checks elsewhere.

There is evidence of a prior vulnerability-checking pilot. [Merged PR #40](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/pull/40),
merged on 29 June 2026, reports Grype A/B checks on consolidated SBOMs from
10 repositories. The maintainer reports that filtering removed a name-only
false-positive class while retaining version-pinned runtime matches. This is
a maintainer-reported historical test, not an independently rerun result or
current full-catalogue assessment. The PR discusses use for estate-wide CVE
scanning, so absence of a matching workflow is not evidence that scanning has
never occurred.

Reproduce and extend that pilot before a continuous full-catalogue check:

1. Select named repositories; freeze their exact SBOM bytes, document dates,
   repository revisions where supplied, generator versions and hashes.
2. Retain the full inventory. Record version ranges and unresolved identities
   as unscannable; never guess versions or count a name-only match as a finding.
3. Match exact package/ecosystem/version or supported package URLs using a
   maintained scanner and freeze its version, advisory date and results.
4. Keep build, test and CI tooling visible as separate contexts. Upstream
   package-name exclusions are heuristic and do not show that those components
   present no supply-chain risk.
5. Distinguish an advisory/package match from a confirmed affected deployment.
   Record withdrawn/aliased advisories, fixed versions, applicability review
   and VEX statements with their issuer, scope and evidence.
6. Publish coverage and unscannable counts alongside candidate matches.
   A zero result means no match in the checked evidence, not secure software.

[CycloneDX](https://cyclonedx.org/capabilities/sbom/) is the machine-readable
inventory format. [VEX](https://cyclonedx.org/capabilities/vex/) represents
product-specific vulnerability applicability/exploitability statements.
[OSV-Scanner documentation](https://google.github.io/osv-scanner/supported-languages-and-lockfiles/)
explains why resolved lockfiles are preferable to unresolved manifests.
No catalogue-wide vulnerability scan or online package/advisory query has been
performed by this experiment.

## Open issues

Direct public Issues API lists were checked for all nine repositories.
All responses fitted within one page; pull requests were excluded. There are
13 open issues: 10 on the main website, two on learning pathways and one on
the Lean Coffee generator. No open issue in the inspected set requests an SBOM
vulnerability-matching pipeline. Titles below are retained verbatim.

| Issue | Title |
| --- | --- |
| [uk-x-gov-software-community.github.io #164](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/164) | Cookie banner |
| [uk-x-gov-software-community.github.io #155](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/155) | Add GovDev Midlands 2026 page |
| [uk-x-gov-software-community.github.io #127](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/127) | Update Objectives for 2025-2026 |
| [uk-x-gov-software-community.github.io #66](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/66) | Discuss reporting of bugs in gov.uk services by the public |
| [uk-x-gov-software-community.github.io #49](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/49) | add contibuting guide |
| [uk-x-gov-software-community.github.io #48](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/48) | Accessibility testing |
| [uk-x-gov-software-community.github.io #47](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/47) | Add analytics |
| [uk-x-gov-software-community.github.io #46](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/46) | package json build |
| [uk-x-gov-software-community.github.io #29](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/29) | Add facilitators roles open |
| [uk-x-gov-software-community.github.io #12](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/issues/12) | Github Action - run gulp |
| [software-developer-learning-pathways #1](https://github.com/uk-x-gov-software-community/software-developer-learning-pathways/issues/1) | Developer Roadmap |
| [software-developer-learning-pathways #2](https://github.com/uk-x-gov-software-community/software-developer-learning-pathways/issues/2) | Hackathons |
| [lean-coffee-hackmd-generator #2](https://github.com/uk-x-gov-software-community/lean-coffee-hackmd-generator/issues/2) | Automate sending of lean coffee reminder emails using the mailchimp API |

Most relevant to this experiment: website #66 concerns routes for public bug
reports; #48 concerns accessibility testing; #47 and #164 concern analytics
and cookie handling. Lean Coffee #2 specifies secret handling and avoidance
of sensitive URL logging in proposed email automation; it is a request, not
evidence that the feature is implemented. No issues or comments were created,
edited or sent as part of this review.

The 14,326 SBOM-path figure above belongs to the initial source snapshot
64e70d84e1d4c7a064695c65583000f9bb8a57916ec2b7f636a84b4be98eda9b
reviewed on 28 October 2026. It is a historical observation. Read the frozen
release quality.json for that release's current distinct-record count.
