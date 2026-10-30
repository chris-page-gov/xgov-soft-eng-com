import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_repository_protection as protection
import check_release_hygiene as hygiene


def fixture():
    policy = json.loads((ROOT / 'config/repository-protection.json').read_text())
    snapshot = {k: copy.deepcopy(policy[k]) for k in ('repository_settings', 'actions_permissions',
                'selected_actions', 'workflow_permissions', 'private_vulnerability_reporting',
                'vulnerability_alerts', 'automated_security_fixes', 'classic_branch_protection')}
    snapshot.update(rulesets=[copy.deepcopy(policy['ruleset'])],
                    effective_rules=copy.deepcopy(policy['ruleset']['rules']),
                    security_and_analysis={f: {'status': 'enabled'} for f in policy['security_features']})
    return policy, snapshot


class RepositoryProtectionTests(unittest.TestCase):
    def test_sole_maintainer_can_merge_a_checked_pr_without_external_approval(self):
        policy, snapshot = fixture()
        self.assertTrue(protection.validate_snapshot(policy, snapshot))
        self.assertEqual(policy['ruleset']['rules'][2]['parameters']['required_approving_review_count'], 0)

    def test_missing_inactive_or_bypassed_rules_fail(self):
        for mutate in (lambda s: s.update(rulesets=[]),
                       lambda s: s['rulesets'][0].update(enforcement='disabled'),
                       lambda s: s['rulesets'][0].update(bypass_actors=[{'actor_id': 5, 'actor_type': 'RepositoryRole', 'bypass_mode': 'always'}])):
            policy, snapshot = fixture(); mutate(snapshot)
            with self.assertRaises(ValueError): protection.validate_snapshot(policy, snapshot)

    def test_effective_rules_reject_weakened_or_deadlocking_controls(self):
        for mutate in (lambda s: s['effective_rules'].pop(),
                       lambda s: s['effective_rules'][2]['parameters'].update(required_approving_review_count=1),
                       lambda s: s['effective_rules'][3]['parameters'].update(strict_required_status_checks_policy=False),
                       lambda s: s['effective_rules'][3]['parameters']['required_status_checks'][0].update(integration_id=999),
                       lambda s: s.update(classic_branch_protection={'required_pull_request_reviews': {'required_approving_review_count': 1}}),
                       lambda s: s.pop('classic_branch_protection'),
                       lambda s: s['effective_rules'].append({'type': 'required_signatures'})):
            policy, snapshot = fixture(); mutate(snapshot)
            with self.assertRaises(ValueError): protection.validate_snapshot(policy, snapshot)

    def test_weak_actions_and_missing_private_reporting_fail(self):
        for key, change in (('actions_permissions', {'sha_pinning_required': False}),
                            ('selected_actions', {'patterns_allowed': ['*']}),
                            ('workflow_permissions', {'can_approve_pull_request_reviews': True}),
                            ('private_vulnerability_reporting', {'enabled': False}),
                            ('automated_security_fixes', {'paused': True})):
            policy, snapshot = fixture(); snapshot[key].update(change)
            with self.assertRaises(ValueError): protection.validate_snapshot(policy, snapshot)
        policy, snapshot = fixture(); snapshot['vulnerability_alerts'] = False
        with self.assertRaises(ValueError): protection.validate_snapshot(policy, snapshot)

    def test_live_reader_only_uses_bounded_get_requests_and_fails_closed(self):
        policy, snapshot = fixture()
        def response(command, **kwargs):
            self.assertEqual(command[:4], ['gh', 'api', '--method', 'GET'])
            self.assertEqual(kwargs['timeout'], 30)
            self.assertTrue(command[4].startswith('repos/' + protection.REPOSITORY))
            return type('Response', (), {'returncode': 1, 'stdout': '', 'stderr': 'denied'})()
        with patch.object(protection.subprocess, 'run', side_effect=response), self.assertRaises(ValueError):
            protection.read_live(policy)

    def test_transitive_versions_hashes_and_extra_requirements_are_bound(self):
        sha = 'a' * 64
        lock = {'package': [{'name': 'fixture', 'version': '1.0', 'source': {'registry': 'https://pypi.org/simple'},
                             'wheels': [{'hash': 'sha256:' + sha}]}]}
        text = 'fixture==1.0 \\\n    --hash=sha256:' + sha + '\n'
        self.assertTrue(protection.validate_requirements(lock, text))
        for bad in (text.replace('==1.0', '==2.0'), text.replace(sha, 'b' * 64),
                    text + 'extra==1.0\n', text + '--extra-index-url https://example.invalid/\n', ''):
            with self.assertRaises(ValueError): protection.validate_requirements(lock, bad)

    def test_checked_in_workflow_and_lock_satisfy_the_local_policy(self):
        self.assertEqual(protection.validate_local(ROOT)['repository'], protection.REPOSITORY)

    def test_pr_titles_are_checked_without_treating_them_as_commands(self):
        hygiene.check_pr_title('pull_request', 'ci: enforce repository policy')
        hygiene.check_pr_title('pull_request', 'docs: explain $(literal) command syntax')
        hygiene.check_pr_title('push', None)
        for title in (None, 'Update files', 'fix: ' + 'x' * 80):
            with self.assertRaises(ValueError): hygiene.check_pr_title('pull_request', title)


if __name__ == '__main__':
    unittest.main()
