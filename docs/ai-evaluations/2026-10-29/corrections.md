# Editorial corrections and disposition

These notes distinguish the historical model outputs from checks against their
actual frozen inputs. The reports evaluated different versions. Their claimed
executions and complete statistical audits have not all been independently
reproduced. Corrections below are bounded to the cited source or retained data.

## Claude report

| ID | Original claim or interpretation | Verified qualification |
| --- | --- | --- |
| C1 | No published archive checksum was found | The release publishes SHA256SUMS, including archive digest d739a2a0…b14d1ae. This matches the hash reported by Claude. |
| C2 | Search silently loses 200 of 400 security matches | The result bound is real. The consumer reports total matches, truncation and display-limit messages. Claude did not exercise the UI, so silence was not established. |
| C3 | Browser acceptance is pending | Browser UNTESTED correctly describes Claude's own run. Separate public acceptance receipts record 38 passing Chrome checks for this v0.3.0 snapshot. Pending wording in the archived documentation lagged those receipts. |
| C4 | The build manifest verification row contains 1,028 controlled inputs and outputs | The exact frozen manifest lists 75 controlled inputs, 3,321 outputs and 1,025 history observations. The report's count needs reconciliation with its original verification code before its aggregate checksum claim can be accepted. |
| C5 | Recent changes are roughly weekly | The retained observation reports 8 commits across 7 active weeks in a 13-week window. This is an observed distribution, not a weekly maintenance commitment. |
| C6 | A push timestamp proves code activity in the history window | It records a reported push. It does not establish a non-zero default-branch contributor count, the content of a change or its applicability to the statistics window. |
| C7 | The 14,326 SBOM-path figure is stale | It describes the explicitly labelled initial source snapshot. The evaluated later snapshot contains 14,399 distinct repositories with paths. Historical figures need clear dates/source hashes rather than replacement by a moving latest count. |
| C8 | Abbreviated evidence paths identify exact archived files | Abbreviations are descriptive references, not literal paths. Some observation suffixes are inconsistent. Resolve the full digest through the frozen history index; do not invent a file from an abbreviated name. |

Verified examples and source:

- [Frozen v0.3.0 input and checksums](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40796536582-1).
- [Consumer result-summary implementation](https://github.com/chris-page-gov/okf-explorer/blob/6fc781ce2b350285705d670c51ca400983d8fad1/apps/okf-explorer/src/lib/search/searchPresentation.ts#L21-L37).
- [Separate v0.3.0 browser receipt](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/baef1d419b6769956bf56163f1fd4646188d3723/validation/browser/2026-10-29/public-browser-verification.json).

The code review confirmed distinct history states collapsing in activity facets,
status strings in account lists, social/cyber ambiguity and plural matching
gaps, and incomplete runtime/RDF metadata parity. These informed v0.4.0 changes.
Source and build identifiers had distinct valid roles but needed clearer names.
Retained history joining a later catalogue is a longitudinal observation; its
binding and dates should be explicit.

## Gemini report

| ID | Original claim or recommendation | Verified qualification |
| --- | --- | --- |
| G1 | The report can assess the newer published bundle | It evaluates v0.2.1 build 5415a6dd…, not Claude's v0.3.0 build cf3cc937…. Coverage, SBOM counts and publication configuration cannot be compared as the same input. |
| G2 | The archive is 26,238,546 bytes | The exact archive with the reported SHA-256 6cb6981f…b089c1 is 39,007,416 bytes. |
| G3 | classify_terms() uses unrestricted substring matching | The cited archive contains classify(), which normalises text and matches whole tokens or phrases with space boundaries. The proposed remedy was already present. The substring examples do not describe this implementation. |
| G4 | CLI search accepts one --facet argument and cannot intersect facets | Search supports repeated named filters, OR within each key and AND across keys. --facet belongs to the facet-listing command. total_matches was already reported. Paging was added later in v0.4.0. |
| G5 | NHS recent history has 4 active weeks and 23 additions / 20 deletions | The exact observation named by the report contains 8 commits across 7 active weeks, 38 additions and 5 deletions. Its observed head is near the statistics request, not an atomic commit binding. |
| G6 | RDF exports omit scope, rights and measurements | All three already appear in the cited archive's RDF. Labels, authority, derivation, observation and review metadata had genuine parity gaps. The report's small field count is also inconsistent with its own enumeration. |
| G7 | Logical routes must gain a concepts/ prefix to match storage | Logical identifiers and physical Markdown placement have different roles. That difference alone does not establish broken navigation or justify changing identifiers. The later content-type route correction is a separate, browser-tested change. |
| G8 | The catalogue contains GitLab and Bitbucket repositories | Every repository URL in the frozen feed uses github.com. Multi-provider contributor identity is a possible future design topic, not a demonstrated property of this dataset. |
| G9 | Records expose organisation_id, created_at, pushed_at, history_status and flat recent/historical commit fields | Those fields are absent from the cited runtime record. Its relevant fields include publisher, timestamp, history_coverage and nested activity. Read the actual frozen schema rather than the report's invented names. |
| G10 | Every linked local file was an inspected archive resource | Several cited resources are absent from the frozen archive. The evidence map marks unresolved paths explicitly. A link to the release identifies the source archive; it does not certify that a named member exists. |

Verified source references in the exact older producer:

- [Whole-term classifier](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py#L127-L136).
- [Filter intersections and named CLI options](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py#L528-L570).
- [RDF scope, rights and measurements](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py#L300-L316).
- [GitHub-only source validation](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py#L77-L92).
- [Frozen v0.2.1 input and checksums](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1).

The exact NHS observation in both inputs is
`source/history/observations/2e9c32ed9b98ed517af9f54c84cdbaa2fdb8124ef78d3b3ed337ca998543bdef.json`.
Its bytes match that content hash. Historical commits total 299 across five
reported accounts; the recent window is 26 July to 25 October 2026, end excluded.

The report usefully identifies limited collection coverage and some semantic
presentation gaps. Its overall PASS summary is not accepted as current-release
assurance. The independent editorial checks do not establish general model
quality or compare model capability: the inputs and environments differed.

## Implemented response and repeatable retest

[v0.4.0](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/v0.4.0)
addresses the confirmed history-state, classification and RDF parity issues,
clarifies provenance, adds CLI paging and supplies an archive-pinned test pack.
It preserves bounded Explorer results and logical routes. History backfill and
broader domain review remain ongoing.

The [v0.4.0 evidence](../../../validation/browser/2026-10-29-v0.4.0/README.md)
records 57 unit/regression tests, 40 Chrome checks and ten offline evaluation
checks on that publication. Those are separate from these historical model
runs. No new Claude or Gemini execution is claimed.

Use [the shared evaluation guide](../../ai-evaluation.md) for the next round:
give both models the same frozen archive, ZIP and SHA256SUMS, use PROMPT.md
unchanged, and preserve each verifier script and machine-readable result.
