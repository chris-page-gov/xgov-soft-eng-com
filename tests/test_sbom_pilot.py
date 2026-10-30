"""Synthetic SBOMs, fake tooling bytes and mocked HTTP/process boundaries only."""
import copy
import datetime as dt
import gzip
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch,Mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import catalogue as c
import permissions
import sbom_pilot as p
import archive
import pages
import verify_bundle
import check_release_hygiene as hygiene

AT=dt.datetime(2026,10,30,12,tzinfo=dt.timezone.utc)


def entry(identifier='synthetic'):
    return {'id':identifier,'repository':'example/synthetic','url':'https://sbom.example.org/'+identifier+'.json',
            'publication':{'kind':'published-document','evidence_url':'https://sbom.example.org/index.json'},
            'access_reuse':{'status':'documented','licence':'CC0-1.0','evidence_url':'https://sbom.example.org/terms','basis':'Synthetic public metadata fixture; not owner approval.'}}


def manifest(*rows):return {'schema':'xgov-public-sbom-pilot.v1','mode':p.MODE,'inputs':list(rows or [entry()])}


def sbom():
    return {'spdxVersion':'SPDX-2.3','dataLicense':'CC0-1.0','creationInfo':{'created':'2026-10-29T00:00:00Z'},
            'packages':[{'SPDXID':'SPDXRef-one','name':'example-package','versionInfo':'1.2.3',
                         'externalRefs':[{'referenceType':'purl','referenceLocator':'pkg:pypi/example-package@1.2.3'}]}]}


def tooling():
    binary=b'synthetic executable bytes; never executed';db=b'synthetic advisory database';metadata=c.encoded({'source':'synthetic fixture'})
    raw_db=b'synthetic compressed DB fixture';version='0.121.0'
    platforms={k:{'url':f'https://github.com/anchore/grype/releases/download/v{version}/grype_{version}_{k}.tar.gz','sha256':p.sha(b'archive'),'bytes':7,'binary_sha256':p.sha(binary)} for k in ('darwin_arm64','linux_amd64')}
    pins={'schema':'xgov-sbom-toolchain-pins.v1','scanner':{'version':version,'platforms':platforms},
          'database':{'url':'https://grype.anchore.io/databases/v6/vulnerability-db_synthetic.tar.zst','bytes':len(raw_db),'sha256':p.sha(raw_db),'built':'2026-10-30T06:00:00Z','files':{'6/vulnerability.db':p.sha(db),'6/import.json':p.sha(metadata)},'file_bytes':{'6/vulnerability.db':len(db),'6/import.json':len(metadata)}}}
    return pins,binary,raw_db,db,metadata


def install(root,pins=None):
    fixture=tooling();pins=pins or fixture[0];base=p.private_dir(root);folder,binary,db,_=p.tool_paths(base,pins)
    for path,raw in [(binary,fixture[1]),(folder/'database.tar.zst',fixture[2]),(db/'6/vulnerability.db',fixture[3]),(db/'6/import.json',fixture[4])]:p.write_private(path,raw,base)
    os.chmod(binary,0o700)
    return base,folder,binary,db


class FakeFetch:
    def __init__(self,data=None,error=None):self.data=data or c.encoded(sbom());self.error=error;self.requests=0;self.deadline=float('inf')
    def get(self,url,max_bytes,redirect_hosts=()):
        self.requests+=1
        if self.error:raise self.error
        if len(self.data)>max_bytes:raise ValueError('Download size limit')
        return self.data,{'origin':url,'final_url':url,'retrieved_at':'2026-10-30T12:00:00Z','sha256':p.sha(self.data),'bytes':len(self.data),'last_modified':'Fri, 30 Oct 2026 12:00:00 GMT'}


class FakeScanner:
    def __init__(self,result=None,version='0.121.0'):self.calls=[];self.result=result;self.version=version
    def __call__(self,command,env,cwd,seconds,limit,base):
        self.calls.append((command,env,cwd,seconds,limit))
        if 'version' in command:return c.encoded({'version':self.version})
        if self.result is not None:return c.encoded(self.result)
        source=next(x[5:] for x in command if x.startswith('sbom:'));document=json.loads(Path(source).read_text())
        matches=[{'artifact':{'name':r['name'],'version':r['version'],'purl':r['purl']},'vulnerability':{'id':'CVE-2099-0001','namespace':'synthetic:pypi','dataSource':'https://example.org/advisories/CVE-2099-0001','severity':'Unknown','fix':{'versions':['1.2.4'],'state':'fixed'}}} for r in document['components']]
        return c.encoded({'matches':matches})


