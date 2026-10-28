import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import catalogue as c
import permissions as p


def synthetic_grant():
    now=dt.datetime.now(dt.timezone.utc)
    return {'schema':'xgov-scan-permission.v1','status':'approved','scope':{'repository':'examplegov/example','mode':p.MODES[0],'input_sha256':'a'*64,'commit_sha':None,'execute_code':False,'active_service_testing':False,'external_service_transfer':'not-approved'},'owner_or_delegate':'synthetic-owner','authority_review':{'confirmed':True,'reviewed_by':'human:synthetic-test','basis':'Synthetic unit-test fixture only'},'response_received_at':(now-dt.timedelta(hours=2)).isoformat(),'valid_from':(now-dt.timedelta(hours=1)).isoformat(),'expires_at':(now+dt.timedelta(hours=1)).isoformat(),'reporting':{'route':'https://example.invalid/security','private_initial_report':True,'disclosure_terms':'Synthetic private report; no public disclosure'},'tool_and_version':'synthetic-scanner/1','conditions':'Synthetic local metadata test only','approval_evidence_sha256':'b'*64}


class PermissionTests(unittest.TestCase):
    def test_contact_information_is_not_approval(self):
        grant=synthetic_grant();grant['status']='pending'
        with self.assertRaisesRegex(ValueError,'No recorded owner approval'):p.validate_grant(grant,'examplegov/example',p.MODES[0],'a'*64)

    def test_exact_input_and_scope_are_required(self):
        for repository,mode,fingerprint in [('othergov/example',p.MODES[0],'a'*64),('examplegov/example',p.MODES[0],'c'*64),('examplegov/example','active-service-testing','a'*64)]:
            with self.subTest(repository=repository,mode=mode),self.assertRaises(ValueError):p.validate_grant(synthetic_grant(),repository,mode,fingerprint)

    def test_expiry_and_authority_review_fail_closed(self):
        grant=synthetic_grant();grant['expires_at']=grant['valid_from']
        with self.assertRaises(ValueError):p.validate_grant(grant,'examplegov/example',p.MODES[0],'a'*64)
        grant=synthetic_grant();grant['authority_review']['confirmed']=False
        with self.assertRaises(ValueError):p.validate_grant(grant,'examplegov/example',p.MODES[0],'a'*64)

    def test_private_record_evidence_tampering_and_revocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);approval=root/'approval.json';evidence=root/'received.txt'
            approval.write_text(json.dumps(synthetic_grant()));evidence.write_text('Synthetic owner response fixture only')
            p.record(root,'examplegov/example',approval,evidence)
            self.assertFalse(p.check(root,'examplegov/example',p.MODES[0],'a'*64)['scan_started'])
            p.revoke(root,'examplegov/example')
            with self.assertRaises(ValueError):p.check(root,'examplegov/example',p.MODES[0],'a'*64)
            self.assertEqual((root/'.consent/examplegov__example/current.json').stat().st_mode & 0o777,0o600)

    def test_draft_is_unsent_and_cannot_change_public_input_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);before=c.controlled_inputs(root)
            result=p.request(root,'examplegov/example',p.MODES[0],'a'*64)
            self.assertEqual(result['status'],'draft-unsent')
            self.assertEqual(c.controlled_inputs(root),before)
            with self.assertRaises(ValueError):p.request(root,'examplegov/example',p.MODES[0],'a'*64)


if __name__=='__main__':unittest.main()
