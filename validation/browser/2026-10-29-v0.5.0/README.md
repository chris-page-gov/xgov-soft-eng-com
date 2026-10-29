# Verified v0.5.0 report publication

Observed on 29 October 2026. The [frozen snapshot](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40909466508-1)
was built from producer commit `be7abc2b1bba978795e6dbb5dcbf03d83f39cf80`.

- Build: `624f1a14ed907ce0bf59ed87f85446b4354df68107d7a64943b72841fdb49c60`.
- Descriptor SHA-256: `a7969e4f7c70e95833839eaeaa733587767f13c17e6a6963d61fd7c960e3274c`.
- Archive SHA-256: `2513a8eaa7f916aca799bf844ed0f75d415abc0cd42e47b7bda646db0a1a1809`.
- Archive: 69,030,647 bytes; 24,019 repository records and 116,619 assertions.
- Consumer: `2922cede88d4cd2b3a84473ffd772055b9f409c1`, app tree
  `e1aad43dc8236e387654c86d67f1575ebdd4fd94256ea1e9628a879829e34c4a`.

## Results

The producer's 67 unit/regression tests, deterministic build/check and
independent complete RDF assurance passed in [CI](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40903975458).
The [Pages workflow](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40910179256)
promoted the same assured snapshot and passed 48 ordinary-Chrome checks.
[The receipt](public-browser-verification.json) binds all four suites to the
same producer and consumer identities, with no console errors, page errors or
failed requests. Existing facets, semantic links and contributor journeys are
included alongside the eight new report checks.

A separate [public report recheck](report-recheck.json) passed all eight report
checks again: catalogue and Explorer navigation, six HTML page identities,
the 35-request Claude capture review, all 16 report-output hashes, supporting
provenance hashes, 390-pixel layouts and private-path exclusions. Desktop and
mobile screenshots were visually reviewed; the earlier long-link overflow in
the Gemini report is resolved.

The downloaded five-file test ZIP's verifier matched the reviewed producer
source before it was run. The [offline replay](offline-verification.json)
passed all ten archive-pinned checks with SHA256SUMS checked. It does not claim
live HTTP, browser coverage or classification accuracy beyond its declared
regressions; those scopes remain separate. The supplied verification-result
asset remains unchanged.

The [README check](readme-functional-check.json) confirms the three-step AI
starter route, copyable prompt, three example links and Copilot report
navigation. GitHub's global navigation emitted an unrelated 404, so this is a
functional check rather than a zero-error assertion about github.com.

The reports are historical examples from different earlier inputs, not a
controlled model comparison or acceptance of this release. No new Claude,
Gemini or Copilot run is claimed. Raw model sessions and the Claude capture
remain private. History collection remains partial; the checks do not establish
all-branch completeness, security, repository rights or human acceptance.
