"""Render only the reviewed public report editions as deterministic static HTML.

This deliberately small Markdown subset escapes raw HTML and validates links.
It never admits the private evaluation capture or runs model-supplied code.
"""
from pathlib import Path
import hashlib
import html
import json
import re
from urllib.parse import quote, urlsplit

SOURCE = Path('docs/ai-evaluations/2026-10-29')
REPORTS_URL = 'https://chris-page-gov.github.io/xgov-soft-eng-com/reports/'
REPOSITORY = 'https://github.com/chris-page-gov/xgov-soft-eng-com/blob/main/'
MARKDOWN = ('README.md', 'claude.md', 'gemini.md', 'copilot.md', 'corrections.md', 'claude-capture-review.md')
SUPPORT = ('publication-manifest.json', 'evidence-map.json', 'claude-capture-review.json', 'SHA256SUMS')
FILES = MARKDOWN + SUPPORT
PAGES = {name: 'index.html' if name == 'README.md' else name[:-3] + '.html' for name in MARKDOWN}
STYLE = '''body{font:1.1rem/1.6 system-ui,sans-serif;color:#0b0c0c;background:#fff;margin:0;overflow-wrap:anywhere}header,main,footer{max-width:78rem;margin:auto;padding:1.5rem}header,footer{background:#f3f2f1}main>p,blockquote,main>ul,main>ol{max-width:80ch}h1,h2,h3,h4{line-height:1.2;margin-top:1.6em}a{color:#1d70b8;text-underline-offset:.15em}a:focus{background:#ffdd00;color:#0b0c0c;outline:3px solid #ffdd00}nav{display:flex;flex-wrap:wrap;gap:.5rem 1.5rem}.table-scroll{overflow-x:auto;margin:1.5rem 0}table{border-collapse:collapse;width:100%;font-size:.95rem}th,td{border:1px solid #b1b4b6;padding:.6rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#f3f2f1}code{font-size:.9em;overflow-wrap:anywhere}pre{overflow-x:auto;background:#f3f2f1;padding:1rem}blockquote{border-left:5px solid #1d70b8;padding:.5rem 1rem;background:#f3f2f1}.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem}'''


def link_target(target, source, root):
    """Permit safe web links, local report links and repository documentation."""
    if not target or re.search(r'[\s\x00-\x1f\x7f"\'<>\\]', target) or re.search(r'%(?![0-9a-fA-F]{2})', target):
        return None
    try:
        parsed = urlsplit(target)
        if parsed.scheme:
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
                return None
            if parsed.port is not None and not 1 <= parsed.port <= 65535:
                return None
            return target
        if parsed.netloc or target.startswith('/') or parsed.query:
            return None
        if not parsed.path:
            return '#' + parsed.fragment if parsed.fragment else None
        resolved = (source.parent / parsed.path).resolve()
        relative = resolved.relative_to(root.resolve()).as_posix()
        fragment = '#' + parsed.fragment if parsed.fragment else ''
        if resolved.parent == (root / SOURCE).resolve() and resolved.name in FILES:
            return PAGES.get(resolved.name, resolved.name) + fragment
        if not resolved.is_file():
            raise ValueError('Unresolved public report link: ' + relative)
        return REPOSITORY + quote(relative, safe='/') + fragment
    except (ValueError, OSError):
        return None


TOKEN = re.compile(r'(`+)([^`\n]+)\1|\[([^\]\n]+)\]\(([^)\n]+)\)|\*\*([^*\n]+)\*\*|\*([^*\n]+)\*|<br\s*/?>')


def inline(text, source, root):
    result=[];last=0
    for match in TOKEN.finditer(text):
        result.append(html.escape(text[last:match.start()]));last=match.end()
        code, body, label, target, bold, emphasis = match.groups()
        if code:
            result.append('<code>' + html.escape(body) + '</code>')
        elif label is not None:
            url=link_target(target, source, root)
            rendered=html.escape(label)
            result.append('<a href="' + html.escape(url, quote=True) + '">' + rendered + '</a>' if url else rendered)
        elif bold is not None:
            result.append('<strong>' + html.escape(bold) + '</strong>')
        elif emphasis is not None:
            result.append('<em>' + html.escape(emphasis) + '</em>')
        else:
            result.append('<br>')
    result.append(html.escape(text[last:]));return ''.join(result)


def cells(line):
    return re.split(r'(?<!\\)\|', line.strip().strip('|'))


