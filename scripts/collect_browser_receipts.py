#!/usr/bin/env python3
"""Validate CLI browser results against an immutable released build manifest."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DESCRIPTOR='https://chris-page-gov.github.io/xgov-soft-eng-com/okf-explorer.json'


def expected_checks():
    facets=json.loads((ROOT/'config/facets.json').read_text())['facets']
    return {
        'facets':{'facet-'+row['key'] for row in facets}|{'hyphenated-repository-search','zero-result-search'},
        'combinations':{'or-within-facet','and-across-facets','unknown-fork-is-separate','high-cardinality-search-and-paging','available-history-filter'},
        'semantics-history':{'history-coverage-notice','history-state-facet-labels','history-counts-period-tables-and-provenance','semantic-assertion-inverse-measurement-and-source','contributor-target-and-inverse-source-navigation','missing-history-is-not-zero','narrow-viewport-navigation-and-reading','repository-deep-link-reload'},
    }


def collect(manifest_path,logs,descriptor_url=DESCRIPTOR):
    manifest_path,logs=Path(manifest_path),Path(logs)
    manifest=json.loads(manifest_path.read_text())
    quality_raw=(manifest_path.parent/'quality.json').read_bytes()
    if hashlib.sha256(quality_raw).hexdigest()!=manifest['outputs']['quality.json']:
        raise ValueError('Released quality metadata checksum differs')
    records=json.loads(quality_raw)['counts']['records']
    receipts={}
    for suite,expected in expected_checks().items():
        text=(logs/(suite+'.txt')).read_text()
        if '### Error' in text or text.count('### Result\n')!=1:
            raise ValueError(suite+': CLI did not return exactly one successful result')
        receipt=json.JSONDecoder().raw_decode(text.split('### Result\n',1)[1])[0]
        if receipt.get('schema')!='xgov-browser-acceptance.v1' or receipt.get('status')!='passed':
            detail=str(receipt.get('failure','browser acceptance failed'))[:2000]
            raise ValueError(suite+': '+detail)
        if receipt.get('descriptor_url')!=descriptor_url or receipt.get('snapshot_id')!=manifest['build_id'] or receipt.get('descriptor_sha256')!=manifest['outputs']['okf-explorer.json'] or receipt.get('records')!=records:
            raise ValueError(suite+': browser identity differs from the released candidate')
        checks=receipt.get('checks',[]);ids=[row.get('id') for row in checks]
        if len(ids)!=len(set(ids)) or set(ids)!=expected or any(row.get('passed') is not True for row in checks):
            raise ValueError(suite+': required browser checks are missing, duplicated or failed')
        if any(type(receipt.get(key)) is not list or receipt[key] for key in ('console_errors','page_errors','failed_requests')):
            raise ValueError(suite+': browser errors or failed requests occurred')
        if not re.fullmatch('[0-9a-f]{40}',str(receipt.get('consumer_commit',''))) or not re.fullmatch('[0-9a-f]{64}',str(receipt.get('consumer_app_tree_sha256',''))) or not isinstance(receipt.get('browser'),str) or not receipt['browser']:
            raise ValueError(suite+': consumer or browser identity is incomplete')
        receipts[suite]=receipt
    consumers={(r['consumer_commit'],r['consumer_app_tree_sha256']) for r in receipts.values()}
    if len(consumers)!=1:raise ValueError('Consumer changed between browser suites')
    consumer_commit,app_tree=next(iter(consumers))
    return {'schema':'xgov-browser-verification.v1','status':'passed','build_id':manifest['build_id'],'descriptor_sha256':manifest['outputs']['okf-explorer.json'],'records':records,'consumer_commit':consumer_commit,'consumer_app_tree_sha256':app_tree,'checks':sum(len(r['checks']) for r in receipts.values()),'suites':receipts}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--logs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:result=collect(args.manifest,args.logs)
    except (ValueError,KeyError,OSError,TypeError) as error:
        result={'schema':'xgov-browser-verification.v1','status':'failed','error':'Browser verification failed: '+str(error)}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='suites'},sort_keys=True))
    if result['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
