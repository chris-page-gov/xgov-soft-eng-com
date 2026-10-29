import datetime as dt
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import history as h


class HistoryTests(unittest.TestCase):
    def test_due_pending_retries_get_a_bounded_share_during_backfill(self):
        due=[(0,'new/'+str(i),{}) for i in range(10)]+[(1,'pending/'+str(i),{}) for i in range(10)]
        selected=h.select_due(due,5)
        self.assertEqual([priority for priority,_,_ in selected].count(1),1)
        self.assertEqual([priority for priority,_,_ in selected].count(0),4)
        self.assertEqual(len({identity for _,identity,_ in selected}),5)
        self.assertEqual(h.select_due(list(reversed(due)),5),selected)

    def test_unused_retry_capacity_returns_to_new_or_refresh_work(self):
        self.assertEqual(len(h.select_due([(0,str(i),{}) for i in range(8)],5)),5)
        due=[(0,'new',{}),(1,'pending',{})]+[(2,str(i),{}) for i in range(8)]
        self.assertEqual([p for p,_,_ in h.select_due(due,5)],[1,0,2,2,2])
        self.assertEqual(len(h.select_due([(1,str(i),{}) for i in range(8)],5)),5)

    def test_a_single_slot_can_retry_pending_and_empty_work_is_safe(self):
        self.assertEqual(h.select_due([(0,'new',{}),(1,'pending',{})],1)[0][0],1)
        self.assertEqual(h.select_due([],500),[])

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
            root=Path(directory);h.c.write(root/'config/catalogue.json',{'source_url':'https://example.invalid/repos.json','max_bytes':10000,'minimum_records':1,'maximum_removal_fraction':0.2})
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
            root=Path(directory);h.c.write(root/'config/catalogue.json',{'source_url':'https://example.invalid/repos.json','max_bytes':10000,'minimum_records':1,'maximum_removal_fraction':0.2})
            response=MagicMock();response.__enter__.return_value=response
            response.geturl.return_value='https://example.invalid/repos.json';response.read.return_value=json.dumps([fixture()]).encode()
            client=MagicMock();client.calls=1;client.get.side_effect=h.BudgetStop()
            with patch.object(h.urllib.request,'urlopen',return_value=response),patch.object(h,'Client',return_value=client):
                result=h.collect(root)
                self.assertTrue(result['budget_checkpoint']);self.assertEqual(h.verify(root)['repositories'],{})

    def test_successful_empty_statistics_keep_a_specific_reason(self):
        from test_catalogue import fixture
        for statistics in (None,[]):
            with self.subTest(statistics=statistics),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);h.c.write(root/'config/catalogue.json',{'source_url':'https://example.invalid/repos.json','max_bytes':10000,'minimum_records':1,'maximum_removal_fraction':0.2})
                response=MagicMock();response.__enter__.return_value=response;response.geturl.return_value='https://example.invalid/repos.json';response.read.return_value=json.dumps([fixture()]).encode()
                client=MagicMock();client.calls=2;client.get.side_effect=[(200,{'private':False,'full_name':'ExampleGov/accessible-forms','default_branch':'main'},'a'*64),(200,statistics,'b'*64)]
                with patch.object(h.urllib.request,'urlopen',return_value=response),patch.object(h,'Client',return_value=client):
                    result=h.collect(root);self.assertEqual(result['coverage'],{'empty-or-unavailable':1})
                    item=h.load_index(root)['repositories']['examplegov/accessible-forms'];observation=h.c.read(root/item['path'])
                    self.assertEqual(observation['http_status'],200);self.assertEqual(observation['reason_code'],'empty-successful-response');self.assertNotIn('profile',observation)

    def test_small_or_mass_removal_feed_cannot_replace_checkpoint(self):
        from test_catalogue import fixture
        for minimum in (1,2):
            with self.subTest(minimum=minimum),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);h.c.write(root/'config/catalogue.json',{'source_url':'https://example.invalid/repos.json','max_bytes':10000,'minimum_records':minimum,'maximum_removal_fraction':0.2})
                h.c.write(root/'source/history/index.json',{'catalogue_records':2000,'repositories':{}})
                previous=(root/'source/history/index.json').read_bytes()
                response=MagicMock();response.__enter__.return_value=response
                response.geturl.return_value='https://example.invalid/repos.json';response.read.return_value=json.dumps([fixture()]).encode()
                with patch.object(h.urllib.request,'urlopen',return_value=response),patch.object(h,'Client') as client:
                    with self.assertRaisesRegex(ValueError,'retained'):h.collect(root)
                    client.assert_not_called()
                self.assertEqual((root/'source/history/index.json').read_bytes(),previous)

    def test_contribution_count_and_provenance_survive_both_projections(self):
        from test_catalogue import fixture
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);shutil.copytree(h.c.ROOT/'config',root/'config')
            shutil.copyfile(h.c.ROOT/'pyproject.toml',root/'pyproject.toml')
            rows=[{**fixture(),'description':'Health service accessible application'}, {**fixture(),'name':'geospatial-library','url':'https://github.com/ExampleGov/geospatial-library','description':'Map geometry data library API'}]
            raw=json.dumps(rows).encode();source_path='source/snapshots/'+h.c.digest(raw)+'.json';(root/source_path).parent.mkdir(parents=True);(root/source_path).write_bytes(raw)
            receipt={'path':source_path,'sha256':h.c.digest(raw),'retrieved_at':'2026-10-28T12:00:00Z'}
            week=int(dt.datetime(2026,10,18,tzinfo=dt.timezone.utc).timestamp())
            profile=h.weekly_profile([{'total':3,'author':{'login':'ExampleUser','type':'User'},'weeks':[{'w':week,'a':2,'d':1,'c':3}]}],receipt['retrieved_at'])
            observation={'profile':profile,'source_url':'https://api.github.com/repos/examplegov/accessible-forms/stats/contributors','observed_at':receipt['retrieved_at']}
            checksum=h.c.digest(observation);path='source/history/observations/'+checksum+'.json';h.c.write(root/path,observation)
            h.c.write(root/'source/history/index.json',{'repositories':{'examplegov/accessible-forms':{'path':path,'sha256':checksum,'state':'available'}}})
            anonymous=h.weekly_profile([{'total':2,'author':None,'weeks':[{'w':week,'a':1,'d':0,'c':2}]}],receipt['retrieved_at'])
            anonymous_observation={**observation,'profile':anonymous};anonymous_hash=h.c.digest(anonymous_observation);anonymous_path='source/history/observations/'+anonymous_hash+'.json';h.c.write(root/anonymous_path,anonymous_observation)
            index=h.load_index(root);index['repositories']['examplegov/geospatial-library']={'path':anonymous_path,'sha256':anonymous_hash,'state':'available'};h.c.write(root/'source/history/index.json',index)
            h.c.build(root,root/'generated',receipt)
            anonymous_record=next(row for row in h.c.records_from(root/'generated') if row['title'].endswith('geospatial-library'))
            self.assertEqual(anonymous_record['recent_contributors'],[])
            self.assertEqual(anonymous_record['recent_contributor_facet_values'],['no-mapped-account'])
            self.assertEqual(anonymous_record['activity']['recent_reported_commits'],2)
            manifest=h.c.read(root/'generated/data/manifest.json')
            assertions=[row for path in manifest['chunks']['relationships'] for row in h.c.read(root/'generated'/path)]
            self.assertTrue(h.c.explorer_projection.validate(root/'generated',h.c.records_from(root/'generated'),assertions))
            descriptor=h.c.read(root/'generated/okf-explorer.json')
            labels=h.c.read(root/'generated'/descriptor['entrypoints']['endpoint_labels']['path'])
            self.assertIn('publisher/examplegov',{row['route'] for row in labels['entries']})
            self.assertEqual(descriptor['snapshot_id'],h.c.read(root/'generated/data/search/manifest.json')['snapshot'])
            recent=next(row for row in assertions if row['kind']=='recent_contributor')
            self.assertEqual(recent['measurement']['reported_commits'],3)
            self.assertEqual(recent['evidence'][0]['source_sha256'],checksum)
            shard=h.c.read(root/'generated/semantic/assertions-000.jsonld.gz')['@graph']
            rdf=next(node for node in shard if node['@id']==recent['id'])
            self.assertEqual(rdf[h.c.PROV+'wasDerivedFrom'],h.c.ref(h.c.NS+'snapshot:'+checksum))
            self.assertEqual(rdf[h.c.NS+'reportedCommitCount'],3)
            search=h.c.read(root/'generated/data/search/manifest.json');search.pop('snapshot');h.c.write(root/'generated/data/search/manifest.json',search)
            with self.assertRaisesRegex(ValueError,'snapshot mismatch'):h.c.explorer_projection.validate(root/'generated',h.c.records_from(root/'generated'),assertions)


if __name__=='__main__':unittest.main()
