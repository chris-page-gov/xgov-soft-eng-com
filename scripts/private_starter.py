#!/usr/bin/env python3
"""Create a new, offline, metadata-only private OKF starter outside this repo."""
import argparse
import json
from pathlib import Path
import shutil

import catalogue as c

BUILD_SCRIPT='''#!/usr/bin/env python3
"""Offline private metadata builder: reads one admitted inventory, never source code."""
import collections, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
policy=json.loads((ROOT/'okf.private.json').read_text())
expected={'classification':'private','network_access':'prohibited','model_calls':'disabled','publication':'disabled','source_code_ingestion':'disabled','scan_permission':'not-granted'}
if any(policy.get(k)!=v for k,v in expected.items()):raise SystemExit('Defaults changed: stop and obtain a separate reviewed workflow before building.')
raw=(ROOT/'inventory/components.json').read_bytes()
if len(raw)>1048576:raise SystemExit('Inventory exceeds the starter limit of 1 MiB')
rows=json.loads(raw)
if not isinstance(rows,list):raise SystemExit('Inventory must be a JSON array')
allowed={'id','title','type','description','service_area','content_type','owner_team','language','lifecycle','source_ref'}
nodes={};counts={key:collections.Counter() for key in ('service_area','content_type','owner_team','language','lifecycle')}
for row in rows:
    if not isinstance(row,dict) or set(row)-allowed:raise SystemExit('Unsupported inventory fields: use reviewed metadata only')
    for key in ('id','title','type','service_area','content_type'):
        if not isinstance(row.get(key),str) or not row[key].strip():raise SystemExit('Every record needs id, title, type, service_area and content_type')
    if row['id'] in nodes:raise SystemExit('Duplicate component identifier')
    route='components/'+str(len(nodes))+'.md'
    facets={key:row.get(key) or 'unknown' for key in counts}
    for key,value in facets.items():
        if not isinstance(value,str):raise SystemExit('Facet values must be strings')
        counts[key][value]+=1
    nodes[row['id']]={'id':row['id'],'route':route,'type':row['type'],'title':row['title'],'description':row.get('description',''),'body':row.get('description',''),'sensitivity':'private','source_ref':row.get('source_ref',''),'learning_facets':facets,'authority':'manual-inventory-unreviewed'}
out=ROOT/'generated';out.mkdir(exist_ok=True)
bundle={'schema':'okf-explorer-bundle.v0','okf_version':'0.2','meta':{'title':'Private metadata OKF starter','sensitivity':'private','publication':'disabled','consumer_acceptance':'pending'},'nodes':nodes,'edges':[]}
def write(name,value):(out/name).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\\n')
write('okf-bundle.json',bundle)
write('facets.json',{key:[{'value':v,'count':n} for v,n in sorted(values.items())] for key,values in counts.items()})
write('build-receipt.json',{'source_sha256':hashlib.sha256(raw).hexdigest(),'records':len(rows),'classification':'private','network_calls':0,'model_calls':0,'source_code_files_read':0,'scan_started':False,'human_acceptance':'not-established'})
print('Built',len(rows),'manually admitted metadata records locally. Publication and scanning remain disabled.')
'''


def create(destination):
    destination=Path(destination).expanduser().resolve()
    if destination.is_relative_to(c.ROOT):raise ValueError("Choose a new folder outside this public repository")
    if destination.exists():raise ValueError("Destination already exists; the starter never overwrites a project")
    if not destination.parent.is_dir():raise ValueError("Choose an existing parent directory")
    destination.mkdir(mode=0o700)
    try:
        (destination/'inventory').mkdir(mode=0o700)
        policy={'schema':'okf-private-starter.v1','classification':'private','network_access':'prohibited','model_calls':'disabled','publication':'disabled','source_code_ingestion':'disabled','scan_permission':'not-granted','admitted_input':'inventory/components.json','owner_review':'required','consumer_acceptance':'pending'}
        (destination/'okf.private.json').write_text(json.dumps(policy,indent=2)+'\n')
        (destination/'inventory/components.json').write_text('[]\n')
        sample=[{'id':'synthetic-example','title':'Synthetic example component','type':'Component','description':'Fictional metadata for learning only. Replace with approved metadata.','service_area':'example-service','content_type':'library','owner_team':'example-team','language':'Python','lifecycle':'experimental','source_ref':'internal-reference-to-agree'}]
        (destination/'inventory/components.example.json').write_text(json.dumps(sample,indent=2)+'\n')
        (destination/'build.py').write_text(BUILD_SCRIPT)
        (destination/'.gitignore').write_text('generated/\n.consent/\n.env\n.env.*\n*.pem\n*.key\n__pycache__/\n.DS_Store\n')
        (destination/'README.md').write_text('---\nokf_version: "0.2"\n---\n# Private metadata OKF starter\n\nPrivate by default. No Git remote, CI, network, model calls or publication is configured.\n\n1. Agree ownership, purpose, classification and access.\n2. Review inventory/components.example.json: it is synthetic.\n3. Enter a few approved metadata records in inventory/components.json. Do not paste code, credentials, personal data or access-bearing URLs.\n4. Run python build.py locally. Inspect generated/okf-bundle.json and generated/facets.json.\n5. Keep outputs in approved private storage. Evaluate a locally deployed, approved Reader separately.\n\nThe script reads the inventory only. It does not inspect a codebase or run a scanner. Metadata and fingerprints can themselves be sensitive. The controls are a starting workflow, not a DLP system or a substitute for your organisation\'s access controls.\n')
    except BaseException:
        shutil.rmtree(destination)
        raise
    return {'created':str(destination),'classification':'private','network_configured':False,'model_calls_configured':False,'git_initialised':False,'publication_configured':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('destination',type=Path);args=parser.parse_args()
    try:print(json.dumps(create(args.destination),indent=2))
    except (OSError,ValueError) as exc:parser.exit(1,'Private starter stopped: '+str(exc)+'\n')
