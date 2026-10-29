# Copilot CLI evaluation: public edition

Public edition prepared on 29 October 2026 from the owner-supplied early
example. No new Copilot run was performed for this edition.

> **Historical model output with editorial qualifications.** The PASS claims
> below remain attributed to the original report. Read the
> [correction ledger](corrections.md#copilot-report) before quoting results.
> This is not acceptance of the current release or a controlled model comparison.

- Evaluated software: **v0.3.0**, build
  `cf3cc937490d7f3f4de51883e3f8e6d6041c5e24e777d2cecf4b10e95e42b94d`.
- Frozen input: [snapshot-40796536582-1](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40796536582-1).
- Archive SHA-256:
  `d739a2a058425eb40e6515a7489bbf3f5d33b439803caa3c2387ca1b5b14d1ae`.
- Retained private provenance records Fusion Max selection and
  `gpt-6-astra` on 37 tool starts/completions, 15 commands and three complete
  JSON outputs. This identifies the recorded calls and resolution events;
  tool transport success is not a substantive test verdict.
- Original report bytes are bound by the [publication manifest](publication-manifest.json).
  Raw sessions, prompts and account environment details remain private.

The complete report is retained below. Its live URLs and numerical findings
refer to its frozen input and test date. The editorial review has not replayed
all original verification code. Local archive paths are descriptive selectors,
not promises that every member is a separately hosted web page. Exact schema
identifiers and source quotations retain their original spelling.

## Original report with qualifications

# Experimental OKF+ Bundle Metadata Test Report

**Test date:** 29 October 2026  
**Scope:** Read-only testing of published bundle metadata.

## Result

**All seven requested metadata tests passed**, with important limits: only **46 of 24,068 repositories have available history**, classifications are unreviewed inferences, and SBOM references are not vulnerability evidence. **No browser acceptance is claimed.**

## Access and snapshot

The live [descriptor](https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json) and the [frozen archive](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/download/snapshot-40796536582-1/xgov-okf.tar.gz) identify the same build:

```text
cf3cc937490d7f3f4de51883e3f8e6d6041c5e24e777d2cecf4b10e95e42b94d
```

Generated: **2026-10-29T00:49:41Z**. The archive contains **24,068 distinct repository records**, **114,470 assertions**, and **212 hosting accounts**. The source has 24,137 rows; the descriptor records 69 duplicate rows.

I used the frozen archive for all subsequent calculations. Its 63,950,126 bytes matched the SHA-256 published in [release metadata](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40796536582-1):

```text
d739a2a058425eb40e6515a7489bbf3f5d33b439803caa3c2387ca1b5b14d1ae
```

**Integrity:** all 3,321 generated-output hashes, 1,025 retained history-observation hashes, two frozen feed hashes and 26 extracted controlled-input hashes matched. I checked the declared sizes and compressed-byte hashes of all **278 runtime shards and 280 semantic files**, following declared gzip compression before JSON parsing. Selected navigation-index hashes and sizes also matched.

**Archive-path convention:** `G/` means `xgov-okf/generated/`; `S/` means `xgov-okf/source/`. Array indexes below are zero-based.

| Resources actually read or programmatically parsed | Scope |
|---|---|
| `G/okf-explorer.json`, `G/build-manifest.json`, `G/data/manifest.json`, `G/data/search/manifest.json`, `G/semantic/manifest.json` | Complete archived descriptors/manifests |
| `G/data/records-000.json.gz` through `records-048.json.gz`; `assertions-000.json.gz` through `assertions-228.json.gz` | Complete record and assertion populations |
| All files listed in `G/semantic/manifest.json` | Parsed; selected assertions and endpoints inspected; reverse-link search across the graph |
| `G/data/facet-definitions.json`, search `doc-map.json`, filters `language`, `sbom`, `capability`, `history_coverage`; lexicon/postings `11`, `nh`, `re` | Discovery and exhaustive filter calculations |
| `G/data/record-locator.json`, locator buckets `00`, `d4`; `G/data/adjacency.json`, adjacency buckets `00`, `d4`, `2c`, `b4`; `G/data/endpoint-labels.json` | Forward and reverse navigation |
| `S/current.json`, frozen repository and SBOM-quality feeds, `S/history/index.json`, the two observations identified below; `G/quality.json` | Source and coverage evidence |
| `xgov-okf/okf.semantic.json`; docs `discovery.md`, `rich-facets.md`, `semantic-model.md`, `history-and-change.md`, `security-and-sbom-review.md` | Published definitions and limitations |

Hash-checking other files is **not** a claim that their contents were inspected. Initial web-tool manifest displays were truncated; complete archived manifests resolved that limitation.

The semantic manifest's `snapshot` is a **source-feed URN**, ending in `ad5605...`, whereas the explorer uses the build identifier above. Both are bound into this same archive; I did not combine separate live snapshots.

## 1. Discovery and facet filtering

### Exact repository

Found exactly **one** result:

**https://github.com/111Online/nhs111-resources**

Matching fields: `title="111Online/nhs111-resources"`, normalized `name="111online/nhs111-resources"`, and the canonical `url` above.

Evidence: `G/data/records-000.json.gz[0]`, source row **14456**. Intersecting the published postings for `111online`, `nhs111`, and `resources` returned only document **0**; `G/data/search/doc-map.json` resolves it to `repositories/111online%2Fnhs111-resources.md`. Locator bucket `G/data/record-locator/d4.json` independently resolves that route to shard/index `[0,0]`.

### Three Python repositories with recorded SBOM information

All three have `language="Python"` and `sbom="present"`:

| Canonical repository URL | Recorded SBOM path | Record reference; source row |
|---|---|---|
| https://github.com/acteng/ate-api | `sbom/acteng/ate-api.json.gz` | `G/data/records-000.json.gz[1]`; **19481** |
| https://github.com/acteng/atip-data-prep | `sbom/acteng/atip-data-prep.json.gz` | `G/data/records-000.json.gz[4]`; **19487** |
| https://github.com/acteng/update-your-capital-schemes | `sbom/acteng/update-your-capital-schemes.json.gz` | `G/data/records-000.json.gz[7]`; **19482** |

Their frozen quality-summary entries report respectively **24/24**, **881/1**, and **81/39** packages/unresolved versions. These are publisher-reported counters, not my inspection of those SBOM documents.

Quality-summary evidence:

```text
S/snapshots/4f905e73fdabf484c23169d42938e00a1144947d7bd4d75158829fb5ac8dad48.sbom-quality.json
```

It declares generation at **2026-10-29T00:33:35.855Z**. **I did not inspect any SBOM payload.** Neither a path, `present` flag, unresolved version nor package count establishes a vulnerability.

### Three security-related repositories

These belong to the published `capability="identity-security"` selection, which contains **400 distinct repositories**. The following are examples, not the complete count.

| Canonical repository URL | Matching metadata | Evidence |
|---|---|---|
| https://github.com/alan-turing-institute/awesome-AVD | Description: "A curated list of research resources in automated vulnerability detection (AVD)"; matched term `vulnerability` | `G/data/records-000.json.gz[78]`; source row **23457** |
| https://github.com/alphagov/aws-security-tools | Description: "Scripts to help reviewing AWS environments as part of a security test"; matched `security`; `archived=true` | `G/data/records-001.json.gz[230]`; source row **1268** |
| https://github.com/alphagov/cyber-security-auto-snyk | Title matches `security`, `cyber`; description says it automates Snyk tests and aggregates results; `archived=true` | `G/data/records-001.json.gz[359]`; source row **674** |

Their capability/content classifications are **inferred from metadata**, not verified functionality. The descriptions establish discovery relevance, not current operation, effectiveness, support or vulnerabilities in these repositories.

### Two-facet combination

I intersected the document-ID sets in:

```text
G/data/search/filters/language.json -> values.Python
G/data/search/filters/sbom.json     -> values.present
```

| Selection | Complete count |
|---|---:|
| Primary language = Python | 2,644 |
| SBOM link reported = present | 14,399 |
| **Python AND SBOM present** | **1,618** |

The intersection exactly matched an independent filter over **all 24,068 records**, after resolving IDs through `doc-map.json`.

Published logic is **OR within a facet, AND between facets** (`xgov-okf/docs/rich-facets.md`). The search manifest declares **`result_limit: 200`**. I did not apply that limit to counts: 1,618 is the full population, not three examples or a capped result list. Browser behavior at that limit remains untested.

## 2. Semantic links and inverse navigation

Both relationships start at:

```text
source:     repositories/111online%2Fnhs111-resources.md
source_iri: urn:okf:xgov:repository:111online%2Fnhs111-resources
```

### Contributor relationship

Evidence: **`G/data/assertions-000.json.gz[7]`**

| Field | Recorded value |
|---|---|
| Assertion identifier | `urn:okf:xgov:assertion:0d7028a9d7391ab2f719986d03ff22f9d315ef423421569cc662ba80986c463a` |
| Target | `contributors/andriaturner.md` |
| Target IRI | `urn:okf:xgov:contributor:andriaturner` |
| Predicate | `urn:okf:xgov:reportedRecentContributor` |
| Preferred / inverse labels | "recent contributor reported by GitHub" / "reported recent contributor to" |
| Status / review / scope | `normalized` / `source-reported-not-independently-verified` / `real-world` |
| Authority | Class `derived`; label "Experimental catalogue projection"; source [GitHub contributor-statistics endpoint](https://api.github.com/repos/111online/nhs111-resources/stats/contributors) |
| Derivation | `urn:okf:xgov:rule:source-field-v1` |
| Observation | **2026-10-28T19:43:34Z** |
| Measurement | **8** reported commits; `recent-complete-weeks`; **2026-07-26 inclusive to 2026-10-25 exclusive** |
| Evidence selector | `profile.contributors`, row **1**, in the observation below |

```text
S/history/observations/2e9c32ed9b98ed517af9f54c84cdbaa2fdb8124ef78d3b3ed337ca998543bdef.json
```

Its filename SHA-256 and the contributor-value hash both verified. The latter is:

```text
5f34bce2abd57b70a249e158e81fe90893227d560b0fad701ed688cca24ec934
```

This establishes an account's **reported contribution in a defined window**. It does not establish a verified person, ownership, maintainership, approval authority, endorsement or permission to scan.

### Domain relationship

Evidence: **`G/data/assertions-000.json.gz[3]`**

| Field | Recorded value |
|---|---|
| Assertion identifier | `urn:okf:xgov:assertion:b4455286cb0ad1a44689ebb69126db4381914173046ee128fd3449b7d13dfa30` |
| Target | `domains/health.md`, labelled **Health and care** |
| Target IRI | `urn:okf:xgov:domains:health` |
| Predicate | `https://schema.org/about` |
| Preferred / inverse labels | "suggested domain" / "suggested domain of" |
| Status / review / scope | `inferred` / `unreviewed` / `real-world` |
| Authority | Class `derived`; label "Experimental catalogue projection"; source [repository feed](https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json) |
| Derivation | `urn:okf:xgov:rule:term-match-v1` |
| Observation | **2026-10-29T00:49:41Z** |
| Evidence selector | Source row **14456**, field `name+description`, matched term **`nhs`** |

Frozen evidence:

```text
S/snapshots/ad5605cbaba3cbb8c391e8e97fddfdb665567dd07c78c5300215f03e85eebc97.json
```

The file hash and canonical name/description value hash verified; the latter is:

```text
cee0df33ec5dd6cabb6c9c89572ad9b1eff35916a458973926d37b5a89327d9d
```

This establishes **why the classifier suggested health**. It does not establish reviewed subject classification, clinical suitability or official endorsement.

### Reverse traversal and missing fields

Starting at `contributors/andriaturner.md`, **`G/data/adjacency/2c.json.gz`** returns the same recent-contributor assertion, preserving repository-to-contributor direction. Its inverse label supplies the readable traversal back to the repository. The repository-side entry is in **`G/data/adjacency/d4.json.gz`**.

Across all **114,470 assertions**, I found **no separately asserted contributor-to-repository relationship** for this pair. Across the semantic graph, the contributor node likewise has no direct reverse property to this repository. Thus **inverse navigation is not an inverse triple**.

All requested fields exist in the two runtime assertions. **Numeric confidence and supporting-assertion lists are absent**; the domain assertion has no measurement. I did not invent them.

The corresponding RDF assertions in `G/semantic/assertions-000.jsonld.gz` retain the triple, status, evidence and provenance, but **omit the runtime labels, authority, derivation, observation and review-status fields**. That is a cross-format information gap, despite successful runtime navigation.

## 3. Contributor history

### Available: `111Online/nhs111-resources`

Evidence: `G/data/records-000.json.gz[0]` and the hash-verified `2e9c32...` observation identified above.

| Measure | Value and exact interpretation |
|---|---|
| Historical commits | **299**, provider-reported contributor totals from available default-branch statistics, not reconstructed all-branch Git history |
| Historical contributors | **5 recorded accounts** in the available profile |
| Recent commits | **8**, during **13 complete Sunday-to-Sunday weeks**, `[2026-07-26T00:00:00Z, 2026-10-25T00:00:00Z)` |
| Recent contributors | **1 account** with reported commits in that window |
| Recent line changes | **43 = 38 additions + 5 deletions**; activity volume, not quality or value |

The current partial week is excluded from "recent." Historical sparse weekly rows extend from the week starting **2020-12-13** through **2026-10-25**, so historical totals can include activity outside the recent window.

The observation records **2026-10-28T19:43:34Z**, HTTP **200**, default branch **`main`**, and observed head:

```text
1f18b4c9836da93ec4305c9811affc4d8e71a063
```

It explicitly says the head/statistics requests are **not atomic**. This older observation is pinned inside the tested build, not a second snapshot fetched during testing.

**Identity evidence:** profile row 1 records login **`AndriaTurner`**, account type **`User`**, **124 historical commits** and **8 recent commits**. The contributor assertion above links precisely to that row. The other four recorded accounts have zero commits in this particular recent window, not necessarily zero activity elsewhere.

**Change over time:** annual reported commit totals are:

| Year of weekly UTC start | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Commits | 17 | 90 | 36 | 51 | 43 | 32 | 30 |

These show continuing recorded activity with varying volume. **2026 is incomplete**; the rows group weeks by their start year, not individual commit dates. All eight recent commits are attributed to AndriaTurner; that is not evidence of a maintainership transfer.

Definitions and exclusions come from `xgov-okf/docs/history-and-change.md`: statistics exclude merge commits, contributor statistics also exclude empty commits, and provider limitations can make line counts unknown.

### Pending: `alan-turing-institute/ai-rss-feeds`

Canonical URL: **https://github.com/alan-turing-institute/ai-rss-feeds**

`G/data/records-000.json.gz[25]` records:

```text
history_coverage = pending-provider-statistics
activity = null
recent_commit_band = not-collected
```

Its frozen observation records HTTP **202** at **2026-10-28T19:45:39Z**, with no contributor profile:

```text
S/history/observations/3dbf269b9d4522395e14523adcc4b42a53962e947e98b7621f585ed878dafd97.json
```

This means the provider's statistics were pending, not zero commits or contributors. The recorded retry time is **2026-10-29T01:45:39Z**; it does not prove a later retry occurred.

### Overall history coverage

Counts independently agree between all record shards and `G/data/search/filters/history_coverage.json`.

| State | Repositories | Share |
|---|---:|---:|
| `available` | 46 | 0.19% |
| `pending-provider-statistics` | 970 | 4.03% |
| `unavailable-response` | 7 | 0.03% |
| `empty-or-unavailable` | 2 | 0.01% |
| `not-collected` | 23,043 | 95.74% |
| **Total** | **24,068** | **100%** |

`S/history/index.json`, updated **2026-10-29T00:10:35Z**, contains **1,025 observation entries**. An entry is not synonymous with available history, and "available" remains bounded by provider coverage.

## Verdicts

| Test | Result | Basis |
|---|---|---|
| Access | **PASS** | Frozen archive accessible; identifiers and checked hashes agree |
| Discovery | **PASS** | Exact repository and all requested examples found with source evidence |
| Facet filtering | **PASS** | Complete 1,618-result intersection reconciled against every record |
| Semantic links | **PASS** | Contributor and inferred domain assertions traced; RDF omissions noted |
| Inverse navigation | **PASS** | Reverse lookup returns the original directed assertion |
| Available history | **PASS** | Defined measures, dates, identity and provenance recoverable |
| Missing-history handling | **PASS** | Pending/null distinguished from zero; complete coverage counted |
| Browser acceptance | **UNTESTED** | No browser exercised |

## Three concrete discovery improvements

1. **Expose complete counts and pagination/export beyond 200 results.** The Python/SBOM selection contains **1,618** records, versus the declared 200-result limit. Preserve the full count even when only a page is returned.

2. **Refine security aliases and separate subject relevance from content type.** `DRL4Sec-Pitfalls` explicitly mentions **"Cybersecurity"** but has `capabilities=["unclassified"]`, while the curated resource list `awesome-AVD` receives `security-tool`. Add reviewed aliases and distinguish literature/resources from executable tools. Evidence: `G/data/records-000.json.gz[209]` and `[78]`.

3. **Carry precise missing-history reasons into dependent facets.** The pending example's commit/contributor facets say `not-collected`, losing the more informative provider-pending state. Display coverage, observation age and retry status together; only **0.19%** currently have available statistics. Evidence: record `[25]`, its observation, and the coverage filter.

## Limitations and unresolved questions

Full counts were not truncated, but the published search result limit is 200. No repository code was executed, repositories scanned, maintainers contacted, SBOM payloads inspected or advisory databases queried. API URLs were treated as recorded provenance, not independently revalidated observations. Individual SBOM freshness/completeness, provider-statistics completeness and real-world classification accuracy remain unestablished.
