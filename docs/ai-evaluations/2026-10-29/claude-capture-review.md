# Claude UI capture: editorial review

Reviewed on 29 October 2026. This supplement supersedes the earlier statement
that the original command history had not been supplied. It does not alter the
historical report or claim a new Claude run.

The user supplied the expanded UI history for the same v0.3.0 build
`cf3cc937490d7f3f4de51883e3f8e6d6041c5e24e777d2cecf4b10e95e42b94d`
and archive digest
`d739a2a058425eb40e6515a7489bbf3f5d33b439803caa3c2387ca1b5b14d1ae`.
Both identities occur in the capture. Its 130,343 bytes have SHA-256
`7111cae8207221509061ae9ad7e3a2cb370f4e3c7a97fd16181b3533a9e836d2`.
The current inspected selector displayed **Opus 5.5, Medium**; it does not
establish the model or settings behind every historical call.

## What the capture establishes

There are 35 displayed command requests, 30 Response labels and five Error
labels. All five Error regions display exit code 1. The other labels do not
establish exit code zero. One helper-creation request is shortened by “14 more
rows”; 15 response regions contain truncation or persisted-output notices.
Twenty-four complete Python bodies were retained. Every request, response
region and complete Python body was compared with its source byte range.

The capture supports the reported archive download and digest; displayed
record and facet counts; exact-name lookup; the Python/SBOM intersection of
1,618; security-query totals; contributor inverse lookup; and the reported
NHS contributor and recent-change totals. These are observations of displayed
requests and response regions. They are not an independently replayed audit.
The shortened helper and remote saved outputs prevent complete portable replay.
Response regions can include intervening model narrative.

The five command errors concern blocked shell network access, a scratch-file
path, reading gzip as plain JSON, an undefined helper alias and treating an
uncompressed semantic file as gzip. Later requests revisit these areas. These
are command errors, not five inferred failed bundle acceptance tests. The
capture provides no browser interaction: Claude's browser UNTESTED status and
the separate public Chrome acceptance evidence remain distinct.

## The checksum count is now explained

Request 9 displays `ok 1028 bad 0 missing 0`. Its code recursively selects
objects containing both `path` and `sha256`. The exact frozen build manifest
has 1,025 such history-observation records plus three other source bindings:
the repository feed, SBOM-quality summary and metadata baseline. That explains
1,028. The 75 controlled inputs and 3,321 generated outputs use path-to-digest
maps, which this selection does not enumerate. The original table's description
of 1,028 as all controlled inputs and outputs overstates this check's coverage.
Separate data/semantic/locator/adjacency checks must retain their own scope.

## Public evidence and limits

The [machine-readable review](claude-capture-review.json) lists each request's
purpose, source line, displayed outcome, explicit exit code when present,
truncation flags and retained-region digests. It contains no local paths or
raw command bodies. Raw capture, account environment details, scratch paths
and remote saved-output locations remain outside this public edition.
No recovered command, repository code or model was executed during this review.
The [repeatable test guide](../../ai-evaluation.md) remains the route for a new
controlled evaluation on identical frozen inputs.

## Displayed request inventory

“Response” means the UI label; “—” means no explicit exit code was displayed.
“Shortened” identifies requests or response regions with omitted UI content.

| Request | Purpose | UI label | Exit code | Shortened |
| --- | --- | --- | --- | --- |
| 1 | Live descriptor shell access | Error | 1 | No |
| 2 | Frozen archive download | Response | — | No |
| 3 | Archive inventory and digest | Response | — | No |
| 4 | Archive directory inventory | Response | — | response |
| 5 | Descriptor and shard layout | Response | — | response |
| 6 | Descriptor entrypoint digests | Response | — | response |
| 7 | Manifest traversal from generated directory | Response | — | response |
| 8 | Inspect persisted checksum results | Response | — | No |
| 9 | Manifest traversal from archive root | Response | — | response |
| 10 | History and discovery documentation | Response | — | response |
| 11 | Semantic and facet documentation | Response | — | response |
| 12 | Load record shards and NHS profile | Response | — | response |
| 13 | Inspect NHS narrative | Response | — | response |
| 14 | Read scratch records using relative path | Error | 1 | No |
| 15 | Correct scratch path and inspect search contract | Response | — | response |
| 16 | Read facet definitions | Response | — | response |
| 17 | Create discovery helper (shortened request) | Response | — | request |
| 18 | Exact search and targeted record lookup | Response | — | response |
| 19 | Validate record-locator buckets | Response | — | No |
| 20 | Python/SBOM intersection and history states | Response | — | No |
| 21 | Security queries and classification examples | Response | — | response |
| 22 | Inspect prefix index and selected examples | Response | — | No |
| 23 | Read compressed adjacency as plain JSON | Error | 1 | No |
| 24 | Validate adjacency digests and inspect rows | Response | — | response |
| 25 | Inspect NHS incident assertions | Response | — | response |
| 26 | Contributor and concept inverse lookup | Response | — | No |
| 27 | RDF inspection with undefined helper alias | Error | 1 | No |
| 28 | RDF assertion inspection and gzip format error | Error | 1 | No |
| 29 | Correct mixed-compression RDF inspection | Response | — | No |
| 30 | Source-feed digest and assertion evidence | Response | — | No |
| 31 | Contributor totals, weekly totals and coverage | Response | — | No |
| 32 | History index and pending-state examples | Response | — | No |
| 33 | Inspect one pending provider observation | Response | — | No |
| 34 | Facet counts and SBOM-quality cross-checks | Response | — | No |
| 35 | Inspect report output directory | Response | — | No |
