#!/usr/bin/env python3
"""Bounded public SBOM data analysis. Dry-run by default; private outputs only.

No repository operations, inventories from code, application images, service
testing, maintainer communication or model calls are implemented here.
"""
import argparse
import collections
import contextlib
import datetime as dt
import fcntl
import gzip
import hashlib
import html
import http.client
import io
import ipaddress
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import socket
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse

import catalogue as c
import permissions

MODE=permissions.PUBLIC_DATA_MODE
PRIVATE='.sbom-pilot'
PIN_FILE=c.ROOT/'config/sbom-pilot-pins.json'
LIMITS={'documents':10,'requests':30,'seconds':900,'request_seconds':20,
        'document_bytes':8*1024**2,'decoded_bytes':32*1024**2,
        'packages':50000,'candidates':5000,'candidate_links':200000,
        'scan_seconds':90,'output_bytes':32*1024**2,'stale_days':90}
ECOSYSTEMS={'pypi':'python','npm':'npm','maven':'java-archive','golang':'go-module',
            'cargo':'rust-crate','gem':'gem','composer':'php-composer','nuget':'dotnet'}
HEX=re.compile('[0-9a-f]{64}')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def timestamp(value):
    if not isinstance(value,str):raise ValueError('Timestamp must be a string')
    result=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('Timestamp needs an explicit time zone')
    return result.astimezone(dt.timezone.utc)


def file_sha(path,deadline=None):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024**2):
            if deadline is not None and time.monotonic()>=deadline:raise BudgetStop('total-time-limit')
            value.update(block)
    return value.hexdigest()


def loads(raw):
    def unique(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError('Duplicate JSON key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Non-finite JSON value')))


def read_json(path,limit=1024**2):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>limit:raise ValueError('Invalid or oversized JSON input')
    return loads(path.read_bytes())


def public_url(value,tool_cdn=False):
    if not isinstance(value,str) or len(value)>2048 or re.search(r'[\s\x00-\x1f\x7f\\<>"`]',value):raise ValueError('Unsafe public URL')
    p=urllib.parse.urlsplit(value)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.fragment or p.port not in (None,443):raise ValueError('Only credential-free HTTPS on port 443 is supported')
    host=p.hostname.encode('idna').decode().lower()
    if host=='localhost' or host.endswith(('.localhost','.local','.internal')):raise ValueError('Non-public host')
    try:
        if not ipaddress.ip_address(host).is_global:raise ValueError('Non-public address')
    except ValueError as exc:
        if str(exc)=='Non-public address':raise
    for key,_ in urllib.parse.parse_qsl(p.query,keep_blank_values=True):
        if key not in ('ref','format','download') and not (tool_cdn and host in ('release-assets.githubusercontent.com','objects.githubusercontent.com')):raise ValueError('Access-bearing or unsupported URL query')
    if re.search('%(?![0-9a-fA-F]{2})',value):raise ValueError('Malformed URL escape')
    return value


def private_dir(root):
    root=Path(root).absolute()
    if root.is_symlink() or root.resolve()!=root:raise ValueError('Workspace must not traverse symbolic links')
    base=root/PRIVATE
    secure_path(base,root,True)
    return base


def secure_path(path,base,directory=False):
    path,base=Path(path).absolute(),Path(base).absolute()
    if not path.is_relative_to(base):raise ValueError('Private path escapes its workspace')
    for part in [base,*list(path.relative_to(base).parents)[::-1]]:
        check=part if part.is_absolute() else base/part
        if check.is_symlink():raise ValueError('Private path must not traverse symbolic links')
    current=base
    for part in path.relative_to(base).parts:
        current=current/part
        if current.is_symlink():raise ValueError('Private path must not traverse symbolic links')
        if current!=path or directory:
            current.mkdir(mode=0o700,exist_ok=True);os.chmod(current,0o700)
    if path.exists() and not directory and not path.is_file():raise ValueError('Private output must be a regular file')
    if path.is_file():
        if path.stat().st_nlink!=1:raise ValueError('Private files must not have hard links')
        os.chmod(path,0o600)
    return path


def write_private(path,value,base):
    path=secure_path(path,base)
    raw=value if isinstance(value,bytes) else value.encode() if isinstance(value,str) else c.encoded(value)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
        temporary=Path(stream.name);stream.write(raw)
    os.chmod(temporary,0o600);os.replace(temporary,path)


@contextlib.contextmanager
def execution_lock(root):
    base=private_dir(root);path=secure_path(base/'runner.lock',base)
    descriptor=os.open(path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        try:fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('Another private pilot operation is active') from None
        yield
    finally:os.close(descriptor)


class Deferred(Exception):
    def __init__(self,reason,seconds=60):self.reason=reason;self.seconds=max(1,min(seconds,86400))


class BudgetStop(Exception):pass


class PinError(ValueError):pass


@contextlib.contextmanager
def request_alarm(seconds):
    # A socket timeout alone does not bound slowly streamed headers or bodies.
    def expired(*_):raise BudgetStop('request-time-limit')
    old=signal.signal(signal.SIGALRM,expired)
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        signal.signal(signal.SIGALRM,old);raise ValueError('Cannot nest the request deadline timer')
    signal.setitimer(signal.ITIMER_REAL,seconds)
    try:yield
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)


