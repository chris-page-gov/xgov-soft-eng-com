import copy
import datetime as dt
import errno
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location("catalogue",Path(__file__).resolve().parents[1]/"scripts/catalogue.py")
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def fixture():
    return {"owner":"ExampleGov","name":"accessible-forms","description":"Accessible application forms", "url":"https://github.com/ExampleGov/accessible-forms","archived":False,"license":None,"language":"Python","stargazersCount":0,"forksCount":0,"openIssuesCount":0,"createdAt":"2025-01-01T00:00:00Z","updatedAt":"2026-01-01T00:00:00Z","pushedAt":"2026-01-01T00:00:00Z"}


class CatalogueTests(unittest.TestCase):
    def test_identical_duplicates_retain_both_source_rows(self):
        row=fixture();unique,duplicates=c.validate_source([row,copy.deepcopy(row)])
        self.assertEqual(len(unique),1);self.assertEqual(unique[0][1],[0,1]);self.assertEqual(len(duplicates),1)

    def test_conflicting_duplicates_fail_instead_of_selecting_winner(self):
        row=fixture();conflict={**row,"description":"Different evidence"}
        with self.assertRaisesRegex(ValueError,"Conflicting duplicate"):c.validate_source([row,conflict])

    def test_identity_and_unsafe_metadata_fail(self):
        for mutation in ({"url":"https://example.org/x"},{"archived":"false"},{"stargazersCount":True},{"sbom":"sbom/../../secret.json.gz"},{"pushedAt":"2026-01-01T00:00:00"}):
            with self.subTest(mutation=mutation),self.assertRaises((ValueError,TypeError)):c.validate_source([{**fixture(),**mutation}])

    def test_missing_fork_is_unknown_not_false(self):
        unique,_=c.validate_source([fixture()]);self.assertIsNone(unique[0][0].get("isFork"))

    def test_matching_has_token_boundaries_and_multiple_labels(self):
        tax={"domains":[{"id":"maps","label":"Maps","terms":["map"]}],"capabilities":[{"id":"accessibility","label":"Accessibility","terms":["accessible"]}]}
        self.assertEqual(c.classify({**fixture(),"name":"roadmap","description":""},tax)["domains"],[])
        self.assertEqual(c.classify(fixture(),tax)["capabilities"][0]["id"],"accessibility")

    def test_fetch_freshness_is_distinct_from_source_activity(self):
        observed={"retrieved_at":"2026-10-01T10:00:00Z"}
        self.assertFalse(c.stale(observed,48,dt.datetime(2026,10,3,10,tzinfo=dt.timezone.utc)))
        self.assertTrue(c.stale(observed,48,dt.datetime(2026,10,3,11,tzinfo=dt.timezone.utc)))

    def test_bad_candidate_does_not_replace_current_build(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/"generated").mkdir();(root/"generated/sentinel").write_text("previous valid output")
            with patch.object(c,"build",side_effect=ValueError("invalid candidate")):
                with self.assertRaises(ValueError):c.promote(root,{})
            self.assertEqual((root/"generated/sentinel").read_text(),"previous valid output")

    def test_inference_can_be_disabled(self):
        record={"title":"Service","description":"WCAG support","domains":[],"capabilities":["accessibility"],"url":"https://github.com/example/service","language":"Python","license_id":"unknown","archived":False,"source_rows":[0],"classification_evidence":{}}
        taxonomy={"domains":[],"capabilities":[{"id":"accessibility","label":"Accessibility","terms":["accessible","wcag"]}]}
        self.assertEqual(len(c.search([record],"accessible",taxonomy)),1)
        self.assertEqual(c.search([record],"accessible",taxonomy,include_inferred=False),[])
        self.assertEqual(c.search([record],"accessible payments",taxonomy),[])

    def test_finder_metadata_cannot_change_controlled_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/"source/upstream";folder.mkdir(parents=True)
            (folder/"evidence.txt").write_text("Public source evidence")
            before=c.controlled_inputs(root)
            (folder/".DS_Store").write_bytes(b"Finder metadata")
            self.assertEqual(c.controlled_inputs(root),before)

    def test_retired_cleanup_retries_metadata_race_with_other_old_shards_remaining(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'retired';failed=root/'data';failed.mkdir(parents=True)
            (failed/'.DS_Store').write_bytes(b'metadata race')
            (root/'old-shard.json').write_text('retired output')
            original=c.shutil.rmtree
            attempts=[]
            def remove(path):
                attempts.append(path)
                if len(attempts)==1:raise OSError(errno.ENOTEMPTY,'metadata race',str(failed))
                original(path)
            with patch.object(c.shutil,'rmtree',side_effect=remove):c.remove_build_tree(root)
            self.assertFalse(root.exists());self.assertEqual(len(attempts),2)

    def test_retired_cleanup_does_not_hide_non_metadata_content_in_failed_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'retired';root.mkdir();(root/'unexpected').write_text('retain')
            with patch.object(c.shutil,'rmtree',side_effect=OSError(errno.ENOTEMPTY,'unexpected content',str(root))) as remove:
                with self.assertRaises(OSError):c.remove_build_tree(root)
            remove.assert_called_once();self.assertTrue((root/'unexpected').exists())


if __name__=="__main__":unittest.main()
