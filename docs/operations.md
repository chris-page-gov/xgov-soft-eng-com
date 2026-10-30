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
Retired-build cleanup retries when Finder recreates only .DS_Store metadata
in the directory whose removal failed, including when old shards remain elsewhere;
other cleanup failures remain visible and the checked candidate is retained.

A byte-identical successful download retains the original receipt and graph
timestamp. source/last-check.json records retrieval. The 48-hour warning
measures successful retrieval, not freshness of each upstream repository.
HTTP Last-Modified, push time and SBOM creation time are distinct observations.

Before release run tests, build, check and
`uv run --locked --group assurance python scripts/assure.py`. The assurance
group in `uv.lock` pins direct and transitive dependencies. CI installs the
matching `requirements-assurance.txt` export with `--require-hashes` in its
disposable runner; production build/search remain standard-library-only.
See [repository protection](repository-protection.md) for drift checks,
dependency updates and the sole-maintainer merge procedure.

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

## Pages publication

The Pages workflow runs after a successful daily refresh, or by manual
dispatch for the current producer commit. It selects that exact snapshot tag,
verifies its commit, asset checksums, archive members and controlled producer
inputs, then extracts only generated data. It never runs code from an archive.
The candidate is copied without rebuilding and must fit within 1 GiB including
its landing page and publication receipt. The deployment uses standard public
GitHub-hosted runners with only contents-read, Pages-write and OIDC permissions.

The static page links to the descriptor, source repository, semantic manifest
and publication receipt. A new snapshot replaces the Pages data; immutable
release archives remain the reproduction route for older snapshots. Browser
integrity bindings reject mixed data after an update rather than combining
different snapshots. Private grants and private starter outputs are excluded.

Run python scripts/pages.py for a local copy, or pass --release with a directory
containing all six assets from one snapshot. An existing destination is never
overwritten. The separate, contents-read verification job checks all 40 declared browser
checks against that release after deployment, then retains a JSON receipt.
It has no Pages-write or OIDC permission. It pins Node 26.7.0, npm 11.19.0 and
Playwright CLI 0.1.17 with the complete transitive lock. `npm ci` verifies
package integrity with lifecycle scripts and audit requests disabled, and the
job runs the local CLI against runner-installed Chrome. Static Python checks
do not require Node; the Node-enabled jobs also verify active runtime versions.
See [npm tooling](npm-tooling.md). A failed verification requires
investigation of the existing deployed candidate; it does not trigger a
rebuild or automatic rollback. Keep the preceding immutable release for
recovery. Verify the exact public URL before advertising it as working.

## Consumer limits

The descriptor and shards follow Explorer's documented large-corpus shapes.
Chrome acceptance covers the declared facets, search, semantic evidence and
contributor-history journeys; see the dated browser report for exact evidence.
The JSON-LD manifest is for RDF tools, not a canonical YAML-LD descriptor.
A successful Python build alone does not establish browser acceptance.

## Frozen AI comparison assets

The archive step first verifies the frozen data, then creates the deterministic
xgov-ai-test-pack.zip from those exact bytes and runs its independent verifier.
The release publishes that ZIP, verification-result.json and SHA256SUMS beside
the data archive. Pages verifies every listed release asset before copying the
already-assured generated files. No model API is called. A failed verifier
blocks publication. The Python 3.12 standard-library helper can be copied out
of the reviewed ZIP; do not execute code from arbitrary data archives.

## Publishing evaluation reports

The reviewed Markdown editions in `docs/ai-evaluations/2026-10-29/` are the
source of truth. `scripts/report_pages.py` renders their bounded Markdown
subset as escaped static HTML in `generated/reports/`, with readable tables,
report navigation, source Markdown and provenance files. It admits only the
named public files, checks their complete SHA256SUMS inventory and rejects
tampering before rendering. Raw HTML is escaped; links permit credential-free
HTTP(S), local report pages and repository documentation. Private captures
and model-supplied commands are neither copied nor executed.

The ordinary catalogue build includes these report bytes in its build manifest.
Pages promotes the same assured archive outputs. The catalogue landing page
links to the collection only when its index is declared in that manifest.
The descriptor's optional `related_links` publishes the canonical HTTPS report
URL for Explorer. Each entry has `label`, `url` and `kind`; Explorer bounds and
validates this navigation metadata before displaying it. These are publication
links, not repository records or semantic assertions. Existing descriptors
without the optional field remain supported.

After editing a public edition or supplement, update its publication manifest
report/supporting-file hashes and SHA256SUMS before building. Check source
links, privacy, deterministic rendering and the real deployed journeys from
both the catalogue and Explorer. Keep historical model claims, displayed UI
outcomes, independent validation and new model runs explicitly separate.

## Pause and run on demand

The owner paused the daily catalogue schedule on 29 October 2026 while leaving
hourly contributor-history collection enabled. The refresh workflow stays
active so its Run workflow button and workflow_dispatch API remain usable.

`OKF_DAILY_REFRESH_ENABLED` is a repository Actions variable. Only `true` admits
scheduled refresh work; `false` or an unset value pauses it. The scheduled run
may appear as skipped. The downstream Pages workflow applies the same guard
so a skipped scheduled refresh does not try to publish a missing snapshot.
Manual refreshes still publish and verify their exact assured snapshot.

```sh
# Refresh and publish on demand; select main in the GitHub Actions UI too.
gh workflow run refresh.yml --repo chris-page-gov/xgov-soft-eng-com --ref main

# Pause or resume only automatic daily refreshes.
gh variable set OKF_DAILY_REFRESH_ENABLED --repo chris-page-gov/xgov-soft-eng-com --body false
gh variable set OKF_DAILY_REFRESH_ENABLED --repo chris-page-gov/xgov-soft-eng-com --body true

# Collect another bounded history checkpoint without publishing a new catalogue.
gh workflow run history.yml --repo chris-page-gov/xgov-soft-eng-com --ref main -f limit=500
```

Do not disable the whole refresh workflow to pause its cron: that also removes
the usable manual route until it is re-enabled. History collection has its own
serial concurrency group, API/time budgets and data branch; it does not update
Pages until the next explicit catalogue refresh. Keep owner approval evidence,
raw security reports and credentials outside public builds.

## Missing scheduled run on 29 October 2026

The daily workflow declared 16:43 UTC, but no schedule-event refresh run was
present when checked after 19:00 UTC. The workflow was active, Actions were
enabled, the default branch was main and the repository was not a fork or
archived. The successful 16:13 UTC refresh was manually dispatched; it was
not the scheduled 16:43 run. No failed scheduled refresh was found.

GitHub documents that scheduled events can be delayed or dropped. The available
API evidence does not establish the exact reason for this missing event. The
history workflow also showed only three scheduled starts on 29 October when
checked: 05:47, 12:59 and 18:57 UTC, despite its hourly cron. They completed
successfully. A run timestamp is observed execution, not a guaranteed mapping
to a particular intended cron tick.

For stronger punctuality, use an independently monitored external scheduler
to dispatch this same manual workflow, with a freshness alert and idempotency
controls. No external scheduler or paid service has been configured here.

References: [GitHub schedule behaviour](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
and [repository variables](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#vars-context).
