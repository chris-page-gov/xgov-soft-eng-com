#!/usr/bin/env python3
"""Independent, bounded offline verification of one frozen OKF+ data archive."""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tarfile

PREFIX='xgov-okf/'
MAX_BYTES=2*1024**3
MAX_FILE=256*1024**2
MAX_FILES=100000
NS='urn:okf:xgov:'
RDF='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS='http://www.w3.org/2000/01/rdf-schema#'
CASE_IDS=['archive-membership-hashes','manifest-identities','complete-record-inventory','facet-postings-counts','python-sbom-intersection','runtime-rdf-parity','history-states-and-accounts','history-measure-reconciliation','security-classification-regressions','targeted-discovery-and-inverse-adjacency']


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n'


def safe(name):
    parts=name.split('/')
    return name.startswith(PREFIX) and '\\' not in name and all(p not in ('','.','..') for p in parts) and not any(p.casefold() in ('.consent','.sbom-pilot','.git','.venv','__pycache__','.ds_store') for p in parts)


def read_archive(path):
    path=Path(path)
    if path.stat().st_size>MAX_BYTES:raise ValueError('Archive exceeds byte limit')
    data={};total=0
    with tarfile.open(path,'r|gz') as archive:
        for member in archive:
            if len(data)>=MAX_FILES or not safe(member.name) or not member.isfile():raise ValueError('Unsafe archive member: '+member.name)
            if member.name in data:raise ValueError('Duplicate archive member: '+member.name)
            total+=member.size
            if not 0<=member.size<=MAX_FILE or total>MAX_BYTES:raise ValueError('Archive decompressed byte limit exceeded')
            stream=archive.extractfile(member);raw=stream.read(member.size+1)
            if len(raw)!=member.size:raise ValueError('Archive member size mismatch')
            data[member.name]=raw
    return data


