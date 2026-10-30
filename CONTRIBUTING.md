# Contribute

Use British English, keep documentation and generated artefacts in lockstep,
and preserve source attribution. Private material, permission responses and
unverified vulnerability details must not enter this public repository.

## Pull requests

Use a branch and pull request for changes to `main`, including changes by the
sole maintainer. Keep the branch up to date and wait for the required `validate`
check from GitHub Actions. Resolve review conversations before merging. No
second-person approval is required; this is a documented sole-maintainer
workflow. The owner still reviews the diff and evidence before merging.

Use a Conventional Commit title for the pull request. Title edits rerun CI.
Merge and squash defaults use that title; automatic merging is disabled.
Merged branches are removed automatically. See the
[protection baseline and recovery procedure](docs/repository-protection.md).

## Commits

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):
type, optional scope, colon and a concise description. Examples:

```text
feat(facets): add source-labelled vulnerability investigation filters
fix(release): include every declared input in the archive
docs(private): explain the offline metadata starter
ci(runtime): pin a compatible Python runner
```

Supported types: build, chore, ci, docs, feat, fix, perf, refactor, revert,
style and test. Use a meaningful imperative description, at most 72 characters
and no final full stop. The length/style limits are project policy, rather
than requirements of the upstream specification. Explain the reason and
material validation in the body. Mark an incompatible API change with ! or
a BREAKING CHANGE footer, and document its migration.

Enable the optional local hook with git config core.hooksPath .githooks.
CI checks every new commit after the documented initial-history baseline.
It excludes only GitHub's temporary pull-request merge at the checked-out head;
the actual commits underneath it and published merge commits remain checked.
Already published commits are preserved. Squash-merge titles must follow the
same convention; review the final title before merging.

## Changelog and versions

Follow [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/): maintain
Unreleased changes, newest released versions first, ISO release dates,
comparison links and relevant Added, Changed, Deprecated, Removed, Fixed or
Security categories. Describe consequences for users; do not paste a commit log.

Use [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for code.
The public interfaces are CLI commands/options, declared data schemas and
documented pack contracts. During 0.x development a minor version can contain
documented interface changes; keep patch releases compatible. Dataset snapshot
tags identify data builds and do not imply a new software version or new feature.

Before a software release, set the version in pyproject.toml, move the reviewed
Unreleased changes into its dated section, update links and run the full gates.
Tag the exact assured commit. Daily dataset releases retain their snapshot IDs
and source/build checksums. Never modify already published release bytes.

## Checks

Run the unit suite, catalogue build and deterministic check, independent
assurance, release hygiene and archive verification. See docs/operations.md.
Changed inputs need the matching documentation and changelog update. Consumer
acceptance, owner permission and the truth of inferred labels remain distinct
from automated structural checks.
