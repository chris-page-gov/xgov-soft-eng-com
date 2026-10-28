#!/usr/bin/env python3
"""Bounded public GitHub history enrichment, with content-addressed checkpoints."""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

import catalogue as c

WEEK=7*24*3600


class BudgetStop(Exception):pass


class Client:
    def __init__(self,budget,max_seconds):
        self.budget=budget;self.calls=0;self.deadline=time.monotonic()+max_seconds

    def get(self,path):
        if self.calls>=self.budget or time.monotonic()>=self.deadline:raise BudgetStop()
        self.calls+=1
        headers={'Accept':'application/vnd.github+json','User-Agent':'xgov-okf-public-history/1','X-GitHub-Api-Version':'2026-03-10'}
        token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
        if token:headers['Authorization']='Bearer '+token
        request=urllib.request.Request('https://api.github.com'+path,headers=headers)
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):return None
        try:
            response=urllib.request.build_opener(NoRedirect).open(request,timeout=25)
        except urllib.error.HTTPError as exc:
            if exc.code in (403,429):raise BudgetStop() from None
            return exc.code,None,None
        with response:
            remaining=int(response.headers.get('X-RateLimit-Remaining','99999'));limit=int(response.headers.get('X-RateLimit-Limit','99999'))
            if remaining<=max(1,math.ceil(limit*0.1)):raise BudgetStop()
            raw=response.read(8_000_001)
            if len(raw)>8_000_000:return 413,None,None
            data=json.loads(raw) if raw and response.status==200 else None
            time.sleep(0.2)
            return response.status,data,hashlib.sha256(raw).hexdigest()


def weekly_profile(rows,observed_at):
    if not isinstance(rows,list):raise ValueError('Contributor statistics must be an array')
    observed=c.parse_date(observed_at)
    day_start=observed.replace(hour=0,minute=0,second=0,microsecond=0)
    sunday=day_start-dt.timedelta(days=(day_start.weekday()+1)%7)
    window_end=int(sunday.timestamp());window_start=window_end-13*WEEK
    contributors=[];weekly={};has_line_counts=False
    for row in rows:
        if type(row.get('total')) is not int or row['total']<0 or not isinstance(row.get('weeks'),list):raise ValueError('Invalid contributor statistics')
        actor=row.get('author') or {};login=actor.get('login')
        if login is not None and not re.fullmatch(r'[A-Za-z0-9-]+(?:\[bot\])?',login):raise ValueError('Unexpected public contributor identifier')
        sparse=[];recent=0
        for week in row['weeks']:
            if any(type(week.get(k)) is not int or week[k]<0 for k in ('w','a','d','c')):raise ValueError('Invalid weekly history values')
            if week['a'] or week['d']:has_line_counts=True
            if any(week[k] for k in ('a','d','c')):sparse.append([week['w'],week['c'],week['a'],week['d']])
            if window_start<=week['w']<window_end:
                recent+=week['c']
                total=weekly.setdefault(week['w'],[0,0,0]);total[0]+=week['c'];total[1]+=week['a'];total[2]+=week['d']
        contributors.append({'login':login,'account_type':actor.get('type') or 'unmapped','historical_reported_commits':row['total'],'recent_reported_commits':recent,'weeks':sparse})
    contributors.sort(key=lambda r:(-r['historical_reported_commits'],r['login'] or ''))
    recent_commits=sum(v[0] for v in weekly.values())
    return {'window':{'label':'13 complete Sunday-to-Sunday weeks','start':dt.datetime.fromtimestamp(window_start,dt.timezone.utc).isoformat(),'end_exclusive':sunday.isoformat()},'contributors':contributors,'weekly_totals':[[w,*values] for w,values in sorted(weekly.items())],'recent_reported_commits':recent_commits,'historical_reported_commits':sum(r['historical_reported_commits'] for r in contributors),'recent_reported_line_changes':sum(v[1]+v[2] for v in weekly.values()) if has_line_counts else None,'line_count_status':'reported-history-contains-nonzero-counts' if has_line_counts else 'unknown-or-omitted-by-api','limitations':['Default-branch statistics exclude merge commits; contributor statistics also exclude empty commits.','GitHub returns zero additions/deletions for repositories with 10,000 or more commits; all-zero line histories remain unknown.','Commit and line counts are activity measures, not quality, value, security, ownership or maintainership.']}


