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
  check. Before release also run scripts/assure.py with requirements-assurance.txt
  in a disposable environment. Production build/search use only the stdlib.
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
- Use Conventional Commits and Keep a Changelog; see CONTRIBUTING.md. Preserve
  the published legacy baseline rather than rewriting remote history.