class PilotTests(unittest.TestCase):
    def root(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup);return Path(temporary.name).resolve()

    def execute(self,root,m=None,pins=None,fetch=None,scanner=None):
        pins=pins or tooling()[0]
        with patch.object(p,'isolated_command',side_effect=lambda command:['synthetic-network-isolation',*command]):
            return p.run(root,m or manifest(),pins,True,fetch or FakeFetch(),scanner or FakeScanner(),AT)

    def report(self,result,name='synthetic'):
        return json.loads((Path(result['private_directory'])/(name+'.json')).read_text())

    def test_dry_run_is_explicit_and_has_no_network_process_or_private_writes(self):
        root=self.root()
        with patch.object(p.subprocess,'Popen',side_effect=AssertionError),patch.object(p.socket,'create_connection',side_effect=AssertionError):
            result=p.run(root,manifest(),tooling()[0])
        self.assertTrue(result['dry_run']);self.assertEqual(result['network_requests'],0);self.assertEqual(result['scanner_invocations'],0)
        self.assertFalse(result['owner_approval_claimed']);self.assertFalse((root/p.PRIVATE).exists())

    def test_wrong_mode_or_inventory_generation_kind_is_rejected(self):
        m=manifest();m['mode']='repository-static-analysis'
        with self.assertRaises(ValueError):p.manifest_plan(m)
        m=manifest();m['inputs'][0]['publication']['kind']='generate-by-running-code'
        with self.assertRaises(ValueError):p.manifest_plan(m)

    def test_explicit_ten_input_limit_and_unique_identifiers(self):
        self.assertEqual(len(p.manifest_plan(manifest(*(entry('input-'+str(n)) for n in range(10))))['inputs']),10)
        for m in (manifest(*(entry('input-'+str(n)) for n in range(11))),manifest(entry(),entry())):
            with self.assertRaises(ValueError):p.manifest_plan(m)

    def test_text_identifiers_cannot_collide_with_control_files_or_json_keys(self):
        for name in ('checkpoint','batch-review'):
            with self.assertRaisesRegex(ValueError,'reserved'):p.manifest_plan(manifest(entry(name)))
        for value in (0,123,None,True,['input'],{'input':1}):
            row=entry();row['id']=value
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,'text input identifiers'):p.manifest_plan(manifest(row))
        self.assertEqual(p.manifest_plan(manifest(entry('123')))['inputs'][0]['id'],'123')

    def test_unknown_repository_is_not_fabricated_for_public_document(self):
        root=self.root();install(root);row=entry();del row['repository']
        result=self.execute(root,manifest(row));self.assertIsNone(self.report(result)['repository_reference'])

    def test_limits_can_only_reduce_governed_caps(self):
        for key,value in [('requests',31),('seconds',901),('document_bytes',0),('other',1)]:
            m=manifest();m['limits']={key:value}
            with self.assertRaises(ValueError):p.manifest_plan(m)

    def test_unclear_and_restricted_are_reviewed_without_tools_or_fetching(self):
        rows=[entry('unclear'),entry('restricted')]
        for row,status in zip(rows,('unclear','restricted')):row['access_reuse']['status']=status
        root=self.root();fetch=FakeFetch();scanner=FakeScanner();result=self.execute(root,manifest(*rows),fetch=fetch,scanner=scanner)
        self.assertEqual(fetch.requests,0);self.assertEqual(scanner.calls,[])
        self.assertEqual({r['status'] for r in result['inputs'].values()},{'review-required'})
        self.assertTrue((Path(result['private_directory'])/'batch-review.md').exists())

    def test_missing_documented_basis_is_not_invented(self):
        row=entry();del row['access_reuse']['basis']
        with self.assertRaises(ValueError):p.manifest_plan(manifest(row))
        self.assertNotIn(p.MODE,permissions.MODES)

    def test_public_data_matching_never_checks_or_fabricates_owner_consent(self):
        root=self.root();install(root)
        with patch.object(permissions,'check',side_effect=AssertionError('Public mode must not call owner approval')):result=self.execute(root)
        report=self.report(result);self.assertFalse(report['owner_approval_claimed']);self.assertEqual(report['mode'],p.MODE)
        self.assertFalse((root/'.consent').exists());self.assertEqual(report['candidate_advisory_matches'][0]['applicability'],'not-assessed')

    def test_full_provenance_and_declared_version_links(self):
        root=self.root();install(root);result=self.execute(root);report=self.report(result);candidate=report['candidate_advisory_matches'][0]
        self.assertEqual(candidate['package']['version'],'1.2.3');self.assertEqual(candidate['sbom_sha256'],report['sbom_sha256'])
        self.assertEqual(candidate['database_sha256'],tooling()[0]['database']['sha256'])
        self.assertEqual(report['retrieval']['sha256'],p.sha(c.encoded(sbom())));self.assertEqual(report['document']['document_date'],'2026-10-29T00:00:00Z')
        self.assertEqual(report['access_reuse']['licence'],'CC0-1.0');self.assertEqual(report['scanner']['binary_sha256'],tooling()[0]['scanner']['platforms'][p.current_platform()]['binary_sha256'])

    def test_scanner_and_database_pins_fail_before_any_input_get(self):
        for which in ('binary','archive','db','extra'):
            with self.subTest(which=which):
                root=self.root();base,folder,binary,db=install(root)
                if which=='binary':binary.write_bytes(b'tampered')
                elif which=='archive':(folder/'database.tar.zst').write_bytes(b'tampered')
                elif which=='db':(db/'6/vulnerability.db').write_bytes(b'tampered')
                else:(db/'extra').write_bytes(b'unknown data')
                fetch=FakeFetch()
                with self.assertRaises(p.PinError):self.execute(root,fetch=fetch)
                self.assertEqual(fetch.requests,0)

    def test_version_mismatch_and_missing_isolation_fail_closed(self):
        root=self.root();install(root);fetch=FakeFetch()
        with self.assertRaises(p.PinError):self.execute(root,fetch=fetch,scanner=FakeScanner(version='0.0.0'))
        self.assertEqual(fetch.requests,0)
        with patch.object(p,'isolated_command',side_effect=ValueError('unavailable')):
            with self.assertRaises(ValueError):p.run(root,manifest(),tooling()[0],True,fetch,FakeScanner())
        self.assertEqual(fetch.requests,0)

    def test_pin_records_are_complete_and_official(self):
        for mutate in (lambda v:v['database'].pop('sha256'),lambda v:v['scanner']['platforms']['darwin_arm64'].update(url='https://example.org/tool'),lambda v:v['database'].update(files={'../db':'0'*64})):
            v=tooling()[0];mutate(v)
            with self.assertRaises((ValueError,KeyError)):p.validate_pins(v)
        p.validate_pins(p.read_json(p.PIN_FILE))

    def test_child_has_no_inherited_secrets_updates_or_network_sources(self):
        root=self.root();install(root);scanner=FakeScanner()
        with patch.dict(os.environ,{'GRYPE_DB_AUTO_UPDATE':'true','HTTP_PROXY':'http://localhost','GITHUB_TOKEN':'synthetic-secret'}):self.execute(root,scanner=scanner)
        for command,env,_,_,_ in scanner.calls:
            self.assertEqual(env['GRYPE_DB_AUTO_UPDATE'],'false');self.assertEqual(env['GRYPE_CHECK_FOR_APP_UPDATE'],'false');self.assertEqual(env['GRYPE_EXTERNAL_SOURCES_ENABLE'],'false')
            self.assertNotIn('GITHUB_TOKEN',env);self.assertNotIn('HTTP_PROXY',env);self.assertEqual(command[0].split('/')[-1],'grype')
        matching=scanner.calls[-1][0];self.assertEqual(sum(s.startswith('sbom:') for s in matching),1)

    def test_missing_versions_ranges_and_unresolved_or_unsupported_identities_are_gaps(self):
        data=sbom();template=data['packages'][0];data['packages']=[]
        for name,version,purl in [('missing',None,'pkg:pypi/a'),('range','^1.0','pkg:npm/a'),('identity','1.2.3',None),('unsupported','1.2.3','pkg:deb/debian/a@1.2.3'),('conflict','1.2.3','pkg:pypi/a@9.9'),('qualifier','1.2.3','pkg:maven/g/a@1.2.3?type=jar')]:
            row=copy.deepcopy(template);row.update(name=name,versionInfo=version,externalRefs=[{'referenceType':'purl','referenceLocator':purl}] if purl else []);data['packages'].append(row)
        inspection=p.inspect_sbom(data,entry(),p.LIMITS,AT)
        self.assertFalse(any(r['eligible'] for r in inspection['packages']))
        self.assertTrue({'missing-or-unresolved-version','unresolved-package-identity','unsupported-ecosystem-by-pilot','conflicting-declared-versions','unsupported-package-qualifiers-by-pilot'}.issubset({r['state'] for r in inspection['gaps']}))

    def test_unresolved_tags_and_wildcards_are_not_exact_versions(self):
        for version in ('unspecified','N/A','next','1.x','[1.2]','>=1.2'):
            data=sbom();data['packages'][0]['versionInfo']=version
            result=p.inspect_sbom(data,entry(),p.LIMITS,AT)
            self.assertFalse(result['packages'][0]['eligible']);self.assertIn('missing-or-unresolved-version',{g['state'] for g in result['gaps']})

    def test_candidate_expansion_limit_is_visible_not_silently_complete(self):
        root=self.root();install(root);data=sbom();data['packages'].append(copy.deepcopy(data['packages'][0]));m=manifest();m['limits']={'candidate_links':1}
        result=self.execute(root,m,fetch=FakeFetch(c.encoded(data)));report=self.report(result)
        self.assertEqual(report['candidate_advisory_matches'],[]);self.assertIn('candidate-report-limit',{g['state'] for g in report['coverage_gaps']})

    def test_completed_cache_tampering_cannot_be_hidden_by_intact_report(self):
        root=self.root();base,_,_,_=install(root);fetch=FakeFetch();self.execute(root,fetch=fetch)
        (base/'cache'/p.sha(c.encoded(entry()))/'body').write_bytes(b'tamper')
        with self.assertRaisesRegex(ValueError,'integrity'):self.execute(root,fetch=fetch)
        self.assertEqual(fetch.requests,1)

    def test_derived_report_size_limit_does_not_write_an_oversized_report(self):
        root=self.root();install(root);m=manifest();m['limits']={'output_bytes':500}
        result=self.execute(root,m,scanner=FakeScanner({'matches':[]}))
        self.assertEqual(result['inputs']['synthetic']['status'],'review-required');self.assertFalse((Path(result['private_directory'])/'synthetic.json').exists())

    def test_external_inventory_references_and_naive_dates_remain_gaps(self):
        data=sbom();data['externalDocumentRefs']=[{'externalDocumentId':'DocumentRef-other','spdxDocument':'https://example.org/other'}];data['creationInfo']['created']='2026-10-29T00:00:00'
        inspection=p.inspect_sbom(data,entry(),p.LIMITS,AT)
        self.assertTrue({'external-document-references-not-resolved','invalid-document-date'}.issubset({g['state'] for g in inspection['gaps']}))

    def test_stale_missing_and_future_dates_and_declared_revisions(self):
        data=sbom();data['creationInfo']['created']='2020-01-01T00:00:00Z'
        self.assertIn('stale-document',{r['state'] for r in p.inspect_sbom(data,entry(),p.LIMITS,AT)['gaps']})
        for value,expected in [(None,'missing-document-date'),('2099-01-01T00:00:00Z','future-document-date'),('wrong','invalid-document-date')]:
            data['creationInfo']['created']=value
            self.assertIn(expected,{r['state'] for r in p.inspect_sbom(data,entry(),p.LIMITS,AT)['gaps']})
        doc={'bomFormat':'CycloneDX','specVersion':'1.5','metadata':{'timestamp':'2026-10-29T00:00:00Z','properties':[{'name':'cdx:git:commit','value':'a'*40}]},'components':[]}
        self.assertEqual(p.inspect_sbom(doc,entry(),p.LIMITS,AT)['source_revision'],'a'*40)

    def test_embedded_licence_conflict_needs_review_without_matching(self):
        root=self.root();install(root);data=sbom();data['dataLicense']='LicenseRef-restricted';scanner=FakeScanner()
        result=self.execute(root,fetch=FakeFetch(c.encoded(data)),scanner=scanner)
        self.assertEqual(result['inputs']['synthetic']['status'],'review-required');self.assertEqual(len(scanner.calls),1)

    def test_build_test_ci_and_unknown_contexts_remain_in_full_view(self):
        root=self.root();install(root);data={'bomFormat':'CycloneDX','specVersion':'1.5','components':[]}
        for index,scope in enumerate(('build','test','ci','runtime','unknown','development')):
            data['components'].append({'bom-ref':str(index),'name':'package-'+str(index),'version':'1.2.3','purl':'pkg:pypi/package-'+str(index)+'@1.2.3','scope':'excluded','properties':[{'name':'dependency:scope','value':scope}]})
        result=self.execute(root,fetch=FakeFetch(c.encoded(data)));report=self.report(result)
        self.assertEqual(len(report['candidate_advisory_matches']),6)
        self.assertEqual(len(report['runtime_view']['candidate_ids']),1);self.assertEqual(len(report['runtime_view']['unknown_context_candidate_ids']),1)
        self.assertEqual({s for v in report['candidate_advisory_matches'] for s in v['package']['declared_contexts']},{'build','test','ci','runtime','unknown','development'})
        self.assertTrue(all(r['declared_requirement']=='excluded' for r in report['declared_packages']))
        document=sbom();document['relationships']=[{'spdxElementId':'SPDXRef-one','relationshipType':'DEV_DEPENDENCY_OF','relatedSpdxElement':'SPDXRef-root'}]
        self.assertEqual(p.inspect_sbom(document,entry(),p.LIMITS,AT)['packages'][0]['declared_contexts'],['development'])

    def test_unreconciled_scanner_version_never_becomes_a_candidate(self):
        root=self.root();install(root);result=self.execute(root,scanner=FakeScanner({'matches':[{'artifact':{'purl':'pkg:pypi/example-package@9.0','version':'9.0'},'vulnerability':{'id':'CVE-2099-0001'}}]}));report=self.report(result)
        self.assertEqual(report['candidate_advisory_matches'],[]);self.assertIn({'state':'unreconciled-scanner-match'},report['coverage_gaps'])

    def test_unsupported_document_is_reported_as_a_gap_without_matching(self):
        root=self.root();install(root);scanner=FakeScanner();result=self.execute(root,fetch=FakeFetch(b'{"bomFormat":"unsupported"}'),scanner=scanner)
        report=self.report(result);self.assertEqual(report['coverage_gaps'][0]['state'],'unsupported-document-format');self.assertFalse(report['matching']['executed']);self.assertEqual(len(scanner.calls),1)

    def test_gzip_api_wrappers_size_and_duplicate_key_boundaries(self):
        raw=c.encoded(sbom());decoded,data=p.decoded_sbom(gzip.compress(raw),100000);self.assertEqual(decoded,raw)
        _,wrapped=p.decoded_sbom(c.encoded({'sbom':sbom()}),100000);self.assertEqual(wrapped,sbom())
        for value,limit in [(gzip.compress(b'x'*10000),50),(b'{"a":1,"a":2}',100),(b'<xml/>',100)]:
            with self.assertRaises(ValueError):p.decoded_sbom(value,limit)

    def test_cached_bytes_and_completed_checkpoints_are_verified_on_resume(self):
        root=self.root();install(root);fetch=FakeFetch();scanner=FakeScanner();result=self.execute(root,fetch=fetch,scanner=scanner)
        self.assertEqual(fetch.requests,1);again=self.execute(root,fetch=fetch,scanner=scanner)
        self.assertEqual(fetch.requests,1);self.assertEqual(len(scanner.calls),2);self.assertEqual(result['run_id'],again['run_id'])
        (Path(result['private_directory'])/'synthetic.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'report integrity'):self.execute(root,fetch=fetch,scanner=scanner)

    def test_changed_pins_or_manifest_get_a_distinct_resume_identity(self):
        root=self.root();install(root);one=self.execute(root)
        m=manifest();m['inputs'][0]['access_reuse']['basis']+=' New review.'
        two=self.execute(root,m);self.assertNotEqual(one['run_id'],two['run_id'])

    def test_tampered_cached_body_is_not_refetched_or_matched(self):
        root=self.root();base,_,_,_=install(root);row=entry();fetch=FakeFetch()
        p.fetch_input(base,row,fetch,p.LIMITS);cache=base/'cache'/p.sha(c.encoded(row));(cache/'body').write_bytes(b'tamper')
        with self.assertRaisesRegex(ValueError,'integrity'):p.fetch_input(base,row,fetch,p.LIMITS)
        self.assertEqual(fetch.requests,1)

    def test_expected_hash_mismatch_is_private_review_and_preserves_retrieval(self):
        root=self.root();base,_,_,_=install(root);row=entry();row['expected_sha256']='0'*64;scanner=FakeScanner();result=self.execute(root,manifest(row),scanner=scanner)
        self.assertEqual(result['inputs']['synthetic']['status'],'review-required');self.assertEqual(len(scanner.calls),1)
        receipt=json.loads((base/'cache'/p.sha(c.encoded(row))/'receipt.json').read_text());self.assertEqual(receipt['sha256'],p.sha(c.encoded(sbom())))

    def test_rate_limit_and_request_budget_stop_and_resume(self):
        for error,status in [(p.Deferred('http-429',3600),'deferred-rate-limit'),(p.BudgetStop('request-limit'),'budget-checkpoint')]:
            with self.subTest(status=status):
                root=self.root();install(root);scanner=FakeScanner();fetch=FakeFetch(error=error)
                result=self.execute(root,manifest(entry(),entry('next')),fetch=fetch,scanner=scanner)
                self.assertEqual(result['inputs']['synthetic']['status'],status);self.assertNotIn('next',result['inputs']);self.assertEqual(fetch.requests,1);self.assertEqual(len(scanner.calls),1)
        root=self.root();fetch=FakeFetch()
        with patch.object(p,'verify_tools',side_effect=p.BudgetStop('total-time-limit')):
            result=self.execute(root,fetch=fetch)
        self.assertEqual(result['stop_reason'],'total-time-limit');self.assertEqual(fetch.requests,0)
        self.assertTrue((Path(result['private_directory'])/'checkpoint.json').is_file())

    def test_private_files_are_restricted_and_symlinks_and_hardlinks_rejected(self):
        root=self.root();base,_,_,_=install(root);result=self.execute(root)
        for f in base.rglob('*'):
            self.assertEqual(f.stat().st_mode&0o077,0,f)
        link=base/'escape';link.symlink_to(root/'outside')
        with self.assertRaises(ValueError):p.write_private(link,b'no',base)
        a=base/'hard-original';a.write_bytes(b'private');os.link(a,base/'hard-copy')
        with self.assertRaises(ValueError):p.write_private(a,b'no',base)

    def test_private_root_link_is_refused(self):
        root=self.root();outside=root/'outside';outside.mkdir();(root/p.PRIVATE).symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError):p.private_dir(root)

    def test_markdown_cannot_embed_untrusted_markup(self):
        root=self.root();install(root);data=sbom();data['packages'][0]['name']='<script>![remote](https://example.org/image)</script>'
        result=self.execute(root,fetch=FakeFetch(c.encoded(data)));text=(Path(result['private_directory'])/'synthetic.md').read_text()
        self.assertNotIn('<script>',text);self.assertNotIn('![remote]',text);self.assertIn('candidate advisory',text)

    def test_scanner_output_size_is_bounded(self):
        root=self.root();install(root);m=manifest();m['limits']={'output_bytes':10}
        result=self.execute(root,m);self.assertEqual(result['inputs']['synthetic']['status'],'review-required')

    def test_mid_batch_pin_failure_stops_before_next_input(self):
        root=self.root();base,_,binary,_=install(root);scanner=FakeScanner()
        def mutate(*args):
            raw=scanner(*args)
            if 'version' not in args[0]:binary.write_bytes(b'tamper')
            return raw
        fetch=FakeFetch()
        with self.assertRaises(p.PinError):self.execute(root,manifest(entry(),entry('next')),fetch=fetch,scanner=mutate)
        self.assertEqual(fetch.requests,1)