def load_index(root):
    path=Path(root)/'source/history/index.json'
    return c.read(path) if path.exists() else {'schema':'xgov-history-index.v1','repositories':{}}


def collect(root,limit=500,budget=1800,max_seconds=1500,repositories=None):
    if not 1<=limit<=500 or budget<1 or max_seconds<1:raise ValueError('Use 1 to 500 repositories and positive request/time budgets')
    root=Path(root);cfg=c.read(root/'config/catalogue.json');req=urllib.request.Request(cfg['source_url'],headers={'User-Agent':'xgov-okf-history/1'})
    with urllib.request.urlopen(req,timeout=60) as response:
        raw=response.read(cfg['max_bytes']+1)
        if response.geturl()!=cfg['source_url'] or len(raw)>cfg['max_bytes']:raise ValueError('Unexpected catalogue response')
    rows,_=c.validate_source(json.loads(raw));targets={str(row['owner']+'/'+row['name']).casefold():row for row,_ in rows}
    if len(rows)<cfg['minimum_records']:raise ValueError('Source unexpectedly small; prior history checkpoint retained')
    catalogue_identities=set(targets)
    if repositories:
        wanted={r.casefold() for r in repositories}
        if wanted-set(targets):raise ValueError('History targets must be in the admitted public catalogue')
        targets={k:v for k,v in targets.items() if k in wanted}
    index=load_index(root);now=c.now();entries=index['repositories']
    previous_count=index.get('catalogue_records',0)
    if previous_count and (len(rows)<previous_count*(1-cfg['maximum_removal_fraction']) or len(set(entries)-catalogue_identities)/previous_count>cfg['maximum_removal_fraction']):raise ValueError('Large removal requires curator review; prior history checkpoint retained')
    client=Client(budget,max_seconds)
    for identity in set(entries)-catalogue_identities:del entries[identity]
    due=[]
    for identity,row in targets.items():
        old=entries.get(identity)
        if old and c.parse_date(old['next_check_at'])>c.parse_date(now) and (old['state']!='available' or old.get('source_pushed_at')==row.get('pushedAt')):continue
        due.append((0 if old is None else 1 if old['state']!='available' else 2,identity,row))
    index.update(catalogue_source_sha256=c.digest(raw),catalogue_records=len(rows),updated_at=c.now())
    c.write(root/'source/history/index.json',index)
    completed=0;stopped=False;stop_reason=None
    for _,identity,row in sorted(due)[:limit]:
        try:
            status,metadata,metadata_hash=client.get('/repos/'+identity)
            observation={'repository':identity,'observed_at':c.now(),'source_url':'https://api.github.com/repos/'+identity,'state':'unavailable-or-not-public','metadata_http_status':status,'metadata_response_sha256':metadata_hash,'catalogue_source_sha256':c.digest(raw)}
            if status==200 and metadata.get('private') is False and metadata.get('full_name','').casefold()==identity:
                branch=urllib.parse.quote(metadata['default_branch'],safe='')
                status,statistics,response_hash=client.get('/repos/'+identity+'/stats/contributors')
                head_status,head,_=client.get('/repos/'+identity+'/branches/'+branch) if status==200 and statistics else (None,None,None)
                observation.update(source_url='https://api.github.com/repos/'+identity+'/stats/contributors',default_branch=metadata['default_branch'],is_fork=metadata.get('fork'),parent_repository=metadata.get('parent',{}).get('full_name'),head_sha_observed=head.get('commit',{}).get('sha') if head_status==200 else None,head_binding='Observed near the statistics request; the API is not an atomic snapshot.',response_sha256=response_hash,http_status=status,source_pushed_at=row.get('pushedAt'))
                if status==200 and statistics:
                    observation.update(state='available',profile=weekly_profile(statistics,observation['observed_at']))
                else:observation['state']={202:'pending-provider-statistics',204:'empty-or-unavailable',413:'response-size-limit',422:'provider-limit'}.get(status,'unavailable-response')
            folder=root/'source/history/observations';folder.mkdir(parents=True,exist_ok=True)
            checksum=c.digest(observation);path='source/history/observations/'+checksum+'.json';c.write(root/path,observation)
            retry_hours=168 if observation['state']=='available' else 6 if observation['state']=='pending-provider-statistics' else 24
            entries[identity]={'state':observation['state'],'path':path,'sha256':checksum,'observed_at':observation['observed_at'],'source_pushed_at':row.get('pushedAt'),'next_check_at':(c.parse_date(observation['observed_at'])+dt.timedelta(hours=retry_hours)).isoformat()}
            completed+=1
            index.update(catalogue_source_sha256=c.digest(raw),catalogue_records=len(targets) if not repositories else index.get('catalogue_records',len(rows)),updated_at=c.now())
            c.write(root/'source/history/index.json',index)
        except BudgetStop:
            stopped=True;stop_reason='request-time-or-rate-budget';break
        except (OSError,ValueError,KeyError,TypeError):
            # No response bodies, emails, tokens or raw author metadata enter logs.
            stopped=True;stop_reason='source-error-checkpoint';break
    return {'processed_this_run':completed,'api_requests':client.calls,'budget_checkpoint':stopped,'stop_reason':stop_reason,'coverage':coverage(index),'catalogue_records':index.get('catalogue_records',len(rows))}


