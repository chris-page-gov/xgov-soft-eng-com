# Changelog

This file records notable user-facing changes using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Software versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html);
daily dataset snapshots have separate identifiers.

## [Unreleased]

### Added

- A repeatable account-security review procedure with private findings and
  owner actions kept outside Git, public bundles, Pages and release archives.
- Locked npm browser tooling, including transitive versions and integrity
  digests, with clean-install checks and local CLI execution in CI.
- A declared sole-maintainer repository protection baseline, read-only live
  drift checks and synthetic tests for required checks, review settings,
  trusted Actions, dependency hashes, incomplete settings, conflicting classic
  protection and private reporting.
- A bounded public SBOM data pilot with explicit admission, documented access
  and reuse basis, no implied owner approval, private JSON/Markdown reports,
  synthetic tests and a no-network dry-run.
- Fifty-two synthetic pilot regressions cover admission, pins, private-output
  exclusion, bounded report expansion and resumable input/report integrity,
  including reserved control-file names and unknown repository references.
- Verified Grype 0.121.0 binary/archive pins and one exact advisory database
  snapshot, offline OS network isolation, integrity-checked caching, rate/time/
  size limits and resumable checkpoints. No real scans or catalogue SBOM
  retrievals were performed during implementation.

### Changed

- Disable npm lifecycle scripts, audit requests and update notifiers during tooling use;
  preserve existing catalogue/history schedules and the no-real-scans boundary.
- Exclude private account-review data and installed npm dependencies from all
  publication planes, including forced Git tracking and symlink admission.
- Credit the original community GitHub repository and SBOM author prominently
  in the README, with dated commit evidence and wider contributor/tool credits.
- Require pull requests and current GitHub Actions validation for `main`, with
  no external approval requirement or standing bypass. Block branch deletion
  and force pushes, resolve review conversations and use Conventional Commit
  pull-request titles for merge defaults.
- Lock the assurance toolchain's transitive dependencies and archive hashes;
  CI installs the matching export with hash verification. Read-only checkouts
  discard Git credentials. Catalogue and history schedules are unchanged.
- Separate public-data matching from genuinely owner-approved source analysis
  or testing, retaining the existing approval and reporting workflow.
- Retain declared development/build/test/CI contexts and dependency requirement
  scopes alongside runtime and unknown views, without dropping packages.
- Preserve a resumable checkpoint when tool verification exhausts the work
  budget before any SBOM request or matching process starts.
- Reject private pilot data from tracked Git files, public controlled inputs,
  Pages, release archives and the standalone bundle verifier. Catalogue and
  contributor-history schedules remain unchanged.

### Fixed

- Reject non-text SBOM input identifiers during admission, before retrieval,
  preventing numeric JSON keys from breaking report filenames and resume.

## [0.5.1] - 2026-10-29

### Added

- A repository-variable pause control for daily refreshes, preserving manual
  publication and the separate hourly contributor-history worker.
- Operational instructions and an evidence-grounded SBOM/Daybreak Blue pilot roadmap.

### Fixed

- Reserve batch capacity for due provider retries so initial backfill does not
  starve already-requested contributor statistics.
- Keep a skipped paused schedule from triggering an attempt to publish a
  missing snapshot to Pages.
- Distinguish the configured daily cron from evidence of actual execution.

## [0.5.0] - 2026-10-29

### Added

- Public editions of the Claude and Gemini evaluations with private paths
  removed, frozen evidence references and verified editorial corrections.

- Static GitHub Pages editions of the three early evaluation reports, with catalogue and Explorer
  navigation, accessible tables, mobile text wrapping and manifest-bound sources.
- Eight repeatable live browser checks for report navigation, identities,
  provenance, hashes, mobile layout and private-path exclusions, required by CI.
- A curated review of the later Claude UI capture, recording displayed
  requests, outcomes, truncation and explicit execution limits.

- A beginner README route for testing the bundle in an AI tool, with a short
  starter prompt, archive-capability guidance and links to all three early examples.

### Fixed

- Qualify later private Gemini session retention without replacing the supplied
  report or treating recorded tool statuses as test verdicts.
- Explain Claude’s 1,028 checksum count as source bindings, rather than all
  controlled inputs and generated outputs, using the supplied command history.

## [0.4.0] - 2026-10-29

### Added

- A deterministic, archive-pinned AI test pack with one prompt for Claude and
  Gemini, an independent offline verifier and machine-readable expected facts.
- Complete RDF assertion metadata under the unchanged shared contract, scoped
  predicate-usage labels, explicit
  source/build identities and captured history-join provenance.
