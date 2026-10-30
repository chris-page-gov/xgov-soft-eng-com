# Analyse published SBOM data privately

The bounded pilot implements `public-sbom-data-analysis`: read an existing
public SBOM and compare its declared package versions with public advisories.
This mode does not require individual repository-owner consent and never
records or implies owner approval for testing. It requires a documented access
and reuse basis for each document. Unclear or restricted inputs stay in review.
See the [permission policy](permission-and-disclosure.md).

## Start with the dry-run

From the repository root:

```sh
uv sync --locked
uv run --locked python scripts/sbom_pilot.py run \
  --manifest examples/public-sbom-pilot.json --dry-run
```

This validates the manifest, mode, URLs, basis, limits and toolchain pin record.
It makes no network request, starts no subprocess and writes no working data.
Omitting both `--dry-run` and `--execute` also selects this preview. An
`eligible-for-retrieval` decision is not proof that a document is available,
unchanged, complete or suitable for matching.

The [one-input example](../examples/public-sbom-pilot.json) uses the public URL
and compressed SHA-256 of a previously retained SPDX sample. Its embedded
`dataLicense` declares CC0-1.0 for that metadata. This is not a new retrieval or
scan, a grant over dependency code, or owner-approved testing. The sample is
old enough to demonstrate a stale-document gap. If the URL now serves different
bytes, execution retains them privately for review and stops admission rather
than silently updating the expected hash. Do not remove a hash merely to make
an input pass. Review the changed document and basis first.

Prepare up to ten named inputs by copying this manifest. Use existing published
document URLs or official public SBOM APIs. Record publication evidence and
`access_reuse.status` as `documented`, `unclear` or `restricted`. A documented
basis needs evidence and an explanation; a licence can apply to the SBOM data
without applying to the software. The runner compares any embedded document
licence with a licence recorded in the manifest. It does not decide legal
sufficiency or independently verify a statement entered by an operator.
Input identifiers must be JSON strings, even when they contain only digits.
Numbers and other JSON types are rejected during admission, before retrieval,
so filenames and persisted checkpoint keys use the same identity.
Repository references are optional and are not independently verified; leave
one absent rather than invent an association. Input identifiers `checkpoint`
and `batch-review` are reserved for the runner's control files.

## Toolchain preparation and later execution

The implementation task used only synthetic SBOMs and mocked matching. No
catalogue SBOM was fetched and no real scan was started. These are commands
for a later operator decision, not instructions to run during implementation:

```sh
# Downloads only the fixed public scanner and advisory database, then imports
# the database locally with network access denied. No SBOM is requested.
uv run --locked python scripts/sbom_pilot.py prepare

# A separate explicit decision: retrieve admitted SBOM documents and match them.
uv run --locked python scripts/sbom_pilot.py run \
  --manifest examples/public-sbom-pilot.json --execute
```

[The pin record](../config/sbom-pilot-pins.json) fixes Grype 0.121.0, archive and
extracted executable SHA-256 values for macOS ARM64 and Linux AMD64, and the
exact v6 advisory archive, digest, build date and extracted database digest.
Downloaded scanner bytes were checked against the official release/API
digests and checksum file; database bytes were checked against the official
listing. Signature verification is not claimed. The compressed database is
about 197 MB, with a 2.55 GB distributed SQLite file. Grype's local index
preparation increases it to about 3.38 GB. Both forms have recorded hashes;
the runner verifies the prepared file and import metadata before matching.
Allow space for the private cache and reports before preparation. Database
import has a separate 4 GiB per-file ceiling; matching output retains the
smaller ceiling below.

Matching checks the binary, database archive and database membership/hashes,
including immediately before each invocation. A scanner version preflight
runs inside the same network sandbox. macOS uses `sandbox-exec` with network
access denied; Linux uses `unshare` with a new user and network namespace.
Unavailable or disallowed isolation stops matching; there is no networked
fallback. Linux user namespaces must be available. These controls isolate the
network, not the complete filesystem or operating system.

The child receives a small explicit environment and config, with application
updates, database updates and external sources disabled. It receives only a
local `sbom:` target, never an image, directory or repository. The pinned
database is intentionally reused even when old; a database older than five
days is reported as a coverage gap. Changing pins requires reviewing new
public downloads, hashes, dates and compatibility, then rerunning tests.

## Bounds, cache and resume

| Limit | Default hard ceiling |
| --- | --- |
| Explicit SBOM documents | 10 |
| Requests, including redirects | 30 per run |
| Run work budget | 900 seconds; checked between bounded stages |
| Individual request, including DNS and streaming | 20 seconds |
| Redirects | 3; only explicit admitted hosts, HTTPS and public addresses |
| Downloaded SBOM bytes | 8 MiB per document |
| Decoded JSON | 32 MiB per document |
| Declared packages | 50,000 per document |
| Delivered candidates | 5,000 per document; truncation is a coverage gap |
| Candidate/component associations | 200,000 per document |
| One matching process | 90 seconds |
| Scanner stdout/stderr and each derived report | 32 MiB each |