def coverage(index):
    result={}
    for item in index['repositories'].values():result[item['state']]=result.get(item['state'],0)+1
    return result


def verify(root,index=None):
    root=Path(root);index=index or load_index(root)
    for item in index['repositories'].values():
        if not re.fullmatch(r'source/history/observations/[0-9a-f]{64}\.json',item['path']):raise ValueError('Unsafe history observation path')
        raw=(root/item['path']).read_bytes()
        if c.digest(raw)!=item['sha256']:raise ValueError('History observation checksum mismatch')
    return index


def pack(root):
    root=Path(root);index=verify(root);paths=['source/history/index.json']+[r['path'] for r in index['repositories'].values()]
    dist=root/'dist';dist.mkdir(exist_ok=True);archive=dist/'history-state.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for path in sorted(set(paths)):tar.add(root/path,arcname=path,recursive=False)
    if archive.stat().st_size>1_000_000_000:raise ValueError('History checkpoint exceeds the 1 GB publication ceiling; shard before continuing')
    c.write(dist/'history-coverage.json',{'catalogue_records':index.get('catalogue_records'),'coverage':coverage(index),'updated_at':index.get('updated_at'),'checkpoint_sha256':c.digest(archive.read_bytes())})
    return str(archive)


def restore(root,archive):
    root=Path(root)
    with tempfile.TemporaryDirectory(dir=root) as directory:
        stage=Path(directory)
        with tarfile.open(archive,'r:gz') as tar:
            for member in tar:
                if not member.isfile() or not (member.name=='source/history/index.json' or re.fullmatch(r'source/history/observations/[0-9a-f]{64}\.json',member.name)):raise ValueError('Unexpected checkpoint member')
                if member.size>8_000_000:raise ValueError('Oversized checkpoint member')
                path=stage/member.name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(tar.extractfile(member).read())
        verify(stage)
        destination=root/'source/history';destination.parent.mkdir(exist_ok=True)
        if destination.exists():shutil.rmtree(destination)
        shutil.move(str(stage/'source/history'),destination)
    return {'restored':True,'coverage':coverage(load_index(root))}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('collect');p.add_argument('--limit',type=int,default=500);p.add_argument('--request-budget',type=int,default=1800);p.add_argument('--max-seconds',type=int,default=1500);p.add_argument('--repository',action='append')
    sub.add_parser('status');sub.add_parser('pack');p=sub.add_parser('restore');p.add_argument('archive',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='collect':result=collect(c.ROOT,args.limit,args.request_budget,args.max_seconds,args.repository)
        elif args.command=='pack':result={'archive':pack(c.ROOT)}
        elif args.command=='restore':result=restore(c.ROOT,args.archive)
        else:
            index=load_index(c.ROOT);result={'coverage':coverage(index),'catalogue_records':index.get('catalogue_records'),'updated_at':index.get('updated_at')}
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as exc:parser.exit(1,'History operation stopped: '+str(exc)+'\n')


if __name__=='__main__':main()
