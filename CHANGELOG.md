# Changelog

This file records notable user-facing changes using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Software versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html);
daily dataset snapshots have separate identifiers.

## [Unreleased]

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

[Unreleased]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/f7eaed15feaa11941b8fa95e1c66aa400f421483...v0.2.0
[0.1.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40749128667-1
