# Build, refresh and recover

Use uv run --locked python scripts/catalogue.py build for an offline build.
Use refresh for an explicit download of the configured public HTTPS feed.
No credential or model API is needed for catalogue acquisition or generation.

Refresh rejects unsafe identities/types/paths, conflicting duplicates,
responses over 100 MB, fewer than 1,000 records, and removal of more than 20%
of previously admitted identities. These are operational tripwires, not
statistical guarantees. Review legitimate changes before adjusting them.

A candidate is built and checked in .build/ before directory promotion.
Ordinary errors restore the previous generated directory. If killed between
moves, recover .build/previous-generated to generated/ before continuing.
Keep source/current.json, its referenced snapshot and baseline together.
Concurrent local writers are unsupported; Actions uses a concurrency group.
Retired-build cleanup retries when Finder recreates only .DS_Store metadata;
other cleanup failures remain visible and the checked candidate is retained.

A byte-identical successful download retains the original receipt and graph
timestamp. source/last-check.json records retrieval. The 48-hour warning
measures successful retrieval, not freshness of each upstream repository.
HTTP Last-Modified, push time and SBOM creation time are distinct observations.

Before release run tests, build, check and scripts/assure.py. The last command
uses the pinned direct dependencies in requirements-assurance.txt in a
disposable environment; production build/search remain standard-library-only.

Workflows pin Ubuntu 24.04 and Python 3.12.11. GitHub's Ubuntu 26.04 runner
does not provide that exact Python build, as confirmed by the initial run and
the official actions/python-versions manifest. Changing the runner or runtime
requires an explicit compatibility check and documentation update.

## Release policy

At 16:43 UTC daily, or manual dispatch, the workflow validates the public feed,
builds and assures a candidate, prepares an archive and checksum file, uploads
them to a draft timestamped release, then publishes that exact release as
latest. A failed candidate does not replace the last published release.
Use the immutable release tag and checksums for reproducibility. GitHub may
delay schedules; Action failures remain visible and no model heartbeat is used.

The archive contains a frozen source/receipt, comparison baseline, generated
pack and build code/config/docs. Generated data is not committed daily.
The checked-in initial snapshot remains an independent reproducible baseline.

Before upload, the packager reopens the archive as a stream and verifies every
declared controlled input, raw source and generated output against the build
manifest. Missing files, duplicate declared members and checksum mismatches
block publication. Hidden build inputs such as .gitignore are included.
Only manifest-declared members are admitted; private consent files and undeclared
source files are rejected. The first snapshot release omitted .gitignore despite
listing its hash: retain it as historical evidence, and use the corrected release
for a complete standalone reproduction.

The separate hourly history workflow checkpoints public contributor statistics
on history-data. The daily pack restores that branch before building. It also
restores the preceding record summary to distinguish actual source-field changes
from changes to derived classification or observation metadata. See
[collection and recovery limits](history-and-change.md).
The first checkpoint uses git switch --orphan in a fresh runner worktree, so
the data branch starts empty and never stages the producer code or source feed.

## Consumer limits

The descriptor and shards follow Explorer's documented large-corpus shapes.
Browser journeys, rich semantic drawers and performance remain unverified.
The JSON-LD manifest is for RDF tools, not a canonical YAML-LD descriptor.
Do not advertise this as a verified hosted Explorer publication.