class NetworkAndPublicationTests(unittest.TestCase):
    def response(self,status=200,headers=None,body=b'{}'):
        response=Mock(status=status);response.getheaders.return_value=list((headers or {}).items());response.read1.side_effect=[body,b''];return response

    def mock_https(self,fetch,response):
        transport=Mock();context=Mock();context.wrap_socket.return_value=transport
        class Connection:
            def __init__(self,*a,**kw):self.sock=None
            def request(self,*a,**kw):self.connect()
            def getresponse(self):return response
            def close(self):pass
        return (patch.object(fetch,'resolve',return_value='8.8.8.8'),patch.object(p.http.client,'HTTPSConnection',Connection),patch.object(p.socket,'create_connection',return_value=transport),patch.object(p.ssl,'create_default_context',return_value=context))

    def test_mock_http_rate_limit_is_deferred_without_retrying(self):
        fetch=p.Fetcher(p.LIMITS);patches=self.mock_https(fetch,self.response(429,{'Retry-After':'3600'}))
        with patches[0],patches[1],patches[2],patches[3]:
            with self.assertRaises(p.Deferred) as raised:fetch.get('https://sbom.example.org/a',100)
        self.assertEqual(raised.exception.seconds,3600);self.assertEqual(fetch.requests,1)

    def test_mock_http_declared_and_streamed_size_limits(self):
        for headers,body in [({'Content-Length':'10000'},b'{}'),({},b'x'*101)]:
            fetch=p.Fetcher(p.LIMITS);patches=self.mock_https(fetch,self.response(headers=headers,body=body))
            with patches[0],patches[1],patches[2],patches[3]:
                with self.assertRaisesRegex(ValueError,'size'):fetch.get('https://sbom.example.org/a',100)

    def test_mock_https_is_bound_to_vetted_ip_and_original_tls_host(self):
        fetch=p.Fetcher(p.LIMITS);patches=self.mock_https(fetch,self.response(body=b'{"safe":true}'))
        with patches[0],patches[1],patches[2] as connect,patches[3] as context:
            data,_=fetch.get('https://sbom.example.org/a',100)
        self.assertEqual(data,b'{"safe":true}');self.assertEqual(connect.call_args.args[0],('8.8.8.8',443));self.assertEqual(context.return_value.wrap_socket.call_args.kwargs['server_hostname'],'sbom.example.org')

    def test_request_counter_and_wall_deadline_stop_without_new_dns(self):
        fetch=p.Fetcher({**p.LIMITS,'requests':1});fetch.requests=1
        with patch.object(fetch,'resolve',side_effect=AssertionError):
            with self.assertRaises(p.BudgetStop):fetch.once('https://sbom.example.org/a',100)
        fetch.deadline=0
        with self.assertRaises(p.BudgetStop):fetch.get('https://sbom.example.org/a',100)

    def test_signed_official_tool_redirect_is_not_a_sbom_admission_route(self):
        destination='https://release-assets.githubusercontent.com/asset?sig=synthetic&jwt=synthetic'
        for tool_download in (False,True):
            fetch=p.Fetcher(p.LIMITS,tool_download=tool_download)
            with patch.object(fetch,'once',side_effect=[(302,{'location':destination},b''),(200,{},b'tool')]):
                if not tool_download:
                    with self.assertRaises(ValueError):fetch.get('https://github.com/anchore/grype/releases/download/v0.121.0/test',100,['release-assets.githubusercontent.com'])
                else:
                    _,receipt=fetch.get('https://github.com/anchore/grype/releases/download/v0.121.0/test',100,['release-assets.githubusercontent.com']);self.assertNotIn('?',receipt['final_url'])

    def test_unsafe_input_urls_are_rejected_without_requests(self):
        for url in ('file:///tmp/sbom','http://example.org/a','https://user:secret@example.org/a','https://127.0.0.1/a','https://169.254.169.254/a','https://example.org:8443/a','https://example.org/a?token=secret','https://localhost/a','https://example.org/a#fragment'):
            with self.subTest(url=url):
                row=entry();row['url']=url
                with self.assertRaises(ValueError):p.manifest_plan(manifest(row))

    def test_dns_rebinding_private_and_mixed_addresses_are_rejected(self):
        fetch=p.Fetcher(p.LIMITS)
        for addresses in (['127.0.0.1'],['8.8.8.8','10.0.0.1']):
            with patch.object(p.subprocess,'run',return_value=Mock(stdout=json.dumps(addresses).encode())):
                with self.assertRaisesRegex(ValueError,'non-public'):fetch.resolve('sbom.example.org')

    def test_redirects_need_explicit_public_hosts(self):
        fetch=p.Fetcher(p.LIMITS)
        with patch.object(fetch,'once',side_effect=[(302,{'location':'https://cdn.example.org/a'},b''),(200,{},b'{}')]):
            raw,receipt=fetch.get('https://sbom.example.org/a',100,['cdn.example.org']);self.assertEqual(raw,b'{}');self.assertEqual(receipt['final_url'],'https://cdn.example.org/a')
        for destination in ('https://127.0.0.1/a','https://unlisted.example.org/a','http://sbom.example.org/a'):
            with patch.object(fetch,'once',return_value=(302,{'location':destination},b'')):
                with self.assertRaises(ValueError):fetch.get('https://sbom.example.org/a',100)

    def test_os_isolation_has_no_networked_fallback(self):
        with patch.object(p.sys,'platform','darwin'),patch.object(p.Path,'is_file',return_value=True):self.assertIn('(deny network*)',p.isolated_command(['grype'])[2])
        with patch.object(p.sys,'platform','linux'),patch.object(p.Path,'is_file',return_value=True):self.assertIn('--net',p.isolated_command(['grype']))
        with patch.object(p.sys,'platform','unknown'):
            with self.assertRaises(ValueError):p.isolated_command(['grype'])

    def test_all_publication_planes_reject_private_paths_and_case_variants(self):
        for part in ('.sbom-pilot','.SBOM-PILOT'):
            name='xgov-okf/'+part+'/report.json';self.assertFalse(verify_bundle.safe(name))
            with self.assertRaisesRegex(ValueError,'Private'):pages._safe_relative(part+'/report.json')
            with tempfile.TemporaryDirectory() as d:
                path=Path(d)/'bad.tar.gz'
                with tarfile.open(path,'w:gz') as tar:
                    item=tarfile.TarInfo(name);item.size=2;tar.addfile(item,io.BytesIO(b'{}'))
                with self.assertRaisesRegex(ValueError,'Private'):archive.verify_archive(path,{'controlled_inputs':{},'source':{'path':'public.json','sha256':'0'*64},'outputs':{}})
                with self.assertRaisesRegex(ValueError,'Unsafe'):verify_bundle.read_archive(path)

    def test_public_controlled_input_cannot_link_into_private_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.sbom-pilot').mkdir();(root/'.sbom-pilot/report.md').write_text('synthetic private report');(root/'docs').mkdir();(root/'docs/leak.md').symlink_to(root/'.sbom-pilot/report.md')
            with self.assertRaisesRegex(ValueError,'Private'):c.controlled_inputs(root)

    def test_forced_private_git_tracking_is_rejected(self):
        for path in (b'.sbom-pilot/report.json\0',b'.SBOM-PILOT/report.md\0'):
            with patch.object(hygiene.subprocess,'check_output',return_value=path):
                with self.assertRaisesRegex(ValueError,'Private'):hygiene.check_private_tracking(Path('.'))