class Fetcher:
    """Anonymous HTTPS GETs; verified public DNS address bound to the TLS socket.

    No proxy, credentials, cookies, HEAD probes or implicit redirect handling.
    DNS runs in an isolated Python process so it has a bounded timeout too.
    """
    def __init__(self,limits,tool_download=False):
        self.limits=limits;self.requests=0;self.deadline=time.monotonic()+limits['seconds'];self.tool_download=tool_download

    def remaining(self):
        value=self.deadline-time.monotonic()
        if value<=0:raise BudgetStop('total-time-limit')
        return value

    def resolve(self,host):
        code='import socket,json,sys;print(json.dumps(sorted({r[4][0] for r in socket.getaddrinfo(sys.argv[1],443,type=socket.SOCK_STREAM)})))'
        result=subprocess.run([sys.executable,'-I','-c',code,host],capture_output=True,timeout=min(5,self.remaining()),env={'PATH':'/usr/bin:/bin'},check=True)
        if len(result.stdout)>16384:raise ValueError('DNS result limit')
        addresses=loads(result.stdout)
        if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):raise ValueError('DNS resolved to a non-public address')
        return addresses[0]

    def once(self,url,max_bytes):
        with request_alarm(min(self.limits['request_seconds'],self.remaining())):
            return self._once(url,max_bytes)

    def _once(self,url,max_bytes):
        self.remaining()
        if self.requests>=self.limits['requests']:raise BudgetStop('request-limit')
        self.requests+=1
        p=urllib.parse.urlsplit(public_url(url,self.tool_download));address=self.resolve(p.hostname)
        timeout=min(self.limits['request_seconds'],self.remaining())
        context=ssl.create_default_context()
        class PinnedHTTPS(http.client.HTTPSConnection):
            def connect(conn):
                sock=socket.create_connection((address,443),timeout=timeout)
                conn.sock=context.wrap_socket(sock,server_hostname=p.hostname)
        connection=PinnedHTTPS(p.hostname,timeout=timeout,context=context)
        try:
            connection.request('GET',urllib.parse.urlunsplit(('','',p.path or '/',p.query,'')),headers={'Accept':'application/json, application/gzip, application/octet-stream','Accept-Encoding':'identity','User-Agent':'xgov-okf-public-sbom-pilot/1'})
            transport=connection.sock
            response=connection.getresponse();headers={k.lower():v for k,v in response.getheaders()}
            if response.status in (429,503) or response.status==403 and headers.get('x-ratelimit-remaining')=='0':
                wait=headers.get('retry-after','60')
                try:delay=int(wait)
                except ValueError:
                    import email.utils
                    try:delay=int((email.utils.parsedate_to_datetime(wait)-dt.datetime.now(dt.timezone.utc)).total_seconds())
                    except (ValueError,TypeError):delay=60
                raise Deferred('http-'+str(response.status),delay)
            if response.status in (301,302,303,307,308):return response.status,headers,b''
            if response.status!=200:raise ValueError('public-get-http-'+str(response.status))
            if int(headers.get('content-length','0'))>max_bytes:raise ValueError('Download size limit')
            data=bytearray()
            while True:
                self.remaining();transport.settimeout(min(timeout,self.remaining()))
                block=response.read1(min(65536,max_bytes-len(data)+1))
                if not block:break
                data.extend(block)
                if len(data)>max_bytes:raise ValueError('Download size limit')
            self.remaining()
            return response.status,headers,bytes(data)
        finally:connection.close()

    def get(self,url,max_bytes,redirect_hosts=()):
        original=public_url(url)
        for hop in range(4):
            status,headers,raw=self.once(url,max_bytes)
            if status==200:
                final=urllib.parse.urlsplit(url)
                safe_final=urllib.parse.urlunsplit((final.scheme,final.netloc,final.path,'','')) if self.tool_download else url
                return raw,{'origin':original,'final_url':safe_final,'retrieved_at':c.now(),'sha256':sha(raw),'bytes':len(raw),'last_modified':headers.get('last-modified')}
            if hop==3:raise ValueError('Redirect limit')
            url=public_url(urllib.parse.urljoin(url,headers.get('location','')),self.tool_download)
            if urllib.parse.urlsplit(url).hostname not in redirect_hosts:raise ValueError('Redirect host needs explicit admission')
        raise ValueError('Unreachable redirect state')


def limits_for(manifest):
    limits=dict(LIMITS)
    for key,value in manifest.get('limits',{}).items():
        if key not in limits or type(value) is not int or not 1<=value<=limits[key]:raise ValueError('Limits may only reduce the governed positive ceilings')
        limits[key]=value
    return limits


def manifest_plan(manifest):
    if manifest.get('schema')!='xgov-public-sbom-pilot.v1' or manifest.get('mode')!=MODE:raise ValueError('Explicit public-sbom-data-analysis mode and manifest schema required')
    limits=limits_for(manifest);rows=manifest.get('inputs')
    if not isinstance(rows,list) or not 1<=len(rows)<=limits['documents']:raise ValueError('Name one to ten explicit SBOM inputs')
    seen=set();plan=[]
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',row['id']) or row['id'] in seen or row['id'] in ('checkpoint','batch-review'):raise ValueError('Use distinct bounded text input identifiers; checkpoint and batch-review are reserved')
        seen.add(row['id']);public_url(row['url'])
        if row.get('repository') is not None:permissions.target(row['repository'])
        publication=row.get('publication',{})
        if publication.get('kind') not in ('published-document','official-api'):raise ValueError('Only an existing published SBOM document or official API is admitted')
        public_url(publication.get('evidence_url'))
        for host in row.get('redirect_hosts',[]):
            if not re.fullmatch('[a-z0-9][a-z0-9.-]*',host):raise ValueError('Invalid explicit redirect host')
        if len(row.get('redirect_hosts',[]))>3:raise ValueError('Too many redirect hosts')
        if row.get('expected_sha256') is not None and not HEX.fullmatch(row['expected_sha256']):raise ValueError('Invalid expected input SHA-256')
        if row.get('source_revision') is not None and not re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}',row['source_revision']):raise ValueError('Invalid declared source revision')
        decision=permissions.public_data_basis(row)
        if decision['status']=='eligible-for-retrieval':public_url(row['access_reuse']['evidence_url'])
        plan.append({'id':row['id'],'origin':row['url'],**decision})
    return {'schema':'xgov-public-sbom-pilot-plan.v1','mode':MODE,'dry_run':True,'network_requests':0,'scanner_invocations':0,'owner_approval_claimed':False,'limits':limits,'inputs':plan}


