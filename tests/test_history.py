import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import history as h


class HistoryTests(unittest.TestCase):
    def test_recent_window_excludes_partial_week_and_preserves_past(self):
        observed=dt.datetime(2026,10,28,tzinfo=dt.timezone.utc);sunday=observed-dt.timedelta(days=3)
        recent=int((sunday-dt.timedelta(days=7)).timestamp());current=int(sunday.timestamp())
        rows=[{'total':18,'author':{'login':'example','type':'User','email':'must-not-be-copied@example.invalid'},'weeks':[{'w':recent-100*h.WEEK,'a':8,'d':2,'c':10},{'w':recent,'a':3,'d':1,'c':3},{'w':current,'a':5,'d':0,'c':5}]}]
        result=h.weekly_profile(rows,observed.isoformat())
        self.assertEqual(result['recent_reported_commits'],3);self.assertEqual(result['historical_reported_commits'],18)
        self.assertEqual(result['recent_reported_line_changes'],4)
        self.assertNotIn('must-not-be-copied',json.dumps(result))

    def test_zero_line_counts_are_unknown_not_zero_churn(self):
        rows=[{'total':10001,'author':{'login':'example','type':'User'},'weeks':[{'w':1000000000,'a':0,'d':0,'c':10001}]}]
        result=h.weekly_profile(rows,'2026-10-28T00:00:00Z')
        self.assertIsNone(result['recent_reported_line_changes']);self.assertEqual(result['line_count_status'],'unknown-or-omitted-by-api')

    def test_content_addressed_history_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path='source/history/observations/'+'a'*64+'.json';(root/path).parent.mkdir(parents=True);(root/path).write_text('{}')
            index={'repositories':{'example/repo':{'path':path,'sha256':'a'*64}}}
            with self.assertRaisesRegex(ValueError,'checksum'):h.verify(root,index)

    def test_pending_statistics_are_checkpointed_and_deferred(self):
        from test_catalogue import fixture
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);h.c.write(root/'config/catalogue.json',{'source_url':'https://example.invalid/repos.json','max_bytes':10000})
            response=MagicMock();response.__enter__.return_value=response
            response.geturl.return_value='https://example.invalid/repos.json';response.read.return_value=json.dumps([fixture()]).encode()
            client=MagicMock();client.calls=2
            client.get.side_effect=[(200,{'private':False,'full_name':'ExampleGov/accessible-forms','default_branch':'main'},'a'*64),(202,None,'b'*64)]
            with patch.object(h.urllib.request,'urlopen',return_value=response),patch.object(h,'Client',return_value=client),patch.object(h.c,'now',return_value='2026-10-28T12:00:00Z'):
                result=h.collect(root)
                self.assertEqual(result['coverage'],{'pending-provider-statistics':1})
                index=h.verify(root);item=index['repositories']['examplegov/accessible-forms']
                self.assertEqual(item['next_check_at'],'2026-10-28T18:00:00+00:00')
                observation=h.c.read(root/item['path'])
                self.assertNotIn('profile',observation)
                self.assertEqual(h.collect(root)['processed_this_run'],0)
                self.assertEqual(client.get.call_count,2)

    def test_budget_stop_keeps_a_valid_empty_checkpoint(self):
        from test_catalogue import fixture
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);h.c.write(root/'config/catalogue.json',{'source_url':'https://example.invalid/repos.json','max_bytes':10000})
            response=MagicMock();response.__enter__.return_value=response
            response.geturl.return_value='https://example.invalid/repos.json';response.read.return_value=json.dumps([fixture()]).encode()
            client=MagicMock();client.calls=1;client.get.side_effect=h.BudgetStop()
            with patch.object(h.urllib.request,'urlopen',return_value=response),patch.object(h,'Client',return_value=client):
                result=h.collect(root)
                self.assertTrue(result['budget_checkpoint']);self.assertEqual(h.verify(root)['repositories'],{})


if __name__=='__main__':unittest.main()
