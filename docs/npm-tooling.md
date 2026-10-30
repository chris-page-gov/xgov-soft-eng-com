# Locked browser acceptance tooling

The Pages browser check uses the exact `@playwright/cli` version 0.1.17. Its
complete dependency tree, package versions and SHA-512 integrity values are
recorded in `package-lock.json`. `package.json` and `setup-node` pin Node
26.7.0 and npm 11.19.0. The npm configuration selects the public npm registry,
requires exact versions, and disables lifecycle scripts, audit and funding
requests.
Update notifications are disabled as well; browser CI sets
`NO_UPDATE_NOTIFIER=1`, so the locked CLI does not query for a newer release.

Install the same dependency tree locally with:

```sh
npm ci --ignore-scripts --no-audit --no-fund
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export NO_UPDATE_NOTIFIER=1
```

Run the local command with `./node_modules/.bin/playwright-cli`. Do not use
`npx` to resolve this tool. The Pages job disables Playwright browser downloads
and uses the runner-installed Chrome. The locked packages are development-only
browser tooling; production Python remains on the standard library.

The offline lock checker verifies exact tool versions, lock format, every
transitive registry URL and integrity value, credential-free public registry
URLs, disabled lifecycle scripts, immutable CI installation and local CLI
invocation. Static checks use only Python, so history collection and offline
bundle verification do not acquire a Node dependency. The explicit `--runtime`
check also verifies the active Node and npm versions; CI runs it after installing
the pinned Node release, which bundles npm 11.19.0. Run the checks with:

```sh
uv run --locked --offline python scripts/check_npm_lock.py
uv run --locked --offline python scripts/check_npm_lock.py --runtime
uv run --locked --offline python -m unittest tests.test_npm_lock -v
```

The normal validation workflow also runs `npm ci` and the repository test
suite, which includes the lock checker regressions. Package lifecycle scripts
remain disabled during installation, including for optional packages that
declare an install script.

To update the tooling, review the desired CLI/Node/npm releases and edit their
exact pins in the manifest, checker and workflows together. Regenerate the lock
using `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`,
review the complete version/registry/integrity diff, then repeat clean install,
static/runtime checks and browser acceptance for the affected change. Update
documentation and the changelog before building. No audit or advisory matching
is part of these install checks. The current checker deliberately admits the
reviewed flat registry tree; nested or aliased dependencies need a reviewed
checker change. Optional platform packages stay in the lock even when the
current platform does not install them; their install scripts remain disabled.