def validate_pins(pins):
    if pins.get('schema')!='xgov-sbom-toolchain-pins.v1' or not re.fullmatch(r'\d+\.\d+\.\d+',pins.get('scanner',{}).get('version','')):raise ValueError('Invalid scanner pin record')
    for name,row in [*pins['scanner']['platforms'].items(),('database',pins['database'])]:
        for key in ('sha256',):
            if not HEX.fullmatch(str(row.get(key,''))):raise ValueError('Missing exact artefact digest')
        public_url(row['url'])
        if name=='database':
            if not row['url'].startswith('https://grype.anchore.io/databases/v6/vulnerability-db_') or not row['url'].endswith('.tar.zst'):raise ValueError('Database must be an exact official snapshot URL')
        elif name not in ('darwin_arm64','linux_amd64') or row['url']!=f"https://github.com/anchore/grype/releases/download/v{pins['scanner']['version']}/grype_{pins['scanner']['version']}_{name}.tar.gz":raise ValueError('Scanner must be an exact official release URL')
        if type(row.get('bytes')) is not int or not 0<row['bytes']<=1024**3:raise ValueError('Invalid pinned artefact size')
        if name!='database' and not HEX.fullmatch(str(row.get('binary_sha256',''))):raise ValueError('Exact scanner binary checksum required')
    db=pins['database'];timestamp(db['built'])
    if set(db.get('files',{}))!={'6/vulnerability.db','6/import.json'} or any(not HEX.fullmatch(v) for v in db['files'].values()):raise ValueError('Exact extracted database file digests required')
    if set(db.get('file_bytes',{}))!=set(db['files']) or any(type(v) is not int or not 0<v<=4*1024**3 for v in db['file_bytes'].values()):raise ValueError('Exact prepared database sizes required')
    return pins


def current_platform():return {'Darwin':'darwin','Linux':'linux'}.get(platform.system(),'unsupported')+'_'+{'arm64':'arm64','aarch64':'arm64','x86_64':'amd64'}.get(platform.machine(),'unsupported')


def isolated_command(command):
    if sys.platform=='darwin' and Path('/usr/bin/sandbox-exec').is_file():
        return ['/usr/bin/sandbox-exec','-p','(version 1)(allow default)(deny network*)',*command]
    if sys.platform.startswith('linux') and Path('/usr/bin/unshare').is_file():
        return ['/usr/bin/unshare','--user','--map-root-user','--net','--',*command]
    raise ValueError('Required OS network isolation is unavailable; no matching allowed')


def clean_env(base,db):
    return {'PATH':'/usr/bin:/bin','HOME':str(base),'TMPDIR':str(base),'LANG':'C.UTF-8',
            'GRYPE_DB_CACHE_DIR':str(db),'GRYPE_DB_AUTO_UPDATE':'false','GRYPE_CHECK_FOR_APP_UPDATE':'false',
            'GRYPE_EXTERNAL_SOURCES_ENABLE':'false','GRYPE_EXTERNAL_SOURCES_MAVEN_SEARCH_MAVEN_UPSTREAM':'false',
            'GRYPE_DB_VALIDATE_AGE':'false','GRYPE_DB_VALIDATE_BY_HASH_ON_START':'true','GOMAXPROCS':'1'}


def process(command,env,cwd,seconds,limit,base):
    """Bound file output, CPU, wall time and descendants. Never execute a shell."""
    out=secure_path(cwd/'stdout.json',base);err=secure_path(cwd/'stderr.txt',base)
    write_private(out,b'',base);write_private(err,b'',base)
    def ceilings():
        file_limit=4*1024**3 if 'import' in command else limit
        os.umask(0o077);resource.setrlimit(resource.RLIMIT_FSIZE,(file_limit,file_limit));resource.setrlimit(resource.RLIMIT_CPU,(seconds+1,seconds+2))
    with out.open('wb') as stdout,err.open('wb') as stderr:
        child=subprocess.Popen(isolated_command(command),env=env,cwd=cwd,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,start_new_session=True,preexec_fn=ceilings)
        deadline=time.monotonic()+seconds
        try:
            while True:
                if out.stat().st_size>limit or err.stat().st_size>limit:raise ValueError('Scanner output limit')
                if time.monotonic()>=deadline:raise ValueError('Scanner wall-time limit')
                try:code=child.wait(timeout=min(0.1,max(0.01,deadline-time.monotonic())));break
                except subprocess.TimeoutExpired:continue
        except BaseException:
            if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
            child.wait();raise
    os.chmod(out,0o600);os.chmod(err,0o600)
    if code!=0:raise ValueError('Isolated scanner command failed; private stderr retained')
    if out.stat().st_size>limit or err.stat().st_size>limit:raise ValueError('Scanner output limit')
    return out.read_bytes()


