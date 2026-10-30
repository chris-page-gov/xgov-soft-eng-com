# Repository protection for a sole maintainer

The reviewed baseline is in
[`config/repository-protection.json`](../config/repository-protection.json).
GitHub settings are separate from Git: the read-only live check verifies the
effective settings rather than assuming that this file applies them.

## Main branch

The active [main ruleset](https://github.com/chris-page-gov/xgov-soft-eng-com/rules/26205671)
requires a pull request, an up-to-date branch and the `validate` check produced
by the GitHub Actions app (integration ID `15368`). It blocks force pushes and
branch deletion and requires review conversations to be resolved. There are
no standing bypass actors, including administrators and Actions.

The approval count is **zero**. A sole developer cannot provide independent
approval for their own pull request. Review the diff, tests and evidence,
then merge through the checked pull request. This preserves a review record
without claiming independent review. GitHub documents
[pull requests with zero required approvals and strict checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).

Merge and squash commit defaults use the pull-request title and body. The
title must follow Conventional Commits; title edits rerun validation.
Merge, squash and rebase are permitted, preserving existing history.
Automatic merging is disabled; GitHub deletes merged branches automatically.
Signed commits and linear history are not mandatory in this baseline.

## Actions and dependencies

- Only GitHub-owned actions are allowed, with full commit SHA pins enforced
  by GitHub and checked locally. Third-party actions need a reviewed policy
  change; Marketplace verification alone does not grant access.
- The default workflow token is read-only and cannot approve pull requests.
  Validation and read-only Pages checkouts discard persisted credentials.
  Release and history jobs retain their explicitly declared write permissions
  for releases and `history-data`; they have no bypass for `main`.
- All jobs use bounded standard hosted runners. No paid model service or new
  scanning workflow is introduced.
- The `assurance` dependency group in `pyproject.toml` and `uv.lock` pins the
  eight direct and transitive packages. The CI requirements export contains
  their archive hashes and is installed with `pip --require-hashes`.
  Production catalogue generation and search still use the standard library.

GitHub recommends
[least-privilege tokens and immutable Action pins](https://docs.github.com/en/actions/reference/security/secure-use).
The local checker rejects missing credential controls, unpinned actions,
unreviewed Action sources and drift between the lock and requirements hashes.

Update dependencies deliberately in a branch:

```sh
uv lock --upgrade --default-index https://pypi.org/simple
uv export --locked --only-group assurance --no-emit-project --no-header --output-file requirements-assurance.txt
uv sync --locked --group assurance
uv run --locked python scripts/check_repository_protection.py --local
uv run --locked python -m unittest discover -s tests -v
uv run --locked python scripts/catalogue.py build
uv run --locked python scripts/catalogue.py check
uv run --locked --group assurance python scripts/assure.py
```

Review direct pins before changing them: `--upgrade` does not override exact
constraints. Update the relevant documentation and changelog before building.
CI deliberately uses the hash-checked pip export on its existing pinned
Python runner, avoiding an additional installer Action. Local Python remains
governed by `uv run --locked`. No dependency-update schedule is added here.

## Private reporting and existing security features

[Report a vulnerability privately](https://github.com/chris-page-gov/xgov-soft-eng-com/security/advisories/new)
for this producer. GitHub private vulnerability reporting is enabled. This
opens a reporting form; it does not submit a report or contact another
repository's maintainers. Follow [SECURITY.md](../SECURITY.md) and omit secrets
and restricted data. GitHub explains the
[private reporting mechanism](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately).

Existing secret scanning, push protection, Dependabot alerts and security
updates remain enabled. No new code analysis, real SBOM matching, maintainer
contact, issue or advisory publication is authorised by this baseline.
Public SBOM data analysis remains distinct from owner-approved testing;
see [the bounded pilot guide](public-sbom-pilot.md).

## Verify and recover

```sh
# Offline source, workflow and lock checks; safe for untrusted PR CI.
uv run --locked python scripts/check_repository_protection.py --local

# Authenticated owner/admin read-only API checks; no settings writes.
uv run --locked python scripts/check_repository_protection.py --live
```

`--live` uses the existing `gh` login and fixed GET endpoints for this
repository, with a 30-second timeout per request. It fails on denied or
missing settings, an unexpected effective rule, an extra approval requirement,
a bypass actor, a missing trusted check or weakened security settings. It
also rejects a classic branch-protection rule layered over the ruleset, so an
additional approval requirement cannot silently lock out the sole maintainer. It
prints a compact status receipt, without tokens or alert contents. `--snapshot`
accepts a saved settings response for offline testing; it does not prove the
current live state. CI runs `--local`, not privileged settings access.

If a check fails, fix the branch, workflow or settings and repeat validation.
Do not bypass the rules to merge. An administrator can edit a ruleset if
recovery is essential: record the reason, review its exact change and restore
the reviewed baseline before resuming ordinary work. A maintainer can still
alter GitHub settings; this is not an account-side or independent-review
security boundary. The `history-data` branch is deliberately outside the
`main` ruleset so its serial worker can checkpoint normally.

## Evidence and limits

The baseline was configured and checked on 30 October 2026. Local regressions
use synthetic settings and mocked GitHub services; live verification reads
effective GitHub rules. The first protection pull request exercises the normal
required-check merge route. The daily refresh pause and hourly history
schedule remain separate and unchanged. No real scans run as part of this work.

This is a measurable maintenance baseline. It is not an exhaustive security,
accessibility or supply-chain certification. Account passkeys/2FA, recovery
codes, token/app permissions and notification delivery need separate owner
review. Browser tooling retains its documented pinned CLI version; its npm
transitive supply chain needs a separate lock review. Real Grype matching and
Linux network isolation remain unexercised. New scanning services, additional
automation and any public findings require separate decisions.