A manifest can reduce the numeric ceilings, never raise them. Tool preparation
is separate: at most 12 requests and 600 seconds for fixed tooling downloads,
followed by a bounded 180-second database import. The database archive and
unpacked files have their own pinned sizes and hashes.
Requests and matching processes have hard timeouts. The parent checks its
overall budget between bounded parsing/report stages and during file hashing;
it saves a checkpoint if tool verification exhausts that budget too.

Retrieval is anonymous HTTPS on port 443. It does not use credentials, cookies,
proxy settings or arbitrary access-bearing query parameters. Public DNS
addresses are checked and bound to the TLS connection; private, loopback,
link-local and mixed public/private resolutions are rejected. Only explicit
public redirects are followed. Rate-limit responses defer the batch, record a
bounded retry time and stop further requests; there is no busy retry loop.
Tool preparation alone permits the official GitHub asset CDN's transient
signed redirects and removes their query strings from retained receipts.
That exception cannot be selected by an SBOM manifest.

The private cache freezes bytes by the complete input entry. Resume verifies
cache and completed report hashes instead of fetching a mutable URL again.
Checkpoint identities include the manifest, pins and runner source hash.
One private file lock prevents concurrent preparation or matching operations.
After a deferral, run the same command after its recorded retry time. Review
failed admission before changing the manifest. A new input entry or revised
expected hash produces a distinct cache key and run; it is not an implicit
refresh or approval. Interruptions retain completed input checkpoints.

## Coverage and reports

Supported documents are JSON SPDX 2.2/2.3 and CycloneDX 1.4–1.6, optionally
gzip compressed or returned in an official API's `sbom` wrapper. External
references are not fetched. The pilot admits exact declared versions and one
resolved language PURL in PyPI, npm, Maven, Go, Cargo, RubyGems, Composer or
NuGet. Other ecosystems, qualifier/subpath forms, absent or ambiguous identities,
missing or ranged versions and unsupported formats remain explicit gaps.
This conservative pilot boundary is narrower than Grype's overall support.

The data-only CycloneDX matching projection includes all eligible packages,
including build, test and CI dependencies. It does not generate an inventory
by running code. Original contexts and dependency requirement scopes remain
in the report; a runtime
view uses explicit runtime declarations only and lists unknown contexts
separately. A required component is not automatically a runtime component.
Unreconciled scanner identities remain gaps instead of guessed associations.

Reports record the original URL, retrieval time and SHA-256, decoded SBOM hash,
document date, declared source revision where available, access/reuse basis,
scanner binary/version and database identity. Missing dates, stale documents
(90 days by default), missing revisions and ambiguous versions remain visible.
The served modification time does not replace the document's own creation date.
Each candidate links the declared package/version and advisory to these hashes.

Everything stays under `.sbom-pilot/`: restricted directories and files hold
cached bytes, checkpoints, tool files, JSON reports and Markdown reports.
`batch-review.json` and `.md` also retain admission and deferred states.
No-match output is not a clean bill of health. Results are labelled **candidate
advisory matches**; applicability, exploitability and deployed exposure are not
assessed. The runner never labels a repository vulnerable.

Git ignores this private root. Public input collection, archive verification,
Pages staging and the standalone bundle verifier reject it, including
case variants and public-input links into it. Do not copy reports elsewhere
inside public source folders or force-add them to Git. Local file modes do not
replace organisational storage, retention and access controls.

## Separate future decisions

This runner does not clone repositories, inspect source, run application code,
install dependencies, pull application images, probe services or exploit
anything. It does not contact maintainers, create issues/advisories, disclose
repository-specific candidates or invoke Daybreak Blue or any other AI.
Those need distinct scope, authority, privacy and reporting decisions. The
existing `.consent/` workflow remains available for genuinely owner-approved
work; it is not used to manufacture permission for public-data analysis.
Catalogue/history schedules and publication routes are unchanged.

## Implementation verification

On 30 October 2026, 122 unit and regression tests passed, including 52 pilot
cases using synthetic SBOMs, fake tool bytes and mocked services. They cover
admission, consent separation, pins, coverage, private output exclusion,
network boundaries, bounded candidate expansion, rate handling and resume.
The public tooling downloader was also checked against the pinned scanner's
checksum file. The verified scanner's version and database import ran with
network access denied; two imports produced the same prepared database hash.
No catalogue SBOM retrieval or real SBOM matching was performed.

The macOS ARM64 tool preparation path was exercised. Linux AMD64 artefact
hashes were checked, but its namespace execution path is covered by mocks,
not a live Linux matching run. Real matching compatibility and performance
remain to be checked in an explicitly started pilot. No security or deployment
acceptance is implied by these implementation checks.