def render_markdown(text, source, root):
    lines=text.splitlines(); out=[];i=0;heading_ids={}
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('```'):
            i+=1;block=[]
            while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
            out.append('<pre><code>'+html.escape('\n'.join(block))+'</code></pre>');i+=1;continue
        heading=re.match(r'^(#{1,6})\s+(.+)', line)
        if heading:
            level=len(heading[1]);title=heading[2];slug=re.sub(r'[^\w\s-]', '', title.lower());slug=re.sub(r'\s+', '-',slug)
            count=heading_ids.get(slug,0);heading_ids[slug]=count+1;slug+=f'-{count}' if count else ''
            out.append(f'<h{level} id="{html.escape(slug,quote=True)}">'+inline(title,source,root)+f'</h{level}>');i+=1;continue
        if i+1<len(lines) and '|' in line and re.fullmatch(r'[\s|:\-]+',lines[i+1]) and '-' in lines[i+1]:
            headers=cells(line);i+=2;rows=[]
            while i<len(lines) and lines[i].strip() and '|' in lines[i]:
                rows.append('<tr>'+''.join('<td>'+inline(cell.strip().replace('\\|','|'),source,root)+'</td>' for cell in cells(lines[i]))+'</tr>');i+=1
            out.append('<div class="table-scroll" role="region" aria-label="Report table" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+inline(cell.strip(),source,root)+'</th>' for cell in headers)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>');continue
        if line.startswith('>'):
            block=[]
            while i<len(lines) and lines[i].startswith('>'):block.append(lines[i][1:].lstrip());i+=1
            out.append('<blockquote><p>'+inline(' '.join(block),source,root)+'</p></blockquote>');continue
        item=re.match(r'^\s*(?:[-*]|\d+\.)\s+(.+)',line)
        if item:
            ordered=bool(re.match(r'^\s*\d+\.',line));tag='ol' if ordered else 'ul';items=[]
            while i<len(lines):
                pattern=r'^\s*\d+\.\s+(.+)' if ordered else r'^\s*[-*]\s+(.+)'
                m=re.match(pattern,lines[i])
                if not m:break
                part=[m[1]];i+=1
                while i<len(lines) and lines[i].startswith('  ') and not re.match(pattern,lines[i]):part.append(lines[i].strip());i+=1
                items.append('<li>'+inline(' '.join(part),source,root)+'</li>')
            out.append('<'+tag+'>'+''.join(items)+'</'+tag+'>');continue
        if re.fullmatch(r'\s*([-*_])\1{2,}\s*',line):out.append('<hr>');i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(?:#{1,6} |```|>|[-*] |\d+\. )',lines[i]):paragraph.append(lines[i]);i+=1
        out.append('<p>'+inline(' '.join(paragraph),source,root)+'</p>')
    return '\n'.join(out)+'\n'


def generate(root, output):
    root,output=Path(root),Path(output);folder=root/SOURCE
    if not folder.exists():return []
    for name in FILES:
        path=folder/name
        if not path.is_file() or path.is_symlink():raise ValueError('Missing or unsafe public report input: '+name)
    declared={}
    for line in (folder/'SHA256SUMS').read_text().splitlines():
        checksum,name=line.split('  ',1)
        if name not in FILES or name=='SHA256SUMS' or name in declared:raise ValueError('Unexpected public report checksum entry')
        declared[name]=checksum
    if set(declared)!=set(FILES)-{'SHA256SUMS'}:raise ValueError('Incomplete public report checksum inventory')
    for name,checksum in declared.items():
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=checksum:raise ValueError('Public report checksum mismatch: '+name)
    target=output/'reports';target.mkdir(parents=True,exist_ok=True)
    for name in FILES:(target/name).write_bytes((folder/name).read_bytes())
    for name in MARKDOWN:
        source=folder/name;text=source.read_text();title=text.splitlines()[0].removeprefix('# ')
        nav='<nav aria-label="Report collection"><a href="index.html">All reports</a><a href="claude.html">Claude report</a><a href="gemini.html">Gemini report</a><a href="copilot.html">Copilot report</a><a href="corrections.html">Corrections</a><a href="claude-capture-review.html">Claude UI capture review</a><a href="../">Catalogue</a></nav>'
        page='<!doctype html>\n<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="icon" href="data:,"><title>'+html.escape(title)+'</title><style>'+STYLE+'</style></head><body><a class="skip" href="#content">Skip to content</a><header>'+nav+'</header><main id="content">'+render_markdown(text,source,root)+'</main><footer><p>Independent experimental evaluation. Read the version, scope and corrections before quoting results.</p><a href="'+name+'">Reviewed Markdown source</a> · <a href="publication-manifest.json">Publication manifest</a> · <a href="SHA256SUMS">Source checksums</a></footer></body></html>\n'
        (target/PAGES[name]).write_text(page)
    return [{'label':'AI evaluation reports','url':REPORTS_URL,'kind':'evaluation-reports'}]
