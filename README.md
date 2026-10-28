---
okf_version: "0.2"
---
# Cross-government software discovery OKF+

An independent experimental Open Knowledge Format pack for discovering UK
public-sector software repositories. It adds task and domain suggestions,
transparent filters and an evidence-linked Semantic Web to the community's
[public repository feed](https://www.uk-x-gov-software-community.org.uk/xgov-opensource-repo-scraper/repos.json).

**This is an experiment, not an official catalogue or security assessment.**
The first frozen snapshot, retrieved on 28 October 2026, has 24,137 rows,
24,068 distinct repositories and 212 hosting accounts. Identical duplicates
retain their original row numbers. Unknown values and inferred labels remain
explicit; stars and recent activity do not establish quality or support.

[Rich discovery facets](docs/rich-facets.md) · [Change and contributor history](docs/history-and-change.md) ·
[Discovery design](docs/discovery.md) · [Semantic model](docs/semantic-model.md) ·
[SBOMs, security helpers and issues](docs/security-and-sbom-review.md) ·
[Operations](docs/operations.md) · [Scope](REPOSITORY_STATUS.md) ·
[Permission and disclosure](docs/permission-and-disclosure.md) ·
[Private-system beginner guide](docs/private-system-starter.md) · [Credits](CREDITS.md)

## Try it

Python 3.12 or later is required. Build and search have no third-party runtime
dependencies. With uv installed:

```sh
uv run --locked python scripts/catalogue.py build
uv run --locked python scripts/catalogue.py search "accessibility" --archived false
uv run --locked python scripts/catalogue.py search --domain health --language Python
uv run --locked python scripts/catalogue.py search --organisation alphagov --licence MIT
uv run --locked python scripts/catalogue.py search --sbom present --is-fork unknown
uv run --locked python scripts/catalogue.py search "notification" --source-only --json
uv run --locked python scripts/catalogue.py facets --facet content_type
uv run --locked python scripts/catalogue.py search --history-coverage available
uv run --locked python scripts/catalogue.py status
uv run --locked python scripts/catalogue.py check
uv run --locked python -m unittest discover -s tests -v
```

Search explains each result. `--source-only` disables expansion through
inferred concepts. Unknown licences, missing languages and unknown fork status
remain visible. Archived repositories are included unless filtered out.
A licence filter reflects a reported identifier, not permission to reuse code.

Outputs include `generated/okf-explorer.json`, lazy search and record shards,
OKF 0.2 Markdown concept pages, RDF JSON-LD, evidence assertions, quality and
change reports and checksums. Consumer acceptance in OKF Explorer is pending.

## Daily updates

The refresh Action is scheduled at **16:43 UTC daily**, with manual dispatch.
GitHub may delay scheduled runs. It validates and assures a candidate before
publishing a timestamped release. Full generated data lives in releases rather
than daily Git commits. The checked-in frozen source remains reproducible.

[Latest complete pack](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/latest)
includes source, code and generated data. Retain its immutable release tag and
checksums when citing results. Run a local update explicitly with:

```sh
uv run --locked python scripts/catalogue.py refresh
```

The upstream project already collects SBOMs on a scheduled Action. This pack
consumes public metadata; it does not clone or execute catalogued code or
perform estate-wide vulnerability matching.

A separate hourly Action progressively enriches every catalogued repository
with all available GitHub contributor statistics. Collection is bounded and
coverage remains explicit while the full backfill runs. It retains recent and
historical activity, without emails or claims of ownership or quality.

The proposed taxonomy has 20 subject domains, 15 engineering tasks and 12
content types, with
matched-term evidence and explicit unclassified buckets. It is a starting
vocabulary, not exhaustive domain knowledge. The [resources page](https://www.uk-x-gov-software-community.org.uk/resources/)
also links guidance absent from the repository feed; admitting that guidance,
README enrichment and human review are separate next steps.

Code is MIT licensed. See [licence decisions](LICENSE_DECISIONS.md) and
[third-party notices](THIRD_PARTY_NOTICES.md) for source boundaries.
