# Offline AI evaluation pack

The release test pack gives Claude and Gemini the same prompt and the same frozen repository archive. It contains a standalone Python standard-library verifier, a manifest with the archive and verifier hashes, and the verifier's expected structural results. The verifier reads archive members as streams; it never extracts or executes their contents.

Run the verifier with `python verify_bundle.py --archive xgov-okf.tar.gz --output result.json`. Add `--checksums SHA256SUMS` to check the release checksum file. Without that argument, checksum status is reported as `not_checked`.

Treat the archive SHA-256 as the identity of the evaluation input. Report automated structural checks, manual interpretations and `UNTESTED` items separately. The pack does not query models or establish that either model interpreted the evidence correctly. It makes no claim about current repositories, code safety, vulnerability status, completeness, or human acceptance.

The test-pack ZIP is deterministic for a fixed archive and verifier. Its contents are `PROMPT.md`, `README.md`, `manifest.json`, `expected-results.json` and `verify_bundle.py`. The ZIP basename is `xgov-ai-test-pack.zip`.

The verifier checks complete archive membership and every declared hash; exact
record inventory; complete facet postings/counts and Python/SBOM intersection;
metadata parity for every runtime/RDF assertion; collection states and account
lists; historical/recent measures from every available observation; the two
confirmed cyber/social classification regressions; and targeted record lookup
with inverse adjacency. Counts are computed from the supplied archive, not
hard-coded to an earlier report.

The adjacent manifest is checked automatically by the standalone helper. A
wrong-version archive fails before evaluation. verification-result.json is also
published beside the archive, ZIP and SHA256SUMS. Compare facts and identities
with expected-results.json; checksum/pin status reflects which companion files
were supplied. Keep manual domain interpretation distinct from automated facts.

## Reading the historical evaluations

The [public report collection](ai-evaluations/2026-10-29/README.md) preserves
the original Claude, Gemini and Copilot claims with editorial corrections. The later
[Claude UI capture review](ai-evaluations/2026-10-29/claude-capture-review.md)
records displayed command history, explicit errors, truncation and replay
limits. Its curated index is public; the raw capture remains private. A UI
Response label does not prove exit code zero. No historical report is
acceptance of a newer bundle or a controlled comparison of model capability.

The catalogue and Explorer link to the HTML report collection on Pages. The
HTML, reviewed Markdown, provenance and checksums are built and released
together. The archive-pinned pack above remains the repeatable test route
for Claude and Gemini; a reviewed historical capture is not its replacement.
