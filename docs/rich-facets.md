# Facets for discovery, code analysis and vulnerability investigation

The authored contract in config/facets.json defines 25 dimensions, each with
a reader question, field, label, evidence basis and deliberate missing value.
Counts cover every distinct repository. Three task dimensions—subject,
engineering task and content type—must distinguish meaningful selections.

| Group | Facets | Evidence boundary |
| --- | --- | --- |
| Purpose and content | Subject domain, engineering task, content type | Unreviewed name/description rules; multiple labels and unclassified values |
| Code analysis | Hosting account, primary language, language family, fork status, archive status, description availability | Source metadata and declared groupings; no source-code inspection or build-system inference |
| Reuse and activity | Reported licence, licence evidence, push year, time since push | No legal clearance, maintenance promise or security rating |
| SBOM investigation | SBOM link, reported version resolution, dependency context, package count band, quality-report age | Upstream quality counters and heuristics; no vulnerability or deployment assessment |
| Change and contribution | Metadata change status/degree, history coverage, recent commit band, line-count availability, historical/recent contributor accounts | Default-branch statistics and snapshot comparisons; no quality, influence or ownership ranking |

Content types include applications/services, libraries/components, API clients,
infrastructure/configuration, data, analysis/notebooks, documentation/guidance,
prototypes/design, tests, security tools, learning material and research.
They are suggestions, not inspection of repository contents. Mixed repositories
can have several types; absent evidence remains unclassified.

The daily refresh also freezes the upstream SBOM quality summary. Its source
URL, SHA-256, retrieval and generation dates accompany per-repository counts.
Counts reconcile against the report; identical duplicate rows retain one
repository profile. Aggregate published totals retain their original raw-row
denominator and must not be confused with distinct package identities.

The version-resolution facet distinguishes missing reports, empty inventories,
fully reported resolved versions, partially unresolved versions and no resolved
versions. An empty or fully resolved inventory does not mean no vulnerabilities.
Runtime/build/CI classifications are publisher heuristics. Quality-report age
does not establish the creation date or completeness of an individual SBOM.

## Explore and combine

```sh
uv run --locked python scripts/catalogue.py facets --facet content_type
uv run --locked python scripts/catalogue.py facets --facet publisher --value-query nhs
uv run --locked python scripts/catalogue.py facets --facet publisher --offset 20 --limit 20
uv run --locked python scripts/catalogue.py facets --language Python --facet sbom_resolution
uv run --locked python scripts/catalogue.py search --language Python --language Java --content-type library-component
uv run --locked python scripts/catalogue.py search --sbom present --sbom-resolution some-unresolved
```

Repeated values are OR within one dimension; dimensions combine with AND.
Facet counts are recomputed within the selected query and filters, with value
search and paging. A repository counts once per value; overlapping counts
cannot be summed as a unique total. Zero-result selections are valid.

Generated search filter-postings, facet definitions, count rows and the Explorer
presentation sidecar share the complete record plane. Checks recompute counts
and reject stale or incomplete classifications. Static tests exercise OR, AND,
empty selections and multi-value counts. Explorer browser acceptance remains
pending; presentation metadata is not proof of working Reader controls.

## Contributor and activity unknowns

Account arrays contain logins only. Contributor facet values use separate
projection fields so missing, pending, empty and unavailable collection states
do not masquerade as accounts or collapse into not-collected. Recent commit
bands and churn availability use the exact non-available coverage state. A
coverage notice states the available denominator before activity is compared.
