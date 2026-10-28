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

A byte-identical successful download retains the original receipt and graph
timestamp. source/last-check.json records retrieval. The 48-hour warning
measures successful retrieval, not freshness of each upstream repository.
HTTP Last-Modified, push time and SBOM creation time are distinct observations.

Before release run tests, build, check and scripts/assure.py. The last command
uses the pinned direct dependencies in requirements-assurance.txt in a
disposable environment; production build/search remain standard-library-only.

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

## Consumer limits

The descriptor and shards follow Explorer's documented large-corpus shapes.
Browser journeys, rich semantic drawers and performance remain unverified.
The JSON-LD manifest is for RDF tools, not a canonical YAML-LD descriptor.
Do not advertise this as a verified hosted Explorer publication.