def verify(data,archive_hash,archive_bytes,checksums=None):
    def document(path):
        raw=data[PREFIX+path]
        if path.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as source:raw=source.read(MAX_FILE+1)
            if len(raw)>MAX_FILE:raise ValueError('JSON decompression byte limit exceeded')
        return json.loads(raw)
    def generated(path):return document('generated/'+path)
    errors=[];checks=[];untested=[]
    def require(condition,message):
        if not condition:raise ValueError(message)
    m=document('generated/build-manifest.json');source=m['source']
    expected={PREFIX+p:h for p,h in m['controlled_inputs'].items()}
    expected.update({PREFIX+'generated/'+p:h for p,h in m['outputs'].items()})
    expected[PREFIX+'generated/build-manifest.json']=digest(data[PREFIX+'generated/build-manifest.json'])
    expected[PREFIX+'source/current.json']=digest(encoded(source))
    expected[PREFIX+source['path']]=source['sha256']
    for row in [*source.get('supplements',{}).values(),*m.get('history_sources',[])]:expected[PREFIX+row['path']]=row['sha256']
    if source.get('baseline_summary'):
        row=source['baseline_summary'];expected[PREFIX+row['path']]=row['sha256']
    if source.get('baseline_path'):expected[PREFIX+source['baseline_path']]=m['baseline_sha256']
    require(set(expected)==set(data),'Archive membership differs from declared source/input/output boundaries')
    require(all(digest(data[name])==sha for name,sha in expected.items()),'A declared archive member checksum differs')
    checks.append(CASE_IDS[0])
    checksum_status='not_checked'
    if checksums:
        rows=[line.split() for line in Path(checksums).read_text().splitlines() if line.strip()]
        matches=[row for row in rows if len(row)==2 and row[1]=='xgov-okf.tar.gz']
        require(len(matches)==1 and matches[0][0]==archive_hash,'External SHA256SUMS archive checksum differs')
        checksum_status='checked'
    descriptor=generated('okf-explorer.json');dm=generated('data/manifest.json');sm=generated('semantic/manifest.json')
    require(descriptor['snapshot_id']==m['build_id']==dm['snapshot']==sm['build_id'],'Complete-bundle build identities disagree')
    require(sm['snapshot']==sm['source_snapshot_iri']==NS+'snapshot:'+source['sha256'],'Source snapshot identity differs')
    for shard in [*sm['shards'],*[row for rows in dm['shards'].values() for row in rows]]:
        raw=data[PREFIX+'generated/'+shard['path']]
        require(digest(raw)==shard['sha256'] and len(raw)==shard['bytes'],'Shard integrity differs: '+shard['path'])
    checks.append(CASE_IDS[1])
    records=[row for path in dm['chunks']['datasets'] for row in generated(path)]
    require(len(records)==descriptor['counts']['records'],'Descriptor record count differs')
    require(len({row['id'] for row in records})==len(records),'Duplicate record identities')
    feed=document(source['path']);feed_index={row['url'].casefold():row for row in feed}
    require(len(feed_index)==len(records),'Runtime records differ from complete source inventory')
    for record in records:
        original=feed_index[record['url'].casefold()]
        require(record['source_metrics']=={key:original[key] for key in ('stargazersCount','forksCount','openIssuesCount')},'Runtime source metrics differ')
    checks.append(CASE_IDS[2])
    specs=generated('data/facet-definitions.json')['facets'];facets=generated('data/facets.json');search=generated('data/search/manifest.json');indexes={}
    for spec in specs:
        wanted=collections.defaultdict(list)
        for ordinal,record in enumerate(records):
            raw=record.get(spec['field']);values=raw if isinstance(raw,list) else [raw]
            if raw is None or raw==[] or raw=='':values=[spec['missing_value']]
            for value in set(str(v).lower() if isinstance(v,bool) else str(v) for v in values):wanted[value].append(ordinal)
        postings=generated(search['entrypoints']['filter_postings'][spec['key']])['values']
        require(dict(wanted)==postings,'Facet postings disagree with complete records: '+spec['key'])
        require({k:len(v) for k,v in wanted.items()}=={r['value']:r['count'] for r in facets[spec['key']]},'Facet counts disagree: '+spec['key'])
        indexes[spec['key']]=postings
    checks.append(CASE_IDS[3])
    python_sbom=sum(row['language']=='Python' and row['sbom']=='present' for row in records)
    require(python_sbom==len(set(indexes['language'].get('Python',[]))&set(indexes['sbom'].get('present',[]))),'Python/SBOM intersection differs')
    checks.append(CASE_IDS[4])
    assertion_ids=set();assertion_count=0
    for path in dm['chunks']['relationships']:
        runtime=generated(path);semantic=generated(path.replace('data/assertions-','semantic/assertions-').replace('.json','.jsonld'))['@graph']
        require(len(runtime)==len(semantic),'RDF assertion count differs')
        for row,node in zip(runtime,semantic):
            require(row['id'] not in assertion_ids,'Duplicate assertion identifier');assertion_ids.add(row['id']);assertion_count+=1
            fields={'@id':row['id'],RDF+'subject':{'@id':row['source_iri']},RDF+'predicate':{'@id':row['predicate']},RDF+'object':{'@id':row['target_iri']},RDFS+'label':row['label']}
            for target,key in [('inverseLabel','inverse_label'),('relationshipKind','kind'),('sourceRoute','source'),('targetRoute','target'),('assertionStatus','assertion_status'),('assertionScope','assertion_scope'),('observedAt','observed_at'),('reviewStatus','review_status')]:fields[NS+target]=row[key]
            fields[NS+'derivation']={'@id':row['derivation']}
            for target,key in [('authority','authority'),('evidence','evidence'),('rightsRecord','rights'),('measurement','measurement')]:
                if key in row:fields[NS+target]={'@value':row[key],'@type':RDF+'JSON'}
            require(all(node.get(k)==v for k,v in fields.items()),'Runtime/RDF metadata differs: '+row['id'])
    checks.append(CASE_IDS[5])
    states=collections.Counter();examples={};available=0
    for record in records:
        state=record['history_coverage'];states[state]+=1;activity=record.get('activity');observation=record.get('history_observation')
        if not activity:
            require(record['recent_contributors']==[] and record['historical_contributors']==[],'Unavailable history has synthetic account names')
            require(record['recent_commit_band']==record['churn_availability']==state,'Unknown activity state collapsed')
            continue
        require(state=='available' and observation,'Activity lacks available observation')
        profile=document(observation['path'])['profile'];available+=1
        for key,measure in [('historical_contributors','historical_reported_commits'),('recent_contributors','recent_reported_commits')]:
            wanted=[r['login'] for r in profile['contributors'] if r.get('login') and r[measure]]
            require(record[key]==wanted,'Account list differs from captured profile')
        window=profile['window'];start=dt.datetime.fromisoformat(window['start'].replace('Z','+00:00')).timestamp();end=dt.datetime.fromisoformat(window['end_exclusive'].replace('Z','+00:00')).timestamp()
        weeks=[w for actor in profile['contributors'] for w in actor['weeks'] if start<=w[0]<end]
        historic=sum(actor['historical_reported_commits'] for actor in profile['contributors']);recent=sum(w[1] for w in weeks);adds=sum(w[2] for w in weeks);deletes=sum(w[3] for w in weeks)
        require(historic==activity['historical_reported_commits']==profile['historical_reported_commits'],'Historical commit sum differs')
        require(recent==activity['recent_reported_commits']==profile['recent_reported_commits'],'Recent commit sum differs')
        if profile['line_count_status']!='unknown-or-omitted-by-api':require(adds+deletes==activity['recent_reported_line_changes'],'Recent line-change sum differs')
        if record['title'].casefold()=='111online/nhs111-resources':examples[record['title']]={'historical_commits':historic,'recent_commits':recent,'additions':adds,'deletions':deletes,'active_weeks':len({w[0] for w in weeks if w[1]}),'observation_sha256':observation['sha256'],'window':window}
    require(dict(states)==descriptor['history_coverage']['counts'],'Coverage banner counts differ')
    checks.extend(CASE_IDS[6:8])
    titles={r['title'].casefold():r for r in records}
    regressions={}
    for name,expected_security in [('public-health-scotland/covid-vulnerability',False),('hmrc/vulnerabilities',True)]:
        if name in titles:
            row=titles[name];actual='identity-security' in row['capabilities'] and 'security-tool' in row['content_types'];require(actual==expected_security,'Security classifier regression: '+name);regressions[name]=actual
    if len(regressions)==2:checks.append(CASE_IDS[8])
    else:untested.append(CASE_IDS[8])
    target=titles.get('111online/nhs111-resources');adjacency_count=None
    if target:
        def bucket(route):
            value=2166136261
            for char in route:value=((value^ord(char))*16777619)&0xffffffff
            return f'{value:08x}'[:2]
        locator=generated('data/record-locator.json');adjacency=generated('data/adjacency.json')
        for binding in [*locator['buckets'].values(),*locator['record_chunks'],*adjacency['buckets'].values()]:
            raw=data[PREFIX+'generated/'+binding['path']]
            require(digest(raw)==binding['sha256'] and len(raw)==binding['bytes'],'Locator or adjacency binding differs')
        slot=generated(locator['buckets'][bucket(target['route'])]['path'])[target['route']]
        located=generated(locator['record_chunks'][slot[0]]['path'])[slot[1]]
        require(located['id']==target['id'],'Exact repository locator points to another record')
        rows=generated(adjacency['buckets'][bucket(target['route'])]['path'])[target['route']]
        adjacency_count=len(rows)
        require(adjacency_count>0,'Targeted repository adjacency is missing')
        for row in rows:
            inverse=generated(adjacency['buckets'][bucket(row['target'])]['path'])[row['target']]
            require(any(item==row for item in inverse),'Inverse adjacency changed or omitted the original assertion')
        checks.append(CASE_IDS[9])
    else:untested.append(CASE_IDS[9])
    return {'schema':'xgov-ai-evaluation-result.v1','status':'passed','archive_sha256':archive_hash,'archive_bytes':archive_bytes,'build_id':m['build_id'],'source_sha256':source['sha256'],'controlled_input_count':len(m['controlled_inputs']),'output_count':len(m['outputs']),'history_source_count':len(m.get('history_sources',[])),'archive_member_count':len(data),'checksum_status':checksum_status,'checks':checks,'untested':untested+['live-http','browser-ui','classification-accuracy-beyond-declared-regressions'],'facts':{'catalogue_records':len(records),'facet_values':sum(len(v) for v in facets.values()),'python_sbom_total':python_sbom,'history_state_counts':dict(sorted(states.items())),'available_profiles_checked':available,'rdf_assertions_checked':assertion_count,'classification_regressions':regressions,'exact_repository':target['url'] if target else None,'target_adjacency_count':adjacency_count,'history_examples':examples},'errors':errors}


