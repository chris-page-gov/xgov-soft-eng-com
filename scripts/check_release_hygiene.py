#!/usr/bin/env python3
"""Check the changelog and prospective Conventional Commit subjects offline."""
import argparse
import datetime as dt
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
LEGACY_BASELINE='f7eaed15feaa11941b8fa95e1c66aa400f421483'
TYPES='build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test'


def check_subject(subject):
    if not re.fullmatch(r'('+TYPES+r')(\([a-z0-9][a-z0-9._/-]*\))?!?: \S.*',subject):raise ValueError('Use type(optional-scope): concise description, following Conventional Commits')
    if len(subject)>72:raise ValueError('Project policy limits commit subjects to 72 characters')
    if subject.endswith('.'):raise ValueError('Project policy omits a final full stop in commit subjects')
    return True


def check_changelog(text):
    if not text.startswith('# Changelog\n'):raise ValueError('Changelog needs its standard title')
    sections=re.findall(r'^## (.+)$',text,re.M)
    if not sections or sections[0]!='[Unreleased]':raise ValueError('Keep an Unreleased section first')
    seen=set();versions=[];dates=[]
    for section in sections[1:]:
        match=re.fullmatch(r'\[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})',section)
        if not match:raise ValueError('Released headings need [major.minor.patch] - YYYY-MM-DD')
        version,date=match.groups();dt.date.fromisoformat(date)
        if version in seen:raise ValueError('Duplicate changelog release')
        seen.add(version);versions.append(tuple(map(int,version.split('.'))));dates.append(date)
    if versions!=sorted(versions,reverse=True) or dates!=sorted(dates,reverse=True):raise ValueError('Keep released versions and dates newest first')
    allowed={'Added','Changed','Deprecated','Removed','Fixed','Security'}
    if any(h not in allowed for h in re.findall(r'^### (.+)$',text,re.M)):raise ValueError('Use Keep a Changelog change categories')
    for name in ['Unreleased',*seen]:
        if f'[{name}]: https://' not in text:raise ValueError('Add comparison/release links for changelog sections')
    return True


def check_pr_title(event, title):
    if event == 'pull_request':
        check_subject(title or '')


def check_history(root,baseline,allow_synthetic_head=False):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    rows=subprocess.check_output(['git','log','--format=%H%x09%P%x09%s',baseline+'..HEAD'],cwd=root,text=True).splitlines()
    for row in rows:
        commit,parents,subject=row.split('\t',2)
        if allow_synthetic_head and commit==head and len(parents.split())>1:continue
        check_subject(subject)


def check_private_tracking(root):
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
    if any(any(part.casefold() in ('.consent','.sbom-pilot') for part in path.split('/')) for path in paths if path):
        raise ValueError('Private approval or SBOM pilot data must not be tracked by Git')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--message-file',type=Path);args=parser.parse_args()
    try:
        check_private_tracking(ROOT)
        if args.message_file:check_subject(args.message_file.read_text().splitlines()[0])
        else:
            check_changelog((ROOT/'CHANGELOG.md').read_text())
            check_pr_title(os.environ.get('GITHUB_EVENT_NAME'), os.environ.get('OKF_PR_TITLE'))
            synthetic=os.environ.get('GITHUB_EVENT_NAME')=='pull_request' and bool(re.fullmatch(r'refs/pull/[1-9][0-9]*/merge',os.environ.get('GITHUB_REF','')))
            check_history(ROOT,LEGACY_BASELINE,synthetic)
        print('Release hygiene checks passed.')
    except (ValueError,IndexError,subprocess.CalledProcessError) as exc:parser.exit(1,'Release hygiene check failed: '+str(exc)+'\n')


if __name__=='__main__':main()
