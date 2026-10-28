# Change and contributor history across the full catalogue

The collection target is every distinct repository in the public feed, not
only the community organisation’s own projects. The nine community projects
are outside that feed and have a separate, dated credits inventory.

Three measures remain separate:

- Catalogue metadata changes: which source fields changed since the preceding
  admitted snapshot. The first comparable observation has no baseline.
- Code activity and volume: GitHub’s reported commit and line-change statistics.
- Contribution: historical and recent activity attributed to public GitHub
  accounts, including automated accounts where the provider identifies them.

## What is collected

The collector reads public repository metadata, the default branch head and
GitHub’s contributor statistics. It retains the full available weekly history,
using sparse rows for non-zero weeks. It stores account handles, account types,
counts, source URLs, retrieval time, response hashes and an observed head SHA.
Email addresses and unrelated profile details are not retained.

Recent activity means 13 complete Sunday-to-Sunday weeks. The current partial
week is excluded. Historical totals are the provider’s reported contributor
totals; they are not a claim to have cloned every branch or reconstructed all
Git history. Forks can contain inherited upstream work. Contribution does not
establish ownership, maintainership, approval authority or endorsement.

[GitHub documents](https://docs.github.com/en/rest/metrics/statistics) that
statistics exclude merge commits, and contributor statistics also exclude
empty commits. The API may return 202 while it computes a result. For
repositories with at least 10,000 commits, additions/deletions may be zeroed;
all-zero line histories are therefore shown as unknown or omitted, not as zero
change. Line counts can include generated or data files and do not measure
engineering value, risk or quality. The head and statistics requests are not
an atomic observation; that limitation is recorded.

## Full-catalogue collection and refresh

The hourly history Action targets the complete current feed. Each run handles
up to 500 repositories, 1,800 API requests and 25 minutes of collection, with
one serial worker and a 10% API-rate reserve. These are request/time limits,
not model-credit limits. No language model or scanner is invoked.

New targets are prioritised. Pending provider results are deferred for at least
six hours; unavailable results are retried later. Available results are normally
rechecked after seven days, or earlier when the source push date changes.
There is no claim that the initial backfill is instant or complete: it requires
multiple runs and its exact completion time depends on GitHub’s responses.

Validated checkpoints are committed to the separate history-data branch using
Conventional Commit subjects. Updates are ordinary fast-forward commits, not
forced history rewrites. The daily pack restores that branch and includes the
exact index and referenced observations in its checksum-bound archive.

Every catalogue record exposes collection coverage: not collected, provider
pending, available, unavailable, size-limited or provider-limited. Missing and
pending data are never converted into zero activity. The dated credits page
remains separate from the continuously collected activity data.
Reported commits without a mapped GitHub account retain their counts and an
explicit no-mapped-account value; no person is invented to fill the gap.

```sh
uv run --locked python scripts/history.py status
uv run --locked python scripts/history.py collect --limit 5 --request-budget 20
uv run --locked python scripts/catalogue.py facets --facet history_coverage
uv run --locked python scripts/catalogue.py search --recent-contributor ACCOUNT
uv run --locked python scripts/catalogue.py search --metadata-change changed
```

Public unauthenticated requests have lower GitHub limits. The scheduled worker
uses its repository-scoped GitHub Actions token; token values are never written
into data or logs. A rate/time checkpoint does not mean collection is complete.
Read Actions and source/history/index.json on history-data for actual coverage.

Full history here means all available provider statistics for every catalogued
repository. Private repositories, inaccessible records, excluded commit kinds
and branches outside the default-branch statistics remain explicit limitations.