class PreparationTests(unittest.TestCase):
    def setup_fixture(self,unsafe=False):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);root=Path(t.name).resolve();pins,binary,archive,db,metadata=tooling();stream=io.BytesIO()
        with tarfile.open(fileobj=stream,mode='w:gz') as tar:
            member=tarfile.TarInfo('../grype' if unsafe else 'grype');member.size=len(binary);tar.addfile(member,io.BytesIO(binary))
        scanner_archive=stream.getvalue()
        for value in pins['scanner']['platforms'].values():value.update(sha256=p.sha(scanner_archive),bytes=len(scanner_archive))
        return root,pins,scanner_archive,archive,db,metadata

    def test_prepare_downloads_only_exact_tools_and_imports_offline(self):
        root,pins,scanner_archive,db_archive,db_data,metadata=self.setup_fixture();calls=[]
        class Fetch(FakeFetch):
            def get(self,url,limit,redirect_hosts):
                self.requests+=1;calls.append(url);raw=scanner_archive if url.endswith('.tar.gz') else db_archive
                return raw,{'origin':url,'sha256':p.sha(raw)}
        def executor(command,env,cwd,*args):
            self.assertEqual(command[-3:-1],['db','import']);self.assertEqual(env['GRYPE_DB_AUTO_UPDATE'],'false');self.assertNotIn('sbom:',str(command))
            base=root/p.PRIVATE;db=Path(env['GRYPE_DB_CACHE_DIR'])
            p.write_private(db/'6/vulnerability.db',db_data,base);p.write_private(db/'6/import.json',metadata,base);return b''
        result=p.prepare(root,pins,Fetch(),executor)
        self.assertEqual(result['status'],'prepared');self.assertEqual(result['sbom_requests'],0);self.assertFalse(result['scanner_matches_started']);self.assertEqual(len(calls),2)
        calls.clear();p.prepare(root,pins,Fetch(),executor);self.assertEqual(calls,[])

    def test_prepare_rejects_download_checksum_mismatch_before_import(self):
        root,pins,*_=self.setup_fixture();executor=Mock(side_effect=AssertionError)
        with self.assertRaisesRegex(ValueError,'pin mismatch'):p.prepare(root,pins,FakeFetch(b'wrong bytes'),executor)
        executor.assert_not_called()

    def test_even_digest_matching_archive_cannot_escape_private_membership(self):
        root,pins,raw,database,*_=self.setup_fixture(unsafe=True)
        class Fetch(FakeFetch):
            def get(self,url,*args):
                value=raw if url.endswith('.tar.gz') else database
                return value,{'origin':url,'sha256':p.sha(value)}
        with self.assertRaisesRegex(ValueError,'archive membership'):p.prepare(root,pins,Fetch(),Mock(side_effect=AssertionError))
        self.assertFalse((root/'grype').exists())

    def test_concurrent_operation_is_rejected(self):
        root,*_=self.setup_fixture()
        with p.execution_lock(root):
            with self.assertRaisesRegex(ValueError,'active'):
                with p.execution_lock(root):pass


if __name__=='__main__':unittest.main()