def tool_paths(base,pins,platform_key=None):
    key=platform_key or current_platform()
    if key not in pins['scanner']['platforms']:raise ValueError('This platform has no reviewed scanner pin')
    folder=secure_path(base/'tools'/sha(c.encoded(pins))/key,base,True)
    return folder,folder/'grype',folder/'db',pins['scanner']['platforms'][key]


def verify_tools(base,pins,deadline=None):
    folder,binary,db,row=tool_paths(base,pins)
    secure_path(binary,base);secure_path(db,base,True)
    if not binary.is_file() or file_sha(binary,deadline)!=row['binary_sha256']:raise PinError('Scanner binary pin mismatch; prepare the toolchain')
    os.chmod(binary,0o700)
    archive=secure_path(folder/'database.tar.zst',base)
    if not archive.is_file() or archive.stat().st_size!=pins['database']['bytes'] or file_sha(archive,deadline)!=pins['database']['sha256']:raise PinError('Database archive pin mismatch')
    # SQLite/metadata only. Extra cache files are not silently trusted.
    found=set()
    for p in db.rglob('*'):
        if p.is_symlink():raise PinError('Database must not contain symbolic links')
        if p.is_file():found.add(p.relative_to(db).as_posix())
        elif not p.is_dir() or p.relative_to(db).as_posix()!='6':raise PinError('Unexpected database directory')
    if found!=set(pins['database']['files']):raise PinError('Database membership pin mismatch')
    for name,digest in pins['database']['files'].items():
        p=secure_path(db/name,base)
        if not p.is_file() or p.stat().st_size!=pins['database']['file_bytes'][name] or file_sha(p,deadline)!=digest:raise PinError('Database file pin mismatch')
    return folder,binary,db


def prepare(root,pins,fetcher=None,executor=process):
    with execution_lock(root):return _prepare(root,pins,fetcher,executor)


def _prepare(root,pins,fetcher=None,executor=process):
    """Only fixed public tooling downloads and an offline DB import; no SBOMs."""
    validate_pins(pins);base=private_dir(root);folder,binary,db,row=tool_paths(base,pins)
    fetcher=fetcher or Fetcher({**LIMITS,'seconds':600,'requests':12,'request_seconds':30},tool_download=True)
    for name,pin in [('scanner.tar.gz',row),('database.tar.zst',pins['database'])]:
        path=secure_path(folder/name,base)
        if path.exists():
            if path.stat().st_size!=pin['bytes'] or file_sha(path)!=pin['sha256']:raise ValueError('Cached tool artefact pin mismatch')
        else:
            raw,receipt=fetcher.get(pin['url'],pin['bytes'],('release-assets.githubusercontent.com','objects.githubusercontent.com'))
            if len(raw)!=pin['bytes'] or sha(raw)!=pin['sha256']:raise ValueError('Downloaded tool artefact pin mismatch')
            write_private(path,raw,base);write_private(folder/(name+'.receipt.json'),receipt,base)
    with tarfile.open(folder/'scanner.tar.gz','r:gz') as tar:
        members=tar.getmembers()
        if len(members)>12 or len({m.name for m in members})!=len(members) or any(not m.isfile() or m.name not in ('grype','LICENSE','README.md','CHANGELOG.md') or m.size>160*1024**2 for m in members):raise ValueError('Unexpected scanner archive membership')
        member=next(m for m in members if m.name=='grype');raw=tar.extractfile(member).read()
        if sha(raw)!=row['binary_sha256']:raise ValueError('Extracted scanner binary pin mismatch')
        write_private(binary,raw,base);os.chmod(binary,0o700)
    secure_path(db,base,True)
    work=secure_path(folder/'import',base,True);config=work/'config.json'
    write_private(config,{},base)
    executor([str(binary),'--config',str(config),'db','import',str(folder/'database.tar.zst')],clean_env(work,db),work,180,1024**2,base)
    verify_tools(base,pins)
    return {'status':'prepared','mode':MODE,'scanner_version':pins['scanner']['version'],'database_sha256':pins['database']['sha256'],'sbom_requests':0,'scanner_matches_started':False}


def decoded_sbom(raw,limit):
    if raw.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:raw=stream.read(limit+1)
    if len(raw)>limit:raise ValueError('Decoded SBOM size limit')
    data=loads(raw)
    if isinstance(data,dict) and isinstance(data.get('sbom'),dict):data=data['sbom'];raw=c.encoded(data)
    if not isinstance(data,dict):raise ValueError('SBOM must be a JSON object')
    return raw,data


def package_identity(purl,version):
    if not isinstance(purl,str) or len(purl)>2048 or re.search(r'[\s\x00-\x1f]',purl):return None,'unresolved-package-identity'
    if '?' in purl or '#' in purl:return None,'unsupported-package-qualifiers-by-pilot'
    match=re.fullmatch(r'pkg:([a-z][a-z0-9.+-]*)/([^?#]+)(?:\?[^#]*)?(?:#.*)?',purl)
    if not match:return None,'unresolved-package-identity'
    ecosystem,coordinate=match.groups()
    if ecosystem not in ECOSYSTEMS:return None,'unsupported-ecosystem-by-pilot'
    if '@' in coordinate:
        coordinate,purl_version=coordinate.rsplit('@',1)
        if urllib.parse.unquote(purl_version)!=version:return None,'conflicting-declared-versions'
    decoded=urllib.parse.unquote(coordinate)
    if not coordinate or re.search(r'[%](?![0-9A-Fa-f]{2})',purl) or re.search(r'[\s\x00-\x1f]',decoded) or any(part in ('','.','..') for part in decoded.split('/')):return None,'unresolved-package-identity'
    return {'ecosystem':ecosystem,'coordinate':coordinate,'purl':purl,'key':ecosystem+'/'+coordinate+'@'+version},None


