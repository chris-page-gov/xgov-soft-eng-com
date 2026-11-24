# OKF core 0.3 migration and source-linked walkthroughs

## Pinned input sets

The checkout retains its 28 October 2026 source snapshot as a baseline. The
published candidate is based on the distinct 29 October 2026 archive
`snapshot-40941783959-1`, source commit
`58eb97ad52c50f9e3c869a57797a1d53e96636b4`, archive size 70,468,434 bytes and
SHA-256
`da822774bcf48c3514324cbdd8aa68b8e5231a496f7f10169b827df4a4b4e8be`. Its
3,356 source JSON files include 3,350 contributor-history observations. The
public input inventory is [`source/published-inputs-2026-10-29.json`](../source/published-inputs-2026-10-29.json).

The restore tool verifies the complete archive hash, then reads only the
manifest-listed JSON source members. It rejects links, unsafe paths, duplicate
or missing members, byte-count differences and per-file digest differences.
It does not unpack or execute archived code and does not contact source APIs.
Restore to a new, private, empty staging path; use the same path for build and
check. The checked-in 28 October inputs and historic releases are not replaced.

```sh
uv run --locked python scripts/hydrate_published_inputs.py \
  --output "$RUNNER_TEMP/xgov-published-inputs"
uv run --locked python scripts/catalogue.py \
  --inputs-root "$RUNNER_TEMP/xgov-published-inputs" build
uv run --locked python scripts/catalogue.py \
  --inputs-root "$RUNNER_TEMP/xgov-published-inputs" check
uv run --locked python scripts/archive.py \
  --inputs-root "$RUNNER_TEMP/xgov-published-inputs"
```

`$RUNNER_TEMP` is supplied by GitHub Actions. For local work, choose a new
private directory that does not already exist. The independent checker refuses
to replace an existing output. Archive packaging uses the same input root and
binds the exact restored source/history files and generated projections into
one verifiable candidate. The standard build uses no source API, GitHub
metadata lookup, SBOM request, code execution or model call.

## Core, profile and extension boundary

`config/taxonomy.json` remains the authored source of 47 typed concepts. The
generator emits versioned OKF core 0.3 Markdown with complete JSON-valued YAML
frontmatter, bodies, document-relative links, source paths and source digests.
`generated/okf-core-explorer.json` preserves the exact Markdown body and
frontmatter for every concept. The canonical semantic IDs and Reader routes
remain the previous values; the generated source paths are separately recorded
under `concepts/`.

The existing 24,000-plus repository and account entities remain in the large
metadata graph. They are source-backed `extension` entities, not fabricated
Markdown concepts. Their assertions keep the original identities and remain
paired with the RDF direct triples. The three taxonomy schemes have no authored
cross-concept references, so the core concept projection contains no invented
edges. Metadata extension and core Markdown coverage are reported separately.

The large-corpus descriptor's `snapshot` and `snapshot_id` both bind the
complete build identity required by the Reader. `source_snapshot_sha256` and
the semantic manifest's `source_snapshot_iri` retain the separate source-feed
hash; a bundle build identity is not presented as the upstream source commit.

The common contract schema is pinned byte-for-byte under
`schemas/standard/v2/`. The active custom XGov software profile is
[`profiles/xgov-software/v2/index.md`](../profiles/xgov-software/v2/index.md).
This validates the producer contract shape and declares the producer's choices;
it does not claim full Bundle Wiki v2 profile conformance. Existing v1 schemas
and contexts remain frozen.

## Separate core-only question: what does the notifications concept mean?

The [core taxonomy walkthrough](../generated/walkthrough/core-taxonomy.html)
answers a question from the taxonomy and its typed concept alone: what does
“Send notifications and messages” and its displayed count tell a reader about
an individual repository’s capability? It follows the exact taxonomy field
through the 0.3 Markdown document to the 47-concept Reader projection. Its SVG
shows the two source hashes and the zero authored core edges. The answer says
that the count is produced by experimental name and description rules, not
evidence that a matching repository can provide the service. A zero count does
not establish absence. This guide does not reuse repository licence, SBOM or
contributor-history claims.

## Separate metadata question: can these Notify components be reused?

The generated [notification-services walkthrough](../generated/walkthrough/notification-software.html)
answers this question from three records in the pinned 29 October source
snapshot: `alphagov/notifications-api`, `alphagov/notifications-local` and
`alphagov/notifications-release`. It follows each repository record to its
reported licence, SBOM reference, inferred notification classification and
separately captured contributor-history state. The page links to the release
archive and shows each source snapshot or observation digest.

The walkthrough distinguishes an API source row that reports MIT from records
whose licence is missing. An SBOM path is only a reported reference; this
acceptance does not download or inspect an SBOM. The two provider-pending
history observations are not treated as zero contributors. A negative control
uses `notifications-release`, which has no reported SBOM path and no reported
licence. The answer does not establish that code is safe to use, compatible
with a particular service, currently maintained, or permitted for a proposed
deployment. Users must inspect authoritative licences and source code through
their own reviewed process.

Long source archive and digest values wrap inside the source-trail panel on
narrow screens so they remain readable without expanding the mobile page
beyond its viewport width.

The paired offline AI test pack verifies these same boundaries without a model
call. Its bounded standard-library verifier checks all 47 typed Markdown
documents and their exact frontmatter, body and source hashes, the separate
extension roles and—when the exact published input-set identity is present—the
three notification records, history observations, licence and SBOM references,
static walkthrough wording and negative release control. The hydrator also
supports `--copy-archive-to` to retain verified archive bytes at a new private
path; it refuses existing paths and checks the copied length and digest. These
checks neither change the pinned source set nor evaluate catalogued code.
The shared Claude and Gemini prompt asks each evaluator to inspect the 47 core
documents and answer both questions within their separate source scopes. Its
answers remain model interpretations; only the packaged deterministic checks
are automated evidence, and no model call is made by the producer build or
local acceptance.

Explorer acceptance opens the large metadata bundle and the separate core
Reader projection. It checks the source-linked question, exact record identity,
classification evidence, the route-to-source mapping, and negative controls.
Offline AI acceptance uses the same immutable archive, release manifest and
verifier. Neither workflow calls a language-model API or executes catalogued
repository code. A passing Reader journey proves access and navigation only;
it does not prove that a model or human interpreted the evidence correctly.
