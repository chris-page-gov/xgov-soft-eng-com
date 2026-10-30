# Review the maintainer's GitHub account security

This is a read-only configuration and access review. It does not run code
analysis, dependency advisory matching, repository scans or credential tests.
Repository protection and personal account protection are separate controls.
The procedure is public; account inventories and findings remain private.

## Scope and evidence

Confirm the signed-in account matches the repository owner before assessing
settings. Use GitHub's authenticated settings pages when APIs do not expose a
field. A missing API field or denied endpoint is **unverified**, not disabled,
empty or safe. Do not expand a token's scopes solely to obtain evidence.

Record each observation with its settings-page source, observation time,
coverage and one of these states:

| State | Meaning |
| --- | --- |
| Observed | A visible setting or permitted API result supplies the evidence |
| Owner action | The review identifies a decision, recognition or maintenance task for the owner |
| Unverified | Access, retention, coverage or independent evidence is insufficient |
| Not assessed | Deliberately outside this personal-account review |

Review completion means the scoped assessment and findings have been recorded.
It does not mean all owner actions are resolved or the account is certified
secure. Do not infer compromise from a place name, stale session, unused grant
or token lifecycle event alone.

## Repeatable review

1. Open [password and authentication](https://github.com/settings/security).
   Check 2FA, preferred methods, passkeys, recovery warnings and fallback
   methods. Record configuration metadata only. Never reveal, copy or download
   recovery codes, passwords, OTP seeds or private keys for this review.
2. Review [sessions](https://github.com/settings/sessions), including mobile
   sessions. The owner must recognise devices and access. Do not revoke a
   session automatically because it is old or its location is unfamiliar.
3. Review [SSH/GPG keys](https://github.com/settings/keys). Record counts,
   purposes and age/usage where shown; avoid retaining key material or full
   fingerprints. Signing policy is a separate decision from account login.
4. Review [installed GitHub Apps](https://github.com/settings/installations),
   authorised GitHub Apps and OAuth Apps. Check ownership, last use, permissions
   and repository selection. Separate installed access from user authorisation
   and from an individual token's current scopes. Broad access needs an owner
   decision based on the workflows it supports.
5. Review classic and fine-grained tokens through
   [developer settings](https://github.com/settings/apps). Check expiry,
   repository selection, scopes and last use. Never regenerate or expose a
   token to inspect it. An expired token is not an active access path; record
   it separately from live OAuth authorisations.
6. Review [security notifications](https://github.com/settings/notifications)
   and this repository's watch/security-alert subscription. Configuration
   does not prove delivery. Do not send a test message or change destinations
   as part of the review.
7. Inspect the [personal security log](https://github.com/settings/security-log)
   for a declared time window and relevant authentication, recovery, token and
   authorisation events. Record query, pagination and coverage limits. Do not
   follow enterprise SSO routes or claim an enterprise-wide audit. Exporting
   all raw events is unnecessary for this configuration review.

GitHub documents [account protections](https://docs.github.com/en/code-security/tutorials/implement-supply-chain-best-practices/securing-accounts),
[OAuth authorisation review](https://docs.github.com/en/apps/oauth-apps/using-oauth-apps/reviewing-your-authorized-oauth-apps),
[2FA configuration](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication)
and [security-log review](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log).

## Private findings and owner decisions

Keep a minimal Markdown/JSON review in `.account-security/` with directory mode
`0700` and file mode `0600` on POSIX systems. Record conclusions, source pages
and actions; omit IP addresses, precise locations, personal email addresses,
token values/suffixes, recovery codes, raw logs and private repository names.
Encryption and a durable private backup are separate owner decisions.

Git ignores this directory and case variants. Release hygiene rejects forced
tracking; admission rejects symlinks into it; archive, standalone verifier and
Pages guards reject its paths. Installed `node_modules/` has the same public
exclusion boundary. Regression fixtures contain synthetic data only.

The owner should handle credential rotation, backup verification, authenticator
changes and access revocation. Plan any change to preserve recovery and ongoing
automation. If GitHub requires reauthentication, hand the existing GitHub prompt
to the owner; do not collect credentials or bypass it. An assessment finding is
not permission to revoke an app, widen access or weaken account protections.

No new scanning service, schedule, external AI review, maintainer contact or
publication of account-specific findings is introduced by this procedure.