- CLI result paging and a visible snapshot-wide history coverage notice
  through the governed facet presentation.

### Fixed

- Keep pending, empty and unavailable history distinct in activity facets;
  store account logins separately from facet status values.
- Retain a specific reason for empty successful GitHub statistics responses.
- Match governed vulnerability aliases with cyber context while excluding
  unsupported social-vulnerability security classifications.
- Publish paired archive, test-pack and verification checksums together, and
  test RDF/runtime field parity and the confirmed report regressions.

## [0.3.0] - 2026-10-29

### Added

- Verified public Pages, Explorer and AI entry points in the README.
- A read-only Pages verification job that checks all 38 browser journeys
  against the released snapshot and retains machine-readable results.
- A separate generated boundary for reviewed browser acceptance receipts.
- Repeatable Chrome acceptance for all 25 facet dimensions, combined filtering,
  value search and paging, and exact-name search.
- Snapshot-bound Explorer search, targeted record lookup, semantic endpoint
  labels and compressed per-route relationship indexes.
- Repository narratives with recent and historical contributor counts, weekly
  and annual change summaries, explicit coverage and source evidence.
- A checked Pages candidate containing only admitted generated public files.
- Pages publication from an immutable assured snapshot, with matching producer
  code and all archive checksums verified before deployment.

### Changed

- Store record, assertion, result and RDF shards as deterministic gzip; search
  summaries hydrate full narratives only when a record is opened. Semantic
  manifests declare each shard's compression, media type and byte length.

### Fixed

- Wait for asynchronously loaded facet counts in fresh browser contexts and
  retain actionable journey failures in automated verification receipts.
- Reject false CLI success, missing browser checks and changed producer or
  consumer identities in automated verification receipts.
- Retry a Finder metadata race in the failed cleanup directory even when
  other retired shards remain elsewhere; retain unrelated cleanup errors.
- Supply the complete experimental-publication notice expected by Explorer.
- Use canonical hyphenated content-type routes and preserve missing dates as
  empty sort values rather than invalid null values.
- Match the browser's declared tokeniser for hyphenated names and accented
  words, and replay every record location against its actual chunk as well as
  validating every incident relationship.

## [0.2.1] - 2026-10-28

### Fixed

- Check actual pull-request commits without rejecting GitHub's temporary test
  merge. Actual commits and published merges still require conventional subjects.
- Retain history checkpoints when a source feed is unexpectedly small or loses
  more than the configured removal threshold.

## [0.2.0] - 2026-10-28

### Added

- Twenty-five authored discovery facets, including content types, dependency
  context, metadata change, contributor accounts and explicit history coverage.
- Queryable historical/recent contribution counts and periods in the semantic
  graph, bound to the same evidence as the runtime assertions.
- A bounded hourly history collector targeting every catalogued repository,
  with minimal public account data, provider-pending states, selectable checkpoint
  sizes and a separate data branch.

- Linked contributor credits across the nine community repositories, with
  automated accounts and inherited fork history distinguished.
- An offline metadata-only starter and beginner guide for private systems,
  with publication, source-code ingestion, models and scanning disabled.
- Private, unsent scan-permission requests with exact-input approval, expiry,
  revocation and agreed private reporting terms.
- Offline checks for Conventional Commit subjects and release-note structure.
- A contribution guide defining public interfaces, versioning and release rules.

### Changed

- Adopt Keep a Changelog, Semantic Versioning and Conventional Commits for
  future releases and commits, while preserving already published history.

### Fixed

- Keep unmapped contributor accounts distinct from no reported recent activity.
- Declare the exact retained SBOM sample and receipt source boundaries.
- Initialise the history data branch with an empty index and working tree.
- Retry cleanup when Finder recreates only its metadata in a retired build.
- Include every declared build input in release archives, including hidden
  inputs, and reject undeclared or private archive members.

## [0.1.0] - 2026-10-28

### Added

- Initial experimental catalogue of public UK government software repositories,
  with frozen sources, repeatable builds, explainable search and domain/task
  suggestions.
- Evidence-bearing relationship records and a sharded RDF JSON-LD projection.
- Daily validated GitHub release builds and source/output checksums.
- A review of existing community security helpers, the reported Grype pilot
  and open issues across the organisation’s nine repositories.

### Fixed

- Pin a runner that supports the governed Python version.
- Exclude Finder metadata from reproducibility checks.

[Unreleased]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.5.1...HEAD
[0.5.1]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/f7eaed15feaa11941b8fa95e1c66aa400f421483...v0.2.0
[0.1.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40749128667-1
