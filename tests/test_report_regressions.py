import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import catalogue as c
import history as h
from test_catalogue import fixture


def candidate(root):
    shutil.copytree(c.ROOT/'config',root/'config');shutil.copyfile(c.ROOT/'pyproject.toml',root/'pyproject.toml')
    rows=[]
    for owner,name,description in [('111Online','nhs111-resources','NHS service resources'),('hmrc','vulnerabilities',''),('Public-Health-Scotland','covid-vulnerability','Community Vulnerability'),('ExampleGov','pending','Map data library'),('ExampleGov','empty','Accessible forms application'),('ExampleGov','unavailable','Java API library')]:
        rows.append({**fixture(),'owner':owner,'name':name,'url':'https://github.com/'+owner+'/'+name,'description':description})
    rows[-1]['language']='Java'
    raw=json.dumps(rows).encode();path='source/snapshots/'+c.digest(raw)+'.json';(root/path).parent.mkdir(parents=True);(root/path).write_bytes(raw)
    receipt={'path':path,'sha256':c.digest(raw),'retrieved_at':'2026-10-29T00:00:00Z'};c.write(root/'source/current.json',receipt)
    profile=h.weekly_profile([{'total':5,'author':{'login':'real-account','type':'User'},'weeks':[{'w':1791676800,'a':8,'d':2,'c':3}]}],receipt['retrieved_at'])
    entries={}
    for identity,state,status in [('111online/nhs111-resources','available',200),('examplegov/pending','pending-provider-statistics',202),('examplegov/empty','empty-or-unavailable',200),('examplegov/unavailable','unavailable-response',404)]:
        observation={'state':state,'http_status':status,'catalogue_source_sha256':'a'*64,'source_url':'https://api.github.com/repos/'+identity+'/stats/contributors','observed_at':receipt['retrieved_at']}
        if state=='available':observation['profile']=profile
        sha=c.digest(observation);op='source/history/observations/'+sha+'.json';c.write(root/op,observation);entries[identity]={'path':op,'sha256':sha,'state':state}
    c.write(root/'source/history/index.json',{'repositories':entries})
    c.build(root,root/'generated',receipt)
    return receipt


class ReportRegressionTests(unittest.TestCase):
    def test_contextual_security_aliases_preserve_token_boundaries(self):
        tax=c.read(c.ROOT/'config/taxonomy.json')
        for name,description,expected in [('vulnerabilities','',True),('dependency-vulnerabilities','dependency scanning',True),('covid-vulnerability','Community Vulnerability',False),('social-vulnerability','Social vulnerability research',False),('covid-vulnerability','CVE security scanner',True)]:
            with self.subTest(name=name,description=description):
                matches=c.classify({**fixture(),'name':name,'description':description},tax)
                self.assertEqual(any(x['id']=='identity-security' for x in matches['capabilities']),expected)
                self.assertEqual(any(x['id']=='security-tool' for x in matches['content_types']),expected)
        tax={'capabilities':[{'id':'ui','label':'UI','terms':['ui']}],'domains':[]}
        self.assertEqual(c.classify({**fixture(),'name':'build-guide-suite','description':''},tax)['capabilities'],[])

    def test_history_states_accounts_and_lossless_rdf(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);candidate(root);records=c.records_from(root/'generated');by_name={r['title'].casefold():r for r in records}
            for name,state in [('pending','pending-provider-statistics'),('empty','empty-or-unavailable'),('unavailable','unavailable-response')]:
                row=by_name['examplegov/'+name]
                self.assertEqual(row['recent_commit_band'],state);self.assertEqual(row['churn_availability'],state)
                self.assertEqual(row['recent_contributors'],[]);self.assertEqual(row['historical_contributors'],[])
                self.assertEqual(row['recent_contributor_facet_values'],[state])
            row=by_name['111online/nhs111-resources'];self.assertEqual(row['history_observation']['catalogue_binding'],'different-or-unrecorded-catalogue-source')
            self.assertEqual(row['recent_contributors'],['real-account'])
            self.assertEqual(row['source_metrics'],{'stargazersCount':0,'forksCount':0,'openIssuesCount':0})
            edges=c.read(root/'generated/data/assertions-000.json.gz');nodes=c.read(root/'generated/semantic/assertions-000.jsonld.gz')['@graph']
            for edge,node in zip(edges,nodes):
                self.assertEqual(node[c.NS+'authority']['@value'],edge['authority'])
                self.assertEqual(node[c.NS+'reviewStatus'],edge['review_status'])
                self.assertEqual(node[c.NS+'derivation'],c.ref(edge['derivation']))
                self.assertEqual(node[c.NS+'rightsRecord']['@value'],edge['rights'])
                self.assertEqual(node[c.NS+'inverseLabel'],edge['inverse_label'])
            vocabulary=c.read(root/'generated/semantic/vocabulary.jsonld.gz')['@graph']
            self.assertTrue(any(node.get(c.NS+'predicate')==c.ref(c.SCHEMA+'about') and node.get(c.NS+'inverseLabel')=='suggested domain of' for node in vocabulary))
            desc=c.read(root/'generated/okf-explorer.json');self.assertIn('1 of 6',desc['history_coverage']['message'])
            self.assertIn(desc['history_coverage']['message'],desc['exploratory_publication']['limitations'])
            definitions=c.read(root/'generated/data/facet-definitions.json')['facets']
            self.assertTrue(any(row['key']=='history_coverage' and '(1/6 available)' in row['label'] and desc['history_coverage']['message'] in row['description'] for row in definitions))

    def test_cli_repeated_filters_count_and_page_the_complete_selection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);candidate(root)
            argv=['catalogue.py','--root',str(root),'search','--language','Python','--language','Java','--archived','false','--limit','2','--offset','2','--json']
            output=io.StringIO()
            with patch.object(sys,'argv',argv),contextlib.redirect_stdout(output):c.main()
            result=json.loads(output.getvalue());self.assertEqual(result['total_matches'],6);self.assertEqual(len(result['results']),2);self.assertEqual(result['offset'],2);self.assertTrue(result['has_more'])
