#!/usr/bin/env python3
"""Check that browser acceptance uses the reviewed, credential-free npm lock."""
import json
import argparse
import base64
import binascii
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'registry.npmjs.org'
NODE_VERSION = '26.7.0'
NPM_VERSION = '11.19.0'
PLAYWRIGHT_CLI = '@playwright/cli'
PLAYWRIGHT_VERSION = '0.1.17'


def validate(root=ROOT, check_runtime=False):
    if check_runtime:
        if subprocess.check_output(['node', '--version'], text=True, timeout=15).strip() != 'v' + NODE_VERSION:
            raise ValueError('Node runtime must be ' + NODE_VERSION)
        if subprocess.check_output(['npm', '--version'], text=True, timeout=15).strip() != NPM_VERSION:
            raise ValueError('npm runtime must be ' + NPM_VERSION)
    package = json.loads((root / 'package.json').read_text())
    lock = json.loads((root / 'package-lock.json').read_text())
    npmrc = (root / '.npmrc').read_text()
    pages = (root / '.github/workflows/pages.yml').read_text()
    validation = (root / '.github/workflows/validate.yml').read_text()

    if package.get('engines') != {'node': NODE_VERSION, 'npm': NPM_VERSION}:
        raise ValueError('package.json must pin the reviewed Node and npm versions')
    if package.get('packageManager') != 'npm@' + NPM_VERSION:
        raise ValueError('package.json must declare the reviewed npm package manager')
    if (package.get('private') is not True or package.get('dependencies', {})
            or package.get('devDependencies') != {PLAYWRIGHT_CLI: PLAYWRIGHT_VERSION}):
        raise ValueError('Playwright CLI must remain an exact direct dependency')
    if {'preinstall', 'install', 'postinstall', 'prepare'} & package.get('scripts', {}).keys():
        raise ValueError('The browser tool manifest must not define install lifecycle scripts')
    lock_root = lock.get('packages', {}).get('', {})
    if (lock.get('lockfileVersion') != 3
            or lock.get('name') != package.get('name') or lock.get('version') != package.get('version')
            or lock_root.get('devDependencies') != {PLAYWRIGHT_CLI: PLAYWRIGHT_VERSION}
            or lock_root.get('engines') != package.get('engines')):
        raise ValueError('package-lock.json must be npm lockfile v3 and match the direct dependency')
    expected_config = {'registry=https://registry.npmjs.org/', 'save-exact=true', 'engine-strict=true',
                       'package-lock=true', 'ignore-scripts=true', 'audit=false', 'fund=false', 'update-notifier=false'}
    config_lines = [line.strip() for line in npmrc.splitlines() if line.strip() and not line.lstrip().startswith('#')]
    if set(config_lines) != expected_config or len(config_lines) != len(expected_config):
        raise ValueError('npm configuration must exactly retain the reviewed script, audit and registry policy')

    packages = lock['packages']
    if 'node_modules/@playwright/cli' not in packages or packages['node_modules/@playwright/cli'].get('version') != PLAYWRIGHT_VERSION:
        raise ValueError('Lock file does not contain the exact Playwright CLI')
    for path, record in packages.items():
        if not path:
            continue
        if not re.fullmatch(r'node_modules/(?:@[A-Za-z0-9._-]+/)?[A-Za-z0-9._-]+', path) or record.get('link'):
            raise ValueError('Unreviewed linked or nested npm package layout: ' + path)
        if not isinstance(record.get('version'), str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', record['version']):
            raise ValueError('Every npm package must have an exact version: ' + path)
        resolved = record.get('resolved')
        if not isinstance(resolved, str):
            raise ValueError('Every npm package must have a resolved registry URL: ' + path)
        url = urlsplit(resolved)
        name = path.removeprefix('node_modules/')
        expected_url = 'https://' + REGISTRY + '/' + name + '/-/' + name.split('/')[-1] + '-' + record['version'] + '.tgz'
        if (url.scheme != 'https' or url.hostname != REGISTRY or url.username or url.password
                or url.port not in (None, 443) or url.query or url.fragment or resolved != expected_url):
            raise ValueError('npm package URL must be credential-free HTTPS on the public registry: ' + path)
        integrity = record.get('integrity', '')
        try:
            digest = base64.b64decode(integrity.removeprefix('sha512-'), validate=True)
        except (binascii.Error, ValueError):
            digest = b''
        if (not integrity.startswith('sha512-') or len(digest) != 64
                or base64.b64encode(digest).decode('ascii') != integrity.removeprefix('sha512-')):
            raise ValueError('Every npm package must have a SHA-512 integrity: ' + path)
        for dependency, version in {**record.get('dependencies', {}), **record.get('optionalDependencies', {})}.items():
            target = packages.get('node_modules/' + dependency)
            if not isinstance(target, dict) or target.get('version') != version:
                raise ValueError('Missing or mismatched transitive dependency: ' + dependency)

    for workflow, label in ((pages, 'Pages'), (validation, 'validation')):
        if "node-version: '" + NODE_VERSION + "'" not in workflow:
            raise ValueError(label + ' workflow must pin Node ' + NODE_VERSION)
        if 'npm ci --ignore-scripts --no-audit --no-fund' not in workflow:
            raise ValueError(label + ' workflow must install immutably with scripts and audits disabled')
        if 'python scripts/check_npm_lock.py --runtime' not in workflow:
            raise ValueError(label + ' workflow must verify the active Node and npm runtimes')
    if 'PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD' not in pages or './node_modules/.bin/playwright-cli' not in pages:
        raise ValueError('Pages must disable browser downloads and invoke the locked local CLI')
    if ('NO_UPDATE_NOTIFIER' not in pages or 'NO_UPDATE_NOTIFIER' not in validation
            or './node_modules/.bin/playwright-cli --version' not in validation):
        raise ValueError('CI must smoke-test the local CLI with update checks disabled')
    if 'npx ' in pages:
        raise ValueError('Pages must not resolve the CLI through npx')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', action='store_true', help='Also check installed Node/npm; static checks need only Python')
    args = parser.parse_args()
    try:
        validate(check_runtime=args.runtime)
        print('npm lock checks passed' + (' with runtime verification.' if args.runtime else ' (static; no Node/npm execution).'))
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit('npm lock check failed: ' + str(exc))


if __name__ == '__main__':
    main()
