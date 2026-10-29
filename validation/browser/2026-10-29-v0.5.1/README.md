# Verified on-demand refresh and history recovery

Observed on 29 October 2026. The [frozen snapshot](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40941783959-1)
was built from producer commit `58eb97ad52c50f9e3c869a57797a1d53e96636b4`.

- Build: `d8f9ebeb1ee2a2c79fcbc414d164d6613ea6f34bb2c29ec73fb90ec66167ee6e`.
- Descriptor SHA-256: `d8352f9507cbbb5fd1b9f724860040a18a6fd9aee163410e08d330bdcc89b036`.
- Archive SHA-256: `da822774bcf48c3514324cbdd8aa68b8e5231a496f7f10169b827df4a4b4e8be`.
- Archive: 70,468,434 bytes; 24,019 repository records and 117,606 assertions.
- Consumer: `2922cede88d4cd2b3a84473ffd772055b9f409c1`, app tree
  `e1aad43dc8236e387654c86d67f1575ebdd4fd94256ea1e9628a879829e34c4a`.

## Pause and manual publication

The owner requested that only daily catalogue publication be paused. The
repository variable `OKF_DAILY_REFRESH_ENABLED` was `false` before the manual
dispatch and remained `false` after verification. Both the refresh and history
workflows remained active. The [manual refresh](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40941783959)
and its automatic [Pages publication and verification](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40942633997)
completed successfully. [The operations receipt](operations-verification.json)
records those observations. No new daily cron tick has occurred since the
pause was applied, so this is not a claim to have observed a scheduled skip.

The missing 16:43 UTC scheduled run had no failed run to inspect. The exact
reason for the absent event remains unknown. The upstream feed and quality
report served modification times of 17:27:56 UTC, after that configured slot;
the quality report declares generation at 17:27:19 UTC. The 19:38 UTC manual
retrieval captured those later inputs. [The source comparison](source-comparison.json)
shows 84 more repositories with reported SBOM paths: 14,393 rather than 14,309.
This does not establish document freshness or vulnerability status.

Use the [on-demand guide](../../../docs/operations.md#pause-and-run-on-demand)
to refresh manually or resume daily publication. Hourly history acquisition
continues independently; its new data reaches Pages at the next catalogue
refresh. GitHub schedules do not guarantee execution at every configured tick.

## History progress

The [first extra batch](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40937773375)
added 500 observations. The [batch using the retry reservation](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40939632259)
processed 100 due retries and 400 new targets using 1,099 API requests, without
reaching its request, rate or time checkpoint. Of those retries, 93 previously
pending entries became available, four remained pending and three returned an
empty or unavailable result. Six new targets also returned usable profiles.

[The comparison](history-progress.json) records the increase from 2,450 to
3,350 observed repositories and from 88 to 189 available profiles. At the last
checkpoint, 3,127 entries remained provider-pending, 25 were empty or
unavailable, eight had unavailable responses and one exceeded the response
size limit. The target is the current 24,019-repository feed; coverage remains
partial. Missing and pending histories are not zero activity.

The frozen index matches the index at history-data commit
`697810aaae0deb7251752bbb68fbaf84f9a75c6f`, SHA-256
`b0bf719a3c28ed69ddf9dd3c6c1a6e92741989b29b86e60a7dfe81e0efbc60f2`.
The archive contains that controlled index and 3,350 referenced observations.
Default-branch statistics retain their documented commit exclusions and do
not establish maintainership or all-branch completeness.

## Assurance

The producer's 70 unit and regression tests, deterministic build/check and
independent complete RDF assurance passed in [CI](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40939531219)
and in the manual refresh. Pages promoted the same assured archive. Its
[browser receipt](public-browser-verification.json) records 48 ordinary-Chrome
checks across facets, combinations, semantic/contributor journeys and reports,
bound to the producer and consumer identities above. A separate
[report recheck](report-recheck.json) passed eight checks against the same
descriptor. Both runs recorded no console errors, page errors or failed requests.

Every downloaded release asset matched SHA256SUMS. The test ZIP's verifier
matched the reviewed producer source before execution. The
[offline replay](offline-verification.json) passed all ten archive-pinned
checks, including the supplied checksum and manifest pins. It does not claim
live HTTP, browser or broader classification assurance.

[Current upstream SBOM counters](sbom-quality-summary.json) are retained as
dated observations. They are not distinct-package counts, advisory matches or
deployed exposure. No scanner, new model evaluation or Daybreak call was run.
The [proposed pilot](../../../docs/sbom-daybreak-pilot.md) keeps permissions,
private findings, applicability review and reporting separate from discovery.
