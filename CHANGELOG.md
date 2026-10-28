# Changelog

This file records notable user-facing changes using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Software versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html);
daily dataset snapshots have separate identifiers.

## [Unreleased]

### Added

- Private, unsent scan-permission requests with exact-input approval, expiry,
  revocation and agreed private reporting terms.
- Offline checks for Conventional Commit subjects and release-note structure.
- A contribution guide defining public interfaces, versioning and release rules.

### Changed

- Adopt Keep a Changelog, Semantic Versioning and Conventional Commits for
  future releases and commits, while preserving already published history.

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

[Unreleased]: https://github.com/chris-page-gov/xgov-soft-eng-com/compare/f7eaed15feaa11941b8fa95e1c66aa400f421483...HEAD
[0.1.0]: https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40749128667-1