def source_revision(data,row,gaps):
    revisions=set()
    metadata=data.get('metadata',{})
    component=metadata.get('component',{}) if isinstance(metadata,dict) else {}
    for source in (metadata,component):
        if not isinstance(source,dict):continue
        for prop in source.get('properties',[]):
            if prop.get('name') in ('cdx:git:commit','cdx:vcs:commit','source:revision','source:commit') and re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}',str(prop.get('value',''))):revisions.add(prop['value'])
        for ref in source.get('externalReferences',[]):
            match=re.fullmatch(r'https://[^/]+/[^/]+/[^/]+/commit/([0-9a-f]{40}|[0-9a-f]{64})',str(ref.get('url','')))
            if ref.get('type')=='vcs' and match:revisions.add(match[1])
    if row.get('source_revision'):revisions.add(row['source_revision'])
    if len(revisions)>1:gaps.append({'state':'conflicting-source-revisions','values':sorted(revisions)});return None,'conflicting-declarations'
    if not revisions:gaps.append({'state':'source-revision-not-supplied'});return None,'unavailable'
    return next(iter(revisions)),'document-or-input-declaration-not-independently-verified'


def inspect_sbom(data,row,limits,at=None):
    gaps=[];packages=[];at=at or dt.datetime.now(dt.timezone.utc)
    if data.get('spdxVersion') in ('SPDX-2.2','SPDX-2.3'):
        format_name=data['spdxVersion'];document_date=data.get('creationInfo',{}).get('created');licences=[data.get('dataLicense')] if data.get('dataLicense') else [];raw=data.get('packages',[])
        scope_map=collections.defaultdict(set)
        if data.get('externalDocumentRefs'):gaps.append({'state':'external-document-references-not-resolved'})
        for rel in data.get('relationships',[]):
            kind={'DEV_DEPENDENCY_OF':'development','BUILD_DEPENDENCY_OF':'build','TEST_DEPENDENCY_OF':'test'}.get(rel.get('relationshipType'))
            if kind:scope_map[rel.get('spdxElementId')].add(kind)
        def convert(p):
            refs=[r.get('referenceLocator') for r in p.get('externalRefs',[]) if str(r.get('referenceType','')).lower()=='purl']
            return p.get('SPDXID'),p.get('name'),p.get('versionInfo'),refs,sorted(scope_map[p.get('SPDXID')]) or ['unknown']
    elif data.get('bomFormat')=='CycloneDX' and data.get('specVersion') in ('1.4','1.5','1.6'):
        format_name='CycloneDX-'+data['specVersion'];metadata=data.get('metadata',{});document_date=metadata.get('timestamp');licences=[r.get('expression') or r.get('license',{}).get('id') for r in metadata.get('licenses',[])];raw=[]
        stack=list(data.get('components',[]))
        if metadata.get('component'):stack.append(metadata['component'])
        while stack:
            p=stack.pop()
            if not isinstance(p,dict):raise ValueError('Component must be an object')
            raw.append(p);stack.extend(p.get('components',[]))
            if len(raw)+len(stack)>limits['packages']:raise ValueError('Package count limit')
        def convert(p):
            scopes=[v.get('value') for v in p.get('properties',[]) if v.get('name') in ('scope','dependency:scope','cdx:dependency:scope') and v.get('value') in ('build','test','ci','runtime','development','dev')]
            return p.get('bom-ref'),p.get('name'),p.get('version'),[p.get('purl')] if p.get('purl') else [],sorted(set(scopes)) or ['unknown']
    else:return {'format':'unsupported','document_date':None,'source_revision':row.get('source_revision'),'packages':[],'gaps':[{'state':'unsupported-document-format'}],'licences':[]}
    if not isinstance(raw,list) or len(raw)>limits['packages']:raise ValueError('Package count limit')
    if not document_date:gaps.append({'state':'missing-document-date'})
    else:
        try:
            date=timestamp(document_date)
            if date>at:gaps.append({'state':'future-document-date'})
            if (at-date).total_seconds()>limits['stale_days']*86400:gaps.append({'state':'stale-document','threshold_days':limits['stale_days']})
        except (ValueError,TypeError):gaps.append({'state':'invalid-document-date'})
    if row['access_reuse'].get('licence') and licences and row['access_reuse']['licence'] not in licences:raise ValueError('Embedded document licence and recorded reuse basis disagree; review required')
    revision,revision_basis=source_revision(data,row,gaps)
    for ordinal,p in enumerate(raw):
        if not isinstance(p,dict):raise ValueError('Package entry must be an object')
        identifier,name,version,purls,scopes=convert(p);ref='component-'+str(ordinal)
        package={'id':ref,'document_id':identifier,'name':name,'version':version,'purls':purls,'declared_contexts':scopes,'declared_requirement':p.get('scope'),'eligible':False}
        if not isinstance(name,str) or not name or len(name)>1024:reason='unresolved-package-identity'
        elif not isinstance(version,str) or not version.strip() or version.upper() in ('NONE','NULL','N/A','NOASSERTION','UNKNOWN','UNRESOLVED','UNSPECIFIED','LATEST','NEXT','CANARY','STABLE','DEVEL') or len(version)>200 or re.search(r'[\s*^~<>=|{}\[\](),;\x00-\x1f]',version) or re.search(r'(^|\.)[xX]($|\.)',version):reason='missing-or-unresolved-version'
        elif len(purls)!=1:reason='unresolved-package-identity'
        else:
            identity,reason=package_identity(purls[0],version)
            if not reason:package.update(identity=identity,eligible=True)
        if not package['eligible']:gaps.append({'state':reason,'component_id':ref})
        packages.append(package)
    if not packages:gaps.append({'state':'no-declared-packages'})
    return {'format':format_name,'document_date':document_date,'source_revision':revision,'source_revision_basis':revision_basis,'licences':licences,'packages':packages,'gaps':gaps}