def run(archive,checksums=None,pack_manifest=None):
    archive=Path(archive)
    archive_bytes=archive.stat().st_size
    if archive_bytes>MAX_BYTES:raise ValueError('Archive exceeds byte limit')
    value=hashlib.sha256()
    with archive.open('rb') as stream:
        while chunk:=stream.read(1024*1024):value.update(chunk)
    archive_hash=value.hexdigest()
    if pack_manifest:
        pin=json.loads(Path(pack_manifest).read_text())
        if pin['archive_sha256']!=archive_hash or pin['archive_bytes']!=archive_bytes:raise ValueError('Archive differs from the paired test pack')
    result=verify(read_archive(archive),archive_hash,archive_bytes,checksums)
    if pack_manifest and (pin['build_id']!=result['build_id'] or pin['source_sha256']!=result['source_sha256']):raise ValueError('Test-pack identities differ from archive')
    result['pin_status']='checked' if pack_manifest else 'not_supplied'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',required=True);parser.add_argument('--output',required=True);parser.add_argument('--checksums');parser.add_argument('--pack-manifest',default=str(Path(__file__).with_name('manifest.json')) if Path(__file__).with_name('manifest.json').exists() else None)
    args=parser.parse_args()
    try:result=run(args.archive,args.checksums,args.pack_manifest)
    except (ValueError,KeyError,OSError,TypeError,tarfile.TarError) as error:result={'schema':'xgov-ai-evaluation-result.v1','status':'failed','errors':[str(error)]}
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='facts'},sort_keys=True))
    return 0 if result['status']=='passed' else 1


if __name__=='__main__':sys.exit(main())
