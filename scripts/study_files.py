#!/usr/bin/env python3
"""Offline, non-executing file helpers. Python 3.10+; optional pypdf/python-pptx."""
import argparse
import hashlib
import json
import re
import shutil
import stat
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_name(value):
    name = re.sub(r'[\x00-\x1f<>:"/\\|?*]', '_', str(value)).strip(' .')[:150]
    if not name or name in {'.', '..'}:
        return 'untitled'
    if name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *[f'COM{i}' for i in range(1, 10)], *[f'LPT{i}' for i in range(1, 10)]}:
        name = '_' + name
    return name


def classify(path, context=''):
    """A reviewable suggestion, never an authoritative teaching-week mapping."""
    s = (str(path) + ' ' + context).lower().replace('_', ' ')
    suffix = Path(path).suffix.lower()
    if 'transcript' in s or 'lecture transcripts' in s:
        return 'Lecture Transcripts'
    if re.search(r'\b(solution|solutions|solns|answer|answers)\b|\b\w+sol\.', s):
        return 'Tutorial Solutions'
    if re.search(r'\b(tutorial files|datasets?|scaffold)\b', s) or suffix in {'.rmd', '.csv', '.json', '.xml', '.java', '.py', '.kts'}:
        return 'Tutorial Files'
    if re.search(r'\b(tutorials?|tute|workshop|labs?)\b', s):
        return 'Tutorial Questions'
    if re.search(r'\b(lectures?|slides?|notes|module\s*\d+|week\s*\d+)\b', s):
        return 'Lecture Materials'
    return 'Needs Review'


def extract_zip(source, out, max_bytes=4 * 1024**3):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    skipped, members = [], []
    with zipfile.ZipFile(source) as z:
        if sum(i.file_size for i in z.infolist()) > max_bytes:
            raise ValueError('ZIP exceeds extraction byte limit')
        for i in z.infolist():
            name = i.filename.replace('\\', '/')
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or re.match(r'^[A-Za-z]:', name):
                raise ValueError('Unsafe ZIP member path')
            if stat.S_ISLNK(i.external_attr >> 16):
                skipped.append({'path': name, 'reason': 'symlink'})
                continue
            if any(p.startswith('.') or p in {'__MACOSX', '__pycache__'} for p in rel.parts):
                skipped.append({'path': name, 'reason': 'cache_or_hidden'})
                continue
            dest = out.joinpath(*rel.parts)
            if not dest.resolve().is_relative_to(out):
                raise ValueError('ZIP member escapes destination')
            if i.is_dir():
                continue
            members.append((i, dest))
        # Validate all names before writing any member. Existing differing files are never replaced.
        for i, dest in members:
            data = z.read(i)
            if dest.exists() and dest.read_bytes() != data:
                raise ValueError(f'Extraction would overwrite a differing file: {dest.name}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    return {'written': len(members), 'skipped': skipped, 'original_sha256': sha256(source)}


class PlainHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}: self.hidden += 1
        if tag in {'p', 'div', 'li', 'h1', 'h2', 'h3', 'tr', 'br'}: self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in {'script', 'style'}: self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


def extract(source):
    p = Path(source)
    suffix = p.suffix.lower()
    units, warnings = [], []
    if suffix == '.pdf':
        try: from pypdf import PdfReader
        except ImportError as e: raise RuntimeError('PDF extraction needs pypdf; use host PDF tools instead if unavailable') from e
        for n, page in enumerate(PdfReader(p).pages, 1):
            text = page.extract_text() or ''
            units.append({'locator': f'page {n}', 'text': text})
            if len(text.strip()) < 60: warnings.append(f'page {n}: sparse text; visual/OCR review required')
        warnings.append('Visual review required for diagrams and equations; extracted text alone is not sufficient.')
    elif suffix == '.pptx':
        try: from pptx import Presentation
        except ImportError as e: raise RuntimeError('PPTX extraction needs python-pptx or the host slide tools') from e
        for n, slide in enumerate(Presentation(p).slides, 1):
            texts = [s.text for s in slide.shapes if s.has_text_frame]
            for shape in slide.shapes:
                if shape.has_table:
                    texts.extend(' | '.join(c.text for c in row.cells) for row in shape.table.rows)
            if slide.has_notes_slide:
                texts.append('Slide notes: ' + slide.notes_slide.notes_text_frame.text)
            units.append({'locator': f'slide {n}', 'text': '\n'.join(texts)})
        warnings.append('Images, charts and equations require visual review.')
    elif suffix == '.ipynb':
        nb = json.loads(p.read_text(encoding='utf-8-sig'))
        for n, cell in enumerate(nb.get('cells', []), 1):
            text = cell.get('source', '')
            if isinstance(text, list): text = ''.join(text)
            units.append({'locator': f'cell {n}', 'cell_type': cell.get('cell_type'), 'text': text})
        warnings.append('Notebook code was read, not executed. Inspect meaningful outputs/figures separately.')
    else:
        text = p.read_text(encoding='utf-8-sig')
        if suffix in {'.html', '.htm'}:
            parser = PlainHTML(); parser.feed(text); text = ''.join(parser.parts)
            warnings.append('HTML flattened to text; review original tables and figures.')
        for n, line in enumerate(text.splitlines(), 1):
            # Keep the exact original line numbering, including blank lines.
            units.append({'locator': f'line {n}', 'text': line})
    return {'source_name': p.name, 'sha256': sha256(p), 'units': units, 'warnings': warnings}


def inventory(root):
    root = Path(root).resolve()
    rows = []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink() or any(x.startswith('.') for x in p.relative_to(root).parts): continue
        rows.append({'path': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size,
                     'sha256': sha256(p), 'suggested_role': classify(p.relative_to(root)),
                     'week': None, 'mapping_status': 'unreviewed'})
    return {'root_name': root.name, 'resources': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('extract-zip', 'extract', 'inventory'):
        q = sub.add_parser(name); q.add_argument('source'); q.add_argument('--out', required=True)
    args = parser.parse_args()
    if args.command == 'extract-zip':
        result = extract_zip(args.source, args.out)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = extract(args.source) if args.command == 'extract' else inventory(args.source)
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Wrote {out.name}')


if __name__ == '__main__':
    main()
