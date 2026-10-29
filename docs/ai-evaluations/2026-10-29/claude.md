# Claude Opus 5.5 evaluation: public edition

Public edition prepared on 29 October 2026 from the owner-supplied report.
The owner attributed the original output to **Claude Opus 5.5**. No new model
run was performed for this edition.

> **Historical model output with editorial corrections.** Original findings,
> PASS claims and recommendations are retained as model-reported claims.
> Several need qualification or correction; read the [correction ledger](corrections.md#claude-report)
> alongside this report. This is not acceptance of the current release.

- Evaluated software: **v0.3.0**.
- Complete build identifier: `cf3cc937490d7f3f4de51883e3f8e6d6041c5e24e777d2cecf4b10e95e42b94d`.
- Frozen input: [snapshot-40796536582-1](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40796536582-1).
- Archive SHA-256: `d739a2a058425eb40e6515a7489bbf3f5d33b439803caa3c2387ca1b5b14d1ae`.
- Provenance and evidence: [publication manifest](publication-manifest.json) and
  [evidence map](evidence-map.json).

Local filesystem URLs have been replaced by immutable source-file links or
frozen-release references. Original line fragments are not endorsed as exact
citations. Archive paths remain visible because generated files are not all
published as individual web pages. Prose uses British English; exact schema
identifiers and quoted source material retain their original spelling.
The expanded UI capture was supplied after the first public edition. Its
[editorial review](claude-capture-review.md) now records the displayed command
history, responses and limits. The capture supports several reported results
and explains the checksum-count discrepancy; it is not a complete portable
replay or independent certification of all claimed executions.

## Original report with annotations

## xgov OKF+ bundle: metadata test report

Test date: 29 October 2026 · Read-only metadata test · No repository code was executed or scanned, and no maintainers were contacted.

> **Editorial note C1/C4:** The archive checksum is published separately. The supplied UI capture explains the 1,028 count as source bindings rather than all controlled inputs and outputs; see [the correction ledger](corrections.md#claude-report).

### 0. Access and snapshot

| Item | Result |
|---|---|
| Live descriptor | `https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json`, read via web fetch. The page fetch returned a summarised view; the shell could not reach github.io (proxy refusal, HTTP 403 on CONNECT). |
| Frozen archive | `https://github.com/chris-page-gov/xgov-soft-eng-com/releases/download/snapshot-40796536582-1/xgov-okf.tar.gz` downloaded in full (63,950,126 bytes, SHA-256 `d739a2a0…b14d1ae`, 4,427 entries). No published archive checksum was found to compare it against. |
| Snapshot used throughout | `cf3cc937490d7f3f4de51883e3f8e6d6041c5e24e777d2cecf4b10e95e42b94d`, generated `2026-10-29T00:49:41Z`. The live descriptor and the archive's `generated/okf-explorer.json` give the same ID, so all analysis used the archive. |
| Source feed | `https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json`, SHA-256 `ad5605cb…bc97`, frozen at `source/snapshots/ad5605…bc97.json`. The file hash was re-verified. |
| Records | 24,068 distinct repositories from 24,137 raw rows (69 duplicates). The 49 record shards decompress to exactly 24,068 records. |
| Relationships | 114,470 assertions across 229 shards. All IDs are unique. |
| Publication state | `exploratory`, `noindex`, `authority_status: independent-research` |

**Checksum verification.** Every declared compression was honoured (gzip shards were decompressed after hashing the compressed bytes).

| Manifest | Entries verified | Mismatches |
|---|---|---|
| Descriptor entrypoints (endpoint labels, record locator, adjacency) | 3, byte length and SHA-256 | 0 |
| `generated/data/manifest.json` shards | 281 | 0 |
| `generated/semantic/manifest.json` shards | 280 (279 gzip, `catalogue.jsonld` uncompressed) | 0 |
| `generated/build-manifest.json` | 1,028 controlled inputs and outputs | 0 |
| Record-locator buckets | 256 | 0 |
| Adjacency buckets | 256 | 0 |

**Resources actually read:** descriptor; data, semantic, search and build manifests; facet definitions; `facets.json`; all record shards; all assertion shards; search lexicon, postings, prefixes, doc-map and filter postings; record-locator and adjacency buckets; semantic shards for repositories, assertions and vocabulary; source feed snapshot; SBOM-quality snapshot; history index; four history observations; docs (`discovery`, `semantic-model`, `rich-facets`, `history-and-change`, `security-and-sbom-review`).

**Not read:** individual per-repository SBOM documents (external host, and out of scope); `endpoint-labels.json` beyond its checksum; Markdown concept pages beyond the listing.

### 1. Discovery

#### 1a. Exact repository: 111Online/nhs111-resources (found)

- Canonical URL: [https://github.com/111Online/nhs111-resources](https://github.com/111Online/nhs111-resources)
- Record ID `urn:okf:xgov:repository:111online%2Fnhs111-resources`, route `repositories/111online%2Fnhs111-resources.md`
- **Route 1, search.** The query tokenises to `111online`, `nhs111`, `resources`. The first two tokens each match exactly one document (df=1), and the query policy requires every token to match. Result: 1 hit, doc 0, score 61.
- **Route 2, record locator.** FNV-1a-32 of the route gives bucket `d4` (`generated/data/record-locator/d4.json`). It maps the route to `[0, 0]`, which is `generated/data/records-000.json.gz`, row 0.
- Source evidence: feed row 14456 (`source_rows`). The `owner`, `language` and `sbom` value hashes in the assertions were recomputed and match.

#### 1b. Python repositories with recorded SBOM information

**Facet combination:** `language = Python` AND `sbom = present`.

- Filter logic: postings are read from `generated/data/search/filters/language.json` and `sbom.json` and intersected. Within one facet, values combine with OR; across facets, with AND.
- Complete count: **1,618**, out of 2,644 Python repositories and 14,399 with an SBOM path. A recomputation from the raw records also gives 1,618.
- Filter postings are complete ID lists with no result cap.
- Breakdown by `sbom_resolution` within the 1,618: some-unresolved 965, none-resolved 650, all-reported-versions-resolved 3.

The examples below are the first three non-archived repositories in document order:

| Repository | Record | SBOM path (metadata) | Upstream quality counts (frozen report, matched) | Resolution / context |
|---|---|---|---|---|
| [https://github.com/acteng/ate-api](https://github.com/acteng/ate-api) | records-000 | `…/sbom/acteng/ate-api.json.gz` | 24 packages, 0 resolved, 24 unresolved | none-resolved; build-test, CI, unresolved |
| [https://github.com/acteng/atip-data-prep](https://github.com/acteng/atip-data-prep) | records-000 | `…/sbom/acteng/atip-data-prep.json.gz` | 881 packages, 880 resolved, 1 unresolved | some-unresolved; runtime, build-test |
| [https://github.com/acteng/update-your-capital-schemes](https://github.com/acteng/update-your-capital-schemes) | records-000 | `…/sbom/acteng/update-your-capital-schemes.json.gz` | 81 packages, 42 resolved, 39 unresolved | some-unresolved; runtime, build-test, CI |

**Evidence levels, kept separate:**

1. **SBOM path / flag.** This is the `sbom` field from the feed and the `urn:okf:xgov:reportedSbom` assertion. It is a reference only.
2. **Upstream SBOM quality counts.** These were inspected. I checked that the per-repository counts in the records match `source/snapshots/4f905e73…dad48.sbom-quality.json` (`perRepo`) for all six repositories tested. This is the publisher's summary, not the SBOM itself.
3. **The SBOM document.** No SBOM document was fetched or inspected.
4. **Vulnerability evidence.** There is none. The bundle declares that no estate-wide vulnerability assessment is provided.

#### 1c. Repositories relevant to security or vulnerability management

| Query or facet | Complete count |
|---|---|
| Text `vulnerability` | 16 |
| Text `vulnerabilities` | 11 (no stemming) |
| Union of those two | 27 |
| Text `security` | **400 matches, more than the 200-result display cap** (`result_limit` in the search manifest) |
| Text `vulnerability management` | **0**, because the policy requires all terms |
| Facet `capability = identity-security` | 400 |
| Facet `content_type = security-tool` | 291 |
| Both facets (AND) | 262 |
| Vulnerability text union ∩ `security-tool` | 19 |

The three selected repositories are the top-ranked `vulnerability` matches whose names indicate security-management purpose:

| Repository | Matching fields | Inferred labels (unreviewed) | SBOM path | History |
|---|---|---|---|---|
| [https://github.com/DEFRA/ci-vulnerability-scanner](https://github.com/DEFRA/ci-vulnerability-scanner) (records-009) | title token `vulnerability` | identity-security; security-tool (matched term "vulnerability") | present, none-resolved (1 package) | not-collected |
| [https://github.com/nice-digital/npm-vulnerability-scan](https://github.com/nice-digital/npm-vulnerability-scan) (records-038) | title | identity-security; security-tool | not-reported | not-collected |
| [https://github.com/DFE-Digital/vulnerability-disclosure-program](https://github.com/DFE-Digital/vulnerability-disclosure-program) (records-014) | title and description ("security.txt…") | identity-security, delivery-operations; security-tool (terms "security", "vulnerability") | present, none-resolved (5 packages) | not-collected |

**Classifier observations.** These are relevant to discovery quality, and none of them is a security finding.

- `Public-Health-Scotland/covid-vulnerability` ("Community Vulnerability") is labelled `security-tool` and `identity-security`. This is a false positive: social vulnerability, not cyber.
- `hmrc/vulnerabilities` has no domain, capability or content type. This is a false negative, because the rules do not match the plural form.
- `UKHomeOffice/dq-packer-vulnerability-scanner` and `trivy-vulnerability-scanner` are archived. They are included by default.

### 2. Semantic links (starting from nhs111-resources)

The adjacency bucket is `generated/data/adjacency/d4.json.gz`. It holds 11 assertions for the route: account, language, SBOM reference, domain, content type, five historical contributors and one recent contributor. There is **no capability edge**, because the record is unclassified and no edge is invented.

#### 2a. Contributor relationship

| Field | Value |
|---|---|
| Assertion ID | `urn:okf:xgov:assertion:1aa737119311251424a78818b99e641b19f0923c23be880ad551aeebf8defc3f` |
| Source → target | `urn:okf:xgov:repository:111online%2Fnhs111-resources` → `urn:okf:xgov:contributor:andriaturner` |
| Predicate | `urn:okf:xgov:reportedHistoricalContributor` (kind `historical_contributor`) |
| Preferred / inverse label | "historical contributor reported by GitHub" / "reported historical contributor to" |
| Status / scope / review | `normalized` / `real-world` / `source-reported-not-independently-verified` |
| Authority | class `derived`, "Experimental catalogue projection", source `https://api.github.com/repos/111online/nhs111-resources/stats/contributors` |
| Derivation | `urn:okf:xgov:rule:source-field-v1` |
| Measurement | 124 reported commits, period `available-provider-history` |
| Evidence | `source/history/observations/2e9c32ed…e17d.json`, field `profile.contributors`, row 1, value SHA `5f34bce2…c934`. **Recomputed and matched.** |
| Observed | 2026-10-28T19:43:34Z |
| Rights | "Public GitHub statistics; no ownership, maintainership, endorsement or scan authority asserted." |

A paired recent assertion, `…0d7028a9…463a`, records 8 commits in the window 2026-07-26 to 2026-10-25 (end exclusive), with the same evidence row.

**What it establishes:** GitHub's contributor-statistics API attributed 124 default-branch commits (excluding merge and empty commits) to the account `AndriaTurner`, as observed on 28 October.

**What it does not establish:** the person's identity, employment, maintainership, ownership, approval authority, or anything about commits on other branches.

#### 2b. Domain relationship

| Field | Value |
|---|---|
| Assertion ID | `urn:okf:xgov:assertion:b4455286cb0ad1a44689ebb69126db4381914173046ee128fd3449b7d13dfa30` |
| Source → target | repository → `urn:okf:xgov:domains:health` (`domains/health.md`) |
| Predicate | `https://schema.org/about` |
| Preferred / inverse label | "suggested domain" / "suggested domain of" |
| Status / review | **`inferred` / `unreviewed`** |
| Derivation | `urn:okf:xgov:rule:term-match-v1`, matched term `nhs` |
| Authority | `derived`, catalogue feed |
| Evidence | feed row 14456, field `name+description`, value SHA `cee0df33…7d9d`. Recomputed and matched, using the hash input `{"description","name"}`. |

This is an inference from the token "nhs" in the name or description. It does not establish that the repository is a health service, NHS-owned, or clinically relevant. Its content type, `application-service`, is likewise inferred from the word "service".

#### Following back and inverse navigation

- `contributors/andriaturner.md` has 2 adjacency entries. Both are incoming, and both are the **same assertion IDs** as above, presented under the target.
- `domains/health.md` has 642 incoming entries. The facet count for `domain=health` is also 642.
- **No separately asserted inverse triple exists:**
  - All 114,470 assertions have a `repositories/…` source.
  - The vocabulary (`semantic/vocabulary.jsonld.gz`) declares no `owl:inverseOf`.
  - The contributor RDF node has only `@type`, `skos:prefLabel` and `route`.
  - Direct triples exist only from repository to target (`semantic/repositories-000.jsonld.gz`).
- So "reported historical contributor to" is a **navigation label** on the forward assertion, not a stored triple.

#### Missing or inconsistent fields

- `rdf:Statement` reification (`semantic/assertions-000.jsonld.gz`): it carries subject, predicate, object, status, scope, evidence, measurement and provenance. It **omits** the preferred and inverse labels, `derivation`, `authority` and `review_status`, which are present only in the runtime JSON.
- `prov:wasDerivedFrom` points to `urn:okf:xgov:snapshot:2e9c…`. That hash belongs to a history *observation*, but it is typed under the "snapshot" namespace.
- The semantic manifest's `snapshot` is `urn:okf:xgov:snapshot:ad5605…` (the source hash). The descriptor's `snapshot_id` is `cf3cc937…` (the build ID). These are two different "snapshot" identifiers.

### 3. Contributor history

#### Available history: 111Online/nhs111-resources

| Measure | Definition (from record and docs) | Value |
|---|---|---|
| Historical reported commits | Provider's reported contributor totals for the default branch, excluding merge and empty commits | **299** (equals the 5 contributor totals: 149 + 124 + 23 + 2 + 1) |
| Recent reported commits | 13 complete Sunday-to-Sunday weeks, excluding the current partial week | **8**, window 2026-07-26 to 2026-10-25 (end exclusive) |
| Recent reported line changes | Additions plus deletions in the window | **43** (38 + 5; recomputed from the weekly rows) |
| Historical contributor accounts | — | 5 |
| Recent contributor accounts | — | 1 (`AndriaTurner`) |
| Line-count status | — | `reported-history-contains-nonzero-counts` |
| Observed at | — | 2026-10-28T19:43:34Z (next check 2026-11-04) |
| Provenance | — | `source/history/observations/2e9c32ed…e17d.json`: HTTP 200, head SHA `1f18b4c9…a063` observed near (not atomically with) the statistics request; response SHA `c0bd5f2a…` |

Annual reported commits (by year of week start, UTC): 2020: 17, 2021: 90, 2022: 36, 2023: 51, 2024: 43, 2025: 32, 2026: 30. The total is 299.

Line changes were large in 2020–2022 (for example, 28,900 additions in 2020 and 27,242 deletions in 2022) and small from 2023 onward (under 310 additions a year).

**Reading the trend.** Commit activity peaked in 2021. It has run at a steady 30–50 commits a year since. Recent changes are small and roughly weekly, and the recent window has a single contributing account, compared with five historically.

This describes reported default-branch activity only. It is not a measure of quality, health or maintenance commitment, and the 2026 figure covers part of the year.

**Provenance wrinkle.** The observation's `catalogue_source_sha256` is `64e70d84…`, an earlier feed. This snapshot's feed is `ad5605cb…`. History was therefore collected against a previous catalogue and joined to this one.

#### Missing history

- **Pending:** [https://github.com/alan-turing-institute/language-models-reading-group](https://github.com/alan-turing-institute/language-models-reading-group) (records-000)
  - `history_coverage = pending-provider-statistics`, and `activity` is null.
  - Observation `…/1397150d…d410.json` records HTTP **202**: GitHub was still computing. `head_sha_observed` is null.
  - The feed reports a push on **2026-07-30**, which falls inside the 13-week window. So there was code activity, but no counts are available. Pending is not zero.
- **Not collected:** [https://github.com/Public-Health-Scotland/cancer-routes-to-diagnosis](https://github.com/Public-Health-Scotland/cancer-routes-to-diagnosis) (records-040)
  - No index entry. The facets show `recent_commit_band = not-collected` and `historical_contributors = ["not-collected"]`.
  - The feed reports a push on 2026-07-30, so this too has activity the history plane cannot see.
- **Unavailable:** [https://github.com/alphagov/ckan-fix](https://github.com/alphagov/ckan-fix) shows `unavailable-response`, yet its observation records HTTP **200** with no profile. The reason is not explained (see open questions).

#### Overall history coverage (this snapshot)

Source: `source/history/index.json`, updated 2026-10-29T00:10:35Z. It contains 1,025 entries, which agrees with the record facets.

| State | Repositories | Share of 24,068 |
|---|---:|---:|
| available | 46 | 0.19% |
| pending-provider-statistics | 970 | 4.03% |
| unavailable-response | 7 | 0.03% |
| empty-or-unavailable | 2 | 0.01% |
| not-collected (no attempt yet) | 23,043 | 95.74% |

- 6,716 not-collected repositories and 118 pending repositories were pushed in the last 90 days.
- Contributor relationships in the graph (855 historical, 74 recent) therefore describe about 46 repositories, not the estate.
- `AndriaTurner` appears on just one repository, but that reflects coverage, not reach.

> **Editorial note C3:** Browser UNTESTED describes this model run. Separate published browser receipts exist.

### 4. Results

| Test | Result | Basis |
|---|---|---|
| Access | **PASS** | The descriptor was read live (summarised view) and the full archive was read. The snapshot ID matches. All 2,104 declared checksums verify. The shell could not reach github.io. |
| Discovery: exact | **PASS** | One exact hit, by search and by record locator |
| Discovery: Python + SBOM | **PASS** | 1,618 complete, cross-checked against raw records |
| Discovery: security | **PASS, with caveats** | Results were found, but "security" truncates at 200 of 400; multi-word queries are all-terms; there is no stemming; classifier false positives and negatives exist |
| Facet filtering | **PASS** | OR within a facet, AND across facets, and complete postings. 1,290 facet counts match the postings exactly. |
| Semantic links | **PASS** | All requested fields are present in the runtime JSON. Evidence hashes recompute. The RDF projection omits labels, authority and derivation. |
| Inverse navigation | **PASS** | It works through target-indexed adjacency with `inverse_label`. It is not a separate inverse triple, and that is a correct but undocumented-in-RDF distinction. |
| Available history | **PASS** | Measures, window, observation and provenance are present, and the sums reconcile |
| Missing-history handling | **PASS** | Null activity, explicit states, and no zero substitution. Minor issue: the band facet labels pending repositories "not-collected". |
| Browser (Explorer UI) | **UNTESTED** | No browser was exercised. The bundle itself states that browser acceptance is pending. |

> **Editorial note C2:** The 200-result bound is real. The consumer reports totals and limits; this report did not test whether the UI disclosed them.

### 5. Three discovery improvements

1. **Remove or expose the 200-result cap, and add OR and stemming for text queries.**
   - "security" silently loses 200 of 400 matches. "vulnerability management" returns 0. "vulnerability" and "vulnerabilities" are disjoint (16 and 11).
   - Suggested fixes: return the total match count with paging, and add a light stemmer or alias list in the task vocabulary.
2. **Tighten the security classification rules and add a negative-context list.**
   - "covid-vulnerability" (social vulnerability) is tagged as a security tool, while `hmrc/vulnerabilities` is unclassified.
   - Suggested fixes: add plural and stem matching, disambiguate "vulnerability" by co-terms (scan, cve, disclosure, dependabot, trivy), and surface `matched_terms` in result lists.
3. **Make history coverage first-class in discovery and fix its labels.**
   - With 95.7% not collected, any contributor or recent-activity filter silently returns a tiny, biased subset.
   - Suggested fixes:
     - Show a coverage banner with counts on contributor and activity facets.
     - Use distinct `pending` and `unavailable` values in `recent_commit_band` and the contributor facets, instead of folding them into `not-collected`.
     - Stop storing the sentinel `"not-collected"` inside the contributor-account list.
     - Prioritise collection for the 6,716 uncollected repositories pushed in the last 90 days.

### 6. Limitations and open questions

- **Tool access.** github.io was blocked from the shell, and web fetch returned a summarised descriptor rather than raw bytes. Live shard bytes on Pages were therefore not compared with the archive; only the descriptor's snapshot ID, counts and checksums were compared. Per-repository SBOMs were not fetched.
- **Archive integrity.** The archive's own SHA-256 (`d739a2a0…`) could not be checked against a published value.
- **Stale documentation.** `docs/security-and-sbom-review.md` and `REPOSITORY_STATUS.md` say 14,326 repositories have SBOM paths. This snapshot derives 14,399 distinct (14,415 raw rows).
- **Open question:** why does `alphagov/ckan-fix` (HTTP 200) end in `unavailable-response` with no profile?
- **Open question:** should history observations bound to an earlier feed (`64e70d84…`) be flagged when joined to a later catalogue?
- **Open question:** which identifier is canonical, the semantic manifest's snapshot URN (`ad5605…`, the source hash) or `snapshot_id` (`cf3cc937…`, the build)?
- **Unexplained field difference:** the RDF repository nodes carry `stars`, `forks` and `openIssues`, but the runtime records do not.

### Evidence index (archive paths, prefix `xgov-okf/`)

| Path | Used for |
|---|---|
| `generated/okf-explorer.json` | Descriptor, snapshot ID, counts |
| `generated/data/manifest.json`, `generated/semantic/manifest.json`, `generated/build-manifest.json` | Checksums |
| `generated/data/records-000.json.gz` row 0 | nhs111 record |
| `generated/data/record-locator/d4.json` | Locator lookup |
| `generated/data/adjacency/d4.json.gz` | nhs111 assertions and the reverse lookup for `contributors/andriaturner.md` |
| `generated/data/search/manifest.json` | `result_limit`: 200 |
| `generated/data/search/filters/{language,sbom,sbom_resolution,history_coverage,capability,content_type}.json` | Facet postings |
| `generated/data/facets.json` | Facet counts |
| `generated/semantic/assertions-000.jsonld.gz`, `repositories-000.jsonld.gz`, `vocabulary.jsonld.gz` | RDF projection |
| `source/snapshots/ad5605cb…bc97.json` row 14456 | Feed evidence |
| `source/snapshots/4f905e73…dad48.sbom-quality.json` | SBOM quality counts |
| `source/history/index.json` | Coverage |
| `source/history/observations/2e9c32ed…e17d.json` | Available history |
| `source/history/observations/1397150d…d410.json` | Pending (HTTP 202) |
| `source/history/observations/6e315970…68bb.json` | Unavailable (HTTP 200) |
| Records-009, -014, -038, -040 | Security and not-collected examples |
