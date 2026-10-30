#!/usr/bin/env python3
"""Check local policy or read live GitHub settings; never change settings."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'chris-page-gov/xgov-soft-eng-com'


def contains(actual, expected, path='policy'):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise ValueError(path + ' is missing')
        for key, value in expected.items():
            contains(actual.get(key), value, path + '.' + key)
    elif type(actual) is not type(expected) or actual != expected:
        raise ValueError(path + ' differs from the reviewed policy')


def validate_snapshot(policy, snapshot):
    rulesets = snapshot.get('rulesets', [])
    selected = [r for r in rulesets if r.get('name') == policy['ruleset']['name']]
    if len(selected) != 1:
        raise ValueError('Exactly one reviewed main ruleset must be present')
    contains(selected[0], policy['ruleset'], 'ruleset')
    effective = snapshot.get('effective_rules', [])
    expected = policy['ruleset']['rules']
    if sorted(r['type'] for r in effective) != sorted(r['type'] for r in expected):
        raise ValueError('Effective main rules differ; review missing or additional rules')
    for rule in expected:
        contains(next(r for r in effective if r['type'] == rule['type']), rule, 'effective.' + rule['type'])
    for key in ('repository_settings', 'actions_permissions', 'selected_actions', 'workflow_permissions',
                'private_vulnerability_reporting', 'vulnerability_alerts', 'automated_security_fixes',
                'classic_branch_protection'):
        if key not in snapshot:
            raise ValueError('Missing verified setting: ' + key)
        contains(snapshot.get(key), policy[key], key)
    for feature in policy['security_features']:
        contains(snapshot.get('security_and_analysis', {}).get(feature), {'status': 'enabled'}, feature)
    return True


def validate_requirements(lock, requirements):
    for line in requirements.splitlines():
        if line.strip() and not (line.lstrip().startswith('#') or re.fullmatch(
                r'[a-z0-9-]+==[^\s;\\]+(?: ; [^\\\n]+)? \\|    --hash=sha256:[a-f0-9]{64}(?: \\)?', line)):
            raise ValueError('Unexpected pip directive or unlocked requirement in assurance export')
    expected = {}
    for package in lock['package']:
        if 'registry' not in package['source']:
            continue
        if package['source']['registry'] != 'https://pypi.org/simple':
            raise ValueError('Assurance dependencies must use the reviewed public index')
        archives = package.get('wheels', []) + ([package['sdist']] if 'sdist' in package else [])
        expected[package['name']] = (package['version'], {a['hash'] for a in archives})
    actual = {}
    for block in re.split(r'(?m)^(?=[A-Za-z0-9-])', requirements):
        if not block.strip() or block.lstrip().startswith('#'):
            continue
        match = re.match(r'([a-z0-9-]+)==([^\s;\\]+)', block)
        if not match or match[1] in actual:
            raise ValueError('Assurance export contains an unsupported or duplicate requirement')
        actual[match[1]] = (match[2], set(re.findall(r'--hash=(sha256:[a-f0-9]{64})', block)))
    if actual != expected or not expected or any(not hashes for _, hashes in actual.values()):
        raise ValueError('Assurance export must exactly match all locked versions and archive hashes')
    return True


def validate_local(root):
    policy = json.loads((root / 'config/repository-protection.json').read_text())
    if policy.get('repository') != REPOSITORY:
        raise ValueError('Unexpected repository policy target')
    # Check the essential invariants even if somebody weakens the policy file.
    rule = policy['ruleset']
    contains(rule, {'target': 'branch', 'enforcement': 'active', 'bypass_actors': [],
                    'conditions': {'ref_name': {'include': ['refs/heads/main'], 'exclude': []}}})
    by_type = {r['type']: r for r in rule['rules']}
    for kind in ('deletion', 'non_fast_forward', 'pull_request', 'required_status_checks'):
        if kind not in by_type:
            raise ValueError('Missing main protection: ' + kind)
    contains(by_type['pull_request']['parameters'], {'required_approving_review_count': 0,
             'require_code_owner_review': False, 'require_last_push_approval': False,
             'required_review_thread_resolution': True})
    contains(by_type['required_status_checks']['parameters'], {
        'required_status_checks': [{'context': 'validate', 'integration_id': 15368}],
        'strict_required_status_checks_policy': True, 'do_not_enforce_on_create': False})
    contains(policy['actions_permissions'], {'enabled': True, 'allowed_actions': 'selected', 'sha_pinning_required': True})
    contains(policy['selected_actions'], {'github_owned_allowed': True, 'verified_allowed': False, 'patterns_allowed': []})
    contains(policy['workflow_permissions'], {'default_workflow_permissions': 'read', 'can_approve_pull_request_reviews': False})
    for path in (root / '.github/workflows').glob('*.yml'):
        text = path.read_text()
        if 'pull_request_target:' in text:
            raise ValueError('Privileged pull-request execution needs separate review')
        for reference in re.findall(r'^\s*-?\s*uses:\s*(\S+)', text, re.M):
            if not re.fullmatch(r'actions/[a-z0-9-]+@[a-f0-9]{40}', reference):
                raise ValueError('Only reviewed SHA-pinned GitHub-owned actions are admitted')
    validation = (root / '.github/workflows/validate.yml').read_text()
    checkout = re.search(r'- uses: actions/checkout@[^\n]+\n(.*?)(?=\n      -|\Z)', validation, re.S)
    if not checkout or 'persist-credentials: false' not in checkout.group(1):
        raise ValueError('PR checkout must not persist credentials')
    for required in ('  validate:', '    types: [opened, reopened, synchronize, edited, ready_for_review]',
                     'permissions:\n  contents: read', 'OKF_PR_TITLE: ${{ github.event.pull_request.title }}',
                     'pip install --require-hashes -r requirements-assurance.txt'):
        if required not in validation:
            raise ValueError('Missing validation workflow invariant: ' + required)
    lock = tomllib.loads((root / 'uv.lock').read_text())
    requirements = (root / 'requirements-assurance.txt').read_text()
    validate_requirements(lock, requirements)
    return policy


def read_live(policy):
    def api(path, empty=False, absent_classic=False):
        result = subprocess.run(['gh', 'api', '--method', 'GET', 'repos/' + REPOSITORY + path],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            if absent_classic:
                error = json.loads(result.stdout)
                if error.get('status') == '404' and error.get('message') == 'Branch not protected':
                    return None
            raise ValueError('Cannot verify GitHub endpoint ' + path)
        return True if empty else json.loads(result.stdout)
    repo = api('')
    rulesets = api('/rulesets')
    details = [api('/rulesets/' + str(int(row['id']))) for row in rulesets]
    return {'repository_settings': {k: repo.get(k) for k in policy['repository_settings']},
            'security_and_analysis': repo.get('security_and_analysis', {}), 'rulesets': details,
            'effective_rules': api('/rules/branches/main'), 'actions_permissions': api('/actions/permissions'),
            'selected_actions': api('/actions/permissions/selected-actions'),
            'workflow_permissions': api('/actions/permissions/workflow'),
            'private_vulnerability_reporting': api('/private-vulnerability-reporting'),
            'classic_branch_protection': api('/branches/main/protection', absent_classic=True),
            'vulnerability_alerts': api('/vulnerability-alerts', empty=True),
            'automated_security_fixes': api('/automated-security-fixes')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--local', action='store_true')
    group.add_argument('--live', action='store_true')
    group.add_argument('--snapshot', type=Path)
    args = parser.parse_args()
    try:
        policy = validate_local(ROOT)
        snapshot = read_live(policy) if args.live else json.loads(args.snapshot.read_text()) if args.snapshot else None
        if snapshot is not None:
            validate_snapshot(policy, snapshot)
        print(json.dumps({'status': 'passed', 'mode': 'live' if args.live else 'snapshot' if args.snapshot else 'local',
                          'repository': REPOSITORY, 'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                          'limitations': ['Local checks do not prove live settings.', 'Administrators can edit repository rules.',
                                          'This checks configuration, not code vulnerabilities or catalogue SBOMs.']}, indent=2))
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, 'Repository protection check failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