def match_projection(inspection):
    # Data-only projection: full eligible inventory, including build/test/CI.
    components=[]
    for p in inspection['packages']:
        if p['eligible']:
            identity=p['identity'];purl='pkg:'+identity['ecosystem']+'/'+identity['coordinate']+'@'+urllib.parse.quote(p['version'],safe='.+-')
            components.append({'type':'library','bom-ref':p['id'],'name':p['name'],'version':p['version'],'purl':purl,'scope':'required'})
    return {'bomFormat':'CycloneDX','specVersion':'1.5','version':1,'components':components}


def candidate_matches(result,inspection,input_sha,pins,limits=None):
    limits=limits or LIMITS
    by_key=collections.defaultdict(list)
    for p in inspection['packages']:
        if p['eligible']:by_key[p['identity']['key']].append(p)
    candidates=[];gaps=[];seen=set();associations=0
    if not isinstance(result.get('matches'),list):raise ValueError('Scanner returned an unsupported result')
    if len(result['matches'])>100000:raise ValueError('Scanner match row limit')
    for match in result['matches']:
        artifact=match.get('artifact',{});vuln=match.get('vulnerability',{});identity,reason=package_identity(artifact.get('purl'),artifact.get('version')) if isinstance(artifact.get('version'),str) else (None,'unresolved-version')
        members=by_key.get(identity['key'],[]) if identity else []
        if not members:
            gaps.append({'state':'unreconciled-scanner-match'});continue
        advisory_id=vuln.get('id');namespace=vuln.get('namespace')
        if not isinstance(advisory_id,str) or not advisory_id or len(advisory_id)>200:raise ValueError('Invalid advisory identifier')
        key=sha(c.encoded([input_sha,identity['key'],advisory_id,namespace,pins['scanner']['version'],pins['database']['sha256']]))
        if key in seen:continue
        if len(candidates)>=limits['candidates'] or associations+len(members)>limits['candidate_links']:
            gaps.append({'state':'candidate-report-limit','delivered_candidates':len(candidates),'delivered_component_links':associations});break
        seen.add(key)
        associations+=len(members)
        links=[]
        for url in [vuln.get('dataSource'),*vuln.get('urls',[])]:
            try:
                if url:links.append(public_url(url))
            except ValueError:pass
        candidates.append({
            'id':key,'label':'candidate advisory match',
            'package':{'name':members[0]['name'],'version':members[0]['version'],
                       'purl':artifact['purl'],'component_ids':[p['id'] for p in members],
                       'declared_contexts':sorted({s for p in members for s in p['declared_contexts']})},
            'advisory':{'id':advisory_id,'namespace':namespace,'urls':sorted(set(links)),
                        'reported_severity':vuln.get('severity'),'reported_fix':vuln.get('fix')},
            'sbom_sha256':input_sha,'scanner_version':pins['scanner']['version'],
            'scanner_binary_sha256':pins['scanner']['platforms'][current_platform()]['binary_sha256'],
            'database_sha256':pins['database']['sha256'],'database_built':pins['database']['built'],
            'applicability':'not-assessed','exploitability':'not-assessed','deployed_exposure':'not-assessed'})
    return candidates,gaps


def markdown(report):
    def text(value):
        value=html.escape(str(value),quote=True)
        return re.sub(r'([\\`*_[\]{}()!|#])',r'\\\1',value).replace('\n',' ')
    lines=['# Private candidate advisory matches','',f"Input: {text(report['input_id'])}",f"Mode: {MODE}; owner approval is not claimed.",f"SBOM SHA-256: {report['sbom_sha256']}",f"Scanner: Grype {report['scanner']['version']}; binary SHA-256 {report['scanner']['binary_sha256']}",f"Database: {report['database']['built']}; SHA-256 {report['database']['sha256']}",'','These data matches do not establish exploitability, deployed exposure or a vulnerable repository.','Build, test and CI components remain in the full results; the runtime view uses explicit declarations only.','','## Candidates','']
    for row in report['candidate_advisory_matches']:
        lines.append(f"- {text(row['advisory']['id'])}: {text(row['package']['name'])} {text(row['package']['version'])}; contexts: {text(', '.join(row['package']['declared_contexts']))}; candidate {row['id']}.")
        for url in row['advisory']['urls']:lines.append('  Advisory: <'+url+'>')
    if not report['candidate_advisory_matches']:lines.append('No reconciled candidate advisory matches were returned. This is not a clean bill of health.')
    lines+=['','## Coverage gaps','']
    lines += ['- '+text(gap['state'])+((': '+text(gap['component_id'])) if gap.get('component_id') else '') for gap in report['coverage_gaps']]
    lines+=['','## Origin and basis','',text(report['retrieval']['origin']),text(report['access_reuse']['basis']),'','Reports remain private. Communication, disclosure, source review, service testing and AI are separate future decisions.','']
    return '\n'.join(lines)


