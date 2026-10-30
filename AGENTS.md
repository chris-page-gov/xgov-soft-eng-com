# Repository instructions

- Use British English, plain English, sentence case, en-GB and Europe/London.
  Preserve source quotations, identifiers, official titles and filenames.
- Read okf.semantic.json, okf.publication.json and LICENSE_DECISIONS.md before
  changing source admission, semantics, build or publication.
- Frozen source bytes and authored rules/documentation are authoritative.
  Never hand-edit generated/. Use uv run --locked python with pinned Python.
- Changes to code, config, schemas or workflows must update relevant docs and
  CHANGELOG.md before rebuilding. Build requires a changelog update for changed
  implementation inputs; check verifies deterministic output and doc hashes.
- Required checks: unittest discover -s tests -v; catalogue.py build; catalogue.py
  check; check_repository_protection.py --local. Before release also run
  uv run --locked --group assurance python scripts/assure.py. Production
  build/search use only the stdlib. The assurance group and hash-checked CI
  requirements export must remain synchronised; see docs/repository-protection.md.
- Public GitHub publication and daily refresh were explicitly authorised on
  28 October 2026. Publish only admitted public sources, reviewed repository
  files and exact checked outputs. Keep credentials and account usage outside.
- Standard GitHub-hosted runners only; no paid model APIs, premium runners,
  credit purchases or billing changes. Do not execute catalogued code.
- Do not open upstream issues, contact maintainers or label repositories
  vulnerable without a separately scoped task and supporting evidence.
- The semantic profile uses a custom experimental profile. Do not claim canonical
  Bundle Wiki v1 conformance, human acceptance or exhaustive domain coverage.
- External schema fields such as license, normalized, and assertion_status,
  upstream evidence, titles and MIT notices are intentional language exceptions.

- Hourly public history acquisition is authorised for all catalogued repositories,
  with one serial worker and bounded GitHub request/time budgets. Preserve
  explicit coverage, default-branch limitations and minimal account data.
- Never admit .consent/, private starters, private reports or approval evidence
  into a public build/archive. Permission tooling creates unsent drafts only.
- Account-security observations belong only in the ignored .account-security/
  directory with private permissions. Keep account inventories, session and
  token details out of Git, public documentation, bundles, Pages and archives.
  Review authentication settings read-only; do not reveal recovery codes,
  expand token scopes or change credentials to complete an assessment.
- Public SBOM data matching uses the explicit public-sbom-data-analysis mode.
  It does not require or imply individual repository-owner approval. Admit only
  already-published documents with a recorded access/reuse basis; unclear or
  restricted inputs need review. Keep .sbom-pilot/ out of Git, public bundles,
  Pages and archives. No real matching or catalogue SBOM retrieval was authorised
  during implementation; synthetic tests and public tooling downloads are allowed.
- Use Conventional Commits and Keep a Changelog; see CONTRIBUTING.md. Preserve
  the published legacy baseline rather than rewriting remote history.
- Main changes use a pull request and the required GitHub Actions validate
  check, including for the sole owner. Do not bypass, disable or weaken the
  rules to merge. No second-person approval is required. Recheck live policy
  with the read-only protection checker after settings changes.
- Browser tooling uses package-lock.json and the pinned Node/npm versions.
  Install with npm ci --ignore-scripts --no-audit --no-fund, disable Playwright
  browser downloads and invoke the local CLI. Do not use npx or npm audit for
  acceptance. Static npm lock checks must remain usable without Node so the
  Python-only history worker and offline verifier keep working.
