# Gemini 4 Argon evaluation: public edition

Public edition prepared on 29 October 2026 from the owner-supplied report.
The owner attributed the original output to **Gemini 4 Argon**. No new model
run was performed for this edition.

> **Historical model output with editorial corrections.** Original findings,
> PASS claims and recommendations are retained as model-reported claims.
> Several need qualification or correction; read the [correction ledger](corrections.md#gemini-report)
> alongside this report. This is not acceptance of the current release.

- Evaluated software: **v0.2.1**.
- Complete build identifier: `5415a6dd1a0a24ae6a0bb16539d9d622b63f15aeb1ae347e2e5e81f8e36d3d6a`.
- Frozen input: [snapshot-40758707312-1](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1).
- Archive SHA-256: `6cb6981f1bbbf9b7db49df0e610309e63405fdd132a8aab455888e4857b089c1`.
- Provenance and evidence: [publication manifest](publication-manifest.json) and
  [evidence map](evidence-map.json).

Local filesystem URLs have been replaced by immutable source-file links or
frozen-release references. Original line fragments are not endorsed as exact
citations. Archive paths remain visible because generated files are not all
published as individual web pages. Prose uses British English; exact schema
identifiers and quoted source material retain their original spelling.
The first edition was prepared without original execution logs. A later private
collection retains Gemini session material and a separate report version; this
public edition preserves the owner-supplied download identified in its manifest.
Those session records have not been fully replayed or independently audited for
this edition. Recorded tool statuses are not substituted for test verdicts.

## Original report with annotations

## Evaluation report: experimental OKF+ bundle (`xgov-soft-eng-com` v0.2.1)

**To:** Authors and maintainers of the UK Cross-Government Open-Source Repository Knowledge Catalogue (`xgov-okf`)  
**Subject:** Read-only metadata, discovery, semantic link, and contributor history evaluation of snapshot `5415a6dd1a0a24ae6a0bb16539d9d622b63f15aeb1ae347e2e5e81f8e36d3d6a`  
**Date:** 29 October 2026 (`Europe/London`)  
**Catalogue version:** `0.2.1` (`okf+ 0.2`)  

---

### Executive summary

This report presents the findings of a structured, read-only evaluation of the experimental `xgov-soft-eng-com` OKF+ bundle (`v0.2.1`). All tests were conducted strictly against a single frozen snapshot without relying on external knowledge, executing catalogued repository code, scanning repositories, contacting maintainers, or inferring vulnerabilities from package metadata alone.

Across the seven test areas:
- **6 areas passed (`PASS`):** archive integrity & deterministic lockstep, repository discovery, multi-facet filtering, semantic assertion traversal, inverse navigation analysis, and contributor history handling (both `available` and `not-collected` states).
- **2 sub-checks were `UNTESTED` due to environment constraints:** live HTTP retrieval of the remote GitHub Pages entry point (`https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json`) inside a network-isolated execution environment, and live headless Chromium acceptance testing of the interactive Explorer (`index.html`).

The bundle demonstrates strong deterministic provenance, clear separation between normalised and inferred assertions, explicit epistemic handling of uncollected contributor history (`not-collected` vs `0`), and well-documented guardrails around SBOM resolution and security interpretation. At the same time, our inspection identified concrete opportunities to improve discovery recall (`config/taxonomy.json` substring vs token matching), CLI multi-facet intersection (`scripts/catalogue.py`), and parity between runtime JSON assertions and JSON-LD semantic exports.

---

> **Editorial note G1/G2:** This is the older v0.2.1 archive. Its verified size is 39,007,416 bytes, rather than the size stated below.

### 0. Access, integrity, and snapshot identity

#### 0.1 Entry point and fallback access

1. **Remote entry point attempt (`https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json`):**
   - Tested via `curl -sS -I https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json`.
   - Failed with `curl` exit code `6` (`Could not resolve host: chris-page-gov.github.io`) because the evaluation environment runs inside a network-isolated sandbox.
   - Notably, [okf.publication.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/okf.publication.json) declares `"mode": "github-snapshots"` with release tag prefix `"snapshot-"` rather than a GitHub Pages deployment target, and [README.md](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/README.md) notes that browser acceptance for the Explorer remains pending.
2. **Frozen archive fallback (`xgov-okf.tar.gz`):**
   - Evaluated using the local copy of the frozen release archive [xgov-okf.tar.gz](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`26,238,546` bytes) alongside [SHA256SUMS](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) and [build-manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), extracted to `xgov-okf/`.

#### 0.2 Checksum and lockstep verification

All five SHA-256 digests published in [SHA256SUMS](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) were independently computed and verified:

| Artefact path | Declared & verified SHA-256 digest | Status |
| :--- | :--- | :--- |
| [xgov-okf.tar.gz](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) | `6cb6981f1bbbf9b7db49df0e610309e63405fdd132a8aab455888e4857b089c1` | Verified |
| [xgov-okf/generated/record-hashes.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) | `13b4bfb142dcac5209c2544f2d3efb4ad2fbeb54c6482748ae71ef38eb651d63` | Verified |
| [xgov-okf/generated/record-summary.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) | `77c870465a3c237705f097ac00c11786a9c526e4204b96245fe89f369adcef79` | Verified |
| [xgov-okf/generated/build-manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) | `6f31550f6f15b085b0b0e2ca59ebfa8ddab138a7729389342698ca080d9ef16f` | Verified |
| [xgov-okf/generated/quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) | `e25dbed2287832ed34d3ea0418cc9a01ffbf69e9de66429db6126c10a890633a` | Verified |

Running [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py) (`status` and `check`) confirmed full deterministic lockstep across all **2,804** generated output files (`"status": "ok"`, `"deterministic_lockstep": "passed"`).

#### 0.3 Snapshot identifiers and record counts

A single consistent snapshot was used throughout:

| Property | Value | Source reference |
| :--- | :--- | :--- |
| **Bundle ID & version** | `xgov-soft-eng-com` (`version: "0.2.1"`, `okf_version: "0.2"`) | [okf.manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/okf-explorer.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **Explorer `snapshot_id` / `build_id`** | `5415a6dd1a0a24ae6a0bb16539d9d622b63f15aeb1ae347e2e5e81f8e36d3d6a` | [generated/okf-explorer.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/build-manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **Semantic `snapshot_id` IRI** | `urn:okf:xgov:snapshot:64e70d84e1d4c7a064695c65583000f9bb8a57916ec2b7f636a84b4be98eda9b` | [generated/semantic/manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **Frozen upstream feed** | `https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json` (`14,991,019` bytes, ETag `"6ae208b4-e4beab"`, Last-Modified `Wed, 28 Oct 2026 14:37:40 GMT`) | [source/current.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/current.json) → [source/snapshots/64e70d84...da9b.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/snapshots/64e70d84e1d4c7a064695c65583000f9bb8a57916ec2b7f636a84b4be98eda9b.json) |
| **Snapshot timestamp (`retrieved_at`)** | `2026-10-28T18:25:09.116932+00:00` | [source/current.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/current.json), [generated/okf-explorer.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **SBOM quality supplement** | `https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom-quality.json` (`3,272,094` bytes, SHA-256 `21147fb5d54a15863c739fe3bd4179011e449cefabcf963fc67c72c169868609`, generated `2026-10-28T14:37:00.969Z`) | [source/sbom-review/sbom-quality.json.receipt.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sbom-quality.json.receipt.json) |
| **Raw upstream rows vs distinct records** | `24,137` raw rows → **`24,068` distinct repositories** (`69` identical duplicate rows collapsed across `best-practice-and-impact` and `onsbigdata`) | [generated/quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/record-summary.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **Organisations / hosting accounts** | `212` | [generated/data/facets.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **Semantic assertions** | `113,825` across `228` runtime/JSON-LD shards | [generated/semantic/manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |
| **Repositories with SBOM path** | `14,326` distinct repositories (`14,342` raw rows) | [generated/quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) |

#### 0.4 Resources actually read

During this evaluation, the following files were directly read and inspected:
- **Root descriptors & configuration:** [okf.manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [okf.publication.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/okf.publication.json), [README.md](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/README.md), [AGENTS.md](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/AGENTS.md), [config/taxonomy.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/config/taxonomy.json), [config/history-collection.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [scripts/catalogue.py](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py).
- **Source snapshots, receipts & history:** [source/current.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/current.json), [source/snapshots/64e70d84e1d4c7a064695c65583000f9bb8a57916ec2b7f636a84b4be98eda9b.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/snapshots/64e70d84e1d4c7a064695c65583000f9bb8a57916ec2b7f636a84b4be98eda9b.json), [source/sbom-review/sbom-quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sbom-quality.json), [source/sbom-review/sbom-quality.json.receipt.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sbom-quality.json.receipt.json), [source/sbom-review/sds-addresses.json.gz](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sds-addresses.json.gz) (decompressed via `gzip`), [source/sbom-review/sds-addresses.json.gz.receipt.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sds-addresses.json.gz.receipt.json), [source/history/current.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), and all 25 files in `source/history/observations/*.json` (specifically [2e9c32ed9b98ed517af9f54c84cdbaa2fdb8124ef78d3b3ed337ca998543bdef.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)).
- **Generated manifests, runtime shards & search indexes:** [generated/okf-explorer.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/build-manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/record-summary.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/record-hashes.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/overview.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/facets.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), `generated/data/records-000.json` through `records-048.json`, `generated/data/assertions-000.json` through `assertions-227.json`, `generated/data/history-000.json`, [generated/data/search/manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/search/doc-map.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/search/postings/11.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/search/postings/nh.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/search/postings/re.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1).
- **Generated semantic plane & Markdown routes:** [generated/semantic/manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/context.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/vocabulary.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/organizations.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/concepts.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/contributors.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/repositories-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/semantic/assertions-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/organisations/111online.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/concepts/domains/health.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/concepts/content_types/application-service.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/contributors/andriaturner.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/reports/sbom-review.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/reports/history-coverage.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1).

---

### 1. Discovery evaluation

#### 1.1 Exact repository: `111Online/nhs111-resources`

- **Canonical repository URL:** `https://github.com/111Online/nhs111-resources`
- **Dataset IRI:** `urn:okf:xgov:repository:111online%2Fnhs111-resources`
- **Logical route:** `repositories/111online%2Fnhs111-resources.md`
- **Supporting bundle references:**
  - Runtime record shard: [generated/data/records-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (index `0`)
  - Semantic JSON-LD shard: [generated/semantic/repositories-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`@graph[0]`)
  - Upstream snapshot row: `source/snapshots/64e70d84e1d4c7a064695c65583000f9bb8a57916ec2b7f636a84b4be98eda9b.json` (array index `14456`, SHA-256 `cee0df33ec5dd6cabb6c9c89572ad9b1eff35916a458973926d37b5a89327d9d`)
  - Static search index: ordinal `0` in [generated/data/search/doc-map.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), indexed under `"111online"` (`[0, 24, 3]` in [postings/11.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)), `"nhs111"` (`[0, 16, 1]` in [postings/nh.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)), and `"resources"` (`[0, 21, 9]` in [postings/re.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)). CLI `catalogue.py search "111Online/nhs111-resources"` returns it at rank 1 with `score: 15` (`"all query tokens in source name/description"`).
- **Matching fields:**
  - `id` / `title`: `"111Online/nhs111-resources"`
  - `organisation_id`: `"111Online"` ([generated/organisations/111online.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1))
  - `description`: `"Publicly available information and resources about the NHS 111 online service"` (`description_status: "present"`)
  - `language`: `"Nunjucks"` | `license_id`: `"unknown"` | `archived`: `false` (`status: "active"`) | `is_fork`: `false` (`fork_status: "source"`)
  - `created_at`: `"2022-07-04T09:57:41Z"` | `pushed_at`: `"2026-10-08T08:52:47Z"`
  - `domains`: `["health"]` (inferred from `"nhs"`) | `content_types`: `["application-service"]` (inferred from `"service"`) | `capabilities`: `["unclassified"]`
  - `sbom`: `"present"` | `sbom_url`: `"https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom/111Online/nhs111-resources.json.gz"`
  - `sbom_resolution`: `"some-unresolved"` | `package_volume`: `"501-2000"` | `sbom_quality.counts`: `{packages: 891, resolved: 888, unresolved: 3, runtime: 769, excludedDev: 118, excludedCi: 3, excludedUnresolved: 1}` (`unresolved_Sample`: `["express-es6-template-engine@github:dnbard/express-es6-template-engine", "github-pages@>= 0"]`).

#### 1.2 Three Python repositories with recorded SBOM information

| # | Repository ID & canonical URL | Matching fields | Supporting bundle references |
| :--- | :--- | :--- | :--- |
| **1** | **`acteng/ate-api`**<br>`https://github.com/acteng/ate-api` | `language`: `"Python"`, `license_id`: `"MIT"`, `archived`: `false`, `description`: `"Active Travel England API."`, `capabilities`: `["apis-integration"]`, `content_types`: `["api-client"]`, `sbom`: `"present"`, `sbom_url`: `"https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom/acteng/ate-api.json.gz"`, `sbom_resolution`: `"none-resolved"`, `package_volume`: `"21-100"`, `sbom_quality.counts`: `{packages: 24, resolved: 0, unresolved: 24, runtime: 0, excludedDev: 5, excludedCi: 8, excludedUnresolved: 11}` | [generated/data/records-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[1]`); [generated/semantic/repositories-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`@graph[1]`); source snapshot row `[19481]`; `sbom-quality.json` key `"acteng/ate-api"` |
| **2** | **`acteng/atip-data-prep`**<br>`https://github.com/acteng/atip-data-prep` | `language`: `"Python"`, `license_id`: `"Apache-2.0"`, `archived`: `false`, `description`: `"Prepare data for use in ATIP"`, `sbom`: `"present"`, `sbom_url`: `"https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom/acteng/atip-data-prep.json.gz"`, `sbom_resolution`: `"some-unresolved"`, `package_volume`: `"501-2000"`, `sbom_quality.counts`: `{packages: 881, resolved: 880, unresolved: 1, runtime: 867, excludedDev: 13, excludedCi: 0, excludedUnresolved: 1}` | [generated/data/records-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[4]`); [generated/semantic/repositories-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`@graph[4]`); source snapshot row `[19487]`; `sbom-quality.json` key `"acteng/atip-data-prep"` |
| **3** | **`acteng/update-your-capital-schemes`**<br>`https://github.com/acteng/update-your-capital-schemes` | `language`: `"Python"`, `license_id`: `"MIT"`, `archived`: `false`, `description`: `"Update your capital schemes service."`, `content_types`: `["application-service"]`, `sbom`: `"present"`, `sbom_url`: `"https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom/acteng/update-your-capital-schemes.json.gz"`, `sbom_resolution`: `"some-unresolved"`, `package_volume`: `"21-100"`, `sbom_quality.counts`: `{packages: 81, resolved: 42, unresolved: 39, runtime: 41, excludedDev: 8, excludedCi: 10, excludedUnresolved: 22}` | [generated/data/records-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[7]`); [generated/semantic/repositories-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`@graph[7]`); source snapshot row `[19482]`; `sbom-quality.json` key `"acteng/update-your-capital-schemes"` |

*(Note: If filtering specifically for `language=Python` AND `sbom_resolution=all-reported-versions-resolved`, the exact 3 repositories in the snapshot are `alphagov/matomo-log-analytics` in `records-001.json[459]`, `companieshouse/ci-packer-container` in `records-005.json[489]`, and `nhsengland/NCDR-reference-library` in `records-033.json[337]`.)*

#### 1.3 Three repositories relevant to security or vulnerability management

| # | Repository ID & canonical URL | Matching fields & taxonomy terms | Supporting bundle references |
| :--- | :--- | :--- | :--- |
| **1** | **`Crown-Commercial-Service/ccs-vulnerability-disclosure-policy`**<br>`https://github.com/Crown-Commercial-Service/ccs-vulnerability-disclosure-policy` | `language`: `"unknown"`, `license_id`: `"unknown"`, `description_status`: `"missing"`, `domains`: `["democracy-policy"]` (`"policy"`), `capabilities`: `["identity-security"]` (`"vulnerability"`), `content_types`: `["security-tool"]` (`"vulnerability"`), `sbom`: `"not-reported"`, `sbom_resolution`: `"no-sbom"` | [generated/data/records-007.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[480]`); `generated/semantic/repositories-007.jsonld` (`@graph[480]`); `generated/data/assertions-036.json` (`[203..207]`); source snapshot row `[14793]` |
| **2** | **`DEFRA/ci-vulnerability-scanner`**<br>`https://github.com/DEFRA/ci-vulnerability-scanner` | `language`: `"JavaScript"`, `license_id`: `"unknown"`, `description_status`: `"missing"`, `capabilities`: `["identity-security"]` (`"vulnerability"`), `content_types`: `["security-tool"]` (`"vulnerability"`, `"scanner"`), `sbom`: `"present"`, `sbom_url`: `"https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom/DEFRA/ci-vulnerability-scanner.json.gz"`, `sbom_resolution`: `"none-resolved"`, `package_volume`: `"1-5"`, `sbom_quality.counts`: `{packages: 1, resolved: 0, unresolved: 1, runtime: 0, excludedDev: 0, excludedCi: 0, excludedUnresolved: 1}` | [generated/data/records-009.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[473]`); `generated/semantic/repositories-009.jsonld` (`@graph[473]`); `generated/data/assertions-045.json` (`[465..470]`); source snapshot row `[20638]` |
| **3** | **`DFE-Digital/vulnerability-disclosure-program`**<br>`https://github.com/DFE-Digital/vulnerability-disclosure-program` | `language`: `"HCL"`, `license_id`: `"MIT"`, `description`: `"This project aims to deploy a security.txt and thanks.txt file under the vulnerability disclosure program started by DfE with NCSC."`, `capabilities`: `["identity-security", "delivery-operations"]` (`"security"`, `"vulnerability"`, `"deploy"`), `content_types`: `["security-tool"]` (`"security"`, `"vulnerability"`), `sbom`: `"present"`, `sbom_url`: `"https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/sbom/DFE-Digital/vulnerability-disclosure-program.json.gz"`, `sbom_resolution`: `"none-resolved"`, `package_volume`: `"1-5"`, `sbom_quality.counts`: `{packages: 5, resolved: 0, unresolved: 5, runtime: 0, excludedDev: 0, excludedCi: 4, excludedUnresolved: 1}` | [generated/data/records-014.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[338]`); `generated/semantic/repositories-014.jsonld` (`@graph[338]`); `generated/data/assertions-069.json` (`[79..85]`); source snapshot row `[2684]` |

#### 1.4 Critical epistemic distinction: SBOM metadata vs inspected SBOM vs vulnerability evidence

1. **SBOM path / metadata flag (`14,326` repositories):**
   - For `111Online/nhs111-resources`, the 3 Python repositories, and the 2 security repositories with `sbom: "present"`, the bundle records **only** a relative upstream path (`sbom/<org>/<repo>.json.gz`), a resolved external URL (`sbom_url`), and summary package counters from `source/sbom-review/sbom-quality.json`.
   - In the semantic plane (`generated/semantic/repositories-*.jsonld`), each of these carries `"okf:verificationStatus": "source-reported-reference-not-fetched-by-build"`. None of those 14,325 individual `.json.gz` SBOM payloads are stored in the archive.
2. **Actually inspected SBOM (`1` repository in the entire bundle):**
   - Exactly **one** raw SPDX SBOM payload is frozen in the archive for methodology review: [source/sbom-review/sds-addresses.json.gz](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sds-addresses.json.gz) (`1,009` bytes compressed, SHA-256 `1d50b48d754d42f67aa60baf37770cbcd0753c783a06d645f90163b86c17026b`, receipt at [sds-addresses.json.gz.receipt.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sds-addresses.json.gz.receipt.json)), corresponding to `surreydigitalservices/sds-addresses` (`generated/data/records-042.json[396]`, source row `[56]`).
   - Decompressing and inspecting `sds-addresses.json.gz` reveals an `SPDX-2.3` document (`created: "2026-04-19T17:29:07Z"`, creator `"Tool: GitHub.com-Dependency-Graph"`) containing **7 packages**: only **1** concrete pinned version (`grunt-legacy-log-utils` at `0.1.1`, `pkg:npm/grunt-legacy-log-utils@0.1.1`) and **6** unresolved version ranges or branch references (`grunt-sass` `^1.0.0`, `node-sass` `^3.2.0`, `grunt` `~0.4.5`, `grunt-contrib-watch` `~0.6.1`, `github-pages` `>= 0`, and root package `gh-pages`).
3. **Evidence of a vulnerability (`0` repositories):**
   - **Zero** repositories in this bundle contain vulnerability advisories, CVE identifiers, exploitability assessments, or runtime deployment statuses. As documented in [generated/reports/sbom-review.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), version ranges (`^`, `~`, `>=`), missing lockfiles (`none-resolved` across 3,504 repos; `some-unresolved` across 9,336 repos), and lack of deployment context mean neither an SBOM flag nor an inspected SPDX file constitutes evidence of a vulnerability.

#### 1.5 Two-facet filtering logic, complete counts, and result limits

##### Filtering logic
Both the Explorer ([generated/index.html](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)) and the static search contract ([generated/data/search/manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)) implement:
- **Within a single facet:** logical **`OR`** across selected values (`recordValues.some(...)`).
- **Across different facets:** logical **`AND`** across every active facet (`Object.entries(state.facets).every(...)`).

##### Complete counts across all 24,068 records (`records-000.json` .. `records-048.json`)

**Combination A: `language = Python` AND `sbom = present`**

| `language` \ `sbom` | `present` | `not-reported` | Total |
| :--- | ---: | ---: | ---: |
| **`Python`** | **1,607** | 1,037 | **2,644** |
| All other languages (68 values incl. `unknown`) | 12,719 | 8,705 | 21,424 |
| **Total** | **14,326** | **9,742** | **24,068** |

Within the **1,607** repositories matching `language = Python` AND `sbom = present`, adding `sbom_resolution` yields:
- `some-unresolved`: **954**
- `none-resolved`: **650**
- `all-reported-versions-resolved`: **3** (`alphagov/matomo-log-analytics`, `companieshouse/ci-packer-container`, `nhsengland/NCDR-reference-library`)

**Combination B: `capability = identity-security` AND `content_type = security-tool`**
- `capability = identity-security`: **400** repositories
- `content_type = security-tool`: **291** repositories
- Intersection (`identity-security` **AND** `security-tool`): **262** repositories (`429` match either).

##### Configured result and truncation limits
1. **Static search index (`generated/data/search/manifest.json`):** `result_limit: 200` (hard cap on returned search matches), `result_doc_chunk_size: 500`, prefix autocomplete suggestions capped at `16` (`scripts/catalogue.py` line 269).
2. **CLI (`scripts/catalogue.py`):** `search` defaults to `--limit 10` and clamps `--limit` to `[1, 200]` (line 699); `facets` defaults to `--limit 20` (line 750); `search` only accepts a single `--facet field=value` argument per invocation rather than multi-facet intersections.
3. **Overview (`generated/data/overview.json`):** `facet_previews` truncated to top **15** values per facet (`organisation` omits 197 of 212 orgs; `language` omits 54 of 69 languages); `recent_datasets` truncated to **10** records.

---

### 2. Semantic links and inverse navigation evaluation

Starting from **`111Online/nhs111-resources`** (`urn:okf:xgov:repository:111online%2Fnhs111-resources`), we inspected all **11** outbound assertions in [generated/data/assertions-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[0..10]`) and [generated/semantic/assertions-000.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`@graph[0..10]`).

#### 2.1 Detailed assertion inspection

| Field | 2a(i). Recent contributor relationship | 2a(ii). Historical contributor relationship | 2b(i). Domain relationship | 2b(ii). Content-type relationship |
| :--- | :--- | :--- | :--- | :--- |
| **Assertion ID** | `urn:okf:xgov:assertion:0d7028a9d7391ab2f719986d03ff22f9d315ef423421569cc662ba80986c463a` | `urn:okf:xgov:assertion:1aa737119311251424a78818b99e641b19f0923c23be880ad551aeebf8defc3f` | `urn:okf:xgov:assertion:b4455286cb0ad1a44689ebb69126db4381914173046ee128fd3449b7d13dfa30` | `urn:okf:xgov:assertion:8f4a37db2fc0d8052f43c74a9fd28d8149fdcbd3073b5c947d53023238d95a8d` |
| **Shard index** | `assertions-000.json[7]` | `assertions-000.json[6]` | `assertions-000.json[3]` | `assertions-000.json[4]` |
| **Source route & IRI** | `repositories/111online%2Fnhs111-resources.md`<br>`urn:okf:xgov:repository:111online%2Fnhs111-resources` | `repositories/111online%2Fnhs111-resources.md`<br>`urn:okf:xgov:repository:111online%2Fnhs111-resources` | `repositories/111online%2Fnhs111-resources.md`<br>`urn:okf:xgov:repository:111online%2Fnhs111-resources` | `repositories/111online%2Fnhs111-resources.md`<br>`urn:okf:xgov:repository:111online%2Fnhs111-resources` |
| **Target route & IRI** | `contributors/andriaturner.md`<br>`urn:okf:xgov:contributor:andriaturner` | `contributors/andriaturner.md`<br>`urn:okf:xgov:contributor:andriaturner` | `domains/health.md`<br>`urn:okf:xgov:domains:health` | `content_types/application-service.md`<br>`urn:okf:xgov:content_types:application-service` |
| **Predicate** | `urn:okf:xgov:reportedRecentContributor` | `urn:okf:xgov:reportedHistoricalContributor` | `https://schema.org/about` | `urn:okf:xgov:suggestedContentType` |
| **Preferred `label`** | `"recent contributor reported by GitHub"` | `"historical contributor reported by GitHub"` | `"suggested domain"` | `"suggested content type"` |
| **`inverse_label`** | `"reported recent contributor to"` | `"reported historical contributor to"` | `"suggested domain of"` | `"suggested content type of"` |
| **`assertion_status`** | `"normalized"` | `"normalized"` | `"inferred"` | `"inferred"` |
| **`review_status`** | *(absent / `null`)* | *(absent / `null`)* | `"unreviewed"` | `"unreviewed"` |
| **`authority`** | `"urn:okf:xgov:authority:source-feed"` | `"urn:okf:xgov:authority:source-feed"` | `"urn:okf:xgov:authority:catalogue-build"` | `"urn:okf:xgov:authority:catalogue-build"` |
| **`derivation`** | `"urn:okf:xgov:rule:source-field-v1"` | `"urn:okf:xgov:rule:source-field-v1"` | `"urn:okf:xgov:rule:term-match-v1"` | `"urn:okf:xgov:rule:term-match-v1"` |
| **`observed_at`** | `"2026-10-28T19:43:34Z"` | `"2026-10-28T19:43:34Z"` | `"2026-10-28T18:25:09.116932+00:00"` | `"2026-10-28T18:25:09.116932+00:00"` |
| **`measurement`** | `{period: "recent-complete-weeks", reported_commits: 8, window_start: "2026-07-26T00:00:00+00:00", window_end_exclusive: "2026-10-25T00:00:00+00:00"}` | `{period: "available-provider-history", reported_commits: 124}` | *(absent / `null`)* | *(absent / `null`)* |
| **`evidence`** | `snapshot_id`: `urn:okf:xgov:snapshot:64e70d84...da9b`; `source_field`: `"contributors_stats[1].weeks"`; `source_record_pointer`: `"/contributors_stats/1"`; `source_url`: `https://api.github.com/repos/111Online/nhs111-resources/stats/contributors`; `source_value_sha256`: `5f34bce2abd57b70a249e158e81fe90893227d560b0fad701ed688cca24ec934` | Same `snapshot_id`, `source_record_pointer`, `source_url`, `source_value_sha256`; `source_field`: `"contributors_stats[1].total"` | `matched_terms`: `["nhs"]`; `source_field`: `"name,description"`; `source_record_pointer`: `"/14456"`; `source_url`: `https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json`; `source_value_sha256`: `cee0df33ec5dd6cabb6c9c89572ad9b1eff35916a458973926d37b5a89327d9d` | Same `snapshot_id`, `source_field`, `source_record_pointer`, `source_url`, `source_value_sha256`; `matched_terms`: `["service"]` |

#### 2.2 What these relationships establish vs what they do not establish

- **Contributor assertions (`2a`):**
  - *Establishes:* GitHub's `/stats/contributors` endpoint reported on `2026-10-28T19:43:34Z` (at `main` branch SHA `1f18b4c9836da93ec4305c9811affc4d8e71a063`) that GitHub account `AndriaTurner` (`id: 42874936`) had `124` commits in available provider history and `8` commits during the 13 complete UTC weeks `2026-07-26` to `2026-10-25`.
  - *Does not establish:* Real-world civil service employment, departmental affiliation, code ownership, current maintainer authority, non-commit contributions (reviews, issues, design), commits on non-default branches, or commits authored with unlinked Git email addresses.
- **Inferred concept assertions (`2b`):**
  - *Establishes:* Deterministic substring rule `urn:okf:xgov:rule:term-match-v1` found `"nhs"` and `"service"` inside the lowercased concatenation of the repository's `name` and `description`, producing unreviewed candidate suggestions (`assertion_status: "inferred"`, `review_status: "unreviewed"`).
  - *Does not establish:* Verified clinical governance or service classification. These are **heuristic lexical inferences**, not human-curated facts (`"Capabilities, domains and content types are inferred with simple transparent term rules unless the upstream source supplies them directly"`).

> **Editorial note G6/G7:** Runtime/RDF parity gaps exist, but scope, rights and measurements are already exported. A logical/storage path difference alone does not establish broken navigation.

#### 2.3 Following a relationship back towards its source (inverse navigation)

We followed both `urn:okf:xgov:domains:health` ([generated/concepts/domains/health.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)) and `urn:okf:xgov:contributor:andriaturner` ([generated/contributors/andriaturner.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)) back to `111Online/nhs111-resources`:

1. **Inverse navigation label vs separately asserted inverse triple:**
   - Across all **113,825** assertions in `generated/data/assertions-000.json` .. `assertions-227.json`, **every single assertion** has a `repository` (`urn:okf:xgov:repository:*`) as `source_iri` (`113,825`) and **zero** assertions have a repository as `target_iri` (`0`). Conversely, concepts (`urn:okf:xgov:domains:health` has `642` inbound assertions), organisations, and contributors (`urn:okf:xgov:contributor:andriaturner` has `2` inbound assertions) appear exclusively as `target_iri`.
   - **There are no separately asserted inverse triples anywhere in the bundle.** Instead, inverse navigation is implemented by scanning forward assertions where `target == current_entity_route` and rendering the forward assertion's `inverse_label` (`"suggested domain of"`, `"reported recent contributor to"`).
2. **Missing fields and discrepancies identified across planes:**
   - **Runtime JSON vs Semantic JSON-LD assertion gap:** In [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py), `generated/semantic/assertions-*.jsonld` retains only 6 fields (`@id`, `@type`, `subject`, `predicate`, `object`, `assertionStatus`, `evidence`) and **drops 9 fields** present in `generated/data/assertions-*.json`: `label`, `inverse_label`, `kind`, `source` (route), `target` (route), `authority`, `derivation`, `observed_at`, and `review_status` (plus `measurement` is only nested inside `evidence`).
   - **External predicates omitted from `vocabulary.jsonld`:** [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py) filters predicates with `if p.startswith(NS)`. Consequently, external predicates used in assertions (`https://schema.org/about` for domains and `https://schema.org/programmingLanguage` for languages) are omitted from [generated/semantic/vocabulary.jsonld](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), which therefore defines no `rdfs:label` or `okf:inverseLabel` for domain or language assertions in the semantic plane.
   - **Concept route vs physical path mismatch:** Concept assertions use logical routes `domains/health.md` and `content_types/application-service.md`, whereas the physical files in the bundle reside under `generated/concepts/domains/health.md` and `generated/concepts/content_types/application-service.md` (with `concepts/` prepended).

---

> **Editorial note G5:** The cited observation has 8 recent commits across 7 active weeks, with 38 additions and 5 deletions. Several values in the following original account are incorrect.

### 3. Contributor history evaluation

#### 3.1 Repository with `available` history: `111Online/nhs111-resources`

Inspected across [source/history/observations/2e9c32ed9b98ed517af9f54c84cdbaa2fdb8124ef78d3b3ed337ca998543bdef.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/data/history-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[0]`), and [generated/data/records-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`[0]`):

- **Exact measure definitions ([config/history-collection.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [scripts/catalogue.py](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py)):**
  - `historical_reported_commits` (**`299`**): Sum of `entry["total"]` across all contributor entries returned by GitHub (`"Total commits across contributors returned by GitHub's contributor statistics endpoint for the repository default branch"`).
  - `historical_reported_contributors` (**`5`**): Count of distinct contributor entries in `contributors_stats` with `total > 0`.
  - `recent_reported_commits` (**`8`**, `recent_commit_band: "1-10"`): Sum of weekly commits (`w["c"]`) across all returned contributors for UTC weeks falling inside the 13 complete UTC weeks preceding the observation week (`window_start <= w["w"] < window_end_exclusive`).
  - `recent_reported_contributors` (**`1`**): Count of contributors with `recent_commits > 0` inside that 13-week window.
  - `recent_reported_additions` (**`23`**), `recent_reported_deletions` (**`20`**), `recent_reported_line_changes` (**`43`**): Sum of `w["a"]`, `w["d"]`, and `a + d` across the 13 complete UTC weeks.
- **Observation date, reporting periods, and provenance:**
  - `observed_at`: `"2026-10-28T19:43:34Z"`
  - `recent_window`: `13` complete UTC weeks (`"2026-07-26T00:00:00+00:00"` to `"2026-10-25T00:00:00+00:00"` exclusive)
  - `default_branch`: `"main"` | `head_sha_observed`: `"1f18b4c9836da93ec4305c9811affc4d8e71a063"`
  - Endpoints: `https://api.github.com/repos/111Online/nhs111-resources`, `/commits/main`, `/stats/contributors` (`http_status: 200`, `response_sha256`: `c0bd5f2a4ceab2aeca094b4d98affec1216af59a067f8ef2c85a081fedadfcc4`).
- **Contributor breakdown & change over time:**
  - 5 historical contributors: `andymantell` (`149` historical / `0` recent), `AndriaTurner` (`124` historical / `8` recent, `+23`/`-20` lines), `jamesbeeson2` (`23` / `0`), `peteneville` (`2` / `0`), `diananita2` (`1` / `0`).
  - **Change over time:** Most of the repository's 299 default-branch commits occurred prior to 26 July 2026 across 5 contributors, led by `andymantell` (49.8%) and `AndriaTurner` (41.5%). Over the recent 13-week window (`26 Jul – 25 Oct 2026`), the repository transitioned to low-volume maintenance carried out solely by `AndriaTurner` (8 commits across 4 active weeks: weeks of `2026-08-02` [3 commits], `2026-08-23` [1 commit], `2026-09-20` [1 commit], and `2026-10-04` [3 commits], totalling 43 line changes).

#### 3.2 Repository with `not-collected` history and overall snapshot coverage

- **Examples inspected:** `DEFRA/ci-vulnerability-scanner` ([generated/data/records-009.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) `[473]`) and `surreydigitalservices/sds-addresses` ([generated/data/records-042.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) `[396]`). Both record `history_status: "not-collected"`, `recent_commit_band: "not-collected"`, `recent_commits: null`, `historical_commits: null`, `recent_contributors: null`, `historical_contributors: null`.
- **Why `not-collected` / `pending` / `unavailable` does not mean zero activity:**
  - The history collector ([scripts/catalogue.py](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py)) is an **opt-in, bounded sampler** (`--max-repos`, default `25`). For repositories not yet queried (`not-collected`), where GitHub returned HTTP `202 Accepted` while computing background statistics (`pending`), or where an API error/404 occurred (`unavailable`), the bundle deliberately sets all commit and contributor counts to `null` rather than `0`. For example, `DEFRA/ci-vulnerability-scanner` has `pushed_at: "2025-11-28T13:34:47Z"`, proving real repository activity despite `history_status: "not-collected"`.
- **Overall history coverage in this snapshot ([generated/quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1), [generated/reports/history-coverage.md](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1)):**

| `history_status` | Repository count | Share of catalogue (`24,068`) |
| :--- | ---: | ---: |
| **`available`** | **25** | **0.104%** |
| **`not-collected`** | **24,043** | **99.896%** |
| `pending` / `unavailable` / `empty-or-no-stats` | 0 | 0.000% |

All 25 `available` observations belong to the first three alphabetically sorted organisations (`111Online`: 1, `acteng`: 7, `adastragrp`: 17), reflecting a single default 25-repository collection run (`261` contributor assertions across `227` distinct contributor accounts).

---

### 4. Assessment summary (`PASS` / `FAIL` / `UNTESTED`)

| Test area | Result | Summary & evidence paths |
| :--- | :---: | :--- |
| **0a. Remote HTTP entry point access** | **UNTESTED** | Sandbox blocks external DNS/HTTPS (`curl` exit code `6` on `chris-page-gov.github.io`); [okf.publication.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/okf.publication.json) targets GitHub Releases (`github-snapshots`). |
| **0b. Frozen archive access, checksums & lockstep** | **PASS** | All 5 SHA-256 checksums in [SHA256SUMS](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) matched; `catalogue.py check` verified all 2,804 files against [generated/build-manifest.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1). |
| **0c. Live browser UI acceptance** | **UNTESTED** | No headless Chromium exercised; [README.md](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/README.md) notes Explorer browser acceptance is pending. |
| **1. Discovery (exact repo, Python+SBOM, security repos, SBOM distinctions)** | **PASS** | Verified across `generated/data/records-*.json`, `generated/data/search/*`, [source/sbom-review/sbom-quality.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sbom-quality.json), and decompressed [source/sbom-review/sds-addresses.json.gz](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/source/sbom-review/sds-addresses.json.gz). |
| **1d. Multi-facet filtering & result limits** | **PASS** | Verified `OR`-within / `AND`-across logic (`Python` AND `sbom=present` = `1,607`; `identity-security` AND `security-tool` = `262`) and documented limits (`200` search cap, `15` overview preview cap). |
| **2a–b. Semantic links (contributor & concept assertions)** | **PASS** | Verified assertion IDs, predicates, labels, authorities, derivations, measurements, and SHA-256 evidence pointers in [generated/data/assertions-000.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1). |
| **2c. Inverse navigation & cross-plane completeness** | **PASS** | Confirmed `0` inverse triples across 113,825 assertions (`inverse_label` used on forward triples) and identified 9 runtime fields omitted from `generated/semantic/assertions-*.jsonld`. |
| **3a. Available contributor history** | **PASS** | Verified `111Online/nhs111-resources` in [2e9c32ed...bdef.json](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40758707312-1) (`299` historical commits across `5` contributors; `8` recent commits by `AndriaTurner`). |
| **3b. Missing/uncollected history & coverage** | **PASS** | Verified `not-collected` uses `null` (not `0`) across `24,043` repos (`99.896%`), with `25` repos (`0.104%`) `available`. |

---

### 5. Concrete recommendations for the authors

> **Editorial note G3/G4:** The cited classifier already uses whole terms and phrases, and the CLI already combines repeated named filters. These two recommendations rest on incorrect descriptions of the inspected code.

#### Recommendation 1: Replace raw substring matching (`t in hay`) with token-aware and curated phrase matching in `classify_terms()`
- **Observation:** In [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py), `classify_terms()` evaluates `[t for t in terms if t in hay]` against the raw lowercased string `f"{name} {desc}"`. Short taxonomy terms in [config/taxonomy.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/config/taxonomy.json) cause systematic false positives across the 24,068 repositories:
  - `"ui"` (`capabilities: user-interface`) matches inside `"b**ui**ld"`, `"g**ui**de"`, `"s**ui**te"`, `"req**ui**rements"`, and `"c**ui**sine"` (**2,053** repositories classified as `user-interface`, including `111Online/nhs111-resources` if `"building"` appeared in its description).
  - `"map"` (`capabilities: geospatial`, `content_types: geospatial-tool`) matches inside `"road**map**"` and `"sitemap"`.
  - `"bus"` (`domains: transport`) matches inside `"**bus**iness"` and `"syl**bus**"`.
  - `"uk"` (`domains: local-public-services`) matches every repository containing `"gov.uk"` or `"uk"` (`1,981` repos).
  - Conversely, `capabilities` is `"unclassified"` for **15,792 of 24,068 repositories (65.6%)** (`domains` is `"unclassified"` for **18,175 (75.5%)**, `content_types` for **14,515 (60.3%)**), and `111Online/nhs111-resources` ("Publicly available information and resources about the NHS 111 online service") receives `capabilities: ["unclassified"]`.
- **Actionable fix:** Match single-word terms against token boundaries (`re.findall(r"[a-z0-9]+", hay)` or `\b` regex boundaries) while keeping phrase matching for multi-word terms (`"design system"`, `"local authority"`, `"machine learning"`), and ingest GitHub repository `topics` into the upstream snapshot to reduce the 60%–75% `unclassified` rate.

#### Recommendation 2: Support multi-facet `AND`/`OR` filtering and un-truncated counts in `scripts/catalogue.py search` and `generated/data/search/`
- **Observation:** While the browser UI supports multi-facet filtering (`AND` across facets, `OR` within a facet), [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py) `cmd_search` accepts only a single `--facet field=value` string and clamps `--limit` to `200` without reporting the total un-truncated match count before slicing (`matches[:limit]`). Furthermore, agent and CLI consumers must scan all 49 `records-*.json` shards to compute a two-facet intersection count (such as `language=Python` AND `sbom=present` = `1,607`).
- **Actionable fix:** Change `--facet` in `scripts/catalogue.py` to `action="append"` (supporting multiple `--facet language=Python --facet sbom=present` arguments with `OR` within repeated keys and `AND` across distinct keys), include `"total_matches": len(matches)` in the JSON output before applying `matches[:limit]`, and emit compact per-facet ordinal bitsets or doc-ID lists under `generated/data/search/facets/` so static clients can intersect facets without downloading all 49 record shards.

#### Recommendation 3: Align semantic JSON-LD assertions (`generated/semantic/assertions-*.jsonld`) and `vocabulary.jsonld` with runtime assertions (`generated/data/assertions-*.json`)
- **Observation:** Three gaps currently affect semantic-plane consumers:
  1. [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py) omits `label`, `inverse_label`, `authority`, `derivation`, `observed_at`, and `review_status` when serialising `generated/semantic/assertions-*.jsonld`.
  2. [`scripts/catalogue.py`](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/scripts/catalogue.py) filters `vocabulary.jsonld` with `if p.startswith(NS)`, omitting `https://schema.org/about` and `https://schema.org/programmingLanguage` so their human-readable labels and inverse labels (`"suggested domain of"`, `" primary language of"`) are absent from the semantic plane.
  3. Concept assertion routes (`domains/health.md`, `content_types/application-service.md`) omit the `concepts/` directory prefix used by physical files (`generated/concepts/domains/health.md`).
- **Actionable fix:** Include `rdfs:label`, `okf:inverseLabel`, `okf:authority`, `okf:derivation`, `okf:observedAt`, and `okf:reviewStatus` in `generated/semantic/assertions-*.jsonld` (and `generated/semantic/context.jsonld`), include external predicate descriptors in `vocabulary.jsonld`, and normalise concept route strings to `concepts/<scheme>/<slug>.md` across both Markdown files and assertion targets.

---

### 6. Tool limitations, truncated results, and unresolved questions

1. **Tool & environment limitations:**
   - Outbound network access is disabled in the evaluation sandbox (`BypassSandbox: false`), preventing live HTTP inspection of `https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json` or fetching the 14,325 external `.json.gz` SBOM files referenced by `sbom_url`.
   - No headless Chromium instance was exercised against `generated/index.html`; accordingly, browser UI acceptance is explicitly marked **`UNTESTED`**.
2. **Truncated results encountered and mitigated:**
   - Static search (`result_limit: 200`), CLI search (`--limit 10`, max `200`), CLI facets (`--limit 20`), and `overview.json` (`facet_previews` capped at `15`) all truncate results by design. To avoid substituting examples for complete counts, all statistical and facet-intersection counts in this report were computed across the complete set of **49 record shards (`24,068` records)** and **228 assertion shards (`113,825` assertions)**.
3. **Unresolved questions for the authors:**
   - **GitHub Pages vs GitHub Releases publication:** Is `https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json` intended to be deployed alongside the `github-snapshots` release artefacts configured in [okf.publication.json](https://github.com/chris-page-gov/xgov-soft-eng-com/blob/6f059605922043a28984ba8b443820588a2665e7/okf.publication.json)?
   - **Duplicate upstream records (`69` rows):** Should `generated/quality.json` explicitly list the repository IDs of the 69 collapsed duplicate rows (currently occurring in `best-practice-and-impact` and `onsbigdata`) so upstream scraper maintainers can deduplicate them at source?
   - **Contributor identity disambiguation across providers:** Contributor IRIs currently key solely on lowercased GitHub login (`urn:okf:xgov:contributor:<login>`). Since the catalogue includes GitLab (`gov.uk` / `nhs`) and Bitbucket repositories alongside GitHub, how should contributor IRIs be namespaced by hosting provider in future versions?
