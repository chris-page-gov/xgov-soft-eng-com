# v0.4.0 publication and repeatable AI test evidence

These generated, reviewed receipts cover producer commit
`47bf8c71b255d8dc17aef9c5f7e859962175369c` and the frozen
[snapshot-40837379391-1](https://github.com/chris-page-gov/xgov-soft-eng-com/releases/tag/snapshot-40837379391-1).
The complete build identifier is
`981bf56a590e2ded030c7f782727b780507064e9135c54eb669ddb3780faca55`.
The public descriptor SHA-256 is
`a48c131e3df0236260cbeed49f4115ae047131881c6ee308e97899315f8c566c`.

The archive is 68,168,185 bytes with SHA-256
`9bceea8753e659cd87e75aa67466b1b41cd101b5bfe2518d02df3207852f61af`.
Its paired test-pack manifest records the same digest and build identifier.

- `public-browser-verification.json`: 40 passing checks against public Pages
  in a separate ordinary Chrome context, with no console errors, page errors
  or failed requests.
- `hosted-browser-verification.json`: the independent 40-check hosted Chrome
  result from [Pages run 40838050643](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40838050643).
- `offline-verification.json`: the helper copied from the downloaded release
  ZIP and run against the downloaded archive and SHA256SUMS. Both the paired
  manifest pin and external archive checksum passed.
- `ai-test-pack-manifest.json`: the exact released pack's archive and verifier
  identity bindings and automated case identifiers.
- `local-browser-verification.json`: the earlier 40-check local archive-derived
  rehearsal. Its own snapshot and consumer identifiers remain unchanged.

The public snapshot contains 24,068 repository records, 115,798 assertions and
1,746 facet values. The offline verifier checks every runtime/RDF assertion,
every facet posting/count, source metrics, exact targeted lookup and inverse
adjacency, and all 69 available history profiles. It recomputes Python plus
reported-SBOM membership as 1,619 records. The captured NHS example has 299
historical commits, 8 recent commits across 7 active weeks, 38 additions and
5 deletions in its exact retained reporting window.

History remains progressive: 69 available, 1,444 pending provider statistics,
3 empty or unavailable, 8 unavailable responses, 1 size-limited response and
22,543 not collected. Account arrays contain logins only; separate facet values
preserve missing and provider states. These observations establish neither
maintainership nor repository quality, vulnerability status or scan permission.

The implementation passed 57 unit/regression tests, deterministic rebuild and
documentation lockstep, and complete schema/RDF assurance in
[refresh run 40837379391](https://github.com/chris-page-gov/xgov-soft-eng-com/actions/runs/40837379391).
The two confirmed cyber/social classification regressions pass. Broader
classification accuracy remains unreviewed. The offline result deliberately
marks live HTTP, browser UI and broader classification accuracy as untested;
browser evidence is supplied separately above. No new Claude or Gemini model
execution is claimed.

This directory is excluded from controlled build inputs as the publication
contract's generated evidence boundary. `SHA256SUMS` covers its files except
itself. No raw browser logs or private account-usage records are included.