def fetch_input(base,row,fetcher,limits):
    folder=secure_path(base/'cache'/sha(c.encoded(row)),base,True);body=folder/'body';receipt_path=folder/'receipt.json'
    if receipt_path.exists():
        receipt=read_json(secure_path(receipt_path,base));secure_path(body,base)
        if receipt.get('origin')!=row['url'] or not body.is_file() or body.stat().st_size>limits['document_bytes'] or body.stat().st_size!=receipt.get('bytes') or file_sha(body)!=receipt['sha256']:raise ValueError('Cached SBOM integrity mismatch')
        timestamp(receipt['retrieved_at']);public_url(receipt['final_url'])
        raw=body.read_bytes();cached=True
    else:
        raw,receipt=fetcher.get(row['url'],limits['document_bytes'],row.get('redirect_hosts',[]));cached=False
        write_private(body,raw,base);write_private(receipt_path,receipt,base)
    if row.get('expected_sha256') and sha(raw)!=row['expected_sha256']:raise ValueError('Cached input differs from its admission hash')
    decoded,data=decoded_sbom(raw,limits['decoded_bytes'])
    return decoded,data,{**receipt,'cache_reused':cached,'sbom_sha256':sha(decoded),'decode':'gzip-or-api-wrapper' if decoded!=raw else 'identity'}


def run(root,manifest,pins,execute=False,fetcher=None,executor=process,at=None):
    if not execute:return _run(root,manifest,pins,False,fetcher,executor,at)
    with execution_lock(root):return _run(root,manifest,pins,True,fetcher,executor,at)


