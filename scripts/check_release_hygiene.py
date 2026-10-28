#!/usr/bin/env python3
"""Check the changelog and prospective Conventional Commit subjects offline."""
import argparse
import datetime as dt
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


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--message-file',type=Path);args=parser.parse_args()
    try:
        if args.message_file:check_subject(args.message_file.read_text().splitlines()[0])
        else:
            check_changelog((ROOT/'CHANGELOG.md').read_text())
            subjects=subprocess.check_output(['git','log','--format=%s',LEGACY_BASELINE+'..HEAD'],cwd=ROOT,text=True).splitlines()
            for subject in subjects:check_subject(subject)
        print('Release hygiene checks passed.')
    except (ValueError,IndexError,subprocess.CalledProcessError) as exc:parser.exit(1,'Release hygiene check failed: '+str(exc)+'\n')


if __name__=='__main__':main()
