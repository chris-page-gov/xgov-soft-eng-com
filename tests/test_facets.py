import datetime as dt
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import catalogue as c
import facets as f


class FacetTests(unittest.TestCase):
    def records(self):
        return [{'title':name,'description':'','url':'https://github.com/example/'+name,'domains':domains,'capabilities':['testing'],'content_types':['documentation'],'language':language,'license_id':'unknown','archived':False,'source_rows':[i],'classification_evidence':{}} for i,(name,domains,language) in enumerate([('one',['health','environment'],'Python'),('two',['health'],'Java'),('three',['justice'],'Python')])]

    def test_or_within_and_across_facets_and_empty_result(self):
        rows=self.records();tax={'domains':[],'capabilities':[]}
        selected=c.search(rows,'',tax,{'language':['Python','Java'],'domains':['health']})
        self.assertEqual({r['title'] for r in selected},{'one','two'})
        self.assertEqual([r['title'] for r in c.search(rows,'',tax,{'language':['Java'],'domains':['justice']})],[])

    def test_counts_are_distinct_per_value_and_complete(self):
        specs=[{'key':'domain','field':'domains','missing_value':'unclassified','required_task_dimension':True}]
        values=f.counts(self.records(),specs)
        self.assertEqual({r['value']:r['count'] for r in values['domain']},{'health':2,'environment':1,'justice':1})
        self.assertTrue(f.validate(self.records(),specs,values))
        values['domain'][0]['count']=99
        with self.assertRaises(ValueError):f.validate(self.records(),specs,values)

    def test_source_report_counts_reconcile_and_no_advisory_match_is_invented(self):
        row={'repo':'example/one','packages':3,'resolved':2,'unresolved':1,'runtime':1,'excludedDev':1,'excludedUnresolved':1,'excludedCi':0}
        report={'generatedAt':'2026-10-28T10:00:00Z','perRepo':[row],'totals':{k:row[k] for k in f.METRICS}}
        self.assertEqual(len(f.quality_rows(report)),1)
        record={'language':'Python','license_id':'unknown','description':'','is_fork':None,'timestamp':'2026-01-01T00:00:00Z'}
        values=f.analysis_values(record,row,dt.datetime(2026,10,28,11,tzinfo=dt.timezone.utc),report['generatedAt'])
        self.assertEqual(values['sbom_resolution'],'some-unresolved');self.assertEqual(values['fork_status'],'unknown')
        self.assertNotIn('vulnerability',values)
        report['totals']['packages']=4
        with self.assertRaises(ValueError):f.quality_rows(report)


if __name__=='__main__':unittest.main()