def _run(root,manifest,pins,execute=False,fetcher=None,executor=process,at=None):
    plan=manifest_plan(manifest);validate_pins(pins)
    if not execute:return {**plan,'toolchain_sha256':sha(c.encoded(pins)),'toolchain_prepared':'not-checked-no-processes-started'}
    limits=plan['limits'];started=time.monotonic();deadline=started+limits['seconds'];base=private_dir(root)
    run_id=sha(c.encoded([manifest,pins,sha(Path(__file__).read_bytes())]));work=secure_path(base/'runs'/run_id,base,True)
    checkpoint=work/'checkpoint.json';state=read_json(checkpoint) if checkpoint.exists() else {'schema':'xgov-public-sbom-checkpoint.v1','run_id':run_id,'inputs':{}}
    if state.get('schema')!='xgov-public-sbom-checkpoint.v1' or state.get('run_id')!=run_id or not isinstance(state.get('inputs'),dict) or set(state['inputs'])-{r['id'] for r in manifest['inputs']}:raise ValueError('Checkpoint identity mismatch')
    fetcher=fetcher or Fetcher(limits);fetcher.deadline=min(fetcher.deadline,deadline)
    def save():write_private(checkpoint,state,base)
    save()
    if any(d['status']=='eligible-for-retrieval' and state['inputs'].get(d['id'],{}).get('status')!='reported' for d in plan['inputs']):
        try:
            folder,binary,db=verify_tools(base,pins,deadline)
            isolated_command([str(binary)])
            remaining=int(deadline-time.monotonic())
            if remaining<1:raise BudgetStop('total-time-limit')
            preflight=secure_path(work/'preflight',base,True);config=preflight/'config.json';write_private(config,{},base)
            version=loads(executor([str(binary),'--config',str(config),'version','--output','json'],clean_env(preflight,db),preflight,min(10,remaining),1024**2,base))
            if version.get('version')!=pins['scanner']['version']:raise PinError('Scanner version and binary pin record disagree')
        except BudgetStop as exc:
            state['stop_reason']=str(exc);save()
            return {'mode':MODE,'run_id':run_id,'private_directory':str(work),'inputs':state['inputs'],'stop_reason':str(exc),'network_requests':fetcher.requests,'owner_approval_claimed':False}
    for row,decision in zip(manifest['inputs'],plan['inputs']):
        previous=state['inputs'].get(row['id'],{})
        if previous.get('status')=='reported':
            for suffix in ('json','md'):
                p=secure_path(work/(row['id']+'.'+suffix),base)
                if not p.is_file() or file_sha(p)!=previous['report_sha256'][suffix]:raise ValueError('Resumable report integrity mismatch')
            receipt_path=secure_path(base/'cache'/sha(c.encoded(row))/'receipt.json',base)
            if not receipt_path.is_file():raise ValueError('Completed input cache is missing')
            _,_,retrieval=fetch_input(base,row,fetcher,limits)
            report=read_json(work/(row['id']+'.json'),limits['output_bytes'])
            if report.get('mode')!=MODE or report.get('owner_approval_claimed') is not False or report.get('sbom_sha256')!=retrieval['sbom_sha256']:raise ValueError('Completed report and source binding disagree')
            continue
        if previous.get('retry_after') and c.parse_date(previous['retry_after'])>dt.datetime.now(dt.timezone.utc):continue
        if decision['status']!='eligible-for-retrieval':state['inputs'][row['id']]=decision;save();continue
        if time.monotonic()-started>=limits['seconds']:state['stop_reason']='total-time-limit';save();break
        state['inputs'][row['id']]={'status':'pending','origin':row['url']};save()
        try:
            decoded,data,retrieval=fetch_input(base,row,fetcher,limits);inspection=inspect_sbom(data,row,limits,at)
            scratch=secure_path(work/(row['id']+'-work'),base,True);projection=match_projection(inspection)
            source=scratch/'sbom.json';write_private(source,c.encoded(projection),base)
            candidates=[];match_gaps=[];scanner_rows=0
            if projection['components']:
                verify_tools(base,pins,deadline)
                config=scratch/'config.json';write_private(config,{'db':{'auto-update':False,'validate-age':False},'check-for-app-update':False,'external-sources':{'enable':False},'ignore':[],'exclude':[],'add-cpes-if-none':False},base)
                remaining=int(deadline-time.monotonic())
                if remaining<1:raise BudgetStop('total-time-limit')
                raw=executor([str(binary),'--config',str(config),'sbom:'+str(source),'--output','json'],clean_env(scratch,db),scratch,min(limits['scan_seconds'],remaining),limits['output_bytes'],base)
                if len(raw)>limits['output_bytes']:raise ValueError('Scanner output size limit')
                result=loads(raw);scanner_rows=len(result.get('matches',[]))
                candidates,match_gaps=candidate_matches(result,inspection,retrieval['sbom_sha256'],pins,limits)
                verify_tools(base,pins,deadline)
            try:
                if (dt.datetime.now(dt.timezone.utc)-timestamp(pins['database']['built'])).total_seconds()>5*86400:match_gaps.append({'state':'stale-advisory-database','threshold_days':5})
            except ValueError:raise PinError('Invalid database build date') from None
            report={
                'schema':'xgov-public-sbom-analysis.v1','mode':MODE,'input_id':row['id'],
                'repository_reference':row.get('repository'),'label':'candidate advisory matches',
                'owner_approval_claimed':False,'observed_at':c.now(),'retrieval':retrieval,
                'sbom_sha256':retrieval['sbom_sha256'],'access_reuse':row['access_reuse'],
                'scanner':{'version':pins['scanner']['version'],
                           'binary_sha256':pins['scanner']['platforms'][current_platform()]['binary_sha256'],
                           'match_input_sha256':file_sha(source)},
                'database':pins['database'],
                'document':{k:v for k,v in inspection.items() if k not in ('packages','gaps')},
                'matching':{'executed':bool(projection['components']),'eligible_packages':len(projection['components']),
                            'declared_packages':len(inspection['packages']),'scanner_match_rows':scanner_rows,
                            'projection':'data-only; all eligible contexts retained'},
                'declared_packages':inspection['packages'],'coverage_gaps':inspection['gaps']+match_gaps,
                'candidate_advisory_matches':candidates,
                'runtime_view':{'basis':'explicit declared runtime only; unknown and build/test/CI retained in full results',
                                'candidate_ids':[v['id'] for v in candidates if 'runtime' in v['package']['declared_contexts']],
                                'unknown_context_candidate_ids':[v['id'] for v in candidates if 'unknown' in v['package']['declared_contexts']]},
                'limitations':[
                    'Data-only package/version advisory matches, not a finding of repository vulnerability, exploitability or deployed exposure.',
                    'No source/code, repository operations, dependency installation, application images, service testing, communication or external AI.',
                    'Supported language PURLs only; unresolved and unsupported packages remain coverage gaps.']}
            encoded=c.encoded(report);prose=markdown(report).encode()
            if len(encoded)>limits['output_bytes'] or len(prose)>limits['output_bytes']:raise ValueError('Derived report size limit')
            write_private(work/(row['id']+'.json'),encoded,base);write_private(work/(row['id']+'.md'),prose,base)
            state['inputs'][row['id']]={'status':'reported','candidates':len(candidates),'coverage_gaps':len(report['coverage_gaps']),'report_sha256':{s:file_sha(work/(row['id']+'.'+s)) for s in ('json','md')}}
        except Deferred as exc:
            state['inputs'][row['id']]={'status':'deferred-rate-limit','reason':exc.reason,'retry_after':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=exc.seconds)).isoformat()};save();break
        except BudgetStop as exc:state['inputs'][row['id']]={'status':'budget-checkpoint','reason':str(exc)};save();break
        except PinError:
            state['inputs'][row['id']]={'status':'stopped-toolchain-pin-failure'};save();raise
        except (ValueError,OSError,KeyError,TypeError,AttributeError,RecursionError,subprocess.SubprocessError):
            # No raw body, package identity, scanner output or access-bearing URL in logs.
            state['inputs'][row['id']]={'status':'review-required','reason':'input-tool-or-result-validation-failed'}
        save()
    review={'schema':'xgov-public-sbom-pilot-review.v1','mode':MODE,'owner_approval_claimed':False,'inputs':[{'id':row['id'],'origin':row['url'],'access_reuse':row['access_reuse'],'outcome':state['inputs'].get(row['id'],{'status':'not-started'})} for row in manifest['inputs']]}
    write_private(work/'batch-review.json',review,base)
    write_private(work/'batch-review.md','# Private SBOM pilot checkpoint\n\nMode: '+MODE+'; no owner approval is claimed.\n\n'+'\n'.join('- '+row['id']+': '+review_row['outcome']['status'] for row,review_row in zip(manifest['inputs'],review['inputs']))+'\n',base)
    return {'mode':MODE,'run_id':run_id,'private_directory':str(work),'inputs':state['inputs'],'network_requests':fetcher.requests,'owner_approval_claimed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('run');p.add_argument('--manifest',type=Path,required=True);group=p.add_mutually_exclusive_group();group.add_argument('--dry-run',action='store_true');group.add_argument('--execute',action='store_true')
    sub.add_parser('prepare')
    args=parser.parse_args()
    try:
        pins=read_json(PIN_FILE)
        result=prepare(c.ROOT,pins) if args.command=='prepare' else run(c.ROOT,read_json(args.manifest),pins,execute=args.execute)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError,BudgetStop,subprocess.SubprocessError) as exc:parser.exit(1,'SBOM pilot stopped: '+str(exc)+'\n')


if __name__=='__main__':main()
