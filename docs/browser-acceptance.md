# OKF Explorer browser acceptance

The browser acceptance work covers the complete public catalogue and its
authored facets, repository details, semantic links and contributor history.
Checks bind the producer snapshot and the Explorer build being exercised.
Browser acceptance establishes these journeys, not semantic truth, human
acceptance, security assurance or completeness of GitHub's statistics.

## Baseline findings on 28 October 2026

The published v0.2.1 pack loaded in Chrome, but Explorer rejected its static
search index because the search manifest omitted the descriptor's snapshot.
The experimental-publication envelope was also incomplete. Facet names were
visible while their distribution counts were unavailable. That baseline did
not pass browser acceptance.

The corrected producer supplies matching snapshot identities, a complete
experimental-publication notice, targeted record locators, readable endpoint
labels and per-route relationship adjacency. The adjacency contains the same
evidence-bearing assertions as the RDF projection, without claiming canonical
Bundle Wiki rich-runtime conformance or inventing confidence scores.
Adjacency buckets use deterministic gzip with compressed-byte integrity
bindings, keeping the static site within the Pages size boundary.
Record, assertion, result and RDF shards are also compressed. The manifests
declare the new .gz paths; external RDF tools must decompress the advertised
shard before parsing JSON-LD. Repository routes and semantic IRIs are unchanged.
The browser search policy uses accent-folded alphanumeric components, so full
hyphenated repository names remain searchable. It requires every meaningful
query component, rather than silently broadening a multi-word query.

Repository Narrative views expose reported historical and recent contribution,
the exact recent window, weekly and annual change, observation hashes and
missing-data limitations. Annual rows group weeks by their UTC start year.
Counts include any inherited fork history; they do not rank engineering value
or establish maintainership, ownership or permission to scan.

Content-type concept routes use the canonical content-types prefix. This
replaces the earlier underscore spelling, which Explorer's governed endpoint
label contract cannot accept. Repository identities and routes are unchanged.

## Evidence and publication

Raw browser snapshots, logs and diagnostic screenshots remain in ignored
output/playwright. Only reviewed, public acceptance receipts and selected
screenshots may be published with the report. Private grants, private starter
outputs, credentials and account-usage checkpoints are outside this boundary.

The Pages candidate is copied from already-checked generated outputs; it does
not rebuild those files. The public descriptor and Explorer journeys must be
checked at their exact deployed URLs before a working public link is advertised.
Dated public evidence is recorded under validation/browser, with each receipt
bound to its own producer snapshot and consumer tree.

## Repeat the browser matrix

Install the [locked npm tooling](npm-tooling.md) with lifecycle scripts and
audit requests disabled. Use ordinary installed Chrome and the local
Playwright CLI 0.1.17. Open the exact
Explorer URL with its bundle parameter, then run:

```sh
./node_modules/.bin/playwright-cli --session xgov-acceptance open "https://chris-page-gov.github.io/okf-explorer/explore/?bundle=https%3A%2F%2Fchris-page-gov.github.io%2Fxgov-soft-eng-com%2Fokf-explorer.json" --browser chrome --headed
./node_modules/.bin/playwright-cli --session xgov-acceptance run-code --filename scripts/browser_acceptance.js
```

The script requires this catalogue's profile. It reads the checked catalogue
distributions, selects All facets and verifies a displayed count and a kept
result count in every dimension. It also checks full hyphenated-name search
and a zero-result query. The receipt records the descriptor hash, snapshot,
record count, consumer commit, application tree, Chrome version and errors.
A returned status of failed is a failure, even if the CLI exits successfully.
Inspect the receipt; do not treat a zero process exit code as acceptance.
The facet check waits for the published distribution before sampling it. A
fresh browser can initially display an unavailable count while its metadata
loads; a missing or incorrect count still fails after the bounded wait.
Failed receipts retain the journey's bounded error message for diagnosis.

The Pages workflow runs all three suites after deployment in a separate
contents-read job, with Ubuntu 24.04, Node 26.7.0, Playwright CLI 0.1.17 and
runner-installed Chrome. It compares all 40 checks with the exact released
build manifest, quality-file checksum, descriptor hash, snapshot and consumer
identity. CLI exit codes alone never establish success. Validated JSON results
are retained as an Action artefact; failed verification marks the workflow
failed without rebuilding or silently changing the deployed candidate.
Python producer CI checks cover
producer determinism, contracts, complete record lookup and assertion
adjacency, schema validity and RDF equivalence. The separate Pages verification job runs Chrome.
Run scripts/browser_combinations.js in the same way for OR within a facet,
AND across facets, unknown fork values, hosting-account value search and
paging, and available-history selection. Use the further semantic and history
journeys below before claiming full browser acceptance. No cross-engine or human usability acceptance is implied.

The semantic and history journey in scripts/browser_semantics_history.js
checks the repository narrative, contributor row, exact period, observation
hash, annual and weekly tables, assertion identity, inverse label, evidence
link, target and source navigation, missing history, a narrow reading view and
reloading the generated repository link. The Inspector JSON is its normalised
common view. Custom contribution measurements are checked in the published
incident assertion and shown to readers in the repository narrative.

## Acceptance record

The local checks on 28 October 2026 passed 38 checks across the facet, combined
filter and semantic/history journeys in ordinary Chrome 156.0.8078.48. The
semantic journey exercised the clean Explorer route-fix commit in
[PR 186](https://github.com/chris-page-gov/okf-explorer/pull/186); its application
tree was 3a8ccd958e125d79f07e8755878e21ddf10eb60f9bef28364890ef3ad51b2660.
The baseline checks remain useful failure evidence; they are not acceptance.

Public deployment acceptance is recorded separately as reviewed JSON receipts
in validation/browser. Each receipt binds its own descriptor, snapshot, source
commit and consumer application tree. A local result alone does not verify a
public URL. Collection coverage in the tested development fixture was 25
available profiles; the separate hourly backfill continues across the whole
catalogue. The live snapshot's coverage must be read from its own facets.

The whole-estate graph and each browser result set have consumer limits. The
complete available assertion dataset remains in the semantic shards; a route
index provides incident assertions without loading that whole graph. The
producer fails closed if endpoint labels exceed 100,000 entries or the Pages
candidate exceeds 1 GiB. A failed publication retains the previous snapshot.

## Report-driven extension in v0.4.0

The current matrix adds two checks to the previous 38: the snapshot-wide history
coverage notice in the history facet must render, and a pending or missing history band must filter
to its exact source-bound count. The 40-check receipt retains all prior facet,
semantic, mobile and deep-link journeys. The separate offline AI test pack
checks complete facet postings, every RDF assertion and all available profile
measures; its results do not imply browser or model interpretation acceptance.

## Public report journeys

`scripts/browser_reports.js` adds eight snapshot-bound checks: navigation from
the catalogue and Explorer; all six HTML report identities; the later Claude
capture review and 35-request inventory; all 16 report output hashes against
the released build manifest; public-edition provenance hashes; six-page mobile
layout; and private-path exclusions. It starts on Explorer with the catalogue
loaded and restores that view afterwards. The Pages workflow runs it after the
three catalogue suites, and the receipt collector requires all four suites
and 48 checks from the same producer and consumer identities.

The initial local mobile check identified overflowing long evidence links in
the Gemini report. The renderer now wraps long text; the browser check covers
all six report pages at 390 pixels. These report checks supplement the
existing facets, semantic and contributor journeys.
