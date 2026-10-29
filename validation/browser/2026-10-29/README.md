# Generated browser acceptance evidence

These sanitised receipts record browser observations on 29 October 2026. This
directory is the generated evidence boundary declared in `okf.publication.json`;
it is excluded from controlled build inputs to avoid a build identifier cycle.

`public-browser-verification.json` records 38 passing checks in ordinary desktop
Chrome against the public catalogue. It binds 24,068 records to producer snapshot
`cf3cc937490d7f3f4de51883e3f8e6d6041c5e24e777d2cecf4b10e95e42b94d`,
descriptor SHA-256
`913133451926d35c4a2bbc1e815d5237ecc1b911f424664357ee33d035171845`,
and Explorer commit `6fc781ce2b350285705d670c51ca400983d8fad1`.

The immutable dataset release is
[snapshot-40796536582-1](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40796536582-1).
Its producer commit is `f24915104e5e9b34c91babab9f00fc5c6bdff02f`.

The checks cover every one of the 25 facet dimensions, two search cases, five
filter combinations and six semantic/history journeys. They compare displayed
counts with the released distributions, follow contributor and inverse links,
check source assertions and activity periods, exercise a narrow viewport and
reload an encoded repository link. No console errors, page errors or failed
requests were observed. The collector verifies the receipts against the released
build manifest and quality checksum.

`automated-browser-verification.json` records the separate headless Chrome run in
the [Pages workflow](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40796929657).
The same verification now follows every successful Pages publication.

The first hosted attempt failed because its facet journey sampled a loading
count. `hosted-pre-fix-failure.json` retains that failed result; the two
`cold-browser-*.json` receipts record the fresh-context reproduction and the
passing correction. A bounded readiness wait fixes the check without changing
the catalogue counts.

`local-*.json` are the earlier 38-check rehearsal against the archive-derived
local candidate and isolated Explorer build. `first-public-smoke.json` is a
smaller observation of the first public snapshot. They retain their original
identifiers and do not describe the final snapshot.

The producer's 49 unit tests, deterministic rebuild, documentation lockstep,
assertion schema validation and complete RDF parse also passed. The Explorer
route fix merged in [PR 186](https://github.com/chris-page-gov/okf-explorer/pull/186)
after its required checks, including the Chrome, Firefox and WebKit suite.

These observations establish the exercised behaviour, not classification
accuracy or exhaustive semantic truth. Contributor-history collection remains
progressive: this public snapshot has 46 available profiles, 970 pending provider
statistics, 9 empty or unavailable responses and 23,043 repositories not yet
collected. Unknown history is distinct from zero activity. The chat web reader
returned an internal error for these URLs; HTTP clients and ordinary Chrome
worked, so AI access still depends on the client's HTTP or file capabilities.

`SHA256SUMS` covers the files in this directory, excluding itself.
