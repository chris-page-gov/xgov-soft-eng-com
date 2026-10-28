import gzip
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import explorer_projection as p


class ExplorerProjectionTests(unittest.TestCase):
    def test_browser_index_tokenisation_handles_repo_names_and_accents(self):
        self.assertEqual(p.search_tokens('DWP/forms-builder and API café'),{'dwp','forms','builder','api','cafe'})
        self.assertEqual(p.QUERY_POLICY['minimum_should_match']['apply_from_query_tokens'],1)

    def test_compression_is_deterministic_and_retains_the_complete_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'one.json.gz';data={'evidence':[{'source':'public','count':123}],'unicode':'Cymru — iechyd'}
            first=p.write_gzip(path,data);raw=path.read_bytes()
            second=p.write_gzip(path,data)
            self.assertEqual(first,second);self.assertEqual(path.read_bytes(),raw)
            self.assertEqual(p.read(path),data);self.assertEqual(gzip.decompress(raw),p.encoded(data))

    def test_unknown_line_counts_are_not_rendered_as_zero_change(self):
        record={'body':'# Synthetic fixture','history_coverage':'available','metadata_change':'unchanged','metadata_changed_fields':[],'activity':{'historical_reported_commits':10001,'recent_reported_commits':1,'window':{'label':'13 complete Sunday-to-Sunday weeks','start':'2026-07-26T00:00:00Z','end_exclusive':'2026-10-25T00:00:00Z'},'contributors':[{'login':None,'historical_reported_commits':10001,'recent_reported_commits':1}],'line_count_status':'unknown-or-omitted-by-api','annual_totals':[[2026,10001,0,0]],'weekly_totals':[[1791676800,1,0,0]],'source':{'observed_at':'2026-10-28T12:00:00Z','sha256':'a'*64}}}
        body=p.narrative(record)['body']
        self.assertIn('Unmapped account',body);self.assertIn('Unknown | Unknown',body)
        self.assertNotIn('| 2026 | 10,001 | 0 | 0 |',body)


if __name__=='__main__':unittest.main()
